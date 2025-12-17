"""
Integration Tests for Tool Registry

Tests tool discovery, registration, and metadata retrieval.
"""

import pytest
from dcisionai_mcp_server.tools.registry import (
    get_all_mcp_tools,
    get_tool_by_name,
    get_tool_metadata,
    get_all_tool_names,
    initialize_registry
)
from dcisionai_workflow.tools.mcp_decorator import is_mcp_tool, get_mcp_tool_metadata


class TestToolRegistry:
    """Tests for tool registry functionality"""
    
    def test_registry_initialized(self):
        """Test that registry is initialized on import"""
        tools = get_all_mcp_tools()
        assert len(tools) > 0, "Registry should contain tools"
    
    def test_get_all_tool_names(self):
        """Test getting all tool names"""
        tool_names = get_all_tool_names()
        assert isinstance(tool_names, list)
        assert len(tool_names) > 0
        
        # Verify expected tools are present
        expected_tools = [
            "dcisionai_solve",
            "dcisionai_solve_with_model",
            "dcisionai_analyze_problem",
            "dcisionai_validate_constraints",
            "dcisionai_search_problem_types",
            "dcisionai_get_problem_type_schema",
            "dcisionai_get_workflow_status",
            "dcisionai_cancel_workflow",
            "dcisionai_get_result",
            "dcisionai_export_result",
            "dcisionai_deploy_model"
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tool_names, f"{tool_name} should be registered"
    
    def test_get_tool_by_name(self):
        """Test retrieving tool by name"""
        tool = get_tool_by_name("dcisionai_solve")
        assert tool is not None, "Should find dcisionai_solve"
        assert is_mcp_tool(tool), "Returned tool should be MCP tool"
        
        # Test non-existent tool
        tool = get_tool_by_name("nonexistent_tool")
        assert tool is None, "Should return None for non-existent tool"
    
    def test_get_tool_metadata(self):
        """Test retrieving tool metadata"""
        metadata = get_tool_metadata("dcisionai_solve")
        assert metadata is not None, "Should return metadata"
        assert "name" in metadata, "Metadata should include name"
        assert "description" in metadata, "Metadata should include description"
        assert "input_schema" in metadata, "Metadata should include input_schema"
        
        # Test non-existent tool
        metadata = get_tool_metadata("nonexistent_tool")
        assert metadata is None, "Should return None for non-existent tool"
    
    def test_all_tools_have_metadata(self):
        """Test that all registered tools have metadata"""
        tool_names = get_all_tool_names()
        
        for tool_name in tool_names:
            metadata = get_tool_metadata(tool_name)
            assert metadata is not None, f"{tool_name} should have metadata"
            assert metadata["name"] == tool_name, f"Metadata name should match tool name"
    
    def test_tool_registry_excludes_template_tools(self):
        """Test that template tools are NOT in registry"""
        tool_names = get_all_tool_names()
        
        # Template tools should NOT be in registry
        assert "dcisionai_list_templates" not in tool_names
        assert "dcisionai_register_template" not in tool_names
    
    def test_tool_metadata_structure(self):
        """Test that tool metadata has correct structure"""
        tool_names = get_all_tool_names()
        
        for tool_name in tool_names[:5]:  # Test first 5 tools
            metadata = get_tool_metadata(tool_name)
            
            # Required fields
            assert "name" in metadata
            assert "description" in metadata
            assert "input_schema" in metadata
            
            # Verify input_schema structure
            input_schema = metadata["input_schema"]
            assert isinstance(input_schema, dict)
            assert "type" in input_schema
            assert input_schema["type"] == "object"
            assert "properties" in input_schema

