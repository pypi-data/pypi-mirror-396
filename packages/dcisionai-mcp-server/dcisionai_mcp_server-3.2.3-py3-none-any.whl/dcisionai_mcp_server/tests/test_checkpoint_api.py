"""
Tests for Checkpoint API (Phase 5)

Tests the checkpoint REST API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any

# Import checkpoint functions
try:
    from dcisionai_mcp_server.tools.checkpointing import (
        create_checkpoint,
        restore_checkpoint,
        list_checkpoints,
        delete_checkpoint
    )
    CHECKPOINTING_AVAILABLE = True
except ImportError:
    CHECKPOINTING_AVAILABLE = False


@pytest.mark.skipif(not CHECKPOINTING_AVAILABLE, reason="Checkpointing not available")
class TestCheckpointAPI:
    """Test checkpoint API functions"""
    
    def test_create_checkpoint(self):
        """Test checkpoint creation"""
        state = {
            "problem_description": "Test problem",
            "workflow_stage": "intent_discovery",
            "session_id": "test_session"
        }
        
        result = create_checkpoint(state, session_id="test_session")
        
        assert "checkpoint_id" in result
        assert "timestamp" in result
        assert "metadata" in result
        assert result["metadata"]["workflow_stage"] == "intent_discovery"
    
    def test_restore_checkpoint(self):
        """Test checkpoint restoration"""
        state = {
            "problem_description": "Test problem",
            "workflow_stage": "intent_discovery"
        }
        
        # Create checkpoint
        checkpoint_result = create_checkpoint(state, session_id="test_session")
        checkpoint_id = checkpoint_result["checkpoint_id"]
        
        # Restore checkpoint
        restored_state = restore_checkpoint(checkpoint_id)
        
        assert restored_state is not None
        assert restored_state["workflow_stage"] == "intent_discovery"
    
    def test_list_checkpoints(self):
        """Test checkpoint listing"""
        # Create multiple checkpoints with unique session IDs to avoid conflicts
        import time
        unique_session = f"test_session_{int(time.time() * 1000)}"
        state1 = {"workflow_stage": "stage1", "session_id": unique_session}
        state2 = {"workflow_stage": "stage2", "session_id": unique_session}
        
        # Create checkpoints with explicit checkpoint IDs to ensure they're different
        checkpoint1 = create_checkpoint(state1, session_id=unique_session, checkpoint_id=f"cp1_{int(time.time() * 1000)}")
        time.sleep(0.01)  # Small delay to ensure different timestamps
        checkpoint2 = create_checkpoint(state2, session_id=unique_session, checkpoint_id=f"cp2_{int(time.time() * 1000)}")
        
        # List checkpoints for this session
        checkpoints = list_checkpoints(session_id=unique_session)
        
        # Should have at least 2 checkpoints
        assert len(checkpoints) >= 2, f"Expected at least 2 checkpoints, got {len(checkpoints)}. Checkpoints: {checkpoints}"
        assert all("checkpoint_id" in cp for cp in checkpoints)
        assert all("timestamp" in cp for cp in checkpoints)
        
        # Verify both checkpoints are in the list
        checkpoint_ids = [cp["checkpoint_id"] for cp in checkpoints]
        assert checkpoint1["checkpoint_id"] in checkpoint_ids, f"Checkpoint 1 not found. IDs: {checkpoint_ids}"
        assert checkpoint2["checkpoint_id"] in checkpoint_ids, f"Checkpoint 2 not found. IDs: {checkpoint_ids}"
    
    def test_delete_checkpoint(self):
        """Test checkpoint deletion"""
        state = {"workflow_stage": "test"}
        
        # Create checkpoint
        checkpoint_result = create_checkpoint(state)
        checkpoint_id = checkpoint_result["checkpoint_id"]
        
        # Delete checkpoint
        success = delete_checkpoint(checkpoint_id)
        assert success == True
        
        # Verify deletion
        restored = restore_checkpoint(checkpoint_id)
        assert restored is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

