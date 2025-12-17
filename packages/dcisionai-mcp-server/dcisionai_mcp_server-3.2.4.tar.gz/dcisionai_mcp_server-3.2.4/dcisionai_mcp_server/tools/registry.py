"""
MCP Tool Registry

Centralized registry for all MCP tools. Eliminates code duplication
by providing a single source of truth for tool discovery and execution.
"""

import logging
from typing import List, Callable, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Tool registry - populated on module load
_TOOL_REGISTRY: Dict[str, Callable] = {}
_TOOL_METADATA: Dict[str, Dict[str, Any]] = {}


def register_tool(tool_func: Callable) -> None:
    """
    Register a tool function in the registry.
    
    Args:
        tool_func: Tool function decorated with @mcp_tool
    """
    from dcisionai_workflow.tools.mcp_decorator import is_mcp_tool, get_mcp_tool_metadata
    
    if not is_mcp_tool(tool_func):
        logger.warning(f"Attempted to register non-MCP tool: {tool_func.__name__}")
        return
    
    metadata = get_mcp_tool_metadata(tool_func)
    if metadata:
        tool_name = metadata.get("name")
        if tool_name:
            _TOOL_REGISTRY[tool_name] = tool_func
            _TOOL_METADATA[tool_name] = metadata
            logger.debug(f"Registered MCP tool: {tool_name}")
        else:
            logger.warning(f"Tool {tool_func.__name__} has no name in metadata")
    else:
        logger.warning(f"Could not get metadata for tool: {tool_func.__name__}")


def get_all_mcp_tools() -> List[Callable]:
    """
    Get all registered MCP tools.
    
    Returns:
        List of tool functions
    """
    return list(_TOOL_REGISTRY.values())


def get_tool_by_name(tool_name: str) -> Optional[Callable]:
    """
    Get a tool function by name.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool function or None if not found
    """
    return _TOOL_REGISTRY.get(tool_name)


def get_tool_metadata(tool_name: str) -> Optional[Dict[str, Any]]:
    """
    Get metadata for a tool by name.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        Tool metadata dict or None if not found
    """
    return _TOOL_METADATA.get(tool_name)


def get_all_tool_names() -> List[str]:
    """
    Get all registered tool names.
    
    Returns:
        List of tool names
    """
    return list(_TOOL_REGISTRY.keys())


def initialize_registry() -> None:
    """
    Initialize the tool registry by importing and registering all MCP tools.
    
    This should be called once at module load time.
    """
    logger.info("Initializing MCP tool registry...")
    
    try:
        # Import optimization tools
        from dcisionai_workflow.tools.optimization.mcp_tools import (
            dcisionai_solve,
            dcisionai_solve_with_model,
            dcisionai_adhoc_optimize
        )
        
        # Import NLP tools
        from dcisionai_workflow.tools.nlp.mcp_tools import dcisionai_nlp_query
        
        # Import data tools (excluding internal engineering tools)
        from dcisionai_workflow.tools.data.mcp_tools import (
            dcisionai_map_concepts,
            dcisionai_prepare_data,
            dcisionai_prepare_salesforce_data
            # NOTE: dcisionai_list_templates and dcisionai_register_template
            # are NOT imported - they are internal engineering tools
        )
        
        # Import intent tools (IDE-focused)
        from dcisionai_workflow.tools.intent.mcp_tools import (
            dcisionai_analyze_problem,
            dcisionai_validate_constraints,
            dcisionai_search_problem_types,
            dcisionai_get_problem_type_schema
        )
        
        # Import client tools (workflow management)
        from dcisionai_workflow.tools.optimization.mcp_tools import (
            dcisionai_get_workflow_status,
            dcisionai_cancel_workflow,
            dcisionai_get_result,
            dcisionai_export_result,
            dcisionai_deploy_model
        )
        
        # Register all public tools
        register_tool(dcisionai_solve)
        register_tool(dcisionai_solve_with_model)
        register_tool(dcisionai_adhoc_optimize)
        register_tool(dcisionai_nlp_query)
        register_tool(dcisionai_map_concepts)
        register_tool(dcisionai_prepare_data)
        register_tool(dcisionai_prepare_salesforce_data)
        # IDE tools
        register_tool(dcisionai_analyze_problem)
        register_tool(dcisionai_validate_constraints)
        register_tool(dcisionai_search_problem_types)
        register_tool(dcisionai_get_problem_type_schema)
        # Client tools
        register_tool(dcisionai_get_workflow_status)
        register_tool(dcisionai_cancel_workflow)
        register_tool(dcisionai_get_result)
        register_tool(dcisionai_export_result)
        register_tool(dcisionai_deploy_model)
        
        logger.info(f"✅ Registered {len(_TOOL_REGISTRY)} MCP tools: {', '.join(_TOOL_REGISTRY.keys())}")
        
    except ImportError as e:
        logger.error(f"Failed to import MCP tools: {e}", exc_info=True)
        logger.error("Tool registry may be incomplete")
    except Exception as e:
        logger.error(f"Error initializing tool registry: {e}", exc_info=True)


# Initialize registry on module load
initialize_registry()

