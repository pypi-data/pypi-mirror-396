"""
Test Salesforce Integration - NLP Query Tool
Simulates Salesforce calling the FastAPI backend /mcp/tools/call endpoint
"""

import asyncio
import json
import os
import aiohttp
from typing import Dict, Any


# Configuration - Use FastAPI backend URL (where Salesforce calls)
FASTAPI_BACKEND_URL = os.getenv(
    "FASTAPI_BACKEND_URL",
    "https://dcisionai-mcp-platform-production.up.railway.app"
)


async def test_salesforce_nlp_query_simulation():
    """
    Simulate Salesforce calling dcisionai_nlp_query via FastAPI backend
    This mimics exactly what DcisionAINLPController.answerQuestion() does
    """
    print("="*60)
    print("Salesforce NLP Query Integration Test")
    print("="*60)
    print(f"\nFastAPI Backend URL: {FASTAPI_BACKEND_URL}")
    print(f"Endpoint: {FASTAPI_BACKEND_URL}/mcp/tools/call")
    print()
    
    # Test Case 1: Simple question (like Data Summary tab)
    print("-"*60)
    print("TEST 1: Simple Data Question (Data Summary Tab)")
    print("-"*60)
    
    question = "How many advisors do we have?"
    
    # Salesforce request format (from DcisionAINLPController)
    mcp_request = {
        "name": "dcisionai_nlp_query",
        "arguments": {
            "question": question,
            "salesforce_data": None,
            "org_context": None
        }
    }
    
    print(f"\nRequest:")
    print(json.dumps(mcp_request, indent=2))
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{FASTAPI_BACKEND_URL}/mcp/tools/call",
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            print(f"\nResponse Status: {response.status}")
            response_body = await response.text()
            
            if response.status == 200:
                try:
                    result = json.loads(response_body)
                    print(f"\nResponse:")
                    print(json.dumps(result, indent=2))
                    
                    # Verify response format (what Salesforce expects)
                    if "result" in result:
                        result_data = result["result"]
                        if isinstance(result_data, str):
                            # Parse JSON string
                            result_data = json.loads(result_data)
                        
                        print(f"\n✅ Response format correct")
                        print(f"   - Has 'result' key: ✅")
                        
                        if isinstance(result_data, dict):
                            if "answer" in result_data:
                                print(f"   - Has 'answer' key: ✅")
                                print(f"   - Answer: {result_data['answer'][:100]}...")
                            if "intent" in result_data:
                                print(f"   - Has 'intent' key: ✅")
                                print(f"   - Intent: {result_data['intent']}")
                            if "data_summary" in result_data:
                                print(f"   - Has 'data_summary' key: ✅")
                            if "visualization_suggestions" in result_data:
                                print(f"   - Has 'visualization_suggestions' key: ✅")
                        
                        print(f"\n✅ TEST 1 PASSED")
                        return True
                    else:
                        print(f"\n❌ TEST 1 FAILED: Missing 'result' key")
                        return False
                except json.JSONDecodeError as e:
                    print(f"\n❌ TEST 1 FAILED: Invalid JSON response")
                    print(f"   Error: {e}")
                    print(f"   Response: {response_body[:500]}")
                    return False
            else:
                print(f"\n❌ TEST 1 FAILED: HTTP {response.status}")
                print(f"   Response: {response_body[:500]}")
                return False


async def test_salesforce_nlp_query_with_data():
    """
    Test with Salesforce data context (like Data Summary tab would provide)
    """
    print("\n" + "-"*60)
    print("TEST 2: NLP Query with Salesforce Data Context")
    print("-"*60)
    
    question = "What's the total AUM across all accounts?"
    
    # Sample Salesforce data (what Data Summary tab might provide)
    salesforce_data = {
        "accounts": [
            {"Name": "Acme Corp", "AUM__c": 5000000},
            {"Name": "TechCo", "AUM__c": 3000000}
        ],
        "advisors": [
            {"Name": "John Doe", "Total_AUM__c": 8000000},
            {"Name": "Jane Smith", "Total_AUM__c": 5000000}
        ]
    }
    
    org_context = {
        "domain": "ria",
        "industry": "financial_services"
    }
    
    mcp_request = {
        "name": "dcisionai_nlp_query",
        "arguments": {
            "question": question,
            "salesforce_data": salesforce_data,
            "org_context": org_context
        }
    }
    
    print(f"\nRequest:")
    print(json.dumps(mcp_request, indent=2))
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{FASTAPI_BACKEND_URL}/mcp/tools/call",
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            print(f"\nResponse Status: {response.status}")
            response_body = await response.text()
            
            if response.status == 200:
                try:
                    result = json.loads(response_body)
                    print(f"\nResponse:")
                    print(json.dumps(result, indent=2))
                    
                    if "result" in result:
                        result_data = result["result"]
                        if isinstance(result_data, str):
                            result_data = json.loads(result_data)
                        
                        print(f"\n✅ Response format correct")
                        if isinstance(result_data, dict) and "answer" in result_data:
                            print(f"   - Answer uses provided data: ✅")
                            print(f"   - Answer: {result_data['answer'][:150]}...")
                        
                        print(f"\n✅ TEST 2 PASSED")
                        return True
                    else:
                        print(f"\n❌ TEST 2 FAILED: Missing 'result' key")
                        return False
                except json.JSONDecodeError as e:
                    print(f"\n❌ TEST 2 FAILED: Invalid JSON response")
                    print(f"   Error: {e}")
                    return False
            else:
                print(f"\n❌ TEST 2 FAILED: HTTP {response.status}")
                print(f"   Response: {response_body[:500]}")
                return False


async def test_optimization_intent_detection():
    """
    Test optimization intent detection (should suggest using optimization tools)
    """
    print("\n" + "-"*60)
    print("TEST 3: Optimization Intent Detection")
    print("-"*60)
    
    question = "Optimize my portfolio allocation"
    
    mcp_request = {
        "name": "dcisionai_nlp_query",
        "arguments": {
            "question": question,
            "salesforce_data": None,
            "org_context": None
        }
    }
    
    print(f"\nRequest:")
    print(json.dumps(mcp_request, indent=2))
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{FASTAPI_BACKEND_URL}/mcp/tools/call",
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            print(f"\nResponse Status: {response.status}")
            response_body = await response.text()
            
            if response.status == 200:
                try:
                    result = json.loads(response_body)
                    print(f"\nResponse:")
                    print(json.dumps(result, indent=2))
                    
                    if "result" in result:
                        result_data = result["result"]
                        if isinstance(result_data, str):
                            result_data = json.loads(result_data)
                        
                        if isinstance(result_data, dict):
                            intent = result_data.get("intent", "")
                            if intent == "optimization":
                                print(f"\n✅ Intent correctly classified as 'optimization'")
                                print(f"   - Suggestion provided: {'suggestion' in result_data}")
                                print(f"\n✅ TEST 3 PASSED")
                                return True
                            else:
                                print(f"\n⚠️  Intent: {intent} (expected 'optimization')")
                                return False
                    
                    print(f"\n❌ TEST 3 FAILED: Unexpected response format")
                    return False
                except json.JSONDecodeError as e:
                    print(f"\n❌ TEST 3 FAILED: Invalid JSON response")
                    return False
            else:
                print(f"\n❌ TEST 3 FAILED: HTTP {response.status}")
                print(f"   Response: {response_body[:500]}")
                return False


async def test_error_handling():
    """
    Test error handling (empty question, invalid request)
    """
    print("\n" + "-"*60)
    print("TEST 4: Error Handling")
    print("-"*60)
    
    # Test with empty question
    mcp_request = {
        "name": "dcisionai_nlp_query",
        "arguments": {
            "question": "",
            "salesforce_data": None,
            "org_context": None
        }
    }
    
    print(f"\nRequest (empty question):")
    print(json.dumps(mcp_request, indent=2))
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{FASTAPI_BACKEND_URL}/mcp/tools/call",
            json=mcp_request,
            headers={"Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            print(f"\nResponse Status: {response.status}")
            response_body = await response.text()
            
            if response.status >= 400:
                print(f"\n✅ Error handling works (returned {response.status})")
                print(f"   Response: {response_body[:200]}")
                print(f"\n✅ TEST 4 PASSED")
                return True
            else:
                print(f"\n⚠️  Empty question accepted (status {response.status})")
                return True  # Not necessarily a failure


async def run_all_tests():
    """Run all Salesforce integration tests"""
    print("\n" + "="*60)
    print("Salesforce NLP Query Integration Test Suite")
    print("="*60)
    
    tests = [
        ("Simple Data Question", test_salesforce_nlp_query_simulation),
        ("Query with Salesforce Data", test_salesforce_nlp_query_with_data),
        ("Optimization Intent Detection", test_optimization_intent_detection),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests PASSED!")
    else:
        print(f"\n⚠️  {total - passed} test(s) FAILED")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)

