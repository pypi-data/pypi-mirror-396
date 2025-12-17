"""Shared utilities for MCP tool definitions.

This module provides common functionality used across all tool categories:
- Client access from MCP context
- Error handling wrapper for consistent error responses
- Validation error formatting
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar

from kdenlive_api.exceptions import KdenliveError, ValidationError
from mcp.server.fastmcp import Context
from pydantic import ValidationError as PydanticValidationError

T = TypeVar("T")


def get_client(ctx: Context):
    """Get Kdenlive client from MCP context.

    Args:
        ctx: MCP request context

    Returns:
        KdenliveClient instance from lifespan context
    """
    return ctx.request_context.lifespan_context.client


def format_validation_error(e: PydanticValidationError) -> str:
    """Format Pydantic validation error into a readable message.

    Args:
        e: Pydantic validation error

    Returns:
        Human-readable error message
    """
    errors = e.errors()
    if len(errors) == 1:
        err = errors[0]
        loc = ".".join(str(x) for x in err["loc"]) if err["loc"] else "input"
        return f"Invalid {loc}: {err['msg']}"
    else:
        messages = []
        for err in errors:
            loc = ".".join(str(x) for x in err["loc"]) if err["loc"] else "input"
            messages.append(f"  - {loc}: {err['msg']}")
        return "Validation errors:\n" + "\n".join(messages)


def mcp_tool_wrapper(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to wrap MCP tools with error handling.

    Catches validation errors and Kdenlive errors, returning them as
    structured error responses instead of raising exceptions.

    This ensures all tools have consistent error handling behavior.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs) -> dict[str, Any] | list[dict] | None:
        try:
            return await func(*args, **kwargs)
        except PydanticValidationError as e:
            return {"error": format_validation_error(e), "code": -32602}
        except ValidationError as e:
            return {"error": str(e), "code": e.code}
        except KdenliveError as e:
            return {"error": str(e), "code": e.code}
        except ValueError as e:
            return {"error": str(e), "code": -32602}
        except Exception as e:
            return {"error": f"Unexpected error: {e}", "code": -32603}

    return wrapper
