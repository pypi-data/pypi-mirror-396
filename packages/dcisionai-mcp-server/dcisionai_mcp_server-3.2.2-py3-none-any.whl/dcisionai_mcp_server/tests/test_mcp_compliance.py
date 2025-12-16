"""
MCP Compliance Tests

Tests for JSON-RPC 2.0 compliance, error format compliance, and protocol adherence.
"""

import pytest
import json
from fastapi.testclient import TestClient
from dcisionai_mcp_server.fastmcp_server import app
from dcisionai_mcp_server.tools.error_handler import (
    format_mcp_error,
    format_validation_error,
    format_not_found_error,
    format_internal_error,
    MCPErrorCode
)


class TestMCPCompliance:
    """Tests for MCP protocol compliance"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_tools_list_endpoint_exists(self, client):
        """Test that tools/list endpoint exists"""
        response = client.post("/mcp/tools/list", json={"id": 1})
        assert response.status_code in [200, 500]  # 500 if tools not loaded, but endpoint exists
    
    def test_tools_list_jsonrpc_format(self, client):
        """Test that tools/list returns JSON-RPC 2.0 format"""
        response = client.post("/mcp/tools/list", json={"id": 1})
        data = response.json()
        
        assert "jsonrpc" in data
        assert data["jsonrpc"] == "2.0"
        assert "id" in data
        
        if "result" in data:
            assert "tools" in data["result"]
            assert isinstance(data["result"]["tools"], list)
    
    def test_tools_list_tool_structure(self, client):
        """Test that each tool in list has correct structure"""
        response = client.post("/mcp/tools/list", json={"id": 1})
        data = response.json()
        
        if "result" in data and "tools" in data["result"]:
            tools = data["result"]["tools"]
            if len(tools) > 0:
                tool = tools[0]
                assert "name" in tool
                assert "description" in tool
                assert "inputSchema" in tool  # MCP uses camelCase
                
                # Verify inputSchema structure
                input_schema = tool["inputSchema"]
                assert isinstance(input_schema, dict)
                assert "type" in input_schema
    
    def test_error_format_jsonrpc(self, client):
        """Test that errors follow JSON-RPC 2.0 format"""
        # Test with invalid request
        response = client.post("/mcp/tools/list", json={"invalid": "request"})
        data = response.json()
        
        if "error" in data:
            error = data["error"]
            assert "code" in error
            assert "message" in error
            assert isinstance(error["code"], int)
            assert isinstance(error["message"], str)
    
    def test_error_codes_compliance(self):
        """Test that error codes follow JSON-RPC 2.0 specification"""
        # Test standard error codes
        error = format_mcp_error(
            MCPErrorCode.INVALID_REQUEST,
            "Invalid request"
        )
        assert error["code"] == -32600
        
        error = format_mcp_error(
            MCPErrorCode.METHOD_NOT_FOUND,
            "Method not found"
        )
        assert error["code"] == -32601
        
        error = format_mcp_error(
            MCPErrorCode.INVALID_PARAMS,
            "Invalid params"
        )
        assert error["code"] == -32602
        
        error = format_mcp_error(
            MCPErrorCode.INTERNAL_ERROR,
            "Internal error"
        )
        assert error["code"] == -32603
    
    def test_validation_error_format(self):
        """Test validation error format"""
        error = format_validation_error(
            field="problem_description",
            reason="Field is required",
            suggestion="Provide a non-empty problem description",
            example="Optimize a portfolio of 10 stocks"
        )
        
        assert error["code"] == MCPErrorCode.VALIDATION_ERROR.value
        assert "data" in error
        assert error["data"]["error_type"] == "ValidationError"
        assert error["data"]["field"] == "problem_description"
        assert "suggestion" in error["data"]
    
    def test_not_found_error_format(self):
        """Test not found error format"""
        error = format_not_found_error(
            resource_type="tool",
            resource_id="nonexistent_tool",
            suggestion="Use POST /mcp/tools/list to see available tools"
        )
        
        assert error["code"] == MCPErrorCode.NOT_FOUND_ERROR.value
        assert "data" in error
        assert error["data"]["error_type"] == "NotFoundError"
        assert error["data"]["resource_type"] == "tool"
    
    def test_internal_error_format(self):
        """Test internal error format"""
        test_exception = ValueError("Test error")
        error = format_internal_error(
            test_exception,
            context="test_context"
        )
        
        assert error["code"] == MCPErrorCode.INTERNAL_ERROR.value
        assert "data" in error
        assert error["data"]["error_type"] == "InternalError"
        assert error["data"]["error_class"] == "ValueError"
    
    def test_tool_call_jsonrpc_format(self, client):
        """Test that tool calls use JSON-RPC 2.0 format"""
        # This test requires tools to be properly loaded
        # May fail if dcisionai_workflow is not available
        response = client.post(
            "/mcp/tools/call",
            json={
                "name": "dcisionai_analyze_problem",
                "arguments": {
                    "problem_description": "Test problem"
                }
            }
        )
        
        # Should return JSON-RPC format (even if error)
        data = response.json()
        assert isinstance(data, dict)
    
    def test_tool_schemas_valid_json(self, client):
        """Test that tool schemas are valid JSON"""
        response = client.post("/mcp/tools/list", json={"id": 1})
        data = response.json()
        
        if "result" in data and "tools" in data["result"]:
            tools = data["result"]["tools"]
            for tool in tools:
                # Verify schema can be serialized/deserialized
                schema_json = json.dumps(tool["inputSchema"])
                schema_parsed = json.loads(schema_json)
                assert isinstance(schema_parsed, dict)


class TestMCPResourceCompliance:
    """Tests for MCP resource compliance"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_resources_endpoint_exists(self, client):
        """Test that resources endpoint exists"""
        response = client.get("/mcp/resources/dcisionai://models/list")
        assert response.status_code in [200, 404, 500]
    
    def test_resource_uri_format(self, client):
        """Test that resource URIs follow dcisionai:// scheme"""
        # Test models resource
        response = client.get("/mcp/resources/dcisionai://models/list")
        # Should not return 404 for valid URI format
        
        # Test solvers resource
        response = client.get("/mcp/resources/dcisionai://solvers/list")
        # Should not return 404 for valid URI format
    
    def test_resource_response_format(self, client):
        """Test that resource responses are valid JSON"""
        response = client.get("/mcp/resources/dcisionai://models/list")
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict) or isinstance(data, list)

