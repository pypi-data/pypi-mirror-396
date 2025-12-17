"""
Model Resources - Direct dcisionai_workflow Integration

Exposes deployed models as MCP resources by directly importing
the model registry from dcisionai_workflow.shared.core.models.model_registry.
"""

import json
import logging
from mcp.types import Resource

# Handle both relative and absolute imports
try:
    from ..config import MCPConfig
except ImportError:
    import os
    import sys
    import importlib.util
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.py')
    config_spec = importlib.util.spec_from_file_location('config', config_path)
    config_module = importlib.util.module_from_spec(config_spec)
    config_spec.loader.exec_module(config_module)
    MCPConfig = config_module.MCPConfig

logger = logging.getLogger(__name__)


def get_model_resources() -> list[Resource]:
    """Get list of model resources"""
    return [
        Resource(
            uri="dcisionai://models/list",
            name="Deployed Models",
            description="List of all deployed DcisionAI models with metadata, capabilities, and usage examples",
            mimeType="application/json"
        )
    ]


async def read_model_resource(uri: str) -> str:
    """
    Read model resource by directly importing from dcisionai_workflow.shared.core.models.model_registry
    
    Args:
        uri: Resource URI (e.g., dcisionai://models/list)
        
    Returns:
        Resource content as JSON string (filtered by domain if configured)
    """
    if uri == "dcisionai://models/list":
        try:
            # Direct import from dcisionai_workflow.shared.core.models.model_registry (no HTTP call)
            # Add project root to sys.path if needed
            import os
            import sys
            
            # In Docker/Railway, PYTHONPATH is set to /app, so dcisionai_workflow should be importable directly
            # Get project root (two levels up from this file: resources/models.py -> dcisionai_mcp_server -> project root)
            current_file = os.path.abspath(__file__)
            project_root = os.path.abspath(os.path.join(os.path.dirname(current_file), '..', '..'))
            
            # Also check /app (Docker default) and current working directory
            possible_roots = [
                project_root,
                '/app',  # Docker default
                os.getcwd(),  # Current working directory
            ]
            
            # Add all possible roots to sys.path
            for root in possible_roots:
                if root and os.path.exists(root) and root not in sys.path:
                    sys.path.insert(0, root)
                    logger.info(f"Added to sys.path: {root}")
            
            # Log current sys.path for debugging
            logger.info(f"Current sys.path (first 5): {sys.path[:5]}")
            logger.info(f"PYTHONPATH env: {os.getenv('PYTHONPATH', 'not set')}")
            
            # Try importing model registry from dcisionai_workflow
            logger.info("Attempting to import from dcisionai_workflow.shared.core.models.model_registry...")
            try:
                from dcisionai_workflow.shared.core.models.model_registry import MODEL_REGISTRY, list_deployed_models
                logger.info("✅ Successfully imported model registry from dcisionai_workflow")
                
                # Get list of deployed models
                models_response = list_deployed_models() if callable(list_deployed_models) else {"models": list(MODEL_REGISTRY.keys())}
                
            except (ImportError, ModuleNotFoundError) as e:
                logger.warning(f"Could not import model registry: {e}, using fallback")
                # Fallback: Return empty list if model registry not available
                models_response = {"models": [], "message": "Model registry not available"}
            
            # Apply domain filtering if configured
            domain_filter = MCPConfig.get_domain_filter()
            if domain_filter != "all" and "models" in models_response:
                models_list = models_response.get("models", [])
                filtered_models = [
                    model for model in models_list
                    if model.get("domain", "").lower() == domain_filter.lower()
                ]
                models_response = {
                    "models": filtered_models,
                    "filtered_by_domain": domain_filter,
                    "total_models": len(models_list),
                    "filtered_count": len(filtered_models)
                }
            
            return json.dumps(models_response, indent=2)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error reading model resource: {e}", exc_info=True)
            
            # Include detailed error information in response for debugging
            error_response = {
                "error": str(e),
                "message": "Failed to load deployed models. Ensure dcisionai_workflow.shared.core.models.model_registry is accessible.",
                "error_type": type(e).__name__,
                "traceback": error_details.split('\n')[-10:] if len(error_details) > 10 else error_details.split('\n')
            }
            
            # Add sys.path info for debugging
            import sys
            error_response["sys_path"] = sys.path[:10]
            error_response["pythonpath_env"] = os.getenv('PYTHONPATH', 'not set')
            error_response["cwd"] = os.getcwd()
            
            return json.dumps(error_response, indent=2)
    else:
        return json.dumps({"error": f"Unknown resource URI: {uri}"})

