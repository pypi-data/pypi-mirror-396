# MCP Server Test Suite

Comprehensive test suite for DcisionAI MCP Server tools, compliance, and performance.

## Test Structure

### Unit Tests (`test_mcp_tools.py`)
- Individual tool testing
- Error handling verification
- Input validation
- Edge case handling

### Integration Tests (`test_integration.py`)
- Tool discovery via registry
- Tool execution via endpoints
- Workflow integration
- Error handling integration

### Registry Tests (`test_tool_registry.py`)
- Tool registration
- Metadata retrieval
- Tool discovery
- Registry consistency

### MCP Compliance Tests (`test_mcp_compliance.py`)
- JSON-RPC 2.0 compliance
- Error format compliance
- Tool schema compliance
- Resource URI compliance

### Performance Tests (`test_performance.py`)
- Response time verification (< 1s for simple, < 5s for complex)
- Concurrent tool call handling
- Load testing

## Running Tests

### Run all tests
```bash
pytest dcisionai_mcp_server/tests/
```

### Run specific test file
```bash
pytest dcisionai_mcp_server/tests/test_mcp_tools.py
```

### Run with coverage
```bash
pytest dcisionai_mcp_server/tests/ --cov=dcisionai_mcp_server --cov-report=html
```

### Run performance tests only
```bash
pytest dcisionai_mcp_server/tests/test_performance.py -v
```

### Run compliance tests only
```bash
pytest dcisionai_mcp_server/tests/test_mcp_compliance.py -v
```

## Test Requirements

- `pytest`
- `pytest-asyncio`
- `pytest-cov` (optional, for coverage)
- `fastapi` (for TestClient)

Install with:
```bash
pip install pytest pytest-asyncio pytest-cov fastapi
```

## Test Coverage Goals

- **Unit Tests**: 80%+ coverage
- **Integration Tests**: All critical paths
- **Compliance Tests**: 100% MCP protocol compliance
- **Performance Tests**: All tools meet SLA

## Notes

- Some tests may require `dcisionai_workflow` to be properly installed
- Performance tests use real tool execution (may be slower)
- Integration tests require FastAPI test client
- Mock data is used where possible to avoid external dependencies

