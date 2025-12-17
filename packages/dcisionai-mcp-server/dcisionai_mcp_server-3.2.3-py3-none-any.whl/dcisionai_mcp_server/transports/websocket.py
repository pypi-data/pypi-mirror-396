"""
WebSocket Transport for MCP Server 2.0

Handles WebSocket connections for React UI real-time streaming.
Streams workflow updates, step completions, and thinking tokens.
"""

import asyncio
import json
import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime, date, time
from fastapi import WebSocket, WebSocketDisconnect
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage

from .websocket_helpers import (
    extract_thinking_content,
    extract_thinking_from_output,
    normalize_node_name,
    is_step_complete_node
)

logger = logging.getLogger(__name__)


def filter_large_fields_for_step_complete(step_output: Dict[str, Any], node_name: str) -> Dict[str, Any]:
    """
    Filter out large data fields from step_output to reduce payload size.

    For non-data steps (solver, business explanation, etc.), we don't need to send
    the full data_pack in _full_output since it was already sent in the data generation step.

    Args:
        step_output: Original step output dict
        node_name: Name of the node/step

    Returns:
        Filtered step output with large fields replaced by summaries
    """
    # For data generation step, keep data_pack intact
    if node_name == "generate_data":
        return step_output

    # For other steps, filter out data_pack and other large intermediate fields
    filtered = {}
    for key, value in step_output.items():
        # Skip large data structures that aren't needed in non-data steps
        if key == "data_pack":
            # Replace with summary
            if isinstance(value, dict):
                filtered[key] = {
                    "records_count": len(value.get("records", [])),
                    "metadata_keys": list(value.get("metadata", {}).keys()) if isinstance(value.get("metadata"), dict) else [],
                    "_note": "Full data_pack omitted to reduce payload size. Available in generate_data step."
                }
            else:
                filtered[key] = {"_note": "Full data_pack omitted to reduce payload size"}
        elif key == "generated_data":
            # Skip generated_data if it duplicates data_pack
            continue
        elif key in ["messages", "decomposition", "domain_context"]:
            # Skip verbose intermediate fields
            filtered[key] = f"<{len(value)} items>" if isinstance(value, (list, dict)) else value
        else:
            # Keep other fields
            filtered[key] = value

    return filtered


def convert_tuple_keys_to_str(obj: Any) -> Any:
    """
    Recursively convert tuple keys in dictionaries to strings for JSON serialization.

    Matrix parameters in data_pack.metadata use tuple keys like (row_idx, col_idx),
    which are not JSON-serializable. This function converts them to string keys.

    Args:
        obj: Object to convert (dict, list, or other)

    Returns:
        Object with tuple keys converted to strings
    """
    if isinstance(obj, dict):
        converted = {}
        for k, v in obj.items():
            # Convert tuple keys to string representation
            if isinstance(k, tuple):
                key_str = str(k)  # e.g., "(0, 1)" -> "(0, 1)"
            else:
                key_str = k
            # Recursively convert nested structures
            converted[key_str] = convert_tuple_keys_to_str(v)
        return converted
    elif isinstance(obj, list):
        return [convert_tuple_keys_to_str(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_tuple_keys_to_str(item) for item in obj)
    else:
        return obj


async def safe_send_json(websocket: WebSocket, data: dict, session_id: str = None, max_size: int = 50000) -> bool:
    """
    Safely send JSON data over WebSocket with error handling and size checking.
    
    Args:
        websocket: WebSocket connection
        data: Data dictionary to send
        session_id: Optional session ID for logging
        max_size: Maximum JSON size in bytes (default: 100KB)
    
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        if websocket.client_state.name != 'CONNECTED':
            logger.debug(f"WebSocket not connected (state: {websocket.client_state.name}), cannot send")
            return False
        
        # Convert tuple keys to strings before JSON serialization (for matrix parameters)
        # This fixes the "keys must be str, int, float, bool or None, not tuple" error
        data = convert_tuple_keys_to_str(data)
        
        # Check JSON size before sending
        try:
            json_str = json.dumps(data, default=str)
            json_size = len(json_str.encode('utf-8'))
            
            logger.debug(f"🔍 [SIZE CHECK] JSON size: {json_size} bytes, max: {max_size} bytes for session {session_id}")
            
            if json_size > max_size:
                logger.warning(f"⚠️ JSON payload too large ({json_size} bytes > {max_size} bytes) for session {session_id}")
                logger.debug(f"   Data type: {type(data)}, Data keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                # Try to reduce size by removing intermediate fields, NOT truncating solver results
                if isinstance(data, dict) and 'result' in data:
                    result = data.get('result', {})
                    
                    # Build essential data - KEEP solver results FULLY intact
                    # Only remove intermediate/verbose fields
                    essential_result = {
                        'workflow_stage': result.get('workflow_stage'),
                        'optimization_status': result.get('optimization_status'),
                        'solver_used': result.get('solver_used'),
                        'objective_value': result.get('objective_value'),
                        # KEEP solver results FULLY - this is our MOAT!
                        'mathematical_solver_result': result.get('mathematical_solver_result'),
                        'dame_solver_result': result.get('dame_solver_result'),
                        'solver_comparison': result.get('solver_comparison'),
                        'optimization_solution': result.get('optimization_solution'),
                        'business_explanation': result.get('business_explanation'),
                        'errors': result.get('errors'),
                        'warnings': result.get('warnings')
                    }
                    
                    # Remove None values
                    essential_result = {k: v for k, v in essential_result.items() if v is not None}
                    
                    essential_data = {
                        'type': data.get('type'),
                        'session_id': data.get('session_id'),
                        'timestamp': data.get('timestamp'),
                        'result': essential_result
                    }
                    
                    json_str = json.dumps(essential_data, default=str)
                    json_size = len(json_str.encode('utf-8'))
                    
                    if json_size > max_size:
                        logger.warning(f"⚠️ Payload still too large ({json_size} bytes) after removing intermediate fields. Implementing chunking for solver results.")
                        
                        # Strategy: Send summary first, then chunk solver solutions separately
                        # Extract solver solutions for chunking
                        math_result = result.get('mathematical_solver_result', {})
                        dame_result = result.get('dame_solver_result', {})
                        opt_solution = result.get('optimization_solution', {})
                        
                        # Helper to extract solution dict and create summary
                        def create_solver_summary(solver_result):
                            if not isinstance(solver_result, dict):
                                return solver_result
                            solution = solver_result.get('solution', {})
                            summary = {
                                k: v for k, v in solver_result.items() 
                                if k != 'solution'
                            }
                            if isinstance(solution, dict):
                                solution_size = len(solution)
                                summary['solution_size'] = solution_size
                                summary['solution_keys'] = list(solution.keys())[:10]  # First 10 keys as preview
                                summary['solution_chunked'] = True
                            return summary
                        
                        # Create summaries without full solutions
                        math_summary = create_solver_summary(math_result) if math_result else None
                        dame_summary = create_solver_summary(dame_result) if dame_result else None
                        opt_summary = create_solver_summary(opt_solution) if opt_solution else None
                        
                        # Build summary payload
                        summary_result = {
                            'workflow_stage': result.get('workflow_stage'),
                            'optimization_status': result.get('optimization_status'),
                            'solver_used': result.get('solver_used'),
                            'objective_value': result.get('objective_value'),
                            'mathematical_solver_result': math_summary,
                            'dame_solver_result': dame_summary,
                            'optimization_solution': opt_summary,
                            'solver_comparison': result.get('solver_comparison'),
                            'business_explanation': result.get('business_explanation'),
                            'errors': result.get('errors'),
                            'warnings': result.get('warnings'),
                            '_message': 'Solver solutions are large and will be sent in chunks. Use fetch_solution_chunk to retrieve full solutions.'
                        }
                        
                        summary_data = {
                            'type': data.get('type'),
                            'session_id': data.get('session_id'),
                            'timestamp': data.get('timestamp'),
                            'result': summary_result
                        }
                        
                        summary_json = json.dumps(summary_data, default=str)
                        summary_size = len(summary_json.encode('utf-8'))
                        
                        if summary_size > max_size:
                            logger.error(f"❌ Even summary payload too large ({summary_size} bytes). Sending minimal status only.")
                            await websocket.send_json({
                                'type': 'workflow_complete',
                                'session_id': session_id,
                                'result': {
                                    'workflow_stage': result.get('workflow_stage'),
                                    'optimization_status': result.get('optimization_status'),
                                    'solver_used': result.get('solver_used'),
                                    'objective_value': result.get('objective_value'),
                                    'errors': result.get('errors'),
                                    '_message': f'Results too large ({json_size} bytes). Check backend logs for full solver results.'
                                },
                                'timestamp': datetime.now().isoformat()
                            }, session_id)
                            return False
                        
                        # Send summary first
                        await websocket.send_json(summary_data)
                        logger.info(f"✅ Sent workflow summary ({summary_size} bytes) for session {session_id}")
                        
                        # Now send solution chunks separately
                        # Helper to chunk a solution dict
                        def chunk_solution(solution_dict: dict, solver_name: str, chunk_size: int = 100):
                            """Split solution dict into chunks."""
                            if not isinstance(solution_dict, dict):
                                return []
                            items = list(solution_dict.items())
                            chunks = []
                            for i in range(0, len(items), chunk_size):
                                chunk = dict(items[i:i + chunk_size])
                                chunks.append({
                                    'type': 'solution_chunk',
                                    'solver': solver_name,
                                    'chunk_index': i // chunk_size,
                                    'total_chunks': (len(items) + chunk_size - 1) // chunk_size,
                                    'chunk': chunk,
                                    'session_id': session_id,
                                    'timestamp': datetime.now().isoformat()
                                })
                            return chunks
                        
                        # Send mathematical solver solution chunks
                        if isinstance(math_result, dict) and isinstance(math_result.get('solution'), dict):
                            math_chunks = chunk_solution(math_result['solution'], 'mathematical')
                            for chunk in math_chunks:
                                chunk_json = json.dumps(chunk, default=str)
                                if len(chunk_json.encode('utf-8')) <= max_size:
                                    await websocket.send_json(chunk)
                                    logger.debug(f"✅ Sent mathematical solution chunk {chunk['chunk_index'] + 1}/{chunk['total_chunks']}")
                                else:
                                    logger.warning(f"⚠️ Mathematical solution chunk too large, skipping")
                        
                        # Send DAME solver solution chunks
                        if isinstance(dame_result, dict) and isinstance(dame_result.get('solution'), dict):
                            dame_chunks = chunk_solution(dame_result['solution'], 'dame')
                            for chunk in dame_chunks:
                                chunk_json = json.dumps(chunk, default=str)
                                if len(chunk_json.encode('utf-8')) <= max_size:
                                    await websocket.send_json(chunk)
                                    logger.debug(f"✅ Sent DAME solution chunk {chunk['chunk_index'] + 1}/{chunk['total_chunks']}")
                                else:
                                    logger.warning(f"⚠️ DAME solution chunk too large, skipping")
                        
                        # Send optimization solution chunks
                        if isinstance(opt_solution, dict) and isinstance(opt_solution.get('solution'), dict):
                            opt_chunks = chunk_solution(opt_solution['solution'], 'optimization')
                            for chunk in opt_chunks:
                                chunk_json = json.dumps(chunk, default=str)
                                if len(chunk_json.encode('utf-8')) <= max_size:
                                    await websocket.send_json(chunk)
                                    logger.debug(f"✅ Sent optimization solution chunk {chunk['chunk_index'] + 1}/{chunk['total_chunks']}")
                                else:
                                    logger.warning(f"⚠️ Optimization solution chunk too large, skipping")
                        
                        logger.info(f"✅ Sent all solution chunks for session {session_id}")
                        return True
                    
                    data = essential_data
                    logger.info(f"✅ Reduced payload size from {len(json.dumps(data, default=str).encode('utf-8'))} to {json_size} bytes by removing intermediate fields (solver results intact)")
                else:
                    # Try chunking even if data structure is unexpected
                    logger.warning(f"⚠️ Unexpected data structure, attempting chunking anyway for session {session_id}")
                    
                    # Try to find solver results - check if they're at top level
                    result = data if isinstance(data, dict) else {}
                    if 'result' not in result and isinstance(data, dict):
                        # Check if solver results are at top level (including solver_result from solver_router)
                        if 'mathematical_solver_result' in data or 'dame_solver_result' in data or 'optimization_solution' in data or 'solver_result' in data:
                            result = data
                    
                    # If we found solver results, try chunking
                    if isinstance(result, dict) and ('mathematical_solver_result' in result or 'dame_solver_result' in result or 'optimization_solution' in result or 'solver_result' in result):
                        math_result = result.get('mathematical_solver_result', {})
                        dame_result = result.get('dame_solver_result', {})
                        opt_solution = result.get('optimization_solution', {})
                        solver_result = result.get('solver_result', {})  # From solver_router node
                        
                        # Helper to create solver summary
                        def create_solver_summary(solver_result):
                            if not isinstance(solver_result, dict):
                                return solver_result
                            solution = solver_result.get('solution', {})
                            summary = {
                                k: v for k, v in solver_result.items() 
                                if k != 'solution'
                            }
                            if isinstance(solution, dict):
                                summary['solution_size'] = len(solution)
                                summary['solution_keys'] = list(solution.keys())[:10]
                                summary['solution_chunked'] = True
                            return summary
                        
                        # Create summaries
                        math_summary = create_solver_summary(math_result) if math_result else None
                        dame_summary = create_solver_summary(dame_result) if dame_result else None
                        opt_summary = create_solver_summary(opt_solution) if opt_solution else None
                        solver_summary = create_solver_summary(solver_result) if solver_result else None
                        
                        # Build minimal summary
                        summary_data = {
                            'type': data.get('type', 'workflow_complete') if isinstance(data, dict) else 'workflow_complete',
                            'session_id': data.get('session_id', session_id) if isinstance(data, dict) else session_id,
                            'timestamp': data.get('timestamp', datetime.now().isoformat()) if isinstance(data, dict) else datetime.now().isoformat(),
                            'result': {
                                'workflow_stage': result.get('workflow_stage'),
                                'optimization_status': solver_result.get('status') if solver_result else result.get('optimization_status'),
                                'solver_used': solver_result.get('solver_used') if solver_result else result.get('solver_used'),
                                'objective_value': solver_result.get('objective_value') if solver_result else result.get('objective_value'),
                                'mathematical_solver_result': math_summary,
                                'dame_solver_result': dame_summary,
                                'optimization_solution': opt_summary,
                                'solver_result': solver_summary,  # Include solver_result summary
                                'errors': result.get('errors'),
                                'warnings': result.get('warnings'),
                                '_message': 'Solver solutions are large and will be sent in chunks.'
                            }
                        }
                        
                        summary_json = json.dumps(summary_data, default=str)
                        summary_size = len(summary_json.encode('utf-8'))
                        
                        if summary_size <= max_size:
                            # Send summary and chunks
                            await websocket.send_json(summary_data)
                            logger.info(f"✅ Sent workflow summary ({summary_size} bytes) via fallback chunking")
                            
                            # Helper to chunk solutions
                            def chunk_solution(solution_dict: dict, solver_name: str, chunk_size: int = 100):
                                if not isinstance(solution_dict, dict):
                                    return []
                                items = list(solution_dict.items())
                                chunks = []
                                for i in range(0, len(items), chunk_size):
                                    chunk = dict(items[i:i + chunk_size])
                                    chunks.append({
                                        'type': 'solution_chunk',
                                        'solver': solver_name,
                                        'chunk_index': i // chunk_size,
                                        'total_chunks': (len(items) + chunk_size - 1) // chunk_size,
                                        'chunk': chunk,
                                        'session_id': session_id,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                return chunks
                            
                            # Send chunks for all solver results (including solver_result from solver_router)
                            for solver_name, solver_result_item in [('mathematical', math_result), ('dame', dame_result), ('optimization', opt_solution), ('solver', solver_result)]:
                                if isinstance(solver_result_item, dict) and isinstance(solver_result_item.get('solution'), dict):
                                    chunks = chunk_solution(solver_result_item['solution'], solver_name)
                                    for chunk in chunks:
                                        chunk_json = json.dumps(chunk, default=str)
                                        if len(chunk_json.encode('utf-8')) <= max_size:
                                            await websocket.send_json(chunk)
                            
                            return True
                    
                    # If chunking didn't work, send minimal error
                    logger.error(f"❌ Cannot reduce payload size - unexpected data structure for session {session_id}")
                    await websocket.send_json({
                        'type': 'error',
                        'message': f'Payload too large ({json_size} bytes) and cannot be reduced. Check backend logs for full results.',
                        'session_id': session_id,
                        'payload_size_bytes': json_size
                    }, session_id)
                    return False
        except Exception as size_check_error:
            logger.warning(f"Failed to check JSON size: {size_check_error}, proceeding anyway")
        
        await websocket.send_json(data)
        return True
    except Exception as e:
        logger.warning(f"Failed to send JSON over WebSocket (session: {session_id}): {e}")
        return False


# normalize_node_name moved to websocket_helpers.py


def serialize_state_for_json(obj: Any, max_depth: int = 5, current_depth: int = 0, max_size: int = 100000) -> Any:
    """
    Serialize LangChain state to JSON-serializable format (recursive).
    
    Args:
        obj: Object to serialize
        max_depth: Maximum recursion depth
        current_depth: Current recursion depth
        max_size: Maximum size in characters (approximate)
    """
    if current_depth > max_depth:
        return "[Max depth reached]"
    
    # Handle datetime objects
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat() if hasattr(obj, 'isoformat') else str(obj)
    
    # Handle LangChain messages
    if isinstance(obj, (BaseMessage, AIMessage, HumanMessage)):
        content = str(obj.content)
        if len(content) > 2000:  # Reduced from 5000 for step_complete events
            content = content[:2000] + "... [truncated]"
        return {
            "type": obj.__class__.__name__,
            "content": content,
            "additional_kwargs": serialize_state_for_json(getattr(obj, "additional_kwargs", {}), max_depth, current_depth + 1, max_size)
        }
    
    # Handle lists - more aggressive limits
    if isinstance(obj, list):
        if len(obj) > 50:  # Reduced from 500 for step_complete events
            return f"[List: {len(obj)} items, showing first 50]"
        return [
            serialize_state_for_json(item, max_depth, current_depth + 1, max_size)
            for item in obj[:50]
        ]
    
    # Handle dicts - more aggressive limits
    if isinstance(obj, dict):
        # Limit dict size
        if len(obj) > 100:  # Reduced from 200 for step_complete events
            # Keep only essential keys
            essential_keys = [
                'problem_description', 'session_id', 'workflow_stage', 'current_step',
                'optimization_solution', 'optimization_status', 'solver_used', 'objective_value',
                'mathematical_solver_result', 'dame_solver_result', 'solver_comparison',
                'business_explanation', 'errors', 'warnings'
            ]
            filtered_dict = {k: v for k, v in obj.items() if k in essential_keys}
            if len(filtered_dict) < len(obj):
                filtered_dict['_truncated'] = f"[{len(obj) - len(filtered_dict)} keys omitted]"
            obj = filtered_dict
        
        return {
            str(k): serialize_state_for_json(v, max_depth, current_depth + 1, max_size)
            for k, v in list(obj.items())[:100]  # Limit to 100 keys
        }
    
    # Handle Pydantic models
    if hasattr(obj, 'model_dump'):
        try:
            return serialize_state_for_json(obj.model_dump(mode='json'), max_depth, current_depth + 1, max_size)
        except:
            pass
    
    if hasattr(obj, 'dict'):
        try:
            return serialize_state_for_json(obj.dict(), max_depth, current_depth + 1, max_size)
        except:
            pass
    
    # Handle Pyomo models (cannot be serialized - exclude from WebSocket)
    try:
        import pyomo.environ as pyo
        if isinstance(obj, pyo.ConcreteModel):
            return {
                "_type": "PyomoModel",
                "_message": "Pyomo model object (excluded from WebSocket serialization - use pyomo_code instead)",
                "model_name": getattr(obj, 'name', 'unknown')
            }
    except ImportError:
        pass
    
    # Handle basic types
    if isinstance(obj, (str, int, float, bool, type(None))):
        if isinstance(obj, str) and len(obj) > 2000:  # Limit string size more aggressively
            return obj[:2000] + "... [truncated]"
        return obj
    
    # Try JSON serialization as fallback
    try:
        json.dumps(obj, default=str)
        return obj
    except (TypeError, ValueError):
        str_val = str(obj)
        if len(str_val) > 5000:
            return str_val[:5000] + "... [truncated]"
        return str_val


async def handle_websocket_connection(websocket: WebSocket, session_id: str):
    """
    Handle WebSocket connection for streaming workflow updates.
    
    Args:
        websocket: WebSocket connection
        session_id: Session identifier
    """
    await websocket.accept()
    logger.info(f"WebSocket connected: {session_id}")
    
    try:
        # Wait for initial message with problem
        data = await websocket.receive_json()
        problem = data.get("problem_description", "")
        
        if not problem:
            await safe_send_json(websocket, {
                "type": "error",
                "message": "Problem description required"
            }, session_id)
            return
        
        # Create workflow
        logger.info(f"Creating workflow for session {session_id}")
        logger.info(f"Problem: {problem[:100]}...")
        
        try:
            # Ensure dcisionai_workflow and dcisionai_kb are in path
            import sys
            import os
            # Add project root to path if not already there
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            # Verify dcisionai_kb is available (core to architecture - Pinecone templates)
            try:
                import dcisionai_kb
                logger.info(f"✅ dcisionai_kb found at: {dcisionai_kb.__file__}")
            except ImportError as kb_err:
                logger.error(f"❌ CRITICAL: dcisionai_kb not found! This is required for Pinecone template matching.")
                logger.error(f"   Project root: {project_root}")
                logger.error(f"   Python path: {sys.path[:5]}")
                logger.error(f"   KB path should be: {os.path.join(project_root, 'dcisionai_kb')}")
                logger.error(f"   KB exists: {os.path.exists(os.path.join(project_root, 'dcisionai_kb'))}")
                raise ImportError(f"dcisionai_kb is required but not found. Ensure it's in the project root. Error: {kb_err}")
            
            # NEW ARCHITECTURE: Use dcisionai_workflow (11 nodes: 9 intent + 1 solver + 1 explanation)
            # This replaces both the old DAME workflow (26 nodes) and clean workflow (4 nodes)
            use_new_workflow = data.get("use_new_workflow", True)  # Default to NEW workflow

            if use_new_workflow:
                # Use NEW dcisionai_workflow (clean architecture)
                logger.info("✨ Using NEW DcisionAI Workflow (11 nodes: 9 intent + solver + explanation)")
                logger.info("   - 9 Intent Discovery nodes (progressive accordions)")
                logger.info("   - 1 Claude SDK Solver node (autonomous solving)")
                logger.info("   - 1 Business Explanation node (executive summary)")
                from dcisionai_workflow import create_workflow
                workflow = create_workflow()
            else:
                # DEPRECATED: Use legacy workflows (for backward compatibility during migration)
                use_clean_workflow = data.get("use_clean_workflow", False)

                if use_clean_workflow:
                    # Legacy: Clean Claude Agent SDK workflow
                    logger.warning("⚠️ Using DEPRECATED Clean Claude Agent SDK Workflow (will be removed)")
                    from dcisionai_workflow.orchestration.claude_agent_workflow import create_claude_agent_workflow
                    workflow = create_claude_agent_workflow()
                else:
                    # Legacy: Traditional DAME workflow
                    logger.warning("⚠️ Using DEPRECATED DAME Workflow (will be removed)")
                    from dcisionai_workflow.orchestration.dame_workflow import create_dame_supervisor_workflow
                    workflow = create_dame_supervisor_workflow(
                        enabled_features=data.get("enabled_features", ["intent"]),
                        enabled_tools=data.get("enabled_tools", []),
                        use_direct_pyomo=True
                    )
            logger.info(f"Workflow created successfully for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to create workflow: {e}", exc_info=True)
            error_msg = f"Failed to create workflow: {str(e)}"
            await safe_send_json(websocket, {
                "type": "error",
                "message": error_msg,
                "session_id": session_id
            }, session_id)
            # Ensure WebSocket is properly closed on error
            try:
                await websocket.close(code=1000, reason="Workflow creation failed")
            except Exception:
                pass  # WebSocket may already be closed
            logger.info(f"Workflow creation failed for session {session_id}, connection closed")
            return
        
        # Send start message
        await safe_send_json(websocket, {
            "type": "workflow_start",
            "session_id": session_id
        }, session_id)
        
        # Create state
        enabled_features = data.get("enabled_features", ["intent"])  # INTENT-ONLY MODE: Only intent discovery
        enabled_tools = data.get("enabled_tools", [])  # INTENT-ONLY MODE: No data or solver tools
        
        # Resolve code_model dynamically if not provided or if invalid
        from dcisionai_workflow.shared.llm.model_resolver import get_code_model
        code_model = data.get("code_model")
        if code_model is None:
            code_model = get_code_model()
        else:
            # Validate model name - if it's an invalid hardcoded name, resolve dynamically
            invalid_models = ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]
            if code_model in invalid_models:
                logger.warning(f"Invalid model name '{code_model}' detected, resolving dynamically")
                code_model = get_code_model()
        
        # Check if Claude SDK is available for enhanced features
        # Note: Claude SDK availability is verified at server startup (start_mcp_server.py:58)
        # If we got here, Claude SDK is available
        try:
            import claude_agent_sdk
            claude_sdk_available = True
            logger.info("✅ Claude Agent SDK available - enabling enhanced features")
        except ImportError:
            claude_sdk_available = False
            logger.warning("⚠️ Claude Agent SDK not available - using standard features")
        
        # SIMPLIFIED: No job pattern - always run intent discovery inline
        # Remove discovered_intent extraction - workflow will run intent discovery sequentially
        logger.info("🚀 Starting workflow with inline sequential intent discovery")

        # Create appropriate state based on workflow type
        if use_new_workflow:
            # NEW: Use WorkflowState from dcisionai_workflow
            from dcisionai_workflow import WorkflowState
            state: WorkflowState = {
                # Core Input
                "problem_description": problem,
                "session_id": session_id,

                # Intent Discovery Results (will be populated)
                "discovered_intent": None,
                "decomposition": None,
                "domain_context": None,
                "classification": None,
                "assumptions": None,
                "entities": None,
                "objectives": None,
                "constraints": None,

                # Solver Results (will be populated)
                "solver_result": None,
                "claude_agent_used": False,
                "claude_agent_status": None,
                "claude_agent_work_dir": None,
                "claude_agent_execution_summary": None,

                # Business Explanation (will be populated)
                "business_explanation": None,

                # Workflow Control
                "workflow_stage": "started",
                "current_step": "start",
                "completed_steps": [],
                "errors": [],
                "warnings": [],

                # Messages
                "messages": [],

                # Configuration
                "claude_agent_solver_config": {
                    "max_retries": data.get("max_retries", 3),
                    "enable_sdv": data.get("enable_sdv", True),
                    "use_few_shot": False,  # No templates
                    "fallback_to_tier_system": False,  # Pure Agent SDK
                    "timeout_seconds": data.get("timeout_seconds", 300),
                },
                "enable_templates": data.get("enable_templates", True),
            }
        elif use_clean_workflow:
            # DEPRECATED: Clean workflow state
            from dcisionai_workflow.orchestration.claude_agent_workflow import ClaudeAgentState
            state: ClaudeAgentState = {
                # Core Input
                "problem_description": problem,
                "session_id": session_id,

                # Intent Discovery Results (will be populated)
                "discovered_intent": None,
                "decomposition": None,
                "domain_context": None,
                "classification": None,
                "assumptions": None,
                "entities": None,
                "objectives": None,
                "constraints": None,

                # Solver Results (will be populated)
                "solver_result": None,
                "claude_agent_used": False,
                "claude_agent_status": None,
                "claude_agent_work_dir": None,
                "claude_agent_execution_summary": None,

                # Business Explanation (will be populated)
                "business_explanation": None,

                # Workflow Control
                "workflow_stage": "started",
                "current_step": "start",
                "completed_steps": [],
                "errors": [],
                "warnings": [],

                # Messages
                "messages": [],

                # Configuration
                "claude_agent_solver_config": {
                    "max_retries": data.get("max_retries", 3),
                    "enable_sdv": data.get("enable_sdv", True),
                    "use_few_shot": False,  # No templates in clean workflow
                    "fallback_to_tier_system": False,  # Pure Agent SDK
                    "timeout_seconds": data.get("timeout_seconds", 300),
                }
            }
        else:
            # Traditional DAME workflow uses DAMEState
            state = {
                "problem_description": problem,
                "session_id": session_id,
                "current_step": "start",
                "completed_steps": [],
                "errors": [],
                "warnings": [],
                "messages": [],
                "enabled_features": enabled_features,
                "enabled_tools": enabled_tools,
                "reasoning_model": data.get("reasoning_model"),  # Will be resolved dynamically if None
                "code_model": code_model,  # Resolved dynamically
                "enable_validation": data.get("enable_validation", False),
                "use_direct_pyomo": True,
                "use_claude_sdk_for_pyomo": data.get("use_claude_sdk_for_pyomo", claude_sdk_available),  # Phase 2: Enhanced Pyomo generation
                # SIMPLIFIED: No discovered_intent - workflow will run intent discovery inline
                "use_parallel_execution": False,  # Sequential flow for reliability
                "enable_templates": data.get("enable_templates", True),
                "template_preferences": data.get("template_preferences", {}),
                "template_fallback": data.get("template_fallback", True),
                # Template hint from use case selection (for better template matching)
                "template_hint": data.get("template_hint") or data.get("templateId"),
                # Phase 4: DAME strategy/config generation (enabled via problem_characteristics)
            }
        
        # Phase 4: Enable Claude SDK for DAME strategy/config if available
        if claude_sdk_available:
            state.setdefault("problem_characteristics", {})
            state["problem_characteristics"]["use_claude_sdk_for_strategy"] = data.get("use_claude_sdk_for_strategy", True)
            state["problem_characteristics"]["use_claude_sdk_for_config"] = data.get("use_claude_sdk_for_config", True)
        
        # Stream workflow updates with thread configuration
        config = {
            "configurable": {
                "thread_id": session_id,
                "checkpoint_ns": "main"
            }
        }
        
        # Collect all chunks to build final result
        final_result = {}
        chunk_count = 0
        # Configurable timeout: default 30 minutes (1800s), can be overridden via request
        timeout_seconds = data.get("timeout_seconds", 1800)  # 30 minute default timeout
        if timeout_seconds < 60:
            timeout_seconds = 60  # Minimum 1 minute
        if timeout_seconds > 3600:
            timeout_seconds = 3600  # Maximum 1 hour
        
        logger.info(f"Starting workflow with {timeout_seconds}s ({timeout_seconds/60:.1f} minutes) timeout for session {session_id}")
        
        # Track start time for progress reporting
        start_time = datetime.now()
        
        try:
            logger.info("Starting astream_events for granular streaming...")
            workflow_cancelled = False
            try:
                async with asyncio.timeout(timeout_seconds):
                    # Stream events using astream_events for granular updates
                    # Note: LangGraph's astream_events streams all events including LLM thinking tokens
                    # Claude thinking tokens come through on_chat_model_stream or on_llm_stream events
                    # CRITICAL: Buffer incremental thinking chunks until we have complete blocks
                    thinking_buffer = {}  # Map of node_name -> accumulated thinking content
                    current_workflow_node = None  # Track current workflow node for ChatAnthropic events
                    
                    async for event in workflow.astream_events(state, config=config, version="v2"):
                        # Check if WebSocket disconnected before processing each event
                        if websocket.client_state.name != 'CONNECTED':
                            logger.info(f"⚠️ WebSocket disconnected during workflow execution for session {session_id}, cancelling workflow")
                            workflow_cancelled = True
                            break
                        
                        chunk_count += 1
                        event_type = event.get("event")
                        
                        # Handle thinking blocks from LLM streaming
                        # LangGraph emits thinking tokens through both on_chat_model_stream and on_llm_stream
                        if event_type in ["on_chat_model_stream", "on_llm_stream"]:
                            data_dict = event.get("data", {})
                            chunk = data_dict.get("chunk", {})
                            
                            # Get node name for buffering
                            # CRITICAL: ChatAnthropic events come from LangChain wrapper, not workflow node
                            # Use current_workflow_node if available, otherwise try to normalize
                            node_name_raw = event.get("name", "unknown")
                            
                            # If this is a ChatAnthropic/LangChain wrapper event, use the current workflow node
                            if node_name_raw in ["ChatAnthropic", "ChatOpenAI", "ChatMistralAI"]:
                                if current_workflow_node:
                                    node_name = current_workflow_node
                                    logger.debug(f"📍 [THINKING] Using current workflow node {current_workflow_node} for {node_name_raw} event")
                                else:
                                    # Fallback: try to get parent node from event metadata
                                    node_name = normalize_node_name(node_name_raw)
                                    logger.warning(f"⚠️ [THINKING] No current workflow node tracked for {node_name_raw}, using normalized: {node_name}")
                            else:
                                node_name = normalize_node_name(node_name_raw)
                            
                            # Extract content from chunk (handle AIMessageChunk objects)
                            chunk_content = ""
                            if hasattr(chunk, 'content'):
                                chunk_content = getattr(chunk, 'content', '')
                            elif isinstance(chunk, dict):
                                chunk_content = chunk.get('content', '') or chunk.get('text', '')
                            elif isinstance(chunk, str):
                                chunk_content = chunk
                            
                            # Buffer incremental thinking chunks
                            if chunk_content:
                                if node_name not in thinking_buffer:
                                    thinking_buffer[node_name] = ""
                                thinking_buffer[node_name] += chunk_content
                                
                                # Check if we have a complete thinking block (has closing tag)
                                buffered_content = thinking_buffer[node_name]
                                if "</thinking>" in buffered_content:
                                    # Extract complete thinking block
                                    thinking_match = re.search(r'<thinking>(.*?)</thinking>', buffered_content, re.DOTALL)
                                    if thinking_match:
                                        thinking_content = thinking_match.group(1).strip()
                                        if len(thinking_content) > 5:  # Filter out empty blocks
                                            logger.info(f"📝 [THINKING] Complete thinking block from {node_name_raw} → {node_name} (length: {len(thinking_content)})")
                                            thinking_msg = {
                                                "type": "thinking",
                                                "step": node_name,
                                                "step_raw": node_name_raw,
                                                "content": thinking_content,
                                                "is_streaming": True,
                                                "session_id": session_id,
                                                "timestamp": datetime.now().isoformat()
                                            }
                                            success = await safe_send_json(websocket, thinking_msg, session_id)
                                            if success:
                                                logger.info(f"✅ [THINKING] Sent complete thinking block from {node_name_raw} - length: {len(thinking_content)}")
                                            else:
                                                logger.warning(f"⚠️ [THINKING] Failed to send thinking block - WebSocket may be closed")
                                            
                                            # Clear buffer after sending (keep content after </thinking> for potential next block)
                                            remaining = buffered_content.split("</thinking>", 1)[1] if "</thinking>" in buffered_content else ""
                                            thinking_buffer[node_name] = remaining if "<thinking>" in remaining else ""
                                        else:
                                            # Clear buffer if content too short
                                            thinking_buffer[node_name] = ""
                                    else:
                                        # No complete block yet, continue buffering
                                        pass
                                elif "<thinking>" in buffered_content:
                                    # We're inside a thinking block, continue buffering
                                    pass
                                else:
                                    # Not a thinking block, clear buffer if it gets too large
                                    if len(buffered_content) > 10000:  # Prevent memory issues
                                        thinking_buffer[node_name] = ""
                            
                            # Also try the original extraction method (for non-incremental formats)
                            thinking_content = extract_thinking_content(chunk)
                            
                            if thinking_content:
                                # Normalize node name for consistent step identification
                                node_name_normalized = normalize_node_name(node_name_raw)
                                
                                # Send thinking chunk immediately (real-time streaming like Cursor IDE)
                                logger.info(f"📝 [THINKING] Streaming thinking chunk from {event_type} {node_name_raw} → {node_name_normalized} (length: {len(thinking_content)}, preview: {thinking_content[:100]}...)")
                                thinking_msg = {
                                    "type": "thinking",
                                    "step": node_name_normalized,  # Use normalized name for consistency
                                    "step_raw": node_name_raw,  # Keep raw name for reference
                                    "content": thinking_content,  # Send chunk immediately as it arrives
                                    "is_streaming": True,  # Flag to indicate this is a streaming chunk
                                    "session_id": session_id,
                                    "timestamp": datetime.now().isoformat()
                                }
                                success = await safe_send_json(websocket, thinking_msg, session_id)
                                if success:
                                    logger.info(f"✅ [THINKING] Sent thinking chunk from {event_type} {node_name_raw} (real-time) - length: {len(thinking_content)}")
                                else:
                                    logger.warning(f"⚠️ [THINKING] Failed to send thinking chunk from {event_type} - WebSocket may be closed")
                                continue  # Skip further processing for thinking events
                            else:
                                # Log when we see streaming events but no thinking content (use INFO for production debugging)
                                if chunk_count <= 20:  # Log first 20 events to debug extraction
                                    logger.info(f"🔍 [STREAM] {event_type} event from {node_name_raw} but no thinking content extracted. Chunk type: {type(chunk)}, Chunk preview: {str(chunk)[:200]}")
                        
                        # Skip other streaming events (not used by icicle chart)
                        if event_type == "on_llm_stream":
                            continue
                        
                        # Handle step start events - send step_start with LLM role info
                        if event_type == "on_chain_start":
                            node_name_raw = event.get("name", "unknown")
                            node_name = normalize_node_name(node_name_raw)
                            
                            # Track current workflow node for thinking chunk association
                            # Only track actual workflow nodes (not ChatAnthropic wrappers)
                            if node_name_raw not in ["ChatAnthropic", "ChatOpenAI", "ChatMistralAI"] and is_step_complete_node(node_name_raw):
                                current_workflow_node = node_name
                                logger.debug(f"📍 [TRACKING] Current workflow node set to: {current_workflow_node} (from {node_name_raw})")
                            
                            # Only send step_start for relevant nodes
                            if is_step_complete_node(node_name_raw) or is_step_complete_node(node_name):
                                # Extract state to get LLM role
                                data_dict = event.get("data", {})
                                state = data_dict.get("input", {}) if isinstance(data_dict.get("input"), dict) else {}
                                
                                # Get LLM role from state (set by template_decision)
                                llm_role = state.get("llm_role", "standard")
                                template_route_type = state.get("template_route_type", "adhoc")
                                match_score = state.get("template_match_score") or state.get("knowledgebase_match_score", 0.0)
                                
                                # Create step start message with LLM role info
                                step_start_msg = {
                                    "type": "step_start",
                                    "step": node_name,
                                    "llm_role": llm_role,
                                    "template_route_type": template_route_type,
                                    "match_score": match_score,
                                    "session_id": session_id,
                                    "timestamp": datetime.now().isoformat()
                                }
                                
                                success = await safe_send_json(websocket, step_start_msg, session_id)
                                if success:
                                    logger.info(f"✅ [STEP START] Sent step_start for {node_name} (LLM Role: {llm_role}, Route: {template_route_type})")
                                else:
                                    logger.warning(f"⚠️ [STEP START] Failed to send step_start for {node_name}")
                        
                        # Handle step completion events
                        if event_type == "on_chain_end":
                            node_name_raw = event.get("name", "unknown")
                            node_name = normalize_node_name(node_name_raw)
                            
                            # Only send step_complete for relevant nodes
                            if is_step_complete_node(node_name_raw) or is_step_complete_node(node_name):
                                    # Extract state update from event
                                data_dict = event.get("data", {})
                                output = data_dict.get("output", {})
                                
                                # Get LLM role from output state (may have been updated)
                                llm_role = output.get("llm_role") if isinstance(output, dict) else None
                                template_route_type = output.get("template_route_type") if isinstance(output, dict) else None
                                
                                # CRITICAL: Extract data_pack BEFORE serialization to prevent truncation
                                # serialize_state_for_json truncates large dicts, which would break data_pack.metadata
                                preserved_data_pack = None
                                if isinstance(output, dict) and 'data_pack' in output:
                                    import copy
                                    preserved_data_pack = copy.deepcopy(output['data_pack'])
                                    logger.info(f"📦 [WEBSOCKET] Preserved data_pack before serialization: {len(preserved_data_pack.get('records', []))} records, {len(preserved_data_pack.get('metadata', {}))} metadata keys")
                                
                                # CRITICAL: Extract solver_result BEFORE serialization to prevent depth truncation
                                # serialize_state_for_json has max_depth=5, which truncates nested solution structures
                                preserved_solver_result = None
                                if isinstance(output, dict) and 'solver_result' in output:
                                    import copy
                                    preserved_solver_result = copy.deepcopy(output['solver_result'])
                                    logger.info(f"🎯 [WEBSOCKET] Preserved solver_result before serialization: status={preserved_solver_result.get('status', 'unknown')}, has_solution={bool(preserved_solver_result.get('solution'))}")
                                
                                # Serialize output to JSON-compatible format
                                serialized_output = serialize_state_for_json(output) if isinstance(output, dict) else output
                                
                                # Restore preserved data_pack after serialization (if it was truncated)
                                if preserved_data_pack and isinstance(serialized_output, dict):
                                    serialized_output['data_pack'] = preserved_data_pack
                                    logger.info(f"✅ [WEBSOCKET] Restored preserved data_pack after serialization")
                                
                                # Restore preserved solver_result after serialization with higher depth limit
                                # Serialize solver_result separately with max_depth=15 to preserve nested structures
                                if preserved_solver_result and isinstance(serialized_output, dict):
                                    serialized_solver_result = serialize_state_for_json(preserved_solver_result, max_depth=15)
                                    serialized_output['solver_result'] = serialized_solver_result
                                    logger.info(f"✅ [WEBSOCKET] Restored preserved solver_result after serialization (max_depth=15)")
                                
                                # DEBUG: Log output structure for generate_data to see if step_outputs exists
                                if (node_name == "generate_data" or node_name_raw == "generate_data") and isinstance(serialized_output, dict):
                                    logger.info(f"🔍 [DEBUG] serialized_output for {node_name} keys: {list(serialized_output.keys())[:30]}")
                                    logger.info(f"🔍 [DEBUG] serialized_output has 'step_outputs': {'step_outputs' in serialized_output}")
                                    if 'step_outputs' in serialized_output:
                                        step_outputs_value = serialized_output['step_outputs']
                                        logger.info(f"🔍 [DEBUG] step_outputs type: {type(step_outputs_value)}")
                                        logger.info(f"🔍 [DEBUG] step_outputs keys: {list(step_outputs_value.keys()) if isinstance(step_outputs_value, dict) else 'N/A'}")
                                
                                # Debug: Log output structure to understand where thinking content might be
                                if node_name == "step3_assumptions" and isinstance(serialized_output, dict):
                                    logger.info(f"🔍 [DEBUG] Output keys for {node_name}: {list(serialized_output.keys())[:20]}")
                                    # Check if assumptions field exists and has _thinking_content
                                    if "assumptions" in serialized_output:
                                        assumptions = serialized_output.get("assumptions")
                                        if isinstance(assumptions, dict) and "_thinking_content" in assumptions:
                                            logger.info(f"✅ [DEBUG] Found _thinking_content in assumptions dict")
                                        elif isinstance(assumptions, list) and len(assumptions) > 0:
                                            logger.info(f"🔍 [DEBUG] assumptions is a list with {len(assumptions)} items")
                                            if isinstance(assumptions[0], dict) and "_thinking_content" in assumptions[0]:
                                                logger.info(f"✅ [DEBUG] Found _thinking_content in assumptions[0]")
                                
                                # Extract thinking blocks from output using helper function
                                thinking_blocks = []
                                if isinstance(serialized_output, dict):
                                    # CRITICAL: Always log output structure in production (use INFO level)
                                    logger.info(f"🔍 [OUTPUT] Extracting thinking from {node_name}. Output keys: {list(serialized_output.keys())[:20] if isinstance(serialized_output, dict) else 'N/A'}")
                                    thinking_blocks = extract_thinking_from_output(serialized_output)
                                    if thinking_blocks:
                                        logger.info(f"🧠 [THINKING] Found {len(thinking_blocks)} thinking block(s) in {node_name} output")
                                    else:
                                        logger.info(f"🔍 [OUTPUT] No thinking blocks found in {node_name} output. Output keys: {list(serialized_output.keys())[:20] if isinstance(serialized_output, dict) else 'N/A'}")
                                        # Try to find _thinking_content in top-level keys
                                        if "_thinking_content" in serialized_output:
                                            logger.info(f"✅ [OUTPUT] Found _thinking_content at top level of {node_name}")
                                        # Check nested structures
                                        for key in serialized_output.keys():
                                            if isinstance(serialized_output[key], dict) and "_thinking_content" in serialized_output[key]:
                                                logger.info(f"✅ [OUTPUT] Found _thinking_content in {node_name}.{key}")
                                
                                # Send thinking blocks as separate messages before step_complete
                                for i, thinking_content in enumerate(thinking_blocks):
                                    logger.info(f"📝 [THINKING] Streaming thinking block {i+1}/{len(thinking_blocks)} from {node_name} (length: {len(thinking_content)})")
                                    thinking_msg = {
                                        "type": "thinking",
                                        "step": node_name,
                                        "content": thinking_content,
                                        "session_id": session_id,
                                        "timestamp": datetime.now().isoformat()
                                    }
                                    success = await safe_send_json(websocket, thinking_msg, session_id)
                                    if success:
                                        logger.info(f"✅ [THINKING] Successfully sent thinking message {i+1}/{len(thinking_blocks)} from {node_name} - length: {len(thinking_content)}")
                                    else:
                                        logger.warning(f"⚠️ [THINKING] Failed to send thinking message {i+1}/{len(thinking_blocks)} from {node_name} - WebSocket may be closed")
                                
                                # Send step_complete event (what React UI expects)
                                # CRITICAL: Reduce payload size for step_complete events
                                # Remove large intermediate fields but keep essential step results
                                step_output = serialized_output.copy() if isinstance(serialized_output, dict) else serialized_output
                                
                                # HYBRID APPROACH: Include complete thinking content in step_complete as reliable source
                                # This ensures thinking is always available even if streaming fails
                                complete_thinking = ""
                                if thinking_blocks:
                                    # Join all thinking blocks into complete content
                                    complete_thinking = "\n\n".join(thinking_blocks)
                                    logger.info(f"📦 [STEP_COMPLETE] Including {len(thinking_blocks)} thinking block(s) in step_complete for {node_name} (total length: {len(complete_thinking)})")
                                
                                # Remove large fields that aren't needed in UI for step updates
                                if isinstance(step_output, dict):
                                    # CRITICAL FIX: Also check for _thinking_content in step_output if extraction failed
                                    # This ensures thinking is preserved even if extract_thinking_from_output() doesn't find it
                                    if not complete_thinking and '_thinking_content' in step_output:
                                        complete_thinking = step_output['_thinking_content']
                                        if complete_thinking:  # Only log if we actually got thinking content
                                            logger.info(f"📝 [THINKING FALLBACK] Found _thinking_content in step_output for {node_name} (length: {len(complete_thinking)})")

                                    # Keep essential fields, remove verbose ones
                                    essential_step_fields = {
                                        'current_step': step_output.get('current_step'),
                                        'completed_steps': step_output.get('completed_steps'),
                                        'workflow_stage': step_output.get('workflow_stage'),
                                        'thinking_content': complete_thinking if complete_thinking else None,  # Add complete thinking
                                        'thinking_available': bool(complete_thinking),  # Flag to indicate thinking is available
                                        '_thinking_content': step_output.get('_thinking_content'),  # CRITICAL: Preserve _thinking_content for frontend
                                        'errors': step_output.get('errors'),
                                        'warnings': step_output.get('warnings'),
                                    }
                                    
                                    # Keep step-specific results (entities, objectives, constraints, etc.)
                                    # CRITICAL: Include all intent discovery step results for UI display
                                    step_result_keys = [
                                        # Intent discovery results (CRITICAL for intent tab)
                                        'discovered_intent',  # CLEAN WORKFLOW: Unified intent from all 9 steps
                                        'entities', 'objectives', 'constraints', 'assumptions',
                                        'classification', 'decomposition', 'domain_context',
                                        'classification_reasoning', 'assumptions_reasoning',
                                        'entities_reasoning', 'objectives_reasoning', 'constraints_reasoning',
                                        # KnowledgeBase research results (including template objectives/constraints)
                                        'knowledgebase_match', 'knowledgebase_match_score', 'knowledgebase_route_type',
                                        'matched_template', 'template_match_score', 'template_route_type',
                                        # Template objectives/constraints from step 0 (shown immediately)
                                        'template_objectives', 'template_constraints',
                                        # Pyomo results
                                        'pyomo_code', 'pyomo_model_structure',
                                        # Data results
                                        'data_pack', 'generated_data', 'data_quality_score',
                                        'data_quality_metrics', 'data_validation', 'data_source',
                                        'data_tier', 'data_tier_status', 'step_outputs',  # SDV Integration: Include tier info and step outputs
                                        # Solver results (CRITICAL for solver tab)
                                        'mathematical_solver_result', 'dame_solver_result', 'solver_comparison',
                                        'optimization_solution', 'optimization_status', 'objective_value',
                                        'solver_used', 'mathematical_solver_error', 'dame_solver_error',
                                        'solver_result', 'solver_tier', 'solver_execution_type', 'solver_selection',
                                        'solver_thinking', 'solver_diagnostics', 'solver_reasoning', 'tuned_parameters',
                                        'business_explanation',
                                        # Generic result field
                                        'result'
                                    ]
                                    
                                    # CRITICAL: Exclude pyomo_model (non-serializable Pyomo object) BEFORE processing
                                    if 'pyomo_model' in step_output:
                                        # Remove it - use pyomo_code instead for WebSocket
                                        del step_output['pyomo_model']
                                        if 'pyomo_code' in step_output:
                                            essential_step_fields['pyomo_code_available'] = True
                                    
                                    # Also check nested structures for pyomo_model
                                    def remove_pyomo_models(obj):
                                        """Recursively remove pyomo_model objects from nested dicts"""
                                        if isinstance(obj, dict):
                                            return {k: remove_pyomo_models(v) for k, v in obj.items() if k != 'pyomo_model'}
                                        elif isinstance(obj, list):
                                            return [remove_pyomo_models(item) for item in obj]
                                        else:
                                            # Check if it's a Pyomo model
                                            try:
                                                import pyomo.environ as pyo
                                                if isinstance(obj, pyo.ConcreteModel):
                                                    return None  # Remove Pyomo models
                                            except:
                                                pass
                                            return obj
                                    
                                    step_output = remove_pyomo_models(step_output)
                                    
                                    for key in step_result_keys:
                                        if key in step_output:
                                            # For large objects, send summary only
                                            value = step_output[key]
                                            
                                            # Special handling for data_pack - preserve structure but limit records
                                            if key == 'data_pack' and isinstance(value, dict):
                                                # Keep data_pack structure but limit records list size
                                                # IMPORTANT: Use deep copy to preserve nested metadata structures
                                                import copy
                                                data_pack_copy = copy.deepcopy(value)
                                                
                                                # Limit records list size (for UI performance)
                                                if 'records' in data_pack_copy and isinstance(data_pack_copy['records'], list):
                                                    if len(data_pack_copy['records']) > 100:
                                                        # Keep first 100 records, add metadata about truncation
                                                        data_pack_copy['records'] = data_pack_copy['records'][:100]
                                                        data_pack_copy['_records_truncated'] = True
                                                        data_pack_copy['_total_records'] = len(value['records'])
                                                
                                                # CRITICAL: Preserve ALL metadata including nested lists (e.g., advisors)
                                                # Don't truncate metadata - it's needed for solver
                                                # Metadata structure: { "advisors": [...], "client_needs": {...}, ... }
                                                essential_step_fields[key] = data_pack_copy
                                                continue
                                            
                                            # Special handling for step_outputs - preserve structure for UI display
                                            if key == 'step_outputs' and isinstance(value, dict):
                                                # CRITICAL: Preserve step_outputs structure for tier-based UI display
                                                # Don't truncate - needed for DataStepsProgress component
                                                import copy
                                                essential_step_fields[key] = copy.deepcopy(value)
                                                continue
                                            
                                            # Special handling for solver_result - preserve structure for SolverStepsProgress component
                                            if key == 'solver_result' and isinstance(value, dict):
                                                # CRITICAL: Preserve solver_result structure for solver UI display
                                                # Don't truncate - needed for SolverStepsProgress component
                                                import copy
                                                essential_step_fields[key] = copy.deepcopy(value)
                                                continue
                                            
                                            if isinstance(value, dict) and len(str(value)) > 10000:
                                                # Create summary for large dicts
                                                essential_step_fields[key] = {
                                                    '_summary': f"Large {key} object ({len(str(value))} chars)",
                                                    '_keys': list(value.keys())[:10] if isinstance(value, dict) else [],
                                                    '_truncated': True
                                                }
                                            else:
                                                essential_step_fields[key] = value
                                    
                                    # Keep reasoning fields for intent steps (they're needed for UI display)
                                    # Only remove messages and other verbose fields
                                    remove_fields = ['messages', 'discovered_intent', 'generated_data', 
                                                    'sympy_formulas',
                                                    'knowledgebase_matches', 'early_template_matches']
                                    # DON'T remove:
                                    # - *_reasoning fields (needed for intent tab display)
                                    # - data_pack (needed for data tab, but will be truncated above)
                                    # - pyomo_model (already removed above)
                                    for field in remove_fields:
                                        if field.startswith('*'):
                                            # Remove all fields matching pattern
                                            pattern = field[1:]  # Remove *
                                            step_output = {k: v for k, v in step_output.items() 
                                                          if not k.endswith(pattern)}
                                        elif field in step_output:
                                            del step_output[field]
                                    
                                    # CRITICAL: Also remove pyomo_model if it somehow still exists
                                    if 'pyomo_model' in step_output:
                                        del step_output['pyomo_model']
                                    
                                    step_output = {**essential_step_fields, **{k: v for k, v in step_output.items() 
                                                                              if k not in essential_step_fields}}
                                
                                # CRITICAL: Use normalized step name for frontend compatibility
                                # Frontend expects step keys like step0_knowledgebase_research, step1_classification, etc.
                                
                                # SIMPLIFIED STRUCTURE FOR generate_data: Send essential fields directly
                                # This matches the JSON structure from test output for easier UI mapping
                                if node_name == "generate_data" or node_name_raw == "generate_data":
                                    # Extract essential fields for direct UI rendering
                                    data_pack = step_output.get('data_pack', {})
                                    data_quality_score = step_output.get('data_quality_score', 0)
                                    data_quality_metrics = step_output.get('data_quality_metrics', {})
                                    data_source = step_output.get('data_source', 'synthetic')
                                    data_tier = step_output.get('data_tier', None)
                                    data_tier_status = step_output.get('data_tier_status', None)
                                    step_outputs = step_output.get('step_outputs', {})
                                    
                                    # CRITICAL: Extract thinking content from step_outputs phases (like intent tool)
                                    # Check each phase in step_outputs for thinking content
                                    phase_thinking = {}
                                    if isinstance(step_outputs, dict):
                                        # Check all possible phase/tier keys (Tier 3 uses 'tier3', Tier 4 uses 'tier4')
                                        for phase_key in ['phase1', 'phase4a', 'phase4d', 'tier3', 'tier4']:
                                            phase_data = step_outputs.get(phase_key, {})
                                            if isinstance(phase_data, dict):
                                                # Check multiple locations for thinking content
                                                phase_thinking_content = (
                                                    phase_data.get('thinking_content') or
                                                    phase_data.get('_thinking_content') or
                                                    phase_data.get('result', {}).get('_thinking_content') or
                                                    phase_data.get('result', {}).get('thinking_content')
                                                )
                                                if phase_thinking_content:
                                                    phase_thinking[phase_key] = phase_thinking_content
                                                    logger.info(f"📝 [WEBSOCKET] Found thinking content for {phase_key} (length: {len(phase_thinking_content)})")
                                    
                                    # DEBUG: Log phase_thinking extraction
                                    if phase_thinking:
                                        logger.info(f"📝 [WEBSOCKET] Extracted thinking content for phases: {list(phase_thinking.keys())}")
                                    else:
                                        logger.warning(f"⚠️ [WEBSOCKET] No thinking content found in step_outputs. step_outputs keys: {list(step_outputs.keys()) if isinstance(step_outputs, dict) else 'N/A'}")
                                    
                                    # Also check top-level thinking content
                                    top_level_thinking = complete_thinking or step_output.get('_thinking_content') or step_output.get('thinking_content')
                                    
                                    # Send flattened structure - UI can use data_pack directly
                                    step_data = {
                                        "type": "step_complete",
                                        "step": node_name,
                                        "step_number": chunk_count,
                                        "llm_role": llm_role,
                                        "template_route_type": template_route_type,
                                        "data": {
                                            node_name: {
                                                # Essential fields at top level for easy UI access
                                                "data_pack": data_pack,  # Main data structure - UI can render directly
                                                "data_quality_score": data_quality_score,
                                                "data_quality_metrics": data_quality_metrics,
                                                "data_source": data_source,
                                                "data_tier": data_tier,
                                                "data_tier_status": data_tier_status,
                                                "step_outputs": step_outputs,
                                                # CRITICAL: Include thinking content (like intent tool)
                                                "thinking_content": top_level_thinking if top_level_thinking else None,
                                                "thinking_available": bool(top_level_thinking or phase_thinking),
                                                "phase_thinking": phase_thinking if phase_thinking else None,
                                                # Keep filtered step_output for backward compatibility (reduce payload size)
                                                "_full_output": filter_large_fields_for_step_complete(step_output, node_name)
                                            }
                                        },
                                        "session_id": session_id,
                                        "timestamp": datetime.now().isoformat()
                                    }
                                elif node_name == "solver_router" or node_name_raw == "solver_router":
                                    # Solver router node: Extract routing info (NOT solver_result - that comes from tier solvers)
                                    # solver_router just determines which tier solver to route to

                                    # Extract tier from intent_context or solver_recommendation
                                    intent_context = serialized_output.get('intent_context', {}) if isinstance(serialized_output, dict) else {}
                                    template_route_type_from_context = intent_context.get('template_route_type', template_route_type)

                                    # Map template_route_type to solver_tier
                                    solver_tier_mapping = {
                                        'template_direct': 'tier3',
                                        'guided_review': 'tier2',
                                        'guided_learning': 'tier1',
                                        'adhoc': 'adhoc',
                                    }
                                    solver_tier = solver_tier_mapping.get(template_route_type_from_context, 'unknown')
                                    solver_execution_type = template_route_type_from_context or 'unknown'

                                    # Send solver router structure with routing info (NOT solver_result)
                                    step_data = {
                                        "type": "step_complete",
                                        "step": node_name,
                                        "step_number": chunk_count,
                                        "llm_role": llm_role,
                                        "template_route_type": template_route_type_from_context,
                                        "solver_tier": solver_tier,
                                        "solver_execution_type": solver_execution_type,
                                        "data": {
                                            node_name: {
                                                # Include routing metadata (solver_result will come from tier solver nodes)
                                                "solver_tier": solver_tier,
                                                "solver_execution_type": solver_execution_type,
                                                "solver_recommendation": serialized_output.get('solver_recommendation', {}),
                                                # Keep filtered step_output for backward compatibility (reduce payload size)
                                                "_full_output": filter_large_fields_for_step_complete(step_output, node_name)
                                            }
                                        },
                                        "session_id": session_id,
                                        "timestamp": datetime.now().isoformat()
                                    }

                                    logger.info(f"🔧 [WEBSOCKET] Solver router routing info: tier={solver_tier}, execution_type={solver_execution_type}")
                                elif node_name in ["tier3_solver", "tier2_solver", "tier1_solver", "adhoc_solver"] or node_name_raw in ["tier3_solver", "tier2_solver", "tier1_solver", "adhoc_solver"]:
                                    # Solver-specific structure: Extract solver CoT data
                                    solver_tier = step_output.get('solver_tier', node_name.replace('_solver', ''))
                                    solver_execution_type = step_output.get('solver_execution_type', 'unknown')
                                    solver_selection = step_output.get('solver_selection', {})
                                    solver_thinking = step_output.get('solver_thinking', '')
                                    solver_diagnostics = step_output.get('solver_diagnostics', {})
                                    solver_reasoning = step_output.get('solver_reasoning', {})
                                    tuned_parameters = step_output.get('tuned_parameters', {})
                                    # CRITICAL: Extract solver_result for status and data_source
                                    solver_result = step_output.get('solver_result', {})
                                    
                                    # Extract thinking content from solver reasoning
                                    solver_thinking_content = {}
                                    if solver_reasoning:
                                        # Extract reasoning from different sources
                                        if isinstance(solver_reasoning, dict):
                                            solver_thinking_content['selection_reasoning'] = solver_reasoning.get('selection_reasoning', {})
                                            solver_thinking_content['parameter_tuning_reasoning'] = solver_reasoning.get('parameter_tuning_reasoning', {})
                                            solver_thinking_content['model_building_thinking'] = solver_reasoning.get('model_building_thinking', '')
                                            solver_thinking_content['solver_execution_thinking'] = solver_reasoning.get('solver_execution_thinking', '')
                                    
                                    # Also check top-level thinking content
                                    top_level_thinking = complete_thinking or step_output.get('_thinking_content') or step_output.get('thinking_content') or solver_thinking
                                    
                                    # Send solver-specific structure
                                    step_data = {
                                        "type": "step_complete",
                                        "step": node_name,
                                        "step_number": chunk_count,
                                        "llm_role": llm_role,
                                        "template_route_type": template_route_type,
                                        "solver_tier": solver_tier,
                                        "solver_execution_type": solver_execution_type,
                                        "data": {
                                            node_name: {
                                                # Essential solver fields at top level for easy UI access
                                                "solver_tier": solver_tier,
                                                "solver_execution_type": solver_execution_type,
                                                "solver_selection": solver_selection,
                                                "solver_thinking": solver_thinking,
                                                "solver_diagnostics": solver_diagnostics,
                                                "solver_reasoning": solver_reasoning,
                                                "tuned_parameters": tuned_parameters,
                                                # CRITICAL: Include solver_result for status and data_source
                                                "solver_result": solver_result,
                                                # CRITICAL: Include thinking content (like intent/data tools)
                                                "thinking_content": top_level_thinking if top_level_thinking else None,
                                                "thinking_available": bool(top_level_thinking or solver_thinking_content),
                                                "solver_thinking_content": solver_thinking_content if solver_thinking_content else None,
                                                # Keep filtered step_output for backward compatibility (reduce payload size)
                                                "_full_output": filter_large_fields_for_step_complete(step_output, node_name)
                                            }
                                        },
                                        "session_id": session_id,
                                        "timestamp": datetime.now().isoformat()
                                    }
                                    
                                    logger.info(f"🔧 [WEBSOCKET] Extracted solver CoT for {solver_tier}: selection={bool(solver_selection)}, thinking={bool(solver_thinking)}, reasoning={bool(solver_reasoning)}, solver_result={bool(solver_result)}")
                                else:
                                    # Standard structure for other steps
                                    step_data = {
                                        "type": "step_complete",
                                        "step": node_name,  # Normalized name (e.g., step0_knowledgebase_research)
                                        "step_number": chunk_count,
                                        "llm_role": llm_role,  # Include LLM role for UI display
                                        "template_route_type": template_route_type,  # Include route type
                                        "data": {
                                            node_name: step_output,  # Use normalized name as key
                                            # Also include raw node name for backward compatibility
                                            node_name_raw: step_output if node_name_raw != node_name else None
                                        },
                                        "session_id": session_id,
                                        "timestamp": datetime.now().isoformat()
                                    }
                                
                                # Remove None values from data
                                step_data["data"] = {k: v for k, v in step_data["data"].items() if v is not None}
                                
                                # DEBUG: Log step_output structure for generate_data
                                if node_name == "generate_data" or node_name_raw == "generate_data":
                                    logger.info(f"🔍 [DEBUG] step_output for {node_name} (before sending):")
                                    logger.info(f"   step_output type: {type(step_output)}")
                                    logger.info(f"   step_output keys: {list(step_output.keys()) if isinstance(step_output, dict) else 'N/A'}")
                                    logger.info(f"   step_output has step_outputs: {'step_outputs' in step_output if isinstance(step_output, dict) else False}")
                                    logger.info(f"   step_data['data'] keys: {list(step_data['data'].keys())}")
                                    logger.info(f"   step_data['data'][{node_name}] keys: {list(step_data['data'][node_name].keys()) if isinstance(step_data['data'].get(node_name), dict) else 'N/A'}")
                                    
                                    # CRITICAL: Verify data_pack is present and not truncated
                                    data_pack_in_step = step_data['data'][node_name].get('data_pack') if isinstance(step_data['data'].get(node_name), dict) else None
                                    if data_pack_in_step:
                                        records_count = len(data_pack_in_step.get('records', []))
                                        metadata_keys = list(data_pack_in_step.get('metadata', {}).keys())
                                        metadata_counts = {k: len(v) if isinstance(v, dict) else (len(v) if isinstance(v, list) else 1) 
                                                          for k, v in data_pack_in_step.get('metadata', {}).items()}
                                        logger.info(f"✅ [DEBUG] data_pack verified: {records_count} records, {len(metadata_keys)} metadata keys: {metadata_counts}")
                                    else:
                                        logger.warning(f"⚠️ [DEBUG] data_pack MISSING from step_data!")
                                
                                # CRITICAL: Increase max_size for generate_data and solver_router to accommodate large data
                                # data_pack contains matrices with thousands of entries (client_needs: 1000, relationship_score: 1500, etc.)
                                # solver_result contains large solution dicts (advisor_assignments, etc.)
                                max_size_for_step = 500000 if (node_name == "generate_data" or node_name_raw == "generate_data") else (200000 if (node_name == "solver_router" or node_name_raw == "solver_router") else 50000)
                                success = await safe_send_json(websocket, step_data, session_id, max_size=max_size_for_step)
                                if success:
                                    logger.info(f"✅ Sent step_complete for {node_name} (raw: {node_name_raw})")
                                else:
                                    logger.warning(f"⚠️ Failed to send step_complete for {node_name} - WebSocket may be closed")
                                    # Don't break - continue processing other events
                                
                                # Handle workflow completion (check if this is the final step)
                                if node_name_raw == "generate_business_explanation" or node_name == "generate_business_explanation":
                                    # Final step completed
                                    raw_result = output if isinstance(output, dict) else {}
                                    # Serialize result to JSON-compatible format
                                    # Use _deep_clean_value for better size control
                                    try:
                                        from dcisionai_workflow.shared.core.graph.state_helpers import _deep_clean_value
                                        final_result = _deep_clean_value(raw_result) if isinstance(raw_result, dict) else raw_result
                                    except ImportError:
                                        final_result = serialize_state_for_json(raw_result) if isinstance(raw_result, dict) else raw_result
                                    
                                    # Limit final result size - remove intermediate fields, KEEP solver results intact
                                    if isinstance(final_result, dict):
                                        # Fields to REMOVE (intermediate/verbose data):
                                        # - messages (can be large, already streamed)
                                        # - discovered_intent (intermediate data)
                                        # - generated_data (intermediate data)
                                        # - data_pack (intermediate data)
                                        # - *_reasoning fields (verbose reasoning trails)
                                        # - decomposition, domain_context (intermediate)
                                        # - sympy_formulas (if present, intermediate)
                                        
                                        # Fields to KEEP (essential results):
                                        essential_fields = {
                                            'problem_description': final_result.get('problem_description'),
                                            'workflow_stage': final_result.get('workflow_stage'),
                                            'optimization_status': final_result.get('optimization_status'),
                                            'solver_used': final_result.get('solver_used'),
                                            'objective_value': final_result.get('objective_value'),
                                            # KEEP solver results FULLY - this is our MOAT!
                                            'mathematical_solver_result': final_result.get('mathematical_solver_result'),
                                            'dame_solver_result': final_result.get('dame_solver_result'),
                                            'solver_comparison': final_result.get('solver_comparison'),
                                            'optimization_solution': final_result.get('optimization_solution'),
                                            'business_explanation': final_result.get('business_explanation'),
                                            'errors': final_result.get('errors'),
                                            'warnings': final_result.get('warnings')
                                        }
                                        
                                        # Remove None values
                                        final_result = {k: v for k, v in essential_fields.items() if v is not None}
                                        
                                        logger.info(f"🔍 [SIZE REDUCTION] Removed intermediate fields, kept solver results intact. Size: {len(str(final_result))} chars")
                                    
                                    # Log final result size before sending
                                    try:
                                        test_json = json.dumps(final_result, default=str)
                                        test_size = len(test_json.encode('utf-8'))
                                        logger.info(f"🔍 [FINAL RESULT SIZE] {test_size} bytes before wrapping for session {session_id}")
                                    except Exception as e:
                                        logger.warning(f"Failed to check final result size: {e}")
                                    
                                    success = await safe_send_json(websocket, {
                                        "type": "workflow_complete",
                                        "session_id": session_id,
                                        "result": final_result,
                                        "timestamp": datetime.now().isoformat()
                                    }, session_id, max_size=50000)  # Use 50KB limit for final results
                                    if success:
                                        logger.info(f"✅ Workflow completed for session {session_id}")
                                        break
                                    else:
                                        logger.warning(f"⚠️ Failed to send workflow_complete - WebSocket may be closed")
                                        break
                        
                        # Send progress update to frontend every 100 events
                        if chunk_count % 100 == 0:
                            event_name = event.get("name", "unknown")
                            elapsed_time = (datetime.now() - start_time).total_seconds() if 'start_time' in locals() else 0
                            
                            # Send progress update to frontend every 100 events
                            if websocket.client_state.name == 'CONNECTED':
                                await safe_send_json(websocket, {
                                    "type": "workflow_progress",
                                    "session_id": session_id,
                                    "event_count": chunk_count,
                                    "elapsed_seconds": elapsed_time,
                                    "timeout_seconds": timeout_seconds,
                                    "current_node": event_name,
                                    "timestamp": datetime.now().isoformat()
                                }, session_id)
                
                # If we exited the loop without completion, check if it was cancelled
                if workflow_cancelled:
                    logger.info(f"⚠️ Workflow execution cancelled for session {session_id} due to WebSocket disconnect")
                    # Don't try to get final state if workflow was cancelled
                    return
                
                # If we exited the loop without completion, check if workflow errored
                # Note: This should rarely happen if events are captured correctly
                if not final_result:
                    logger.warning(f"Workflow loop exited without final result for session {session_id}")
                    # Check if workflow errored - if so, don't restart, just send error
                    workflow_stage = state.get("workflow_stage", "")
                    errors = state.get("errors", [])
                    
                    if workflow_stage == "error" or errors:
                        logger.warning(f"⚠️ Workflow ended with errors, not restarting. Errors: {errors}")
                        if websocket.client_state.name == 'CONNECTED':
                            await safe_send_json(websocket, {
                                "type": "workflow_error",
                                "session_id": session_id,
                                "errors": errors,
                                "workflow_stage": workflow_stage,
                                "timestamp": datetime.now().isoformat()
                            }, session_id)
                        return  # Don't restart workflow
                    
                    # Only try to get final state if WebSocket is still connected AND workflow didn't error
                    if websocket.client_state.name == 'CONNECTED':
                        try:
                            # CRITICAL FIX: Don't restart workflow - just get current state
                            # workflow.ainvoke would restart from beginning, causing infinite loop
                            # Instead, serialize the current state (which should be at END node)
                            # Use _deep_clean_value for better size control
                            try:
                                from dcisionai_workflow.shared.core.graph.state_helpers import _deep_clean_value
                                final_result = _deep_clean_value(state) if isinstance(state, dict) else state
                            except ImportError:
                                final_result = serialize_state_for_json(state) if isinstance(state, dict) else state
                            
                            # Limit final result size - remove intermediate fields, KEEP solver results intact
                            if isinstance(final_result, dict):
                                # Fields to REMOVE (intermediate/verbose data):
                                # - messages (can be large, already streamed)
                                # - discovered_intent (intermediate data)
                                # - generated_data (intermediate data)
                                # - data_pack (intermediate data)
                                # - *_reasoning fields (verbose reasoning trails)
                                # - decomposition, domain_context (intermediate)
                                # - sympy_formulas (if present, intermediate)
                                
                                # Fields to KEEP (essential results):
                                essential_fields = {
                                    'problem_description': final_result.get('problem_description'),
                                    'workflow_stage': final_result.get('workflow_stage'),
                                    'optimization_status': final_result.get('optimization_status'),
                                    'solver_used': final_result.get('solver_used'),
                                    'objective_value': final_result.get('objective_value'),
                                    # KEEP solver results FULLY - this is our MOAT!
                                    'mathematical_solver_result': final_result.get('mathematical_solver_result'),
                                    'dame_solver_result': final_result.get('dame_solver_result'),
                                    'solver_comparison': final_result.get('solver_comparison'),
                                    'optimization_solution': final_result.get('optimization_solution'),
                                    'business_explanation': final_result.get('business_explanation'),
                                    'errors': final_result.get('errors'),
                                    'warnings': final_result.get('warnings')
                                }
                                
                                # Remove None values
                                final_result = {k: v for k, v in essential_fields.items() if v is not None}
                                
                                logger.info(f"🔍 [SIZE REDUCTION] Removed intermediate fields, kept solver results intact. Size: {len(str(final_result))} chars")
                            
                            # Log final result size before sending
                            try:
                                test_json = json.dumps(final_result, default=str)
                                test_size = len(test_json.encode('utf-8'))
                                logger.info(f"🔍 [FINAL RESULT SIZE] {test_size} bytes before wrapping for session {session_id}")
                            except Exception as e:
                                logger.warning(f"Failed to check final result size: {e}")
                            
                            success = await safe_send_json(websocket, {
                                "type": "workflow_complete",
                                "session_id": session_id,
                                "result": final_result,
                                "timestamp": datetime.now().isoformat()
                            }, session_id, max_size=50000)  # Use 50KB limit for final results
                            if success:
                                logger.info(f"✅ Sent workflow_complete (fallback) for session {session_id}")
                            else:
                                logger.warning(f"⚠️ Failed to send workflow_complete (fallback) - WebSocket may be closed")
                        except Exception as e:
                            logger.error(f"Error getting final state: {e}", exc_info=True)
                            if websocket.client_state.name == 'CONNECTED':
                                await safe_send_json(websocket, {
                                    "type": "error",
                                    "message": f"Workflow completed but failed to retrieve final result: {str(e)}"
                                }, session_id)
                    else:
                        logger.info(f"⚠️ WebSocket disconnected, skipping final state retrieval for session {session_id}")
            except asyncio.TimeoutError:
                logger.error(f"Workflow timeout after {timeout_seconds}s for session {session_id}")
                if websocket.client_state.name == 'CONNECTED':
                    await safe_send_json(websocket, {
                        "type": "error",
                        "message": f"Workflow timeout after {timeout_seconds} seconds",
                        "session_id": session_id
                    }, session_id)
                        
        except asyncio.TimeoutError:
            logger.error(f"Workflow timeout after {timeout_seconds}s for session {session_id}")
            await safe_send_json(websocket, {
                "type": "error",
                "message": f"Workflow timeout after {timeout_seconds} seconds"
            }, session_id)
        except Exception as e:
            logger.error(f"Error during workflow execution: {e}", exc_info=True)
            await safe_send_json(websocket, {
                "type": "error",
                "message": f"Workflow error: {str(e)}"
            }, session_id)
            
    except WebSocketDisconnect:
        logger.info(f"⚠️ WebSocket disconnected by client for session {session_id} - workflow execution stopped")
        # Workflow execution will stop automatically when WebSocket disconnects
        # No cleanup needed - LangGraph will handle cancellation
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}", exc_info=True)
        try:
            await safe_send_json(websocket, {
                "type": "error",
                "message": str(e),
                "session_id": session_id
            }, session_id)
        except Exception:
            logger.warning(f"Could not send error message - WebSocket already closed for session {session_id}")
        finally:
            # Ensure WebSocket is closed on error
            try:
                await websocket.close(code=1011, reason=f"Server error: {str(e)}")
            except Exception:
                pass  # WebSocket may already be closed

