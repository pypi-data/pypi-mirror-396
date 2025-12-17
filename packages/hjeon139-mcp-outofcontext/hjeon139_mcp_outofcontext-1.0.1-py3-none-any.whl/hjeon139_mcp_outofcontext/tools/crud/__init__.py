"""CRUD tools for context management."""

__all__ = ["register_tools"]


def register_tools() -> None:
    """Register all CRUD tools with FastMCP.

    Tools are registered via @mcp.tool() decorators when imported.
    This function ensures all tool modules are imported.
    """
    from . import (
        delete_context,  # noqa: F401
        get_context,  # noqa: F401
        put_context,  # noqa: F401
    )
