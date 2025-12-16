"""
Test WebSocket Implementation for MCP Server 2.0

Tests the WebSocket endpoint for React UI streaming.
Mimics the React UI's WebSocket connection behavior.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

try:
    import websockets
except ImportError:
    print("❌ websockets library not installed")
    print("Install with: pip install websockets")
    sys.exit(1)


# Configuration
WS_URL = os.getenv(
    "WS_URL",
    "ws://localhost:8080"  # Default to local development
)


async def test_websocket_connection():
    """Test WebSocket connection and streaming"""
    session_id = f"test_{int(datetime.now().timestamp())}"
    ws_url = f"{WS_URL}/ws/{session_id}"
    
    print(f"🔌 Connecting to WebSocket: {ws_url}")
    print(f"📋 Session ID: {session_id}")
    print()
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected")
            print()
            
            # Send initial message (mimics React UI)
            initial_message = {
                "problem_description": "Optimize a portfolio of $500K across 10 stocks with 12% concentration limit",
                "enabled_features": ["intent", "data", "optimize"],
                "enabled_tools": ["data", "optimize"],
                "reasoning_model": "claude-3-5-haiku-20241022",
                "code_model": "codestral-latest",
                "enable_validation": False,
                "enable_templates": True,
                "template_preferences": {},
                "template_fallback": True
            }
            
            print("📤 Sending initial message:")
            print(json.dumps(initial_message, indent=2))
            print()
            
            await websocket.send(json.dumps(initial_message))
            
            # Receive and process messages
            step_count = 0
            received_types = set()
            
            print("📥 Receiving messages...")
            print("-" * 80)
            
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get("type", "unknown")
                    received_types.add(msg_type)
                    
                    if msg_type == "workflow_start":
                        print(f"✅ [{msg_type}] Workflow started")
                        print(f"   Session ID: {data.get('session_id')}")
                        print()
                    
                    elif msg_type == "step_complete":
                        step_count += 1
                        step_name = data.get("step", "unknown")
                        step_number = data.get("step_number", step_count)
                        
                        print(f"📊 [{msg_type}] Step {step_number}: {step_name}")
                        
                        # Show step data keys (not full content to avoid clutter)
                        step_data = data.get("data", {})
                        if isinstance(step_data, dict):
                            data_keys = list(step_data.keys())
                            print(f"   Data keys: {', '.join(data_keys[:5])}{'...' if len(data_keys) > 5 else ''}")
                        
                        print()
                    
                    elif msg_type == "workflow_complete":
                        print(f"🎉 [{msg_type}] Workflow completed!")
                        print(f"   Session ID: {data.get('session_id')}")
                        
                        result = data.get("result", {})
                        if isinstance(result, dict):
                            result_keys = list(result.keys())
                            print(f"   Result keys: {', '.join(result_keys[:10])}{'...' if len(result_keys) > 10 else ''}")
                            
                            # Show solution summary if available
                            if "solution" in result:
                                print("   ✅ Solution available")
                            if "objective_value" in result:
                                print(f"   📈 Objective value: {result.get('objective_value')}")
                            if "status" in result:
                                print(f"   📊 Status: {result.get('status')}")
                        
                        print()
                        break
                    
                    elif msg_type == "error":
                        print(f"❌ [{msg_type}] Error occurred")
                        print(f"   Message: {data.get('message', 'Unknown error')}")
                        print()
                        break
                    
                    else:
                        print(f"⚠️  [{msg_type}] Unknown message type")
                        print(f"   Data: {json.dumps(data, indent=2)[:200]}...")
                        print()
                    
                    # Safety: limit message count to prevent infinite loops
                    if step_count > 50:
                        print("⚠️  Stopping after 50 steps (safety limit)")
                        break
                
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse message: {e}")
                    print(f"   Raw message: {message[:200]}...")
                    print()
                except Exception as e:
                    print(f"❌ Error processing message: {e}")
                    print()
            
            # Summary
            print("-" * 80)
            print("📊 Test Summary:")
            print(f"   Total steps received: {step_count}")
            print(f"   Message types: {', '.join(sorted(received_types))}")
            print()
            
            # Verify expected message types
            expected_types = {"workflow_start", "step_complete", "workflow_complete"}
            missing_types = expected_types - received_types
            
            if missing_types:
                print(f"⚠️  Missing message types: {', '.join(missing_types)}")
            else:
                print("✅ All expected message types received")
            
            if "error" in received_types:
                print("❌ Error occurred during workflow execution")
                return False
            elif "workflow_complete" in received_types:
                print("✅ Workflow completed successfully")
                return True
            else:
                print("⚠️  Workflow did not complete (may have timed out or disconnected)")
                return False
    
    except (OSError, ConnectionError) as e:
        if "Connection refused" in str(e) or "Connect call failed" in str(e):
            print(f"❌ Connection refused. Is the server running at {WS_URL}?")
            print("   Start the server with: python3 dcisionai_mcp_server_2.0/start_mcp_server.py")
            return False
        raise
    except Exception as e:
        print(f"❌ Connection error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_websocket_error_handling():
    """Test WebSocket error handling (missing problem description)"""
    session_id = f"test_error_{int(datetime.now().timestamp())}"
    ws_url = f"{WS_URL}/ws/{session_id}"
    
    print(f"\n🧪 Testing error handling...")
    print(f"🔌 Connecting to: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            # Send invalid message (missing problem_description)
            invalid_message = {
                "enabled_features": ["intent", "data", "optimize"]
            }
            
            print("📤 Sending invalid message (missing problem_description)...")
            await websocket.send(json.dumps(invalid_message))
            
            # Should receive error
            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(message)
            
            if data.get("type") == "error":
                print(f"✅ Error handling works: {data.get('message')}")
                return True
            else:
                print(f"❌ Expected error, got: {data.get('type')}")
                return False
    
    except asyncio.TimeoutError:
        print("❌ Timeout waiting for error response")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Run all WebSocket tests"""
    print("=" * 80)
    print("🧪 WebSocket Implementation Test")
    print("=" * 80)
    print()
    
    # Test 1: Normal workflow
    print("Test 1: Normal Workflow Execution")
    print("-" * 80)
    test1_result = await test_websocket_connection()
    
    # Test 2: Error handling
    print("\nTest 2: Error Handling")
    print("-" * 80)
    test2_result = await test_websocket_error_handling()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 Test Results Summary")
    print("=" * 80)
    print(f"   Test 1 (Normal Workflow): {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"   Test 2 (Error Handling): {'✅ PASSED' if test2_result else '❌ FAILED'}")
    print()
    
    if test1_result and test2_result:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

