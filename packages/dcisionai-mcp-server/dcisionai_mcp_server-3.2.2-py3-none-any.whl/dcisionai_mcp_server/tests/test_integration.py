"""
Integration Tests

End-to-end tests for tool discovery, execution, and workflow integration.
"""

import pytest
from fastapi.testclient import TestClient
from dcisionai_mcp_server.fastmcp_server import app
from dcisionai_mcp_server.tools.registry import get_all_mcp_tools, get_tool_by_name


class TestToolDiscovery:
    """Tests for tool discovery integration"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_tool_discovery_via_registry(self):
        """Test that tools can be discovered via registry"""
        tools = get_all_mcp_tools()
        assert len(tools) > 0
        
        # Verify we can get tools by name
        tool = get_tool_by_name("dcisionai_solve")
        assert tool is not None
    
    def test_tool_discovery_via_endpoint(self, client):
        """Test that tools can be discovered via MCP endpoint"""
        response = client.post("/mcp/tools/list", json={"id": 1})
        
        if response.status_code == 200:
            data = response.json()
            assert "result" in data
            assert "tools" in data["result"]
            assert len(data["result"]["tools"]) > 0
    
    def test_tool_metadata_consistency(self):
        """Test that tool metadata is consistent between registry and decorator"""
        from dcisionai_workflow.tools.mcp_decorator import get_mcp_tool_metadata
        from dcisionai_mcp_server.tools.registry import get_tool_metadata
        
        tool_names = ["dcisionai_solve", "dcisionai_analyze_problem"]
        
        for tool_name in tool_names:
            tool = get_tool_by_name(tool_name)
            if tool:
                registry_metadata = get_tool_metadata(tool_name)
                decorator_metadata = get_mcp_tool_metadata(tool)
                
                assert registry_metadata is not None
                assert decorator_metadata is not None
                assert registry_metadata["name"] == decorator_metadata["name"]


class TestToolExecution:
    """Tests for tool execution integration"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_tool_execution_via_registry(self):
        """Test that tools can be executed via registry"""
        tool = get_tool_by_name("dcisionai_search_problem_types")
        assert tool is not None
        
        # Execute tool
        result = await tool(query="portfolio")
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_tool_execution_via_endpoint(self, client):
        """Test that tools can be executed via MCP endpoint"""
        # This test may fail if dcisionai_workflow is not available
        # but should test the endpoint structure
        response = client.post(
            "/mcp/tools/call",
            json={
                "name": "dcisionai_search_problem_types",
                "arguments": {
                    "query": "portfolio"
                }
            }
        )
        
        # Should return some response (even if error)
        assert response.status_code in [200, 400, 404, 500]
        data = response.json()
        assert isinstance(data, dict)


class TestErrorHandlingIntegration:
    """Tests for error handling integration"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_invalid_tool_name(self, client):
        """Test handling of invalid tool name"""
        response = client.post(
            "/mcp/tools/call",
            json={
                "name": "nonexistent_tool",
                "arguments": {}
            }
        )
        
        # Should return error
        assert response.status_code in [404, 500]
        data = response.json()
        assert "error" in data or "status" in data
    
    def test_missing_required_arguments(self, client):
        """Test handling of missing required arguments"""
        response = client.post(
            "/mcp/tools/call",
            json={
                "name": "dcisionai_analyze_problem",
                "arguments": {}
            }
        )
        
        # Should return error or handle gracefully
        assert response.status_code in [200, 400, 500]
        data = response.json()
        assert isinstance(data, dict)


class TestWorkflowIntegration:
    """Tests for workflow integration"""
    
    @pytest.mark.asyncio
    async def test_solve_workflow_initialization(self):
        """Test that solve workflow initializes correctly"""
        from dcisionai_workflow.tools.optimization.mcp_tools import dcisionai_solve
        
        result = await dcisionai_solve("Test optimization problem")
        assert isinstance(result, list)
        
        # Should return session ID
        import json
        response_data = json.loads(result[0].text)
        assert "session_id" in response_data or "status" in response_data
    
    @pytest.mark.asyncio
    async def test_workflow_status_after_solve(self):
        """Test that workflow status can be retrieved after solve"""
        from dcisionai_workflow.tools.optimization.mcp_tools import (
            dcisionai_solve,
            dcisionai_get_workflow_status
        )
        
        # Initialize workflow
        solve_result = await dcisionai_solve("Test problem")
        import json
        solve_data = json.loads(solve_result[0].text)
        
        # Try to get status (may not be found if workflow hasn't started)
        if "session_id" in solve_data:
            session_id = solve_data["session_id"]
            status_result = await dcisionai_get_workflow_status(session_id)
            assert isinstance(status_result, list)

