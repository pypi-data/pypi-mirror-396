from __future__ import annotations

import importlib
import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional

from jarvis_model import Error, ToolArgsValidationError, ToolDefinition, ToolInvocationRequest, ToolResult, ToolSummary, validate_tool_args


ToolHandler = Callable[[dict[str, Any], Optional[dict[str, Any]], Optional[dict[str, Any]]], dict[str, Any]]


@dataclass(frozen=True, slots=True)
class Tool:
    definition: ToolDefinition
    handler: ToolHandler


def load_domain_tools(domain_names: Iterable[str]) -> list[Tool]:
    tools: list[Tool] = []
    for domain_name in domain_names:
        module = importlib.import_module(f"tool_registry.domains.{domain_name}")
        load_fn = getattr(module, "load_tools", None)
        if not callable(load_fn):
            raise RuntimeError(f"Domain module tool_registry.domains.{domain_name} is missing load_tools()")
        loaded = load_fn()
        if not isinstance(loaded, list) or not all(isinstance(t, Tool) for t in loaded):
            raise RuntimeError(f"Domain module {domain_name} returned invalid tool list")
        tools.extend(loaded)
    return tools


class ToolCatalog:
    def __init__(self, tools: Iterable[Tool]):
        self._tools: dict[str, Tool] = {}
        for tool in tools:
            name = tool.definition.name
            if name in self._tools:
                raise ValueError(f"Duplicate tool name: {name}")
            self._tools[name] = tool

    def list_summaries(self) -> list[ToolSummary]:
        return [
            ToolSummary(
                name=tool.definition.name,
                description=tool.definition.description,
                version=tool.definition.version,
                tags=tool.definition.tags,
            )
            for tool in self._tools.values()
        ]

    def get_definition(self, name: str) -> ToolDefinition:
        tool = self._tools.get(name)
        if tool is None:
            raise KeyError(name)
        return tool.definition

    def invoke(self, name: str, request: ToolInvocationRequest) -> ToolResult:
        start = time.perf_counter()

        tool = self._tools.get(name)
        if tool is None:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return ToolResult(
                ok=False,
                error=Error(
                    code="tool.not_found",
                    message=f"Unknown tool: {name}",
                    details={"tool_name": name},
                    retryable=False,
                ),
                metrics={"latency_ms": latency_ms},
            )

        try:
            validate_tool_args(tool.definition.parameters, request.args)
        except ToolArgsValidationError as exc:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return ToolResult(ok=False, error=exc.error, metrics={"latency_ms": latency_ms})

        try:
            result = tool.handler(request.args, request.context, request.trace)
        except ValueError as exc:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return ToolResult(
                ok=False,
                error=Error(
                    code="tool.execution_error",
                    message=str(exc) or "Tool execution failed",
                    details={"tool_name": name},
                    retryable=False,
                ),
                metrics={"latency_ms": latency_ms},
            )
        except Exception as exc:  # pragma: no cover - defensive
            latency_ms = int((time.perf_counter() - start) * 1000)
            return ToolResult(
                ok=False,
                error=Error(
                    code="tool.handler_error",
                    message="Tool handler raised an exception",
                    details={"tool_name": name, "exception": repr(exc)},
                    retryable=False,
                ),
                metrics={"latency_ms": latency_ms},
            )

        latency_ms = int((time.perf_counter() - start) * 1000)
        return ToolResult(ok=True, result=result, metrics={"latency_ms": latency_ms})
