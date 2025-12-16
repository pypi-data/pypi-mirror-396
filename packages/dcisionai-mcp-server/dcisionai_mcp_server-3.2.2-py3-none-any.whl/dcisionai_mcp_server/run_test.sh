#!/bin/bash
# Run WebSocket Test Script
# Activates venv and runs the test

set -e

cd "$(dirname "$0")/.."
source venv/bin/activate

echo "🧪 Running WebSocket Test..."
echo ""

python3 dcisionai_mcp_server_2.0/test_websocket.py

