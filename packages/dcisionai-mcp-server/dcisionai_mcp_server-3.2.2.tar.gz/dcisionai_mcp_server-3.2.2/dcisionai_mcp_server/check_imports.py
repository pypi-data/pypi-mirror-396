#!/usr/bin/env python3
"""Check if MCP Server 2.0 imports correctly"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import using importlib to avoid syntax issues
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "fastmcp_server",
        os.path.join(os.path.dirname(__file__), "fastmcp_server.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    mcp = module.mcp
    app = module.app
    
    print('✅ MCP Server 2.0 imports successfully')
    print(f'✅ FastMCP app: {type(mcp)}')
    print(f'✅ FastAPI app: {type(app) if app else "None"}')
    sys.exit(0)
except Exception as e:
    print(f'❌ Import error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

