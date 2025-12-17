"""
MCP Error Handler

Standardized error handling for MCP tools following JSON-RPC 2.0 specification.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class MCPErrorCode(Enum):
    """JSON-RPC 2.0 error codes"""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    # Application-specific error codes (reserved range: -32000 to -32099)
    VALIDATION_ERROR = -32000
    NOT_FOUND_ERROR = -32001
    RESOURCE_ERROR = -32002
    TIMEOUT_ERROR = -32003


class MCPError(Exception):
    """Base exception for MCP errors"""
    
    def __init__(
        self,
        code: MCPErrorCode,
        message: str,
        data: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.message = message
        self.data = data or {}
        super().__init__(self.message)


def format_mcp_error(
    code: MCPErrorCode,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Format an error response following JSON-RPC 2.0 specification.
    
    Args:
        code: Error code from MCPErrorCode enum
        message: Human-readable error message
        data: Optional additional error data
        
    Returns:
        JSON-RPC 2.0 error object
    """
    error_obj = {
        "code": code.value,
        "message": message
    }
    
    if data:
        error_obj["data"] = data
    
    return error_obj


def format_validation_error(
    field: str,
    reason: str,
    suggestion: Optional[str] = None,
    example: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format a validation error with actionable details.
    
    Args:
        field: Field name that failed validation
        reason: Reason for validation failure
        suggestion: Optional suggestion for fixing the error
        example: Optional example of correct format
        
    Returns:
        JSON-RPC 2.0 error object with validation details
    """
    data = {
        "error_type": "ValidationError",
        "field": field,
        "reason": reason
    }
    
    if suggestion:
        data["suggestion"] = suggestion
    if example:
        data["example"] = example
    
    return format_mcp_error(
        code=MCPErrorCode.VALIDATION_ERROR,
        message=f"Validation error: {field} - {reason}",
        data=data
    )


def format_not_found_error(
    resource_type: str,
    resource_id: str,
    suggestion: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format a not found error.
    
    Args:
        resource_type: Type of resource (e.g., "model", "session")
        resource_id: ID of the resource that was not found
        suggestion: Optional suggestion
        
    Returns:
        JSON-RPC 2.0 error object
    """
    data = {
        "error_type": "NotFoundError",
        "resource_type": resource_type,
        "resource_id": resource_id
    }
    
    if suggestion:
        data["suggestion"] = suggestion
    
    return format_mcp_error(
        code=MCPErrorCode.NOT_FOUND_ERROR,
        message=f"{resource_type} '{resource_id}' not found",
        data=data
    )


def format_internal_error(
    error: Exception,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format an internal error.
    
    Args:
        error: The exception that occurred
        context: Optional context about where the error occurred
        
    Returns:
        JSON-RPC 2.0 error object
    """
    data = {
        "error_type": "InternalError",
        "error_class": type(error).__name__
    }
    
    if context:
        data["context"] = context
    
    # Log the full error for debugging
    logger.error(f"Internal error: {error}", exc_info=True)
    
    return format_mcp_error(
        code=MCPErrorCode.INTERNAL_ERROR,
        message="An internal error occurred",
        data=data
    )


def handle_tool_error(
    error: Exception,
    tool_name: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Handle an error from a tool execution and format appropriately.
    
    Args:
        error: The exception that occurred
        tool_name: Name of the tool that failed
        context: Optional context
        
    Returns:
        JSON-RPC 2.0 error object
    """
    if isinstance(error, MCPError):
        return format_mcp_error(error.code, error.message, error.data)
    
    # Handle specific error types
    if isinstance(error, ValueError):
        return format_validation_error(
            field="input",
            reason=str(error),
            suggestion="Check input format and required fields"
        )
    
    if isinstance(error, KeyError):
        return format_not_found_error(
            resource_type="resource",
            resource_id=str(error),
            suggestion="Verify the resource exists and is accessible"
        )
    
    # Default to internal error
    return format_internal_error(error, context=f"Tool: {tool_name}, {context or ''}")

