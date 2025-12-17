# DcisionAI MCP Server Documentation

**Version**: 2.0  
**Last Updated**: 2025-12-13  
**Status**: Production Ready

---

## Overview

The DcisionAI MCP Server is a Model Context Protocol (MCP) server that exposes DcisionAI optimization capabilities as standardized MCP tools and resources. It serves as the primary integration point for enterprise platforms (Salesforce, PowerBI, Excel, Tableau), IDEs, and CLI clients.

**Key Features**:
- ✅ **16 Public MCP Tools** - Optimization, NLP, data preparation, IDE integration, and workflow management
- ✅ **Full MCP Compliance** - JSON-RPC 2.0 protocol compliance
- ✅ **Direct Integration** - Direct Python imports from `dcisionai_workflow` (no HTTP layer)
- ✅ **Tool Registry** - Centralized tool discovery and management
- ✅ **Standardized Errors** - JSON-RPC 2.0 compliant error handling

---

## Architecture

### Three-Layer Architecture

```
MCP Clients → MCP Server → dcisionai_workflow
```

1. **MCP Clients**: Salesforce, React UI, IDEs, CLI
2. **MCP Server**: Protocol adapter (`dcisionai_mcp_server/`)
3. **Core Engine**: Optimization workflow (`dcisionai_workflow/`)

### Key Components

- **Tool Registry** (`tools/registry.py`): Single source of truth for all MCP tools
- **Error Handler** (`tools/error_handler.py`): JSON-RPC 2.0 compliant error handling
- **FastMCP Server** (`fastmcp_server.py`): Protocol layer implementing MCP specification

---

## Documentation Index

### Core Documentation

- **[Architecture Guide](./ARCHITECTURE.md)** - Detailed architecture and design principles
- **[MCP Compliance](./MCP_COMPLIANCE.md)** - MCP protocol compliance details
- **[Anthropic Compliance](./ANTHROPIC_COMPLIANCE.md)** - Anthropic MCP Directory requirements

### Architectural Decision Records

- **[ADR-029: MCP Server Integration Architecture](../../docs/adr/029-mcp-server-integration-architecture.md)** - Initial MCP server design
- **[ADR-038: MCP Server Architecture v2.0](../../docs/adr/038-mcp-server-architecture-v2.md)** - Tool registry, compliance, and tool expansion

### Implementation Documentation

- **[MCP Tools Implementation Plan](../../docs/implementation/MCP_TOOLS_IMPLEMENTATION_PLAN.md)** - Complete implementation plan and status
- **[Phase 4 Testing Summary](../../docs/implementation/PHASE_4_TESTING_SUMMARY.md)** - Test suite documentation

### Client Integration

- **[Client Integration Guide](./CLIENT_INTEGRATION.md)** - How to integrate with MCP server
- **[Deployment Architecture](./DEPLOYMENT_ARCHITECTURE.md)** - Deployment architecture and patterns
- **[Customer Deployment Guide](./CUSTOMER_DEPLOYMENT_GUIDE.md)** - Customer deployment instructions

---

## Quick Start

### For Developers

1. **Review Architecture**: Start with [ADR-038](../../docs/adr/038-mcp-server-architecture-v2.md)
2. **Understand Tools**: See [MCP Tools Implementation Plan](../../docs/implementation/MCP_TOOLS_IMPLEMENTATION_PLAN.md)
3. **Check Compliance**: Review [MCP Compliance](./MCP_COMPLIANCE.md)

### For Integrators

1. **Client Integration**: See [Client Integration Guide](./CLIENT_INTEGRATION.md)
2. **Tool Reference**: See [MCP Tools Implementation Plan](../../docs/implementation/MCP_TOOLS_IMPLEMENTATION_PLAN.md) for tool list
3. **Deployment**: See [Customer Deployment Guide](./CUSTOMER_DEPLOYMENT_GUIDE.md)

---

## MCP Tools Reference

### Optimization Tools

- `dcisionai_solve` - Full optimization workflow (async, WebSocket)
- `dcisionai_solve_with_model` - Deployed model execution (sync, fast)
- `dcisionai_adhoc_optimize` - Ad-hoc optimization

### IDE Tools

- `dcisionai_analyze_problem` - Quick problem analysis (< 2s)
- `dcisionai_validate_constraints` - Constraint validation (< 1s)
- `dcisionai_search_problem_types` - Problem type search (< 1s)
- `dcisionai_get_problem_type_schema` - Schema generation (< 1s)

### Client Tools

- `dcisionai_get_workflow_status` - Workflow status tracking
- `dcisionai_cancel_workflow` - Workflow cancellation
- `dcisionai_get_result` - Result retrieval
- `dcisionai_export_result` - Multi-format export
- `dcisionai_deploy_model` - Model deployment

### Data & NLP Tools

- `dcisionai_nlp_query` - Natural language questions
- `dcisionai_map_concepts` - Concept mapping (Salesforce)
- `dcisionai_prepare_data` - Data preparation (CSV/JSON)
- `dcisionai_prepare_salesforce_data` - Salesforce data preparation

---

## MCP Resources Reference

- `dcisionai://models/list` - List deployed models
- `dcisionai://solvers/list` - List available solvers

---

## Testing

Comprehensive test suite available in `dcisionai_mcp_server/tests/`:

- **Unit Tests**: Individual tool testing
- **Integration Tests**: End-to-end workflow testing
- **Compliance Tests**: MCP protocol compliance verification
- **Performance Tests**: Response time SLA validation

See [Phase 4 Testing Summary](../../docs/implementation/PHASE_4_TESTING_SUMMARY.md) for details.

---

## Related Documentation

- **[Main Platform Architecture](../../docs/guides/Architecture.md)** - Overall platform architecture
- **[ADR Index](../../docs/adr/README.md)** - All architectural decision records
- **[Developer Guide](../../docs/guides/DEVELOPER_GUIDE.md)** - Developer onboarding guide

---

**Last Updated**: 2025-12-13  
**Maintained By**: Architecture Team
