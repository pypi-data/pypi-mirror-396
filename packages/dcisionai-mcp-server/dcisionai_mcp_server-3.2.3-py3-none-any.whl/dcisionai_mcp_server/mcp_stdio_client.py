"""
MCP stdio client wrapper for IDE integration (Cursor, VS Code)

This script acts as a bridge between IDE MCP clients (which use stdio)
and the Railway-deployed HTTP MCP server.

Protocol:
- IDE → stdio (JSON-RPC 2.0) → This script → HTTP → Railway MCP Server
- Railway MCP Server → HTTP → This script → stdio → IDE
"""

import sys
import json
import asyncio
import aiohttp
import os
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Log to stderr so stdout is reserved for JSON-RPC
)
logger = logging.getLogger(__name__)

# Railway MCP Server URL
MCP_SERVER_URL = os.getenv(
    "DCISIONAI_MCP_SERVER_URL",
    "https://dcisionai-mcp-server-production.up.railway.app"
)


class MCPStdioClient:
    """MCP stdio client that proxies to HTTP MCP server"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def start(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
        )
        logger.info(f"MCP stdio client started, connecting to {self.server_url}")
        
    async def stop(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("MCP stdio client stopped")
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON-RPC 2.0 request"""
        method = request.get("method")
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                # MCP initialization
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                            "resources": {}
                        },
                        "serverInfo": {
                            "name": "dcisionai-optimization",
                            "version": "3.2.3"
                        }
                    }
                }
            
            elif method == "tools/list":
                # List available tools (MCP-compliant JSON-RPC 2.0 POST request)
                async with self.session.post(
                    f"{self.server_url}/mcp/tools/list",
                    json={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "method": "tools/list",
                        "params": {}
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": data.get("result", {})
                        }
                    else:
                        raise Exception(f"HTTP {resp.status}: {await resp.text()}")
            
            elif method == "tools/call":
                # Call a tool
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                async with self.session.post(
                    f"{self.server_url}/mcp/tools/call",
                    json={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "method": "tools/call",
                        "params": {
                            "name": tool_name,
                            "arguments": arguments
                        }
                    }
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": data.get("result", {})
                        }
                    else:
                        error_text = await resp.text()
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32603,
                                "message": f"Tool call failed: HTTP {resp.status}",
                                "data": error_text
                            }
                        }
            
            elif method == "resources/list":
                # List available resources
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "resources": [
                            {
                                "uri": "dcisionai://models/list",
                                "name": "Deployed Models",
                                "description": "List of deployed optimization models",
                                "mimeType": "application/json"
                            },
                            {
                                "uri": "dcisionai://solvers/list",
                                "name": "Available Solvers",
                                "description": "List of available optimization solvers",
                                "mimeType": "application/json"
                            }
                        ]
                    }
                }
            
            elif method == "resources/read":
                # Read a resource
                params = request.get("params", {})
                uri = params.get("uri")
                
                async with self.session.get(
                    f"{self.server_url}/mcp/resources/{uri}"
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "contents": [
                                    {
                                        "uri": uri,
                                        "mimeType": "application/json",
                                        "text": json.dumps(data, indent=2)
                                    }
                                ]
                            }
                        }
                    else:
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32603,
                                "message": f"Resource read failed: HTTP {resp.status}"
                            }
                        }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            logger.error(f"Error handling request: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }


async def main():
    """Main stdio loop"""
    client = MCPStdioClient(MCP_SERVER_URL)
    
    try:
        await client.start()
        
        # Read from stdin line by line (JSON-RPC 2.0 messages)
        while True:
            line = await asyncio.get_event_loop().run_in_executor(
                None, sys.stdin.readline
            )
            
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            try:
                request = json.loads(line)
                response = await client.handle_request(request)
                
                # Write response to stdout
                print(json.dumps(response), flush=True)
            
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {e}"
                    }
                }
                print(json.dumps(error_response), flush=True)
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await client.stop()


def entry_point():
    """Entry point for uvx/pipx"""
    asyncio.run(main())

if __name__ == "__main__":
    entry_point()

