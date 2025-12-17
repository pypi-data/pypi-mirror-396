# DcisionAI MCP Server

**AI-Powered Optimization for Cursor, Claude Desktop & VS Code**

Solve complex optimization problems directly in your IDE using natural language. Get mathematically-verified solutions with **90%+ trust scores** in seconds.

## 🚀 Quick Start

### Installation (Zero Configuration!)

```bash
# That's it! No installation needed with uvx
```

### Configure Your IDE

**For Cursor or Claude Desktop:**

Add to your MCP config file (`~/.cursor/mcp.json` on Mac):

```json
{
  "mcpServers": {
    "dcisionai-optimization": {
      "command": "uvx",
      "args": ["dcisionai-mcp-stdio@latest"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      },
      "autoApprove": ["dcisionai_solve", "dcisionai_solve_with_model"]
    }
  }
}
```

### Use It!

In Cursor or Claude Desktop, just ask:

```
"Use DcisionAI to optimize my $500K portfolio concentrated in tech stocks"

"Use DcisionAI to optimize delivery routes for 20 customers"

"Use DcisionAI to optimize employee scheduling for 30 workers across 50 shifts"
```

## ✨ What Can It Do?

### 📊 Finance
- Portfolio rebalancing with risk constraints
- Trading schedule optimization  
- Asset allocation with concentration limits
- Private equity exit timing

### 🏪 Retail
- Store layout optimization (shelf space allocation)
- Inventory management
- Pricing optimization
- Supply chain optimization

### 🏭 Manufacturing
- Production scheduling
- Resource allocation
- Job shop optimization
- Workforce scheduling

### 🚚 Logistics
- Vehicle routing (VRP)
- Delivery route optimization
- Warehouse layout
- Distribution network design

## 🛠️ Tools

- **`dcisionai_solve`** - Full optimization workflow (classification, intent extraction, solving, explanation)
- **`dcisionai_solve_with_model`** - Solve using deployed models (faster for known problem types)

## 📚 Resources

- **`dcisionai://models/list`** - Available deployed models
- **`dcisionai://solvers/list`** - Available solvers (HiGHS, SCIP, DAME, OR-Tools)

## 🔧 Configuration

Set environment variables (optional):

- `ANTHROPIC_API_KEY`: Your Anthropic API key (required for LLM features)
- `DCISIONAI_MCP_SERVER_URL`: Override server URL (default: production Railway URL)
- `DCISIONAI_DOMAIN_FILTER`: Domain filter (`"all"`, `"ria"`, `"pe"`, etc.)
- `DCISIONAI_LOG_LEVEL`: Logging level (`"INFO"`, `"DEBUG"`, etc.)

**Note**: The Railway server URL is configured internally. You only need to set `ANTHROPIC_API_KEY` for normal use.

## 📖 Documentation

- [Full Documentation](https://github.com/ameydhavle/dcisionai-mcp-platform)
- [MCP Server Planning](https://github.com/ameydhavle/dcisionai-mcp-platform/blob/main/docs/MCP_SERVER_PLANNING.md)
- [Architecture Decision Record](https://github.com/ameydhavle/dcisionai-mcp-platform/blob/main/docs/adr/029-mcp-server-integration-architecture.md)

## 🤝 Contributing

Contributions welcome! See our [GitHub repository](https://github.com/ameydhavle/dcisionai-mcp-platform) for details.

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Links

- **Homepage**: https://dcisionai.com
- **Repository**: https://github.com/ameydhavle/dcisionai-mcp-platform
- **Issues**: https://github.com/ameydhavle/dcisionai-mcp-platform/issues

