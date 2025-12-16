# Deployed Models Feature - MCP Server 2.0

**Date**: 2025-11-25  
**Status**: Design Phase

---

## Overview

**Deployed Models** are a **KEY FEATURE** of DcisionAI. MCP Server 2.0 must fully support this feature through direct integration with `api.models_endpoint`.

---

## Current Architecture (v1.0)

**Flow**:
```
MCP Server → HTTP Client → FastAPI /api/models → api.models_endpoint → dcisionai_graph/core/models/
```

**Components**:
- `MODEL_REGISTRY` in `api/models_endpoint.py` - Maps model IDs to file paths
- `run_deployed_model()` - Executes deployed models
- `list_deployed_models()` - Lists available models
- Model classes in `dcisionai_graph/core/models/` - Actual model implementations

---

## New Architecture (v2.0)

**Flow**:
```
MCP Server → Direct Import → api.models_endpoint → dcisionai_graph/core/models/
```

**Benefits**:
- ✅ No HTTP overhead
- ✅ Direct access to model registry
- ✅ Faster execution
- ✅ Simpler code

---

## Deployed Models

### Available Models

1. **`portfolio_optimization_v1`**
   - **Class**: `PortfolioOptimizationModel`
   - **File**: `dcisionai_graph/core/models/portfolio_optimization_model.py`
   - **Domain**: Private Equity / RIA
   - **Purpose**: Optimize multi-asset portfolio allocation

2. **`portfolio_rebalancing_v1`**
   - **Class**: `PortfolioRebalancingModel`
   - **File**: `dcisionai_graph/core/models/portfolio_rebalancing_model.py`
   - **Domain**: RIA
   - **Purpose**: Rebalance client portfolios

3. **`capital_deployment_v1`**
   - **Class**: `CapitalDeploymentModel`
   - **File**: `dcisionai_graph/core/models/capital_deployment_model.py`
   - **Domain**: Private Equity
   - **Purpose**: Optimize deployment pacing across market cycles

4. **`fund_structure_v1`**
   - **Class**: `FundStructureOptimizer`
   - **File**: `dcisionai_graph/core/models/fund_structure_model.py`
   - **Domain**: Private Equity
   - **Purpose**: Optimize fund structure and team capacity

---

## MCP Server 2.0 Implementation

### Resource: `dcisionai://models/list`

**Implementation**:
```python
# dcisionai_mcp_server_2.0/resources/models.py
from api.models_endpoint import list_deployed_models

async def read_model_resource(uri: str) -> str:
    if uri == "dcisionai://models/list":
        models_response = list_deployed_models()  # Direct import, no HTTP
        return json.dumps(models_response, indent=2)
```

**Returns**:
```json
{
  "models": [
    {
      "id": "portfolio_optimization_v1",
      "name": "Portfolio Optimization",
      "description": "...",
      "domain": "private_equity",
      "status": "active",
      "capabilities": {...}
    }
  ]
}
```

### Tool: `dcisionai_solve_with_model`

**Implementation**:
```python
# dcisionai_mcp_server_2.0/tools/optimization.py
from api.models_endpoint import run_deployed_model, MODEL_REGISTRY

async def dcisionai_solve_with_model(model_id: str, data: Dict[str, Any], options: Dict[str, Any] = None):
    # Direct import, no HTTP call
    result = await run_deployed_model(model_id, data, options)
    return result
```

**Example Usage**:
```json
{
  "name": "dcisionai_solve_with_model",
  "arguments": {
    "model_id": "portfolio_optimization_v1",
    "data": {
      "concentration_limit": 0.12,
      "generate_data": true,
      "seed": 42
    },
    "options": {
      "solver": "scip",
      "time_limit": 60
    }
  }
}
```

---

## Key Features Preserved

### ✅ Model Registry
- Direct access to `MODEL_REGISTRY`
- No HTTP calls needed
- Instant model lookup

### ✅ Model Execution
- Direct call to `run_deployed_model()`
- Supports all 4 deployed models
- Model-specific data handling preserved

### ✅ Model Listing
- Direct call to `list_deployed_models()`
- Domain filtering support
- Full model metadata

### ✅ Model Metadata
- Model capabilities
- Usage examples
- Domain information
- Status and availability

---

## Integration Points

### React UI
**Current**: Calls `/api/models` and `/api/models/{id}/optimize`
**New**: Uses MCP resource `dcisionai://models/list` and tool `dcisionai_solve_with_model`

**Migration**:
```javascript
// Old
const models = await fetch('/api/models');
const result = await fetch(`/api/models/${modelId}/optimize`, {...});

// New (via MCP client)
const models = await mcpClient.readResource('dcisionai://models/list');
const result = await mcpClient.callTool('dcisionai_solve_with_model', {
  model_id: modelId,
  data: {...}
});
```

### Salesforce
**Current**: Uses `dcisionai_solve_with_model` tool (already MCP)
**New**: Same tool, but faster (direct import instead of HTTP)

**Migration**: ✅ **No changes needed** - same protocol, better performance

---

## Benefits

1. **Performance**: Direct imports eliminate HTTP overhead
2. **Simplicity**: No HTTP client wrapper needed
3. **Reliability**: No network calls, fewer failure points
4. **Consistency**: Same model registry and execution logic

---

## Testing

### Test Cases

1. **List Models**
   - ✅ Resource `dcisionai://models/list` returns all models
   - ✅ Domain filtering works correctly
   - ✅ Model metadata is complete

2. **Execute Model**
   - ✅ `dcisionai_solve_with_model` executes successfully
   - ✅ All 4 model types work
   - ✅ Error handling for invalid model IDs
   - ✅ Solver options are respected

3. **Integration**
   - ✅ React UI can list and execute models
   - ✅ Salesforce can list and execute models
   - ✅ Performance improved vs v1.0

---

**Last Updated**: 2025-11-25

