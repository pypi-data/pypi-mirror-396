#!/usr/bin/env python3
"""
Simple WebSocket Test - Minimal test to verify server is running
"""

import asyncio
import json
import sys

try:
    import websockets
except ImportError:
    print("❌ websockets not installed")
    print("Install with: pip3 install --user websockets")
    sys.exit(1)


async def test_connection():
    """Test basic WebSocket connection"""
    ws_url = "ws://localhost:8080/ws/test_simple"
    
    print(f"🔌 Connecting to: {ws_url}")
    
    try:
        async with websockets.connect(ws_url, ping_interval=None) as websocket:
            print("✅ Connected!")
            
            # Send test message
            message = {
                "problem_description": "Test optimization problem"
            }
            
            print("📤 Sending test message...")
            await websocket.send(json.dumps(message))
            
            # Wait for response (with timeout)
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"📥 Received: {data.get('type', 'unknown')}")
                
                if data.get("type") == "workflow_start":
                    print("✅ Server responded correctly!")
                    return True
                elif data.get("type") == "error":
                    print(f"⚠️  Server error: {data.get('message')}")
                    return False
                else:
                    print(f"⚠️  Unexpected response: {data}")
                    return False
            except asyncio.TimeoutError:
                print("⏱️  Timeout waiting for response (server may be processing)")
                return False
    
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused - Is the server running?")
        print("   Start with: python3 -m dcisionai_mcp_server_2.0.start_mcp_server")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Simple WebSocket Connection Test")
    print("=" * 60)
    print()
    
    result = asyncio.run(test_connection())
    
    print()
    if result:
        print("✅ Test passed!")
        sys.exit(0)
    else:
        print("❌ Test failed")
        sys.exit(1)

