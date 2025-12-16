"""
Performance Tests

Tests for response time compliance (< 1s for simple tools, < 5s for complex tools).
"""

import pytest
import time
import asyncio
from dcisionai_workflow.tools.intent.mcp_tools import (
    dcisionai_analyze_problem,
    dcisionai_validate_constraints,
    dcisionai_search_problem_types,
    dcisionai_get_problem_type_schema
)
from dcisionai_workflow.tools.optimization.mcp_tools import (
    dcisionai_solve,
    dcisionai_get_workflow_status,
    dcisionai_cancel_workflow,
    dcisionai_get_result,
    dcisionai_export_result
)


class TestPerformance:
    """Tests for tool performance"""
    
    @pytest.mark.asyncio
    async def test_analyze_problem_performance(self):
        """Test that analyze_problem responds quickly (< 2s)"""
        start_time = time.time()
        result = await dcisionai_analyze_problem("Optimize a portfolio")
        elapsed = time.time() - start_time
        
        assert elapsed < 2.0, f"analyze_problem took {elapsed:.2f}s, should be < 2s"
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_validate_constraints_performance(self):
        """Test that validate_constraints responds quickly (< 1s)"""
        constraints = ["x >= 0", "x <= 100"]
        start_time = time.time()
        result = await dcisionai_validate_constraints(
            constraints=constraints,
            problem_description="Test"
        )
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"validate_constraints took {elapsed:.2f}s, should be < 1s"
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_search_problem_types_performance(self):
        """Test that search_problem_types responds quickly (< 1s)"""
        start_time = time.time()
        result = await dcisionai_search_problem_types(query="portfolio")
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"search_problem_types took {elapsed:.2f}s, should be < 1s"
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_get_problem_type_schema_performance(self):
        """Test that get_problem_type_schema responds quickly (< 1s)"""
        start_time = time.time()
        result = await dcisionai_get_problem_type_schema("portfolio")
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"get_problem_type_schema took {elapsed:.2f}s, should be < 1s"
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_get_workflow_status_performance(self):
        """Test that get_workflow_status responds quickly (< 1s)"""
        start_time = time.time()
        result = await dcisionai_get_workflow_status("test_session")
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"get_workflow_status took {elapsed:.2f}s, should be < 1s"
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_cancel_workflow_performance(self):
        """Test that cancel_workflow responds quickly (< 1s)"""
        start_time = time.time()
        result = await dcisionai_cancel_workflow("test_session")
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"cancel_workflow took {elapsed:.2f}s, should be < 1s"
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_get_result_performance(self):
        """Test that get_result responds quickly (< 1s)"""
        start_time = time.time()
        result = await dcisionai_get_result("test_session")
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0, f"get_result took {elapsed:.2f}s, should be < 1s"
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_export_result_performance(self):
        """Test that export_result responds quickly (< 3s)"""
        start_time = time.time()
        result = await dcisionai_export_result("test_session", "json")
        elapsed = time.time() - start_time
        
        assert elapsed < 3.0, f"export_result took {elapsed:.2f}s, should be < 3s"
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_solve_returns_quickly(self):
        """Test that dcisionai_solve returns session ID quickly (< 1s)"""
        start_time = time.time()
        result = await dcisionai_solve("Test problem")
        elapsed = time.time() - start_time
        
        # dcisionai_solve should return immediately with session ID
        assert elapsed < 1.0, f"dcisionai_solve took {elapsed:.2f}s, should return < 1s"
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self):
        """Test that multiple tools can be called concurrently"""
        async def call_tool(tool_func, *args, **kwargs):
            return await tool_func(*args, **kwargs)
        
        # Call multiple tools concurrently
        start_time = time.time()
        results = await asyncio.gather(
            dcisionai_search_problem_types("portfolio"),
            dcisionai_get_problem_type_schema("portfolio"),
            dcisionai_validate_constraints(["x >= 0"], "Test"),
            return_exceptions=True
        )
        elapsed = time.time() - start_time
        
        # Concurrent calls should be faster than sequential
        assert elapsed < 2.0, f"Concurrent calls took {elapsed:.2f}s"
        
        # All should succeed
        for result in results:
            assert not isinstance(result, Exception), f"Tool call failed: {result}"
            assert isinstance(result, list)

