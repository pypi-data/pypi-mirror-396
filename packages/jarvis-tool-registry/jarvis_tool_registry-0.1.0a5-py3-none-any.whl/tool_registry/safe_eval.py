from __future__ import annotations

import ast
from typing import Any


class UnsafeExpressionError(ValueError):
    pass


_ALLOWED_BINOPS = (
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
)
_ALLOWED_UNARYOPS = (ast.UAdd, ast.USub)


def safe_eval_arithmetic(expression: str) -> float:
    """Evaluate a simple arithmetic expression safely.

    Supports numbers and +-*/%//** with parentheses. Disallows names/calls/attrs.
    """
    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise UnsafeExpressionError(f"Invalid expression syntax: {exc}") from exc

    node_count = sum(1 for _ in ast.walk(parsed))
    if node_count > 200:
        raise UnsafeExpressionError("Expression is too complex")

    return float(_eval_node(parsed.body))


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise UnsafeExpressionError("Only numeric constants are allowed")
        return float(node.value)

    if isinstance(node, ast.UnaryOp):
        if not isinstance(node.op, _ALLOWED_UNARYOPS):
            raise UnsafeExpressionError("Unsupported unary operator")
        operand = _eval_node(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise UnsafeExpressionError("Unsupported unary operator")

    if isinstance(node, ast.BinOp):
        if not isinstance(node.op, _ALLOWED_BINOPS):
            raise UnsafeExpressionError("Unsupported operator")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.FloorDiv):
            return left // right
        if isinstance(node.op, ast.Mod):
            return left % right
        if isinstance(node.op, ast.Pow):
            # Basic DoS guard.
            if abs(right) > 1000:
                raise UnsafeExpressionError("Exponent too large")
            return left**right
        raise UnsafeExpressionError("Unsupported operator")

    raise UnsafeExpressionError(f"Unsupported expression node: {type(node).__name__}")


def as_number(value: Any) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise UnsafeExpressionError("Result is not a number")
    return value

