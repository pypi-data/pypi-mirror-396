"""
MCP Tools Module

Centralized tool registry and error handling for MCP server.
"""

from .registry import (
    get_all_mcp_tools,
    get_tool_by_name,
    get_tool_metadata,
    get_all_tool_names,
    initialize_registry
)

from .error_handler import (
    MCPErrorCode,
    MCPError,
    format_mcp_error,
    format_validation_error,
    format_not_found_error,
    format_internal_error,
    handle_tool_error
)

__all__ = [
    # Registry functions
    'get_all_mcp_tools',
    'get_tool_by_name',
    'get_tool_metadata',
    'get_all_tool_names',
    'initialize_registry',
    # Error handling
    'MCPErrorCode',
    'MCPError',
    'format_mcp_error',
    'format_validation_error',
    'format_not_found_error',
    'format_internal_error',
    'handle_tool_error',
]
