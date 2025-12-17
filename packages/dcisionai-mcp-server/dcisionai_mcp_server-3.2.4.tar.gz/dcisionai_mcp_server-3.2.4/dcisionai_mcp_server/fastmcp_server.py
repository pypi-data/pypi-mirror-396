"""
DcisionAI MCP Server - FastMCP Server

FastMCP-compatible server with direct dcisionai_workflow integration.
No HTTP client layer - all imports are direct Python imports.

Entrypoint for FastMCP Cloud: dcisionai_mcp_server.fastmcp_server:mcp
"""

import os
import sys
import json
import logging
import asyncio
from fastmcp import FastMCP
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# CRITICAL: Ensure project root is in Python path for dcisionai_kb and dcisionai_workflow
# This must happen BEFORE any imports that use these modules
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Verify dcisionai_kb is available (core to architecture - Pinecone templates)
try:
    import dcisionai_kb
    _kb_available = True
except ImportError:
    _kb_available = False
    import logging
    _logger = logging.getLogger(__name__)
    _logger.warning("⚠️ dcisionai_kb not found at module load time. Will try to import dynamically.")

# Initialize logger early for error reporting
logger = logging.getLogger(__name__)

# First, always try to load MCPConfig (required for server initialization)
# This must be done before any code that uses MCPConfig
MCPConfig = None
try:
    from .config import MCPConfig
except (ImportError, Exception) as config_import_err:
    # Fallback: Load config using importlib (for when loaded via importlib)
    try:
        import importlib.util
        config_path = os.path.join(os.path.dirname(__file__), 'config.py')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        config_spec = importlib.util.spec_from_file_location('config', config_path)
        config_module = importlib.util.module_from_spec(config_spec)
        config_spec.loader.exec_module(config_module)
        MCPConfig = config_module.MCPConfig
        logger.info("✅ Loaded MCPConfig via importlib fallback")
    except Exception as config_err:
        logger.error(f"Failed to load MCPConfig: {config_err}")
        logger.error(f"Original import error: {config_import_err}")
        raise ImportError(f"MCPConfig is required but could not be loaded: {config_err}")

# Verify MCPConfig was loaded
if MCPConfig is None:
    raise ImportError("MCPConfig is required but was not loaded")

# Now import tools using centralized registry
try:
    # Use centralized tool registry (eliminates code duplication)
    from .tools.registry import get_all_mcp_tools, get_tool_by_name
    from .resources.models import read_model_resource
    from .resources.solvers import read_solver_resource
except (ImportError, Exception) as e:
    # Fallback for when loaded via importlib (no parent package)
    try:
        import importlib.util
        registry_path = os.path.join(os.path.dirname(__file__), 'tools', 'registry.py')
        if os.path.exists(registry_path):
            registry_spec = importlib.util.spec_from_file_location('tool_registry', registry_path)
            registry_module = importlib.util.module_from_spec(registry_spec)
            registry_spec.loader.exec_module(registry_module)
            get_all_mcp_tools = registry_module.get_all_mcp_tools
            get_tool_by_name = registry_module.get_tool_by_name
        else:
            logger.warning(f"Tool registry not found at {registry_path}, falling back to direct imports")
            raise ImportError("Tool registry not available")
    except Exception as registry_err:
        # Final fallback: direct imports (legacy)
        logger.warning(f"Could not load tool registry: {registry_err}, using direct imports")
        try:
            from dcisionai_workflow.tools.optimization.mcp_tools import (
                dcisionai_solve,
                dcisionai_solve_with_model,
                dcisionai_adhoc_optimize
            )
            from dcisionai_workflow.tools.nlp.mcp_tools import dcisionai_nlp_query
            from dcisionai_workflow.tools.data.mcp_tools import (
                dcisionai_map_concepts,
                dcisionai_prepare_data,
                dcisionai_prepare_salesforce_data
                # NOTE: Template tools removed - they are internal engineering tools
            )
            # Create fallback registry function
            def get_all_mcp_tools():
                return [
                    dcisionai_solve,
                    dcisionai_solve_with_model,
                    dcisionai_adhoc_optimize,
                    dcisionai_nlp_query,
                    dcisionai_map_concepts,
                    dcisionai_prepare_data,
                    dcisionai_prepare_salesforce_data
                ]
            def get_tool_by_name(name: str):
                tools_map = {
                    "dcisionai_solve": dcisionai_solve,
                    "dcisionai_solve_with_model": dcisionai_solve_with_model,
                    "dcisionai_adhoc_optimize": dcisionai_adhoc_optimize,
                    "dcisionai_nlp_query": dcisionai_nlp_query,
                    "dcisionai_map_concepts": dcisionai_map_concepts,
                    "dcisionai_prepare_data": dcisionai_prepare_data,
                    "dcisionai_prepare_salesforce_data": dcisionai_prepare_salesforce_data
                }
                return tools_map.get(name)
        except ImportError as import_err:
            logger.error(f"Failed to import tools: {import_err}")
            logger.error("Tools are required - server may not function correctly")
    
    # Load resources (still needed even if tools import fails)
    try:
        import importlib.util
        resources_models_path = os.path.join(os.path.dirname(__file__), 'resources', 'models.py')
        resources_models_spec = importlib.util.spec_from_file_location('resources_models', resources_models_path)
        resources_models_module = importlib.util.module_from_spec(resources_models_spec)
        resources_models_spec.loader.exec_module(resources_models_module)
        read_model_resource = resources_models_module.read_model_resource
        
        resources_solvers_path = os.path.join(os.path.dirname(__file__), 'resources', 'solvers.py')
        resources_solvers_spec = importlib.util.spec_from_file_location('resources_solvers', resources_solvers_path)
        resources_solvers_module = importlib.util.module_from_spec(resources_solvers_spec)
        resources_solvers_spec.loader.exec_module(resources_solvers_module)
        read_solver_resource = resources_solvers_module.read_solver_resource
    except Exception as resource_err:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Could not load resources: {resource_err}")

# Store registry functions in module-level variables for easy access
# This ensures they're available even when loaded via importlib
try:
    _REGISTRY_GET_ALL_TOOLS = get_all_mcp_tools
    _REGISTRY_GET_TOOL_BY_NAME = get_tool_by_name
except NameError:
    # Functions not yet imported (will be set by importlib fallback)
    _REGISTRY_GET_ALL_TOOLS = None
    _REGISTRY_GET_TOOL_BY_NAME = None
        # Resources will be handled by fallback functions below

# Initialize logger early for error reporting
logger = logging.getLogger(__name__)

# Verify critical imports succeeded
if 'read_model_resource' not in globals():
    logger.error("❌ CRITICAL: read_model_resource not imported!")
    # Create a fallback that returns an error
    async def read_model_resource(uri: str) -> str:
        import json
        return json.dumps({
            "error": "Model resource handler not available",
            "message": "Failed to import resources.models module"
        })

if 'read_solver_resource' not in globals():
    logger.error("❌ CRITICAL: read_solver_resource not imported!")
    # Create a fallback that returns an error
    async def read_solver_resource(uri: str) -> str:
        import json
        return json.dumps({
            "error": "Solver resource handler not available",
            "message": "Failed to import resources.solvers module"
        })


def _convert_python_to_json_types(obj):
    """Recursively convert Python types to JSON-compatible types"""
    if isinstance(obj, dict):
        return {k: _convert_python_to_json_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_python_to_json_types(item) for item in obj]
    elif isinstance(obj, bool):
        # Python bool -> JSON boolean (but this is already handled by json.dumps)
        return obj
    elif obj is None:
        return None
    else:
        return obj

# Create FastMCP app with domain-aware name
try:
    _domain_filter = MCPConfig.get_domain_filter()
    if _domain_filter != "all":
        server_name = f"DcisionAI Optimization Server 2.0 - {_domain_filter.upper()} Edition"
    else:
        server_name = "DcisionAI Optimization Server 2.0"
except Exception as e:
    logger.warning(f"Failed to get domain filter: {e}, using default")
    server_name = "DcisionAI Optimization Server 2.0"

try:
    mcp = FastMCP(server_name)
except Exception as e:
    logger.error(f"Failed to create FastMCP instance: {e}", exc_info=True)
    raise

# Create our own FastAPI app to have full control over WebSocket endpoints
# FastMCP will be mounted on this app
try:
    app = FastAPI(title=server_name)
except Exception as e:
    logger.error(f"Failed to create FastAPI app: {e}", exc_info=True)
    raise

# Add CORS middleware for web clients
try:
    # Process CORS origins - handle wildcards for Vercel
    cors_origins = MCPConfig.CORS_ORIGINS if MCPConfig else ["*"]
    
    # Check if we're in production (Railway sets PORT env var)
    is_production = os.getenv("PORT") is not None or os.getenv("RAILWAY_ENVIRONMENT") is not None
    
    # FastAPI CORSMiddleware doesn't support wildcards directly
    # For production, allow all origins since Vercel uses dynamic subdomains
    # 
    # NOTE: Railway domains don't need to be in CORS origins because:
    # - Railway = BACKEND (server) - where the API runs
    # - Vercel = FRONTEND (client) - where requests come from
    # - CORS origins = CLIENT domains that can call the backend
    # 
    # This is safe because:
    # 1. Railway URL is already protected
    # 2. We use credentials check
    # 3. API key authentication can be added if needed
    processed_origins = []
    has_wildcard = False
    
    for origin in cors_origins:
        origin = origin.strip()
        if not origin:
            continue
        if origin == "*" or "*.vercel.app" in origin:
            has_wildcard = True
            break
        processed_origins.append(origin)
    
    # In production or if wildcard detected, allow all origins
    if is_production or has_wildcard:
        processed_origins = ["*"]
        logger.info("CORS: Production mode - allowing all origins (Vercel dynamic subdomains)")
    elif not processed_origins:
        processed_origins = ["*"]  # Fallback to allow all if empty
    
    logger.info(f"CORS origins configured: {processed_origins} (production: {is_production})")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=processed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
except Exception as e:
    logger.warning(f"Failed to add CORS middleware: {e}, continuing without it")
    # Fallback: allow all origins if CORS setup fails
    try:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.warning("CORS: Fallback to allow all origins")
    except Exception as fallback_error:
        logger.error(f"CORS fallback also failed: {fallback_error}")

# CRITICAL: Add health endpoint FIRST before any other routes
# This ensures healthcheck works even if other imports fail
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment - must be available immediately"""
    try:
        return JSONResponse({
            "status": "ok",
            "service": "dcisionai-mcp-server",
            "version": "3.2.1",
            "dcisionai_kb_available": _kb_available
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return JSONResponse({
            "status": "error",
            "error": str(e)
        }, status_code=500)

# Try to mount FastMCP on our app if possible
# NOTE: We define our own routes directly on app, so FastMCP mounting is optional
# If FastMCP mounting succeeds, it might conflict with our routes, so we skip it
try:
    # FastMCP may expose routes we can mount
    fastmcp_app = getattr(mcp, 'app', None) or getattr(mcp, '_app', None)
    if fastmcp_app and isinstance(fastmcp_app, FastAPI):
        # Don't mount FastMCP - we define our own routes directly on app
        # Mounting would cause route conflicts since we define /mcp/* routes ourselves
        logger.info("⚠️  FastMCP app detected but not mounted (using direct routes)")
except Exception as e:
    logger.debug(f"FastMCP app check: {e}")

# Add checkpoint API endpoints (Phase 5)
try:
    from .api.checkpoints import router as checkpoint_router
    app.include_router(checkpoint_router)
    logger.info("✅ Checkpoint API endpoints registered")
except ImportError:
    logger.warning("Checkpoint API endpoints not available")

# Add async job queue API endpoints
try:
    from .api.jobs import router as jobs_router
    app.include_router(jobs_router)
    logger.info("✅ Async job queue API endpoints registered")
except (ImportError, Exception) as e:
    # Fallback for when loaded via importlib (no parent package)
    try:
        import importlib.util
        jobs_path = os.path.join(os.path.dirname(__file__), 'api', 'jobs.py')
        if os.path.exists(jobs_path):
            jobs_spec = importlib.util.spec_from_file_location('jobs_api', jobs_path)
            jobs_module = importlib.util.module_from_spec(jobs_spec)
            jobs_spec.loader.exec_module(jobs_module)
            jobs_router = jobs_module.router
            app.include_router(jobs_router)
            logger.info("✅ Async job queue API endpoints registered (via importlib)")
        else:
            logger.warning(f"Async job queue API not found at: {jobs_path}")
    except Exception as fallback_error:
        logger.warning(f"Async job queue API endpoints not available: {e}, fallback: {fallback_error}")

@app.get("/api/workflow/capabilities")
async def get_workflow_capabilities_endpoint():
    """
    Get workflow capabilities (available features and tools).
    
    Returns the default enabled features/tools and all available options.
    This allows the UI to dynamically configure itself based on the workflow graph.
    """
    try:
        # Return basic workflow capabilities for the UI
        # This allows the UI to configure available tools and features
        capabilities = {
            "enabled_tools": [
                "intent_discovery",
                "data_preparation",
                "solver",
                "explanation"
            ],
            "enabled_features": [
                "vagueness_detection",
                "template_matching",
                "entity_extraction",
                "data_generation",
                "optimization_solving"
            ]
        }
        return JSONResponse(capabilities)
    except Exception as e:
        import traceback
        logger.error(f"Error getting workflow capabilities: {e}", exc_info=True)
        return JSONResponse({
            "error": str(e),
            "traceback": traceback.format_exc().split('\n')[-10:]
        }, status_code=500)

@app.get("/api/models")
async def get_models_endpoint():
    """Convenience endpoint to get models list - calls MCP resource internally"""
    try:
        models_json = await read_model_resource("dcisionai://models/list")
        models_dict = json.loads(models_json)
        # If the response contains an error, return it as JSON but with 500 status
        if "error" in models_dict:
            return JSONResponse(models_dict, status_code=500)
        return JSONResponse(models_dict)
    except Exception as e:
        logger.error(f"Error in get_models_endpoint: {e}", exc_info=True)
        import traceback
        return JSONResponse({
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc().split('\n')[-10:]
        }, status_code=500)

@app.post("/mcp/tools/list")
async def mcp_list_tools(request: Request):
    """
    MCP-compliant tools/list endpoint (JSON-RPC 2.0)
    
    Returns list of available tools following MCP specification.
    This is the standard MCP protocol method for tool discovery.
    """
    request_id = 1
    try:
        body = await request.json()
        request_id = body.get("id", 1)
        
        # Use centralized tool registry (eliminates code duplication, ensures all 16 tools are included)
        try:
            from dcisionai_workflow.tools.mcp_decorator import is_mcp_tool, get_mcp_tool_metadata
            
            # Get registry function - try multiple strategies
            registry_func = None
            
            # Strategy 1: Use module-level stored function
            if _REGISTRY_GET_ALL_TOOLS:
                registry_func = _REGISTRY_GET_ALL_TOOLS
                logger.info("Using module-level stored _REGISTRY_GET_ALL_TOOLS")
            
            # Strategy 2: Try direct access to module-level function
            if not registry_func:
                try:
                    registry_func = get_all_mcp_tools
                    logger.info("Using direct get_all_mcp_tools")
                except NameError:
                    pass
            
            # Strategy 3: Try relative import
            if not registry_func:
                try:
                    from .tools.registry import get_all_mcp_tools
                    registry_func = get_all_mcp_tools
                    logger.info("Using relative import get_all_mcp_tools")
                except ImportError:
                    pass
            
            # Strategy 4: Try absolute import
            if not registry_func:
                try:
                    from dcisionai_mcp_server.tools.registry import get_all_mcp_tools
                    registry_func = get_all_mcp_tools
                    logger.info("Using absolute import get_all_mcp_tools")
                except ImportError as abs_err:
                    logger.error(f"All import strategies failed: {abs_err}")
                    raise ImportError("Could not import get_all_mcp_tools from any source")
            
            # Get all tools from registry (includes all 16 public tools)
            all_tool_functions = registry_func()
            logger.info(f"Registry returned {len(all_tool_functions)} tool functions")
            
            # Extract metadata for each tool
            tools = []
            for func in all_tool_functions:
                try:
                    if is_mcp_tool(func):
                        metadata = get_mcp_tool_metadata(func)
                        if metadata:
                            tools.append(metadata)
                        else:
                            logger.warning(f"Tool {func.__name__} has no metadata")
                    else:
                        logger.warning(f"Tool {func.__name__} is not decorated with @mcp_tool")
                except Exception as tool_err:
                    logger.error(f"Error processing tool {func.__name__}: {tool_err}", exc_info=True)
            
            logger.info(f"MCP tools/list: Returning {len(tools)} tools from registry")
        except Exception as e:
            logger.error(f"Error loading tools from registry: {e}", exc_info=True)
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            tools = []
        
        if not tools:
            logger.warning("No tools found - server may not function correctly")
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": "No tools available"
                }
            }, status_code=500)
        
        # Convert Tool metadata dicts to MCP-compliant format
        # get_mcp_tool_metadata returns dicts with keys: name, description, input_schema
        tools_list = []
        for tool in tools:
            try:
                # get_mcp_tool_metadata returns a dict
                tool_name = tool.get("name", "unknown")
                tool_description = tool.get("description", "")
                input_schema = tool.get("input_schema", {})  # Note: decorator uses "input_schema" (snake_case)
                
                # Convert inputSchema to JSON-compatible format (Python False/True -> JSON false/true)
                if isinstance(input_schema, dict):
                    # Serialize to JSON string and parse back to convert Python booleans to JSON booleans
                    # This ensures Python False/True becomes JSON false/true
                    try:
                        input_schema = json.loads(json.dumps(input_schema))
                    except Exception as e:
                        logger.warning(f"Failed to convert inputSchema for {tool_name}: {e}, using original")
                        # Fallback: manually convert booleans
                        input_schema = _convert_python_to_json_types(input_schema)
                
                tool_dict = {
                    "name": tool_name,
                    "description": tool_description,
                    "inputSchema": input_schema  # MCP spec uses camelCase
                }
                tools_list.append(tool_dict)
            except Exception as e:
                tool_name_str = tool.get("name", "unknown") if isinstance(tool, dict) else "unknown"
                logger.error(f"Error processing tool {tool_name_str}: {e}", exc_info=True)
                # Skip this tool but continue with others
                continue
        
        # Return JSON-RPC 2.0 compliant response
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools_list
            }
        })
    except Exception as e:
        logger.error(f"Error in mcp_list_tools: {e}", exc_info=True)
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        }, status_code=500)

@app.get("/api/tools")
async def get_tools_endpoint():
    """
    Convenience REST endpoint for tools list (non-MCP, for backward compatibility)
    
    NOTE: This is NOT MCP-compliant. Use POST /mcp/tools/list with JSON-RPC 2.0 for MCP compliance.
    """
    try:
        # Use centralized tool registry (eliminates code duplication)
        try:
            from dcisionai_workflow.tools.mcp_decorator import is_mcp_tool, get_mcp_tool_metadata
            from .tools.registry import get_all_mcp_tools
            
            # Get all tools from registry
            all_tool_functions = get_all_mcp_tools()
            
            # Extract metadata for each tool
            tools = [get_mcp_tool_metadata(func) for func in all_tool_functions if is_mcp_tool(func)]
            tools = [t for t in tools if t is not None]  # Filter out None values
        except Exception as e:
            logger.error(f"Error loading tools from registry: {e}", exc_info=True)
            tools = []
        
        if not tools:
            logger.warning("No tools found - server may not function correctly")
            return JSONResponse({"error": "No tools available"}, status_code=500)
        
        # Convert Tool objects to dictionaries
        tools_list = []
        for tool in tools:
            try:
                # Convert inputSchema to JSON-compatible format (Python False/True -> JSON false/true)
                input_schema = tool.inputSchema
                if isinstance(input_schema, dict):
                    # Serialize to JSON string and parse back to convert Python booleans to JSON booleans
                    try:
                        input_schema = json.loads(json.dumps(input_schema))
                    except Exception as e:
                        logger.warning(f"Failed to convert inputSchema for {tool.name}: {e}, using original")
                        # Fallback: manually convert booleans
                        input_schema = _convert_python_to_json_types(input_schema)
                
                tool_dict = {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": input_schema
                }
                tools_list.append(tool_dict)
            except Exception as e:
                logger.error(f"Error processing tool {tool.name}: {e}", exc_info=True)
                # Skip this tool but continue with others
                continue
        return JSONResponse({"tools": tools_list})
    except Exception as e:
        logger.error(f"Error in get_tools_endpoint: {e}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/mcp/tools/call")
async def mcp_call_tool(request: Request):
    """
    HTTP wrapper for MCP tool calls (JSON-RPC 2.0 format)
    Allows Salesforce and other HTTP clients to call MCP tools
    """
    from fastapi import HTTPException
    
    try:
        body = await request.json()
        tool_name = body.get("name") or (body.get("params", {}).get("name") if body.get("params") else None)
        arguments = body.get("arguments") or (body.get("params", {}).get("arguments") if body.get("params") else {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="Tool name required")
        
        logger.info(f"HTTP JSON-RPC call: {tool_name} with args: {list(arguments.keys())}")
        
        # Use centralized tool registry
        try:
            # Try relative import first, fallback to absolute import (for importlib loading)
            try:
                from .tools.registry import get_tool_by_name
                from .tools.error_handler import handle_tool_error, format_not_found_error
            except ImportError:
                from dcisionai_mcp_server.tools.registry import get_tool_by_name
                from dcisionai_mcp_server.tools.error_handler import handle_tool_error, format_not_found_error
        except ImportError as import_err:
            logger.error(f"Failed to import tool registry or error handler: {import_err}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Tool registry not available: {import_err}"
            )
        
        try:
            # Get tool from registry
            tool_func = get_tool_by_name(tool_name)
            if not tool_func:
                error_data = format_not_found_error(
                    resource_type="tool",
                    resource_id=tool_name,
                    suggestion=f"Use POST /mcp/tools/list to see available tools"
                )
                raise HTTPException(
                    status_code=404,
                    detail=error_data
                )
            
            # Call tool with arguments (with timeout protection)
            # Fast tools (< 5s): no timeout needed
            # Medium tools (5-30s): 60s timeout
            # Slow tools (> 30s): 120s timeout (for classification tools)
            import asyncio
            tool_timeout = 120.0  # Default 2 minutes for classification tools
            
            # Adjust timeout based on tool type
            if tool_name in ["dcisionai_analyze_problem"]:
                tool_timeout = 180.0  # 3 minutes for full classification
            elif tool_name in ["dcisionai_validate_constraints", "dcisionai_search_problem_types", "dcisionai_get_problem_type_schema"]:
                tool_timeout = 30.0  # 30 seconds for fast IDE tools
            
            try:
                result_text_contents = await asyncio.wait_for(
                    tool_func(**arguments),
                    timeout=tool_timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"Tool {tool_name} exceeded timeout of {tool_timeout}s")
                error_data = {
                    "error": "Tool execution timeout",
                    "message": f"Tool '{tool_name}' exceeded maximum execution time of {tool_timeout} seconds",
                    "tool": tool_name,
                    "timeout_seconds": tool_timeout,
                    "suggestion": "For long-running operations, consider using the async workflow endpoint (/ws/{session_id})"
                }
                raise HTTPException(status_code=504, detail=error_data)
            
            # Extract text from TextContent objects
            if result_text_contents and len(result_text_contents) > 0:
                text_content = result_text_contents[0].text if hasattr(result_text_contents[0], 'text') else str(result_text_contents[0])
                try:
                    result_json = json.loads(text_content)
                    return {"result": result_json}
                except json.JSONDecodeError:
                    return {"result": {"text": text_content}}
            return {"result": {}}
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}", exc_info=True)
            try:
                error_data = handle_tool_error(e, tool_name, "mcp_call_tool")
            except NameError:
                # Fallback if handle_tool_error wasn't imported
                error_data = {"error": str(e), "tool": tool_name}
            raise HTTPException(
                status_code=500,
                detail=error_data
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in mcp_call_tool: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mcp/resources/{uri:path}")
async def mcp_read_resource(uri: str):
    """
    HTTP wrapper for MCP resource reading
    Allows Salesforce and other HTTP clients to read MCP resources
    """
    try:
        # Normalize URI
        if not uri.startswith("dcisionai://"):
            uri = f"dcisionai://{uri}"
        
        logger.info(f"HTTP resource read: {uri}")
        
        result_str = None
        if uri == "dcisionai://models/list":
            result_str = await read_model_resource(uri)
        elif uri == "dcisionai://solvers/list":
            result_str = await read_solver_resource(uri)
        else:
            return JSONResponse({"error": f"Unknown resource URI: {uri}"}, status_code=404)
        
        return JSONResponse(json.loads(result_str))
        
    except Exception as e:
        logger.error(f"Error reading MCP resource: {e}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for streaming workflow updates (React UI)
    
    Protocol:
    1. Client connects to /ws/{session_id}
    2. Client sends initial message with problem_description
    3. Server streams step_complete events
    4. Server sends workflow_complete when done
    """
    # Handle relative import for websocket transport
    # When loaded via importlib, relative imports fail, so use absolute import
    try:
        from dcisionai_mcp_server.transports.websocket import handle_websocket_connection
    except ImportError:
        try:
            from .transports.websocket import handle_websocket_connection
        except ImportError:
            # Fallback: Load using importlib (for when loaded via importlib)
            import importlib.util
            websocket_path = os.path.join(os.path.dirname(__file__), 'transports', 'websocket.py')
            if not os.path.exists(websocket_path):
                raise FileNotFoundError(f"WebSocket transport not found: {websocket_path}")
            websocket_spec = importlib.util.spec_from_file_location('websocket_transport', websocket_path)
            websocket_module = importlib.util.module_from_spec(websocket_spec)
            websocket_spec.loader.exec_module(websocket_module)
            handle_websocket_connection = websocket_module.handle_websocket_connection
    
    await handle_websocket_connection(websocket, session_id)


# Job WebSocket Endpoint (Restored for async job queue)
# This endpoint streams real-time updates for jobs in the async Celery queue.
# It subscribes to Redis pub/sub channel: job_updates:{job_id}
@app.websocket("/ws/job/{job_id}")
async def job_websocket_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for job-based streaming.

    Subscribes to Redis pub/sub channel `job_updates:{job_id}` and streams
    real-time updates to the client.

    Protocol:
    1. Client connects to /ws/job/{job_id}
    2. Server sends initial job status
    3. Server streams updates from Redis pub/sub
    4. Connection closes when job completes or client disconnects
    """
    try:
        from dcisionai_mcp_server.transports.job_websocket import handle_job_websocket
    except ImportError:
        logger.error("Failed to import job_websocket handler")
        await websocket.close(code=1011, reason="WebSocket handler not available")
        return

    await handle_job_websocket(websocket, job_id)


# Register MCP tools using FastMCP decorators
@mcp.tool()
async def dcisionai_solve_tool(problem_description: str) -> str:
    """
    Solve an optimization problem using DcisionAI.
    
    Provides full optimization workflow including problem classification,
    intent extraction, model generation, solving, and business explanation.
    """
    try:
        # Import here to ensure it's available (handles production import issues)
        from dcisionai_workflow.tools.optimization.mcp_tools import dcisionai_solve
        result = await dcisionai_solve(problem_description)
        if result and len(result) > 0:
            return result[0].text if hasattr(result[0], 'text') else str(result[0])
        return json.dumps({"error": "No result returned"})
    except Exception as e:
        logger.error(f"Error in dcisionai_solve_tool: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


@mcp.tool()
async def dcisionai_solve_with_model_tool(model_id: str, data: dict, options: dict = None) -> str:
    """
    Solve an optimization problem using a deployed DcisionAI model.
    
    Faster than full solve for known problem types.
    """
    try:
        # Import here to ensure it's available (handles production import issues)
        from dcisionai_workflow.tools.optimization.mcp_tools import dcisionai_solve_with_model
        result = await dcisionai_solve_with_model(model_id, data, options)
        if result and len(result) > 0:
            return result[0].text if hasattr(result[0], 'text') else str(result[0])
        return json.dumps({"error": "No result returned"})
    except Exception as e:
        logger.error(f"Error in dcisionai_solve_with_model_tool: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


@mcp.tool()
async def dcisionai_nlp_query_tool(
    question: str,
    salesforce_data: dict = None,
    org_context: dict = None,
    schema_json: str = None,
    eda_json: str = None
) -> str:
    """
    Answers natural language questions about Salesforce data or optimization problems.
    """
    try:
        # Import here to ensure it's available (handles production import issues)
        from dcisionai_workflow.tools.nlp.mcp_tools import dcisionai_nlp_query
        result = await dcisionai_nlp_query(
            question=question,
            salesforce_data=salesforce_data,
            org_context=org_context,
            schema_json=schema_json,
            eda_json=eda_json
        )
        if result and len(result) > 0:
            return result[0].text if hasattr(result[0], 'text') else str(result[0])
        return json.dumps({"error": "No result returned"})
    except Exception as e:
        logger.error(f"Error in dcisionai_nlp_query_tool: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


@mcp.tool()
async def dcisionai_map_concepts_tool(
    required_concepts: list,
    schema_json: str,
    intent_description: str = None
) -> str:
    """
    Map business concepts to platform schema using Claude-powered semantic mapping.
    """
    try:
        # Import here to ensure it's available (handles production import issues)
        from dcisionai_workflow.tools.data.mcp_tools import dcisionai_map_concepts
        result = await dcisionai_map_concepts(
            required_concepts=required_concepts,
            schema_json=schema_json,
            intent_description=intent_description
        )
        if result and len(result) > 0:
            return result[0].text if hasattr(result[0], 'text') else str(result[0])
        return json.dumps({"error": "No result returned"})
    except Exception as e:
        logger.error(f"Error in dcisionai_map_concepts_tool: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


@mcp.tool()
async def dcisionai_prepare_data_tool(
    data: str,
    problem_type: str = "auto",
    domain_hint: str = None,
    config: str = "{}"
) -> str:
    """
    Prepare data from direct upload (CSV/JSON) for optimization.
    
    Transforms raw tabular data into solver-ready structures.
    Auto-detects problem type, matches templates, recommends solvers.
    Returns classification, entities, template_match, and data_pack.
    """
    try:
        # Import here to ensure it's available (handles production import issues)
        from dcisionai_workflow.tools.data.mcp_tools import dcisionai_prepare_data
        result = await dcisionai_prepare_data(
            data=data,
            problem_type=problem_type,
            domain_hint=domain_hint,
            config=config
        )
        if result and len(result) > 0:
            return result[0].text if hasattr(result[0], 'text') else str(result[0])
        return json.dumps({"error": "No result returned"})
    except Exception as e:
        logger.error(f"Error in dcisionai_prepare_data_tool: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


@mcp.tool()
async def dcisionai_prepare_salesforce_data_tool(
    object_name: str,
    fields: str,
    data: str,
    record_count: int = None,
    soql_query: str = None,
    config: str = "{}"
) -> str:
    """
    Prepare Salesforce data from Agentforce for optimization.
    
    Called by Salesforce MCP client (Apex) after schema discovery and SOQL fetch.
    Auto-infers problem type from SF object, creates field mappings.
    Returns classification, entities, template_match, field_mappings, and data_pack.
    """
    try:
        # Import here to ensure it's available (handles production import issues)
        from dcisionai_workflow.tools.data.mcp_tools import dcisionai_prepare_salesforce_data
        result = await dcisionai_prepare_salesforce_data(
            object_name=object_name,
            fields=fields,
            data=data,
            record_count=record_count,
            soql_query=soql_query,
            config=config
        )
        if result and len(result) > 0:
            return result[0].text if hasattr(result[0], 'text') else str(result[0])
        return json.dumps({"error": "No result returned"})
    except Exception as e:
        logger.error(f"Error in dcisionai_prepare_salesforce_data_tool: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


# NOTE: Template tools (dcisionai_list_templates, dcisionai_register_template) removed from MCP
# They are internal engineering tools, not customer-facing features.
# Engineering team can access them via direct Python imports or CLI scripts.

@mcp.tool()
async def dcisionai_adhoc_optimize_tool(
    problem_description: str,
    salesforce_data: dict = None,
    org_context: dict = None
) -> str:
    """
    Build and solve optimization problems from natural language descriptions.
    """
    try:
        # Import here to ensure it's available (handles production import issues)
        from dcisionai_workflow.tools.optimization.mcp_tools import dcisionai_adhoc_optimize
        result = await dcisionai_adhoc_optimize(
            problem_description=problem_description,
            salesforce_data=salesforce_data,
            org_context=org_context
        )
        if result and len(result) > 0:
            return result[0].text if hasattr(result[0], 'text') else str(result[0])
        return json.dumps({"error": "No result returned"})
    except Exception as e:
        logger.error(f"Error in dcisionai_adhoc_optimize_tool: {e}", exc_info=True)
        return json.dumps({"error": str(e)})


# Register MCP resources
@mcp.resource("dcisionai://models/list")
async def get_models_resource() -> str:
    """Get list of deployed DcisionAI models."""
    return await read_model_resource("dcisionai://models/list")


@mcp.resource("dcisionai://solvers/list")
async def get_solvers_resource() -> str:
    """Get list of available optimization solvers."""
    return await read_solver_resource("dcisionai://solvers/list")

