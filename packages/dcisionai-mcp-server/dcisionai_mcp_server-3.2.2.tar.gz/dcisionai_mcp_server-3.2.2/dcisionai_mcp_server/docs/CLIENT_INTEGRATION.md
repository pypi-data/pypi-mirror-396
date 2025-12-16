# Client Integration Guide

**Date**: 2025-11-25  
**Status**: Planning Phase

---

## Architecture: 3-Project Separation

Per ADR-029, we follow the **3-project architecture**:

1. **`dcisionai_graph/`** - Core optimization engine (unchanged)
2. **`dcisionai_mcp_server/`** - MCP protocol adapter (server-side only)
3. **`dcisionai_mcp_clients/`** - Platform-specific clients (client-side libraries)

**Key Principle**: MCP Server contains **server-side code only**. All client libraries belong in `dcisionai_mcp_clients/`.

---

## Client Locations

### React MCP Client
**Location**: `dcisionai_mcp_clients/react-mcp-client/`

**Purpose**: React hooks and utilities for connecting React UI to MCP Server 2.0

**Structure**:
```
dcisionai_mcp_clients/react-mcp-client/
├── README.md
├── package.json
├── src/
│   ├── index.js                 # Main export
│   ├── hooks/
│   │   ├── useMCPTool.js        # Hook for calling MCP tools
│   │   ├── useMCPResource.js   # Hook for reading MCP resources
│   │   └── useMCPWebSocket.js  # Hook for WebSocket streaming
│   └── utils/
│       ├── mcpClient.js        # Core MCP client
│       └── websocket.js        # WebSocket utilities
└── examples/
    └── WorkspaceDetailDAME.js   # Example usage
```

### Salesforce MCP Client
**Location**: `dcisionai_mcp_clients/salesforce-mcp-client/` ✅ **Already exists**

**Purpose**: Apex controllers and LWC components for Salesforce integration

**Status**: ✅ Already implemented, compatible with MCP Server 2.0

---

## Integration Patterns

### React UI → MCP Server 2.0

**Step 1**: Install React MCP Client
```bash
cd dcisionai_mcp_clients/react-mcp-client
npm install
```

**Step 2**: Use in React Components
```javascript
import { useMCPTool, useMCPWebSocket } from '@dcisionai/react-mcp-client';

function WorkspaceDetailDAME() {
  const { callTool } = useMCPTool();
  const { connect, stream } = useMCPWebSocket();
  
  const handleRun = async () => {
    // Call MCP tool
    const result = await callTool('dcisionai_solve', {
      problem_description: input
    });
    
    // Or use WebSocket for streaming
    connect(`ws://localhost:8080/ws/${sessionId}`);
    stream.on('thinking', (data) => { ... });
  };
}
```

### Salesforce → MCP Server 2.0

**Status**: ✅ **No changes needed**

Salesforce already uses HTTP JSON-RPC 2.0, which MCP Server 2.0 supports.

**Just update endpoint URL**:
```apex
// Update MCP server URL
String mcpServerUrl = 'https://dcisionai-mcp-platform-v2.up.railway.app';
// Same protocol, same format - works as-is
```

---

## MCP Server 2.0 Responsibilities

**Server-Side Only**:
- ✅ MCP protocol implementation (tools, resources, prompts)
- ✅ Transport handlers (HTTP, WebSocket, SSE)
- ✅ Direct `dcisionai_graph` integration
- ✅ Authentication and authorization
- ✅ Rate limiting and security

**NOT Server Responsibilities**:
- ❌ Client libraries (belong in `dcisionai_mcp_clients/`)
- ❌ UI components (belong in `dcisionai_mcp_clients/react-mcp-client/`)
- ❌ Platform-specific code (belong in respective client directories)

---

## Development Workflow

### For MCP Server 2.0
```bash
cd dcisionai_mcp_server_2.0
# Develop server-side code only
```

### For React Client
```bash
cd dcisionai_mcp_clients/react-mcp-client
# Develop React hooks and utilities
```

### For Salesforce Client
```bash
cd dcisionai_mcp_clients/salesforce-mcp-client
# Develop Apex and LWC components
```

---

## Benefits of Separation

1. **Clear Boundaries**: Server vs Client code separation
2. **Independent Development**: Can develop clients separately
3. **Reusability**: Client libraries can be used by multiple projects
4. **Maintainability**: Easier to find and update client code
5. **Compliance**: Matches ADR-029 architecture

---

**Last Updated**: 2025-11-25

