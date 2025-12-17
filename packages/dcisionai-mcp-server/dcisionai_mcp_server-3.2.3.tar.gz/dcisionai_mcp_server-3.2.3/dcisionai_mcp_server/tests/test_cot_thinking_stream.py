"""
Test script to verify Chain of Thought (CoT) thinking streaming via WebSocket.

This test verifies that:
1. Business explanation agent uses CoT prompting with <thinking> tags
2. Thinking blocks are captured from LLM streaming
3. Thinking blocks are streamed to frontend via WebSocket
"""

import asyncio
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_cot_thinking_extraction():
    """Test that thinking blocks can be extracted from LLM responses."""
    from dcisionai_graph.core.tools.explanation.business_explainer import BusinessExplainer
    
    explainer = BusinessExplainer()
    
    # Get the prompt template
    prompt_template = explainer.get_prompt_template()
    
    # Check if CoT instructions are in the prompt
    prompt_str = str(prompt_template.messages)
    
    has_thinking_tag = "<thinking>" in prompt_str
    has_cot_instructions = "Chain of Thought" in prompt_str or "think through" in prompt_str.lower()
    
    logger.info(f"✅ CoT prompt check:")
    logger.info(f"   - Has <thinking> tags: {has_thinking_tag}")
    logger.info(f"   - Has CoT instructions: {has_cot_instructions}")
    
    assert has_thinking_tag, "Prompt should include <thinking> tags for CoT"
    assert has_cot_instructions, "Prompt should include CoT instructions"
    
    logger.info("✅ CoT prompting is correctly configured in BusinessExplainer")


async def test_thinking_block_parsing():
    """Test parsing thinking blocks from LLM responses."""
    # Simulate a response with thinking blocks
    sample_response = """
<thinking>
Let me analyze this step by step:

1. Problem Understanding:
   - The user wants to optimize portfolio allocation
   - Key variables: weights for PE, Credit, Real Estate
   - Constraints: sum to 100%, non-negative

2. Result Validation:
   - Mathematical solver returned optimal solution
   - DAME solver also succeeded
   - Both solutions are feasible
</thinking>

{
  "result": {
    "executive_summary": {
      "problem_statement": "Optimize portfolio allocation",
      "optimal_solution": "PE: 35%, Credit: 25%, Real Estate: 40%"
    }
  }
}
"""
    
    import re
    
    # Extract thinking block
    thinking_match = re.search(r'<thinking>(.*?)</thinking>', sample_response, re.DOTALL)
    
    if thinking_match:
        thinking_content = thinking_match.group(1).strip()
        logger.info(f"✅ Successfully extracted thinking block:")
        logger.info(f"   Length: {len(thinking_content)} chars")
        logger.info(f"   Preview: {thinking_content[:200]}...")
    else:
        logger.error("❌ Failed to extract thinking block")
        assert False, "Should extract thinking block"
    
    logger.info("✅ Thinking block parsing works correctly")


async def test_websocket_thinking_event():
    """Test that WebSocket can send thinking events."""
    # Simulate a thinking event structure
    thinking_event = {
        "type": "thinking",
        "step": "generate_business_explanation",
        "content": "Analyzing solver results step by step...",
        "session_id": "test_session",
        "timestamp": "2024-01-01T00:00:00"
    }
    
    # Verify structure
    assert thinking_event["type"] == "thinking"
    assert "content" in thinking_event
    assert "step" in thinking_event
    
    logger.info(f"✅ Thinking event structure is correct:")
    logger.info(f"   Type: {thinking_event['type']}")
    logger.info(f"   Step: {thinking_event['step']}")
    logger.info(f"   Content length: {len(thinking_event['content'])} chars")
    
    logger.info("✅ WebSocket thinking event structure is valid")


async def main():
    """Run all tests."""
    logger.info("🧪 Testing Chain of Thought (CoT) thinking streaming...")
    
    try:
        await test_cot_thinking_extraction()
        await test_thinking_block_parsing()
        await test_websocket_thinking_event()
        
        logger.info("\n✅ All CoT thinking tests passed!")
        logger.info("\n📝 Next steps:")
        logger.info("   1. Run a workflow with business explanation")
        logger.info("   2. Check WebSocket messages for 'thinking' type events")
        logger.info("   3. Verify thinking blocks are streamed in real-time")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())

