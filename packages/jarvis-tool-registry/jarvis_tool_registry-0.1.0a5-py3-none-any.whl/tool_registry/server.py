from __future__ import annotations

import json
import logging
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Optional
from urllib.parse import urlparse
from uuid import uuid4

from jarvis_model import Error, ToolInvocationRequest

from .catalog import ToolCatalog, load_domain_tools

logger = logging.getLogger("tool_registry.http")


class ToolRegistryApp:
    def __init__(self, catalog: ToolCatalog):
        self._catalog = catalog

    def handle(self, *, method: str, path: str, body: Optional[dict[str, Any]]) -> tuple[HTTPStatus, Any, Optional[str]]:
        parsed = urlparse(path)

        if method == "GET":
            return self._handle_get(parsed.path)
        if method == "POST":
            return self._handle_post(parsed.path, body)
        return HTTPStatus.METHOD_NOT_ALLOWED, {"error": Error(code="request.method_not_allowed", message="Not allowed").to_dict()}, None

    def _handle_get(self, path: str) -> tuple[HTTPStatus, Any, Optional[str]]:
        if path == "/v1/tools":
            payload = [s.to_planner_dict() for s in self._catalog.list_summaries()]
            return HTTPStatus.OK, payload, None

        if path.startswith("/v1/tools/"):
            tool_name = path[len("/v1/tools/") :]
            if not tool_name:
                return HTTPStatus.NOT_FOUND, {"error": Error(code="route.not_found", message="Not found").to_dict()}, None

            try:
                definition = self._catalog.get_definition(tool_name)
            except KeyError:
                return (
                    HTTPStatus.NOT_FOUND,
                    {
                        "error": Error(
                            code="tool.not_found",
                            message=f"Unknown tool: {tool_name}",
                            details={"tool_name": tool_name},
                        ).to_dict()
                    },
                    tool_name,
                )

            return HTTPStatus.OK, definition.to_dict(), tool_name

        return HTTPStatus.NOT_FOUND, {"error": Error(code="route.not_found", message="Not found").to_dict()}, None

    def _handle_post(self, path: str, body: Optional[dict[str, Any]]) -> tuple[HTTPStatus, Any, Optional[str]]:
        if not path.startswith("/v1/tools/") or not path.endswith(":invoke"):
            return HTTPStatus.NOT_FOUND, {"error": Error(code="route.not_found", message="Not found").to_dict()}, None

        tool_name = path[len("/v1/tools/") : -len(":invoke")]
        if not tool_name:
            return HTTPStatus.NOT_FOUND, {"error": Error(code="tool.not_found", message="Missing tool name").to_dict()}, None

        if body is None:
            return (
                HTTPStatus.BAD_REQUEST,
                {
                    "error": Error(
                        code="request.invalid_json",
                        message="Request body must be valid JSON",
                        retryable=False,
                    ).to_dict()
                },
                tool_name,
            )

        try:
            request = ToolInvocationRequest.from_dict(body)
        except Exception as exc:
            return (
                HTTPStatus.BAD_REQUEST,
                {"error": Error(code="request.invalid_shape", message=str(exc), retryable=False).to_dict()},
                tool_name,
            )

        result = self._catalog.invoke(tool_name, request)
        if result.ok:
            status = HTTPStatus.OK
        else:
            code = result.error.code if result.error else ""
            if code == "tool.not_found":
                status = HTTPStatus.NOT_FOUND
            elif code == "tool.invalid_args":
                status = HTTPStatus.BAD_REQUEST
            else:
                status = HTTPStatus.INTERNAL_SERVER_ERROR
        return status, result.to_dict(), tool_name


class ToolRegistryServer:
    def __init__(self, *, host: str, port: int, domains: list[str]):
        tools = load_domain_tools(domains)
        self._catalog = ToolCatalog(tools)
        self._app = ToolRegistryApp(self._catalog)
        self._host = host
        self._port = port
        self._httpd = ThreadingHTTPServer((host, port), self._make_handler())

    @property
    def server_address(self) -> tuple[str, int]:
        host, port = self._httpd.server_address[:2]
        return str(host), int(port)

    def serve_forever(self) -> None:
        host, port = self.server_address
        logger.info("tool_registry.start host=%s port=%s", host, port)
        self._httpd.serve_forever()

    def shutdown(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()

    def _make_handler(self):
        app = self._app

        class Handler(BaseHTTPRequestHandler):
            server_version = "ToolRegistry/0.1"

            def do_GET(self):  # noqa: N802
                started = time.perf_counter()
                request_id = self._get_request_id()
                try:
                    status, payload, tool_name = app.handle(method="GET", path=self.path, body=None)
                except Exception as exc:  # pragma: no cover - defensive
                    status, payload, tool_name = (
                        HTTPStatus.INTERNAL_SERVER_ERROR,
                        {"error": Error(code="server.error", message=str(exc)).to_dict()},
                        None,
                    )
                ok = int(status) < 400
                self._send_json(status=status, payload=payload, request_id=request_id)
                self._log(request_id, tool_name=tool_name, started=started, ok=ok)

            def do_POST(self):  # noqa: N802
                started = time.perf_counter()
                request_id = self._get_request_id()
                body = self._read_json_body()
                try:
                    status, payload, tool_name = app.handle(method="POST", path=self.path, body=body)
                except Exception as exc:  # pragma: no cover - defensive
                    status, payload, tool_name = (
                        HTTPStatus.INTERNAL_SERVER_ERROR,
                        {"error": Error(code="server.error", message=str(exc)).to_dict()},
                        None,
                    )
                ok = int(status) < 400
                self._send_json(status=status, payload=payload, request_id=request_id)
                self._log(request_id, tool_name=tool_name, started=started, ok=ok)

            def _read_json_body(self) -> Optional[dict[str, Any]]:
                length = self.headers.get("Content-Length")
                if not length:
                    return None
                try:
                    raw = self.rfile.read(int(length))
                except Exception:
                    return None
                try:
                    data = json.loads(raw.decode("utf-8"))
                except Exception:
                    return None
                return data if isinstance(data, dict) else None

            def _get_request_id(self) -> str:
                incoming = self.headers.get("X-Request-Id")
                if incoming and str(incoming).strip():
                    return str(incoming).strip()
                return str(uuid4())

            def _send_json(self, *, status: HTTPStatus, payload: Any, request_id: str) -> None:
                encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
                self.send_response(int(status))
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.send_header("X-Request-Id", request_id)
                self.end_headers()
                self.wfile.write(encoded)

            def _log(self, request_id: str, *, tool_name: Optional[str], started: float, ok: bool) -> None:
                latency_ms = int((time.perf_counter() - started) * 1000)
                logger.info(
                    "request request_id=%s tool_name=%s ok=%s latency_ms=%s method=%s path=%s",
                    request_id,
                    tool_name or "-",
                    ok,
                    latency_ms,
                    self.command,
                    self.path,
                )

            def log_message(self, format: str, *args):  # noqa: A002
                # Use structured logging via _log instead of default stderr logs.
                return

        return Handler
