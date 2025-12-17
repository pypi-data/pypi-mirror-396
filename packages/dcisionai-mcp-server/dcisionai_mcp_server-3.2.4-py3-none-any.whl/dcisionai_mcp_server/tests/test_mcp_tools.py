"""
Unit Tests for MCP Tools

Tests each tool individually for correctness, error handling, and edge cases.
"""

import pytest
import json
from typing import List
from mcp.types import TextContent

# Import tools
from dcisionai_workflow.tools.optimization.mcp_tools import (
    dcisionai_solve,
    dcisionai_solve_with_model,
    dcisionai_adhoc_optimize,
    dcisionai_get_workflow_status,
    dcisionai_cancel_workflow,
    dcisionai_get_result,
    dcisionai_export_result,
    dcisionai_deploy_model
)
from dcisionai_workflow.tools.nlp.mcp_tools import dcisionai_nlp_query
from dcisionai_workflow.tools.data.mcp_tools import (
    dcisionai_map_concepts,
    dcisionai_prepare_data,
    dcisionai_prepare_salesforce_data
)
from dcisionai_workflow.tools.intent.mcp_tools import (
    dcisionai_analyze_problem,
    dcisionai_validate_constraints,
    dcisionai_search_problem_types,
    dcisionai_get_problem_type_schema
)


class TestOptimizationTools:
    """Tests for optimization tools"""
    
    @pytest.mark.asyncio
    async def test_dcisionai_solve_basic(self):
        """Test basic dcisionai_solve call"""
        result = await dcisionai_solve("Optimize a portfolio of 10 stocks")
        assert isinstance(result, List)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)
        
        # Parse response
        response_data = json.loads(result[0].text)
        assert "session_id" in response_data or "status" in response_data
    
    @pytest.mark.asyncio
    async def test_dcisionai_solve_empty_input(self):
        """Test dcisionai_solve with empty input"""
        result = await dcisionai_solve("")
        assert isinstance(result, List)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_dcisionai_solve_with_model_invalid_model(self):
        """Test dcisionai_solve_with_model with invalid model ID"""
        result = await dcisionai_solve_with_model(
            model_id="invalid_model",
            data={}
        )
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        assert "error" in response_data or "available_models" in response_data
    
    @pytest.mark.asyncio
    async def test_dcisionai_adhoc_optimize_basic(self):
        """Test basic dcisionai_adhoc_optimize call"""
        result = await dcisionai_adhoc_optimize(
            problem_description="Minimize cost subject to constraints"
        )
        assert isinstance(result, List)
        assert len(result) > 0


class TestIDETools:
    """Tests for IDE tools"""
    
    @pytest.mark.asyncio
    async def test_dcisionai_analyze_problem_basic(self):
        """Test basic problem analysis"""
        result = await dcisionai_analyze_problem(
            "Optimize a portfolio of 10 stocks with 12% concentration limit"
        )
        assert isinstance(result, List)
        assert len(result) > 0
        
        response_data = json.loads(result[0].text)
        assert "status" in response_data
        if response_data["status"] == "success":
            assert "analysis" in response_data
    
    @pytest.mark.asyncio
    async def test_dcisionai_validate_constraints_valid(self):
        """Test constraint validation with valid constraints"""
        constraints = [
            "Total investment <= 1000000",
            "Each stock allocation >= 0",
            "Sum of allocations == 1"
        ]
        result = await dcisionai_validate_constraints(
            constraints=constraints,
            problem_description="Portfolio optimization"
        )
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        assert "status" in response_data
    
    @pytest.mark.asyncio
    async def test_dcisionai_validate_constraints_empty(self):
        """Test constraint validation with empty constraints"""
        result = await dcisionai_validate_constraints(
            constraints=[],
            problem_description="Test problem"
        )
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        assert "status" in response_data
    
    @pytest.mark.asyncio
    async def test_dcisionai_search_problem_types_basic(self):
        """Test problem type search"""
        result = await dcisionai_search_problem_types(query="portfolio")
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        assert "status" in response_data
        if response_data["status"] == "success":
            assert "problem_types" in response_data
    
    @pytest.mark.asyncio
    async def test_dcisionai_search_problem_types_with_domain(self):
        """Test problem type search with domain filter"""
        result = await dcisionai_search_problem_types(
            query="optimization",
            domain="finance"
        )
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        assert "status" in response_data
    
    @pytest.mark.asyncio
    async def test_dcisionai_get_problem_type_schema_valid(self):
        """Test schema retrieval for valid problem type"""
        result = await dcisionai_get_problem_type_schema("portfolio")
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        assert "status" in response_data
    
    @pytest.mark.asyncio
    async def test_dcisionai_get_problem_type_schema_invalid(self):
        """Test schema retrieval for invalid problem type"""
        result = await dcisionai_get_problem_type_schema("invalid_type")
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        assert "status" in response_data
        assert response_data["status"] == "error" or "available_types" in response_data


class TestClientTools:
    """Tests for client tools"""
    
    @pytest.mark.asyncio
    async def test_dcisionai_get_workflow_status(self):
        """Test workflow status retrieval"""
        result = await dcisionai_get_workflow_status(session_id="test_session_123")
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        assert "status" in response_data
        assert "session_id" in response_data
    
    @pytest.mark.asyncio
    async def test_dcisionai_cancel_workflow(self):
        """Test workflow cancellation"""
        result = await dcisionai_cancel_workflow(session_id="test_session_123")
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        assert "status" in response_data
    
    @pytest.mark.asyncio
    async def test_dcisionai_get_result(self):
        """Test result retrieval"""
        result = await dcisionai_get_result(session_id="test_session_123")
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        assert "status" in response_data
    
    @pytest.mark.asyncio
    async def test_dcisionai_export_result_json(self):
        """Test JSON export"""
        result = await dcisionai_export_result(
            session_id="test_session_123",
            format="json"
        )
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        assert "status" in response_data
    
    @pytest.mark.asyncio
    async def test_dcisionai_export_result_invalid_format(self):
        """Test export with invalid format"""
        result = await dcisionai_export_result(
            session_id="test_session_123",
            format="invalid_format"
        )
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        assert "status" in response_data
        assert response_data["status"] == "error" or "supported_formats" in response_data
    
    @pytest.mark.asyncio
    async def test_dcisionai_deploy_model(self):
        """Test model deployment"""
        result = await dcisionai_deploy_model(
            model_spec={"problem_type": "portfolio", "code": "def solve(): pass"},
            name="test_model",
            domain="finance"
        )
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        assert "status" in response_data


class TestDataTools:
    """Tests for data tools"""
    
    @pytest.mark.asyncio
    async def test_dcisionai_prepare_data_basic(self):
        """Test basic data preparation"""
        data = '[{"stock": "AAPL", "return": 0.12}, {"stock": "GOOGL", "return": 0.10}]'
        result = await dcisionai_prepare_data(data=data)
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        assert "status" in response_data
    
    @pytest.mark.asyncio
    async def test_dcisionai_map_concepts_basic(self):
        """Test concept mapping"""
        result = await dcisionai_map_concepts(
            required_concepts=["portfolio", "risk"],
            schema_json='{"objects": []}'
        )
        assert isinstance(result, List)
        response_data = json.loads(result[0].text)
        # May return error if schema_json is empty, which is expected
        assert isinstance(response_data, dict)


class TestErrorHandling:
    """Tests for error handling"""
    
    @pytest.mark.asyncio
    async def test_tools_return_text_content(self):
        """Verify all tools return List[TextContent]"""
        tools_to_test = [
            (dcisionai_solve, {"problem_description": "test"}),
            (dcisionai_analyze_problem, {"problem_description": "test"}),
            (dcisionai_validate_constraints, {"constraints": [], "problem_description": "test"}),
            (dcisionai_search_problem_types, {"query": "test"}),
            (dcisionai_get_problem_type_schema, {"problem_type": "portfolio"}),
            (dcisionai_get_workflow_status, {"session_id": "test"}),
            (dcisionai_cancel_workflow, {"session_id": "test"}),
            (dcisionai_get_result, {"session_id": "test"}),
            (dcisionai_export_result, {"session_id": "test", "format": "json"}),
        ]
        
        for tool_func, kwargs in tools_to_test:
            result = await tool_func(**kwargs)
            assert isinstance(result, List), f"{tool_func.__name__} should return List"
            if len(result) > 0:
                assert isinstance(result[0], TextContent), f"{tool_func.__name__} should return TextContent"
    
    @pytest.mark.asyncio
    async def test_error_responses_have_status(self):
        """Verify error responses include status field"""
        # Test with invalid inputs that should trigger errors
        result = await dcisionai_get_problem_type_schema("invalid_type")
        response_data = json.loads(result[0].text)
        assert "status" in response_data
        
        result = await dcisionai_export_result("test", "invalid_format")
        response_data = json.loads(result[0].text)
        assert "status" in response_data

