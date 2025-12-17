from __future__ import annotations

import logging
import os
from typing import Sequence

from .server import ToolRegistryServer


def _split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def main(argv: Sequence[str] | None = None) -> int:
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

    host = os.getenv("TOOL_REGISTRY_HOST", "127.0.0.1")
    port = int(os.getenv("TOOL_REGISTRY_PORT", "8000"))
    domains = _split_csv(os.getenv("TOOL_REGISTRY_DOMAINS", "core"))

    server = ToolRegistryServer(host=host, port=port, domains=domains)
    server.serve_forever()
    return 0

