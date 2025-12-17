#!/bin/bash
# Start MCP Server 2.0
# Activates venv and starts the server

set -e

cd "$(dirname "$0")/.."
source venv/bin/activate

echo "🚀 Starting MCP Server 2.0..."
echo ""

python3 -m dcisionai_mcp_server_2.0.start_mcp_server

