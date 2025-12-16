# MCP Server 2.0 Architecture

**Date**: 2025-11-25  
**Status**: Design Phase

---

## Design Principles

1. **MCP as Primary Interface**: All clients (UI, Salesforce, IDEs) use MCP protocol
2. **Direct Integration**: MCP server directly imports `dcisionai_graph` (no FastAPI layer)
3. **Multi-Transport**: Support HTTP, WebSocket, and SSE transports
4. **Anthropic Compliance**: Follow Anthropic MCP Directory best practices
5. **Backward Compatible**: Existing clients continue to work

---

## Architecture Layers

### Layer 1: Transport Layer
**Purpose**: Handle different transport protocols

- **HTTP JSON-RPC 2.0**: For Salesforce and HTTP clients
- **WebSocket**: For React UI real-time streaming
- **SSE**: For IDE integrations

### Layer 2: MCP Protocol Layer
**Purpose**: Implement MCP protocol (tools, resources, prompts)

- **Tools**: Functions that can be invoked
- **Resources**: Read-only data sources
- **Prompts**: Template-based interactions

### Layer 3: Business Logic Layer
**Purpose**: Direct integration with `dcisionai_graph`

- **Direct Imports**: Import `dcisionai_graph` functions directly
- **No HTTP Wrapper**: No client/server HTTP calls
- **In-Process Calls**: All calls are in-process Python calls

---

## Transport Implementations

### HTTP JSON-RPC 2.0 (Salesforce)

**Endpoint**: `POST /mcp/tools/call`

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "dcisionai_solve",
    "arguments": {
      "problem_description": "..."
    }
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{...optimization results...}"
      }
    ]
  }
}
```

### WebSocket (React UI)

**Connection**: `ws://host:port/ws/{session_id}`

**Message Format**:
```json
{
  "type": "tool_call",
  "tool": "dcisionai_solve",
  "arguments": {
    "problem_description": "...",
    "stream_thinking": true
  }
}
```

**Streaming Response**:
```json
{
  "type": "thinking",
  "content": "..."
}
```

```json
{
  "type": "result",
  "content": "{...optimization results...}"
}
```

### SSE (IDEs)

**Endpoint**: `GET /mcp/sse`

**Stream Format**:
```
data: {"type": "tool_result", "content": "..."}

data: {"type": "thinking", "content": "..."}
```

---

## Tool Implementation Pattern

### Example: `dcisionai_solve`

**Current (v1.0 - Thin Adapter)**:
```python
# dcisionai_mcp_server/tools/optimization.py
async def dcisionai_solve(problem_description: str):
    # HTTP call to FastAPI
    result = await _client.optimize(problem_description)
    return result
```

**New (v2.0 - Direct Integration)**:
```python
# dcisionai_mcp_server_2.0/tools/optimization.py
from dcisionai_graph.core.agents.optimization_agent import run_optimization_workflow

async def dcisionai_solve(problem_description: str):
    # Direct import and call
    result = await run_optimization_workflow(problem_description)
    return result
```

---

## Resource Implementation Pattern

### Example: `dcisionai://models/list`

**Current (v1.0)**:
```python
async def read_model_resource(uri: str):
    # HTTP call to FastAPI /api/models
    models_response = await _client.get_models()
    return json.dumps(models_response)
```

**New (v2.0)**:
```python
async def read_model_resource(uri: str):
    # Direct import from dcisionai_graph
    from dcisionai_graph.core.models.model_registry import get_all_models
    models = get_all_models()
    return json.dumps({"models": models})
```

---

## Client Integration

### React UI Integration

**Location**: `dcisionai_mcp_clients/react-mcp-client/` (separate project)

**Current**: Uses FastAPI endpoints + WebSocket
**New**: Uses MCP WebSocket transport via React MCP client library

**Migration**:
```javascript
// Old (FastAPI)
const response = await fetch('/api/optimize', {...});

// New (MCP via client library)
import { useMCPTool } from '@dcisionai/react-mcp-client';
const { callTool } = useMCPTool();
const result = await callTool('dcisionai_solve', {
  problem_description: input
});
```

### Salesforce Integration

**Current**: Uses HTTP JSON-RPC 2.0 (already compatible)
**New**: Same protocol, no changes needed

**Migration**: None required - already using MCP protocol

---

## Performance Comparison

| Metric | Current (v1.0) | New (v2.0) |
|--------|---------------|------------|
| **Latency** | ~150-300ms (HTTP hop) | ~0-50ms (direct call) |
| **Services** | 2 (FastAPI + MCP) | 1 (MCP only) |
| **Code Complexity** | Medium (2 layers) | Low (1 layer) |
| **Maintenance** | Update 2 services | Update 1 service |

---

## Migration Strategy

### Phase 1: Parallel Development
- Build MCP Server 2.0 alongside v1.0
- No changes to existing systems
- Test independently

### Phase 2: Gradual Migration
- Migrate React UI to MCP client
- Keep FastAPI as fallback
- Test thoroughly

### Phase 3: Full Migration
- Remove FastAPI dependency
- All clients use MCP Server 2.0
- Deprecate v1.0

---

## Anthropic MCP Compliance

### Tool Annotations

```python
@mcp.tool()
@mcp.annotation("title", "Solve Optimization Problem")
@mcp.annotation("readOnlyHint", False)
async def dcisionai_solve(problem_description: str) -> str:
    """
    Solve an optimization problem using DcisionAI.
    
    Provides full optimization workflow including problem classification,
    intent extraction, model generation, solving, and business explanation.
    """
    ...
```

### Error Handling

```python
async def dcisionai_solve(problem_description: str):
    try:
        result = await run_optimization_workflow(problem_description)
        return {
            "content": [{"type": "text", "text": json.dumps(result)}]
        }
    except ValueError as e:
        return {
            "isError": True,
            "content": [{
                "type": "text",
                "text": f"Invalid input: {str(e)}"
            }]
        }
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        return {
            "isError": True,
            "content": [{
                "type": "text",
                "text": "An error occurred during optimization. Please try again."
            }]
        }
```

---

## Security Considerations

1. **Authentication**: OAuth 2.0 for remote clients (per Anthropic requirements)
2. **Rate Limiting**: Per-client rate limits
3. **Input Validation**: Validate all inputs before processing
4. **Error Messages**: Don't expose internal errors to clients
5. **CORS**: Proper CORS configuration for web clients

---

## Monitoring & Observability

1. **Metrics**: Tool call counts, latency, error rates
2. **Logging**: Structured logging for debugging
3. **Tracing**: Request tracing across layers
4. **Health Checks**: `/health` endpoint for monitoring

---

**Last Updated**: 2025-11-25

