from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

from jarvis_model import ToolDefinition

from ..catalog import Tool
from ..safe_eval import UnsafeExpressionError, safe_eval_arithmetic


def load_tools() -> list[Tool]:
    return [
        Tool(definition=_echo_definition(), handler=_echo),
        Tool(definition=_calc_definition(), handler=_calc),
        Tool(definition=_time_now_definition(), handler=_time_now),
    ]


def _echo_definition() -> ToolDefinition:
    return ToolDefinition(
        name="echo",
        description="Echoes the provided text.",
        version="0.1.0",
        parameters={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
        tags=["core"],
    )


def _calc_definition() -> ToolDefinition:
    return ToolDefinition(
        name="calc",
        description="Evaluate a simple arithmetic expression.",
        version="0.1.0",
        parameters={
            "type": "object",
            "properties": {"expression": {"type": "string", "minLength": 1}},
            "required": ["expression"],
            "additionalProperties": False,
        },
        tags=["core"],
    )


def _time_now_definition() -> ToolDefinition:
    return ToolDefinition(
        name="time_now",
        description="Return the current time as an ISO 8601 timestamp in the provided IANA timezone (default UTC).",
        version="0.1.0",
        parameters={
            "type": "object",
            "properties": {"tz": {"type": ["string", "null"], "default": "UTC"}},
            "required": ["tz"],
            "additionalProperties": False,
        },
        tags=["core"],
    )


def _echo(args: dict[str, Any], context: Optional[dict[str, Any]], trace: Optional[dict[str, Any]]) -> dict[str, Any]:
    return {"text": str(args.get("text") or "")}


def _calc(args: dict[str, Any], context: Optional[dict[str, Any]], trace: Optional[dict[str, Any]]) -> dict[str, Any]:
    expression = str(args.get("expression") or "")
    try:
        value = safe_eval_arithmetic(expression)
    except UnsafeExpressionError as exc:
        # Raise a regular exception; catalog will normalize it.
        raise ValueError(str(exc)) from exc
    return {"expression": expression, "value": value}


def _time_now(args: dict[str, Any], context: Optional[dict[str, Any]], trace: Optional[dict[str, Any]]) -> dict[str, Any]:
    tz_name = str(args.get("tz") or "UTC")
    try:
        tz = ZoneInfo(tz_name)
    except Exception as exc:
        raise ValueError(f"Unknown timezone: {tz_name}") from exc
    now = datetime.now(tz=tz)
    return {"tz": tz_name, "iso": now.isoformat()}
