# DcisionAI Deployment Architecture with MCP Server 2.0

**Date**: 2025-11-25  
**Status**: Architecture Overview  
**Audience**: PE, Engineering, Product

---

## 🏗️ Overall Architecture

### Current State (Pre-MCP Server 2.0)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DcisionAI Platform                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │  React UI        │────────▶│  FastAPI Backend  │            │
│  │  (platform.      │  HTTP   │  (api/)           │            │
│  │   dcisionai.com) │         │                   │            │
│  └──────────────────┘         └────────┬──────────┘            │
│                                         │                        │
│                                         │ Import                 │
│                                         ▼                        │
│                                  ┌──────────────┐                │
│                                  │ dcisionai_   │                │
│                                  │   graph/     │                │
│                                  │ (Core Engine)│                │
│                                  └──────────────┘                │
│                                         ▲                        │
│                                         │ HTTP                   │
│  ┌──────────────────┐         ┌────────┴──────────┐            │
│  │  Salesforce      │────────▶│  MCP Server 1.0  │            │
│  │  (Apex/LWC)      │  MCP    │  (Thin Adapter)   │            │
│  └──────────────────┘         └──────────────────┘            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Characteristics**:
- FastAPI backend serves React UI
- MCP Server 1.0 is thin adapter (calls FastAPI via HTTP)
- `dcisionai_graph` only imported by FastAPI
- Two deployment units: FastAPI + MCP Server

---

## 🚀 New Architecture (MCP Server 2.0)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DcisionAI Platform                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐         ┌──────────────────────────┐     │
│  │  React UI        │────────▶│                          │     │
│  │  (MCP Client)   │  MCP    │                          │     │
│  └──────────────────┘         │                          │     │
│                                 │   MCP Server 2.0        │     │
│  ┌──────────────────┐         │   (Primary Interface)    │     │
│  │  Salesforce      │────────▶│                          │     │
│  │  (MCP Client)    │  MCP    │                          │     │
│  └──────────────────┘         └──────────┬───────────────┘     │
│                                            │                     │
│                                            │ Direct Import      │
│                                            ▼                     │
│                                     ┌──────────────┐             │
│                                     │ dcisionai_   │             │
│                                     │   graph/     │             │
│                                     │ (Core Engine)│             │
│                                     └──────────────┘             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Characteristics**:
- MCP Server 2.0 is **primary interface** (not adapter)
- Directly imports `dcisionai_graph` (no HTTP layer)
- React UI becomes MCP client (like Salesforce)
- Single deployment unit: MCP Server 2.0

---

## 📦 Component Breakdown

### 1. `dcisionai_graph/` - Core Optimization Engine

**Status**: ✅ **KEEPS EXISTING** (No Changes)

**What It Is**:
- Core optimization engine
- LangGraph workflows
- DAME solver
- Deployed models
- Domain configurations

**Deployment**:
- Deployed as Python package/library
- Imported by MCP Server 2.0
- Can be used independently (CLI, notebooks, etc.)

**Customer Access**:
- ✅ Via MCP Server 2.0 (primary)
- ✅ Direct Python import (advanced users)
- ✅ Via CLI tools (if built)

---

### 2. `dcisionai_mcp_server_2.0/` - MCP Primary Interface

**Status**: ✅ **NEW** (Replaces MCP Server 1.0)

**What It Is**:
- Primary interface for all clients
- Direct integration with `dcisionai_graph`
- Multi-transport support (HTTP, WebSocket, SSE)
- FastMCP framework

**Deployment**:
- Single service deployment
- Runs on Railway/Cloud
- Exposes MCP protocol endpoints

**Customer Access**:
- ✅ Salesforce (via HTTP JSON-RPC 2.0)
- ✅ React UI (via WebSocket)
- ✅ IDEs (via SSE/MCP protocol)
- ✅ Any MCP client

---

### 3. `api/` (FastAPI Backend)

**Status**: ⚠️ **DEPRECATED** (Phased Out)

**What It Was**:
- HTTP REST API backend
- Served React UI
- Called by MCP Server 1.0

**Migration Path**:
- **Phase 1**: Keep running (backward compatibility)
- **Phase 2**: Migrate React UI to MCP client
- **Phase 3**: Retire FastAPI backend

**Timeline**:
- Keep until React UI migration complete
- Then deprecate and remove

---

### 4. `dcisionai_mcp_server/` (MCP Server 1.0)

**Status**: ⚠️ **DEPRECATED** (Replaced by 2.0)

**What It Was**:
- Thin MCP protocol adapter
- Called FastAPI backend via HTTP
- Protocol translation layer

**Migration Path**:
- **Immediate**: New deployments use MCP Server 2.0
- **Existing**: Migrate to MCP Server 2.0
- **Timeline**: Deprecate after migration complete

---

### 5. `dcisionai_mcp_clients/` - Platform Clients

**Status**: ✅ **KEEPS EXISTING** (Updated for MCP Server 2.0)

**What It Is**:
- Salesforce MCP client (Apex/LWC)
- React MCP client (new, to be built)
- Platform-specific integrations

**Updates Needed**:
- ✅ Salesforce client: Already compatible (HTTP JSON-RPC 2.0)
- ⏳ React client: Needs MCP client library
- ⏳ Update endpoint URLs to MCP Server 2.0

---

## 🎯 Customer Deployment Scenarios

### Scenario 1: Cloud SaaS (Current)

**Deployment**:
```
┌─────────────────────────────────────────┐
│  Railway/Cloud Platform                │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  MCP Server 2.0                 │  │
│  │  - HTTP JSON-RPC 2.0            │  │
│  │  - WebSocket                    │  │
│  │  - SSE                          │  │
│  └──────────────┬───────────────────┘  │
│                 │                       │
│                 │ Import                │
│                 ▼                       │
│  ┌──────────────────────────────────┐  │
│  │  dcisionai_graph (Package)       │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
         ▲                    ▲
         │                    │
    ┌────┴────┐         ┌─────┴─────┐
    │React UI │         │ Salesforce │
    │(MCP)    │         │ (MCP)     │
    └─────────┘         └───────────┘
```

**Characteristics**:
- Single service deployment
- All clients connect via MCP
- Scalable, cloud-native
- Easy to maintain

---

### Scenario 2: On-Premise Enterprise

**Deployment**:
```
┌─────────────────────────────────────────┐
│  Customer Infrastructure                │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  MCP Server 2.0                  │  │
│  │  (Docker Container)              │  │
│  └──────────────┬───────────────────┘  │
│                 │                       │
│                 │ Import                │
│                 ▼                       │
│  ┌──────────────────────────────────┐  │
│  │  dcisionai_graph (Package)       │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
         ▲                    ▲
         │                    │
    ┌────┴────┐         ┌─────┴─────┐
    │Internal │         │ Salesforce │
    │React UI │         │ (MCP)     │
    │(MCP)    │         │           │
    └─────────┘         └───────────┘
```

**Characteristics**:
- Self-hosted deployment
- Customer controls infrastructure
- Same MCP protocol
- Can integrate with customer systems

---

### Scenario 3: Hybrid (Cloud + On-Premise)

**Deployment**:
```
┌──────────────────┐         ┌──────────────────┐
│  Cloud (SaaS)    │         │  On-Premise     │
│                  │         │                  │
│  ┌────────────┐ │         │  ┌────────────┐ │
│  │MCP Server  │ │         │  │MCP Server  │ │
│  │2.0 (Cloud) │ │         │  │2.0 (Local) │ │
│  └─────┬──────┘ │         │  └─────┬──────┘ │
│        │         │         │        │        │
│        │         │         │        │        │
│        ▼         │         │        ▼        │
│  ┌────────────┐ │         │  ┌────────────┐ │
│  │dcisionai_  │ │         │  │dcisionai_  │ │
│  │graph       │ │         │  │graph       │ │
│  └────────────┘ │         │  └────────────┘ │
└──────────────────┘         └──────────────────┘
```

**Characteristics**:
- Cloud for public-facing
- On-premise for sensitive data
- Same MCP protocol
- Customer chooses deployment

---

## 🔄 Migration Timeline

### Phase 1: Parallel Operation (Current)

**Duration**: 1-2 months

**What Happens**:
- ✅ MCP Server 2.0 deployed alongside existing services
- ✅ Both MCP Server 1.0 and 2.0 available
- ✅ FastAPI backend continues running
- ✅ React UI continues using FastAPI
- ✅ Salesforce can use either MCP Server

**Goal**: Zero downtime migration

---

### Phase 2: Client Migration

**Duration**: 1-2 months

**What Happens**:
- ✅ Salesforce migrates to MCP Server 2.0
- ✅ React UI migrates to MCP client (WebSocket)
- ✅ New customers onboard to MCP Server 2.0
- ⚠️ FastAPI backend marked deprecated

**Goal**: All clients on MCP Server 2.0

---

### Phase 3: Retirement

**Duration**: 1 month

**What Happens**:
- ❌ FastAPI backend retired
- ❌ MCP Server 1.0 retired
- ✅ Only MCP Server 2.0 remains
- ✅ Simplified architecture

**Goal**: Clean, single-service architecture

---

## 📊 What Gets Retired

### ❌ Retired Components

1. **`api/` (FastAPI Backend)**
   - **Why**: React UI migrates to MCP client
   - **When**: After React UI migration complete
   - **Impact**: No HTTP REST API (use MCP instead)

2. **`dcisionai_mcp_server/` (MCP Server 1.0)**
   - **Why**: Replaced by MCP Server 2.0
   - **When**: After all clients migrated
   - **Impact**: Thin adapter no longer needed

### ✅ Kept Components

1. **`dcisionai_graph/`**
   - **Why**: Core engine, reusable
   - **Status**: No changes, continues as-is

2. **`dcisionai_mcp_clients/`**
   - **Why**: Platform integrations needed
   - **Status**: Updated for MCP Server 2.0

---

## 🎯 Customer Deployment Options

### Option A: Cloud SaaS (Recommended)

**Deployment**: Railway, AWS, GCP, Azure

**Components**:
- MCP Server 2.0 (single service)
- `dcisionai_graph` (package dependency)

**Benefits**:
- ✅ Simple deployment
- ✅ Automatic scaling
- ✅ Managed infrastructure
- ✅ Easy updates

**Use Case**: Most customers

---

### Option B: On-Premise

**Deployment**: Customer infrastructure

**Components**:
- MCP Server 2.0 (Docker container)
- `dcisionai_graph` (package dependency)

**Benefits**:
- ✅ Data stays on-premise
- ✅ Customer control
- ✅ Compliance-friendly

**Use Case**: Enterprise, regulated industries

---

### Option C: Hybrid

**Deployment**: Cloud + On-Premise

**Components**:
- MCP Server 2.0 (both locations)
- `dcisionai_graph` (both locations)

**Benefits**:
- ✅ Flexibility
- ✅ Data sovereignty
- ✅ Performance optimization

**Use Case**: Large enterprises

---

## 🔧 Deployment Architecture Details

### MCP Server 2.0 Deployment

**Single Service**:
```yaml
Service: dcisionai-mcp-server-2.0
Port: 8080
Endpoints:
  - /health (HTTP GET)
  - /mcp/tools/call (HTTP POST - JSON-RPC 2.0)
  - /mcp/resources/{uri} (HTTP GET)
  - /ws/{session_id} (WebSocket)
  - /api/models (HTTP GET - convenience)
```

**Dependencies**:
- `dcisionai_graph` (Python package)
- FastMCP framework
- FastAPI (for HTTP/WebSocket)

**Environment Variables**:
- `PORT` (default: 8080)
- `DCISIONAI_DOMAIN_FILTER` (optional)
- `ANTHROPIC_API_KEY` (required)
- `DCISIONAI_LOG_LEVEL` (optional)

---

### Client Connections

**Salesforce**:
```
Salesforce Apex → HTTP POST /mcp/tools/call
                → JSON-RPC 2.0 format
                → Returns JSON result
```

**React UI**:
```
React Component → WebSocket /ws/{session_id}
                → Streams step_complete events
                → Receives workflow_complete
```

**IDEs (Cursor, VS Code)**:
```
IDE → MCP Protocol (SSE/HTTP)
    → Standard MCP tools/resources
    → Returns TextContent
```

---

## 📈 Benefits of New Architecture

### 1. **Simplified Deployment**
- ✅ Single service (vs 2 services)
- ✅ Fewer moving parts
- ✅ Easier to maintain

### 2. **Better Performance**
- ✅ Direct imports (no HTTP overhead)
- ✅ Lower latency
- ✅ More efficient

### 3. **Unified Protocol**
- ✅ All clients use MCP
- ✅ Consistent interface
- ✅ Easier to support

### 4. **Future-Proof**
- ✅ MCP is standard protocol
- ✅ Easy to add new clients
- ✅ Scalable architecture

---

## 🚨 Migration Considerations

### For Existing Customers

1. **No Breaking Changes** (During Migration)
   - Both MCP Server 1.0 and 2.0 available
   - FastAPI backend continues running
   - Gradual migration possible

2. **Update Required** (After Migration)
   - Update endpoint URLs
   - Test MCP Server 2.0 compatibility
   - Migrate React UI to MCP client

3. **Benefits After Migration**
   - Better performance
   - Simpler architecture
   - Unified protocol

---

## 📝 Summary

### Architecture Evolution

**Before (MCP Server 1.0)**:
- 3 services: FastAPI + MCP Server + `dcisionai_graph`
- Mixed protocols: HTTP REST + MCP
- Complex deployment

**After (MCP Server 2.0)**:
- 1 service: MCP Server 2.0 + `dcisionai_graph`
- Unified protocol: MCP only
- Simple deployment

### What Stays
- ✅ `dcisionai_graph` (core engine)
- ✅ `dcisionai_mcp_clients` (platform clients)

### What Goes
- ❌ `api/` (FastAPI backend)
- ❌ `dcisionai_mcp_server/` (MCP Server 1.0)

### Customer Impact
- ✅ Simpler deployments
- ✅ Better performance
- ✅ Unified interface
- ⚠️ Migration required (gradual, non-breaking)

---

**Last Updated**: 2025-11-25

