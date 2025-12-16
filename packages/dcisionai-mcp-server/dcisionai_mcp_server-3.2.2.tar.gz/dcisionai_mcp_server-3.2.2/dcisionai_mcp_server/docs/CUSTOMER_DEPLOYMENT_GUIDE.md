# Customer Deployment Guide - MCP Server 2.0

**Date**: 2025-11-25  
**Audience**: Customers, Sales, Support

---

## 🎯 Overview

DcisionAI MCP Server 2.0 is the **primary interface** for all DcisionAI capabilities. All clients (Salesforce, React UI, IDEs) connect via the Model Context Protocol (MCP).

---

## 📦 What You Get

### Single Service Deployment

**MCP Server 2.0** provides:
- ✅ Optimization capabilities (via MCP tools)
- ✅ Model management (via MCP resources)
- ✅ Real-time streaming (via WebSocket)
- ✅ Standard MCP protocol support

**No Additional Services Required**:
- ❌ No FastAPI backend needed
- ❌ No separate HTTP API needed
- ✅ Everything via MCP

---

## 🚀 Deployment Options

### Option 1: Cloud SaaS (Recommended)

**Deployment**: Managed by DcisionAI

**What You Get**:
- ✅ Fully managed service
- ✅ Automatic scaling
- ✅ High availability
- ✅ Regular updates

**Access**:
- **Salesforce**: Connect via HTTP JSON-RPC 2.0
- **React UI**: Connect via WebSocket
- **IDEs**: Connect via MCP protocol

**URL**: `https://dcisionai-mcp-platform-production.up.railway.app`

---

### Option 2: On-Premise

**Deployment**: Self-hosted on your infrastructure

**What You Get**:
- ✅ Full control
- ✅ Data stays on-premise
- ✅ Custom configuration
- ✅ Compliance-friendly

**Requirements**:
- Docker or Python 3.10+
- Network access (for API keys)
- Port 8080 available

**Deployment Steps**:
1. Install `dcisionai_graph` package
2. Install `dcisionai_mcp_server_2.0` package
3. Configure environment variables
4. Start MCP Server 2.0
5. Connect clients

---

### Option 3: Hybrid

**Deployment**: Cloud + On-Premise

**What You Get**:
- ✅ Cloud for public-facing
- ✅ On-premise for sensitive data
- ✅ Flexibility
- ✅ Performance optimization

**Use Case**: Large enterprises with data sovereignty requirements

---

## 🔌 Client Connections

### Salesforce Integration

**Connection Type**: HTTP JSON-RPC 2.0

**Endpoint**: `POST /mcp/tools/call`

**Example**:
```apex
// Apex code
HttpRequest req = new HttpRequest();
req.setEndpoint('https://your-mcp-server.com/mcp/tools/call');
req.setMethod('POST');
req.setHeader('Content-Type', 'application/json');
req.setBody(JSON.serialize(new Map<String, Object>{
    'name' => 'dcisionai_solve',
    'arguments' => new Map<String, Object>{
        'problem_description' => 'Optimize portfolio...'
    }
}));
```

**Available Tools**:
- `dcisionai_solve` - Full optimization workflow
- `dcisionai_solve_with_model` - Use deployed model
- `dcisionai_nlp_query` - Answer questions
- `dcisionai_map_concepts` - Map concepts to schema
- `dcisionai_adhoc_optimize` - Ad-hoc optimization

---

### React UI Integration

**Connection Type**: WebSocket

**Endpoint**: `ws://your-mcp-server.com/ws/{session_id}`

**Example**:
```javascript
const ws = new WebSocket('ws://your-mcp-server.com/ws/session123');

ws.onopen = () => {
  ws.send(JSON.stringify({
    problem_description: 'Optimize portfolio...',
    enabled_features: ['intent', 'data', 'optimize'],
    enabled_tools: ['data', 'optimize']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'step_complete') {
    // Update UI with step progress
  } else if (data.type === 'workflow_complete') {
    // Show final result
  }
};
```

**Message Types**:
- `workflow_start` - Workflow initialization
- `step_complete` - Individual step completion
- `workflow_complete` - Final result
- `error` - Error messages

---

### IDE Integration (Cursor, VS Code)

**Connection Type**: MCP Protocol (SSE/HTTP)

**Configuration**:
```json
{
  "mcpServers": {
    "dcisionai": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-dcisionai"],
      "env": {
        "DCISIONAI_MCP_SERVER_URL": "https://your-mcp-server.com"
      }
    }
  }
}
```

**Available Tools**:
- Same as Salesforce (via MCP protocol)

---

## 🔐 Security & Authentication

### API Keys

**Required**: `ANTHROPIC_API_KEY`

**Usage**: For LLM calls (Claude)

**Storage**: Environment variable or secure config

### Network Security

**Recommendations**:
- ✅ Use HTTPS/WSS in production
- ✅ Implement API key rotation
- ✅ Use VPN for on-premise deployments
- ✅ Configure firewall rules

---

## 📊 Monitoring & Observability

### Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "ok",
  "service": "dcisionai-mcp-server-2.0",
  "version": "2.0.0"
}
```

### Logging

**Log Levels**: `DEBUG`, `INFO`, `WARNING`, `ERROR`

**Configuration**: `DCISIONAI_LOG_LEVEL` environment variable

**Logs Include**:
- WebSocket connections
- Tool calls
- Workflow execution
- Errors

---

## 🎯 Migration from Previous Architecture

### If Using FastAPI Backend

**Migration Steps**:
1. Update endpoint URLs to MCP Server 2.0
2. Change protocol from HTTP REST to MCP
3. Update client code (if needed)
4. Test functionality
5. Decommission FastAPI backend

**Timeline**: Gradual migration (no downtime)

### If Using MCP Server 1.0

**Migration Steps**:
1. Update endpoint URL to MCP Server 2.0
2. Test compatibility (should work as-is)
3. Decommission MCP Server 1.0

**Timeline**: Simple URL change

---

## 📞 Support

### Getting Help

- **Documentation**: See `dcisionai_mcp_server_2.0/` directory
- **Architecture**: See `DEPLOYMENT_ARCHITECTURE.md`
- **Migration**: See `MIGRATION.md`

### Common Issues

**Connection Refused**:
- Check server is running
- Verify port 8080 is accessible
- Check firewall rules

**Import Errors**:
- Ensure `dcisionai_graph` is installed
- Check Python path
- Verify package installation

**WebSocket Errors**:
- Check WebSocket URL format
- Verify server supports WebSocket
- Check network connectivity

---

**Last Updated**: 2025-11-25

