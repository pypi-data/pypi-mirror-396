"""
Checkpointing Tool for MCP Server (Phase 5)

Provides checkpoint management functionality following MCP protocol.
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# In-memory checkpoint storage (can be replaced with persistent storage)
_checkpoint_storage: Dict[str, Dict[str, Any]] = {}


def create_checkpoint(state: Dict[str, Any], session_id: Optional[str] = None, checkpoint_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a checkpoint of current workflow state.
    
    Args:
        state: LangGraph state to checkpoint
        session_id: Optional session ID
        checkpoint_id: Optional checkpoint ID (auto-generated if None)
        
    Returns:
        Dict with checkpoint_id and metadata
    """
    if checkpoint_id is None:
        checkpoint_id = f"checkpoint_{int(time.time() * 1000)}"
    
    checkpoint_data = {
        "checkpoint_id": checkpoint_id,
        "session_id": session_id or state.get("session_id", "unknown"),
        "timestamp": datetime.now().isoformat(),
        "state": _serialize_state(state),
        "metadata": {
            "workflow_stage": state.get("workflow_stage", "unknown"),
            "completed_steps": state.get("completed_steps", []),
            "problem_description": state.get("problem_description", "")[:100]  # Truncate for display
        }
    }
    
    _checkpoint_storage[checkpoint_id] = checkpoint_data
    logger.info(f"Created checkpoint: {checkpoint_id} for session: {session_id}")
    
    return {
        "checkpoint_id": checkpoint_id,
        "timestamp": checkpoint_data["timestamp"],
        "metadata": checkpoint_data["metadata"]
    }


def restore_checkpoint(checkpoint_id: str) -> Optional[Dict[str, Any]]:
    """
    Restore state from checkpoint.
    
    Args:
        checkpoint_id: Checkpoint ID to restore
        
    Returns:
        Restored state or None if checkpoint not found
    """
    if checkpoint_id not in _checkpoint_storage:
        logger.warning(f"Checkpoint not found: {checkpoint_id}")
        return None
    
    checkpoint_data = _checkpoint_storage[checkpoint_id]
    logger.info(f"Restored checkpoint: {checkpoint_id}")
    
    return checkpoint_data["state"]


def list_checkpoints(session_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all checkpoints, optionally filtered by session_id.
    
    Args:
        session_id: Optional session ID to filter by
        
    Returns:
        List of checkpoint metadata
    """
    checkpoints = []
    
    for checkpoint_id, checkpoint_data in _checkpoint_storage.items():
        if session_id is None or checkpoint_data.get("session_id") == session_id:
            checkpoints.append({
                "checkpoint_id": checkpoint_id,
                "session_id": checkpoint_data.get("session_id"),
                "timestamp": checkpoint_data.get("timestamp"),
                "metadata": checkpoint_data.get("metadata", {})
            })
    
    # Sort by timestamp (newest first)
    checkpoints.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return checkpoints


def delete_checkpoint(checkpoint_id: str) -> bool:
    """
    Delete a checkpoint.
    
    Args:
        checkpoint_id: Checkpoint ID to delete
        
    Returns:
        True if deleted, False if not found
    """
    if checkpoint_id in _checkpoint_storage:
        del _checkpoint_storage[checkpoint_id]
        logger.info(f"Deleted checkpoint: {checkpoint_id}")
        return True
    
    logger.warning(f"Checkpoint not found for deletion: {checkpoint_id}")
    return False


def _serialize_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize state for storage (remove non-serializable objects).
    
    Args:
        state: LangGraph state
        
    Returns:
        Serialized state dict
    """
    serialized = {}
    
    for key, value in state.items():
        try:
            # Try to serialize
            json.dumps(value)
            serialized[key] = value
        except (TypeError, ValueError):
            # Skip non-serializable values (like Pyomo models)
            logger.debug(f"Skipping non-serializable key: {key}")
            serialized[key] = None
    
    return serialized


# Note: MCP tool decorators would be added here if using FastMCP
# For now, these functions are used by the REST API endpoints
# The functions above (create_checkpoint, restore_checkpoint, etc.) are the core implementation

# MCP Tool functions (for future FastMCP integration)
# These can be registered with @mcp.tool() decorator when needed
# Example:
# from fastmcp import FastMCP
# mcp = FastMCP("DcisionAI Server")
# 
# @mcp.tool()
# def checkpoint_create(state: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
#     return create_checkpoint(state, session_id)
#
# @mcp.tool()
# def checkpoint_restore(checkpoint_id: str) -> Dict[str, Any]:
#     restored_state = restore_checkpoint(checkpoint_id)
#     if restored_state is None:
#         return {"error": f"Checkpoint not found: {checkpoint_id}"}
#     return {"state": restored_state}
#
# @mcp.tool()
# def checkpoint_list(session_id: Optional[str] = None) -> Dict[str, Any]:
#     return {"checkpoints": list_checkpoints(session_id)}
#
# @mcp.tool()
# def checkpoint_delete(checkpoint_id: str) -> Dict[str, Any]:
#     success = delete_checkpoint(checkpoint_id)
#     return {"success": success, "checkpoint_id": checkpoint_id}

