"""
Helper functions for WebSocket transport.

Extracted from websocket.py to simplify the main handler.
"""

import re
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


def extract_thinking_content(chunk: Any) -> Optional[str]:
    """
    Extract thinking content from various Claude streaming formats.
    
    LangGraph streams Claude thinking tokens through astream_events() in these formats:
    1. content_block with type="thinking" (Claude's native format)
    2. delta with type="thinking_delta" (Claude streaming delta)
    3. Text content with <thinking> tags (CoT prompts)
    4. Nested structures (content_block in delta)
    
    Args:
        chunk: Chunk from LangGraph event (dict, str, or object)
        
    Returns:
        Extracted thinking content, or None if not found
    """
    thinking_content = None
    
    # CRITICAL: Log chunk structure in production (use INFO level)
    if not hasattr(extract_thinking_content, '_debug_count'):
        extract_thinking_content._debug_count = 0
    extract_thinking_content._debug_count += 1
    if extract_thinking_content._debug_count <= 20:  # Log first 20 chunks in production
        logger.info(f"🔍 [THINKING EXTRACT] Chunk #{extract_thinking_content._debug_count} - Type: {type(chunk)}, Keys: {list(chunk.keys()) if isinstance(chunk, dict) else 'N/A'}, Preview: {str(chunk)[:300]}")
    
    if isinstance(chunk, dict):
        # Format 1: content_block with thinking type (Claude's native thinking format)
        if "content_block" in chunk:
            content_block = chunk.get("content_block", {})
            if content_block.get("type") == "thinking":
                # Claude's native thinking format - extract text directly
                thinking_content = content_block.get("text", "") or content_block.get("content", "")
                logger.debug(f"✅ Found thinking content_block: type={content_block.get('type')}, text_length={len(thinking_content) if thinking_content else 0}")
            else:
                text_content = content_block.get("text", "") or content_block.get("content", "")
                if text_content and ("<thinking>" in text_content or "</thinking>" in text_content):
                    thinking_content = text_content
        
        # Format 2: delta with thinking (Claude streaming delta format)
        if "delta" in chunk and not thinking_content:
            delta = chunk.get("delta", {})
            # Check for thinking_delta type (Claude's native thinking streaming)
            if delta.get("type") == "thinking_delta":
                thinking_content = delta.get("text", "") or delta.get("content", "")
                logger.debug(f"✅ Found thinking_delta: text_length={len(thinking_content) if thinking_content else 0}")
            else:
                text_delta = delta.get("text", "") or delta.get("content", "")
                if text_delta and ("<thinking>" in text_delta or "</thinking>" in text_delta):
                    thinking_content = text_delta
        
        # Format 2b: Check for content_block in delta (nested structure)
        if "delta" in chunk and not thinking_content:
            delta = chunk.get("delta", {})
            if isinstance(delta, dict) and "content_block" in delta:
                content_block = delta.get("content_block", {})
                if content_block.get("type") == "thinking":
                    thinking_content = content_block.get("text", "") or content_block.get("content", "")
                    logger.debug(f"✅ Found thinking content_block in delta: text_length={len(thinking_content) if thinking_content else 0}")
        
        # Format 2c: Check if chunk itself is a content_block dict (direct structure)
        if not thinking_content and isinstance(chunk, dict):
            if chunk.get("type") == "thinking":
                thinking_content = chunk.get("text", "") or chunk.get("content", "")
                logger.debug(f"✅ Found thinking type in chunk root: text_length={len(thinking_content) if thinking_content else 0}")
            elif "type" in chunk and "text" in chunk:
                # Might be a content_block structure at root level
                if chunk.get("type") == "thinking":
                    thinking_content = chunk.get("text", "")
                    logger.debug(f"✅ Found thinking in chunk root (type+text): text_length={len(thinking_content) if thinking_content else 0}")
        
        # Format 3: direct content with thinking tags
        if "content" in chunk and not thinking_content:
            content = chunk.get("content", "")
            if isinstance(content, str) and ("<thinking>" in content or "</thinking>" in content):
                thinking_content = content
        
        # Format 4: Check if chunk itself is a string with thinking tags
        if not thinking_content:
            chunk_str = str(chunk)
            if "<thinking>" in chunk_str or "</thinking>" in chunk_str:
                thinking_match = re.search(r'<thinking>(.*?)</thinking>', chunk_str, re.DOTALL)
                if thinking_match:
                    thinking_content = thinking_match.group(1)
    
    elif isinstance(chunk, str):
        # Format 5: Chunk is directly a string
        if "<thinking>" in chunk or "</thinking>" in chunk:
            thinking_match = re.search(r'<thinking>(.*?)</thinking>', chunk, re.DOTALL)
            if thinking_match:
                thinking_content = thinking_match.group(1)
    
    # Format 6: AIMessageChunk with content attribute
    if not thinking_content and hasattr(chunk, 'content'):
        content = getattr(chunk, 'content', '')
        if isinstance(content, str) and ("<thinking>" in content or "</thinking>" in content):
            thinking_match = re.search(r'<thinking>(.*?)</thinking>', content, re.DOTALL)
            if thinking_match:
                thinking_content = thinking_match.group(1)
    
    # Clean up thinking content
    if thinking_content:
        if "<thinking>" in thinking_content or "</thinking>" in thinking_content:
            # Use greedy match to handle nested tags better
            thinking_match = re.search(r'<thinking>(.*)</thinking>', thinking_content, re.DOTALL)
            if thinking_match:
                thinking_content = thinking_match.group(1).strip()
                # Remove any remaining nested thinking tags
                thinking_content = re.sub(r'</?thinking>', '', thinking_content)
            else:
                # No complete tags, just remove tag markers
                thinking_content = re.sub(r'</?thinking>', '', thinking_content)
        
        # Filter out malformed/incomplete thinking blocks
        thinking_content = thinking_content.strip()
        if len(thinking_content) <= 5:
            return None
        
        # Skip if content is just opening braces or malformed JSON
        if thinking_content in ['{', '}', '{</thinking>', '<thinking>', '</thinking>']:
            return None
        
        return thinking_content
    
    return None


def extract_thinking_from_output(output: Dict[str, Any]) -> List[str]:
    """
    Recursively extract thinking blocks from nested output dict.
    
    Args:
        output: Output dictionary from LangGraph event
        
    Returns:
        List of thinking content strings
    """
    thinking_blocks = []
    
    def extract_from_dict(d: Any, path: str = "") -> List[str]:
        """Recursively extract thinking blocks from nested dict."""
        found = []
        if isinstance(d, dict):
            # Check for _thinking_content key (stored by BaseIntentTool or workflow nodes)
            if "_thinking_content" in d:
                thinking_content = d.get("_thinking_content", "")
                if isinstance(thinking_content, str) and thinking_content.strip():
                    found.append(thinking_content.strip())
                    logger.info(f"✅ Found _thinking_content at {path}: {len(thinking_content)} chars")
            
            # Also check for thinking content in step-specific fields (e.g., assumptions_result)
            # Some nodes store thinking in nested result structures
            for key in ["assumptions_result", "entities_result", "objectives_result", "constraints_result"]:
                if key in d and isinstance(d[key], dict):
                    if "_thinking_content" in d[key]:
                        thinking_content = d[key].get("_thinking_content", "")
                        if isinstance(thinking_content, str) and thinking_content.strip():
                            found.append(thinking_content.strip())
                            logger.info(f"✅ Found _thinking_content in {key} at {path}: {len(thinking_content)} chars")
            
            # Check for thinking_blocks key
            if "thinking_blocks" in d:
                blocks = d.get("thinking_blocks", [])
                if isinstance(blocks, list):
                    found.extend([b for b in blocks if isinstance(b, str)])
            
            # Check for thinking tags in string values
            for key, value in d.items():
                if isinstance(value, str) and ("<thinking>" in value or "</thinking>" in value):
                    thinking_match = re.search(r'<thinking>(.*?)</thinking>', value, re.DOTALL)
                    if thinking_match:
                        found.append(thinking_match.group(1).strip())
            
            # Recursively search nested dicts
            for key, value in d.items():
                if isinstance(value, dict):
                    found.extend(extract_from_dict(value, f"{path}.{key}" if path else key))
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            found.extend(extract_from_dict(item, f"{path}.{key}[{i}]" if path else f"{key}[{i}]"))
        return found
    
    thinking_blocks = extract_from_dict(output)
    
    # Also check the raw output string representation
    if not thinking_blocks:
        output_str = str(output)
        if "<thinking>" in output_str or "</thinking>" in output_str:
            thinking_match = re.search(r'<thinking>(.*?)</thinking>', output_str, re.DOTALL)
            if thinking_match:
                thinking_blocks.append(thinking_match.group(1).strip())
    
    return thinking_blocks


def normalize_node_name(raw_name: str) -> str:
    """Normalize node name for consistent step identification"""
    node_map = {
        # Legacy mappings (old workflow node names)
        "early_knowledgebase_research": "step0_knowledgebase_research",
        "decompose_query": "step0_decomposition",  # Fixed: was step1, should be step0
        "build_context": "step0_context",  # Fixed: was step1, should be step0
        "classify_problem": "step1_classification",  # Fixed: was step2, should be step1
        "generate_assumptions": "step3_assumptions",
        "extract_entities": "step4_entities",
        "guided_review_entities": "step4_entities",  # Tier 2: Guided Review
        "template_entities": "step4_entities",  # Tier 3: Template Direct
        "guided_learning_entities": "step4_entities",  # Tier 1: Guided Learning
        "extract_objectives": "step5_objectives",
        "extract_constraints": "step6_constraints",

        # Current workflow raw names (from backend logs)
        "knowledgebase_research": "step0_knowledgebase_research",
        "decomposition": "step0_decomposition",
        "context_building": "step0_context",
        "classification": "step1_classification",
        "assumptions": "step3_assumptions",
        "entities": "step4_entities",
        "objectives": "step5_objectives",
        "constraints": "step6_constraints",

        # Solver and other workflow nodes
        "solver_router": "solver_router",
        "run_both_solvers": "run_both_solvers",
        "dame_solver": "dame_solver",
        "generate_data": "generate_data",  # Data generation step
        "generate_business_explanation": "generate_business_explanation",
    }
    return node_map.get(raw_name, raw_name)


def is_step_complete_node(node_name: str) -> bool:
    """
    Check if a node is a step completion node (sends step_complete messages).

    Includes:
    - Intent discovery steps (step0_knowledgebase_research, step1_classification, etc.)
    - Data generation steps (generate_data)
    - Solver steps (tier3_solver, tier2_solver, tier1_solver, adhoc_solver)
    - Clean workflow nodes (intent_discovery, claude_agent_solver, business_explanation)
    - Other workflow completion nodes
    """
    step_complete_nodes = [
        'early_knowledgebase_research', 'knowledgebase_research',
        'decompose_query', 'query_decomposition', 'build_context',
        'classify_problem', 'generate_assumptions',
        # 3-tier entity extraction nodes (CRITICAL for architecture compliance)
        'extract_entities',  # Ad-hoc path
        'guided_review_entities',  # Tier 2: Guided Review (phd_reviewer)
        'template_entities',  # Tier 3: Template Direct (lightweight_adjuster)
        'guided_learning_entities',  # Tier 1: Guided Learning (student_learning)
        'extract_objectives', 'extract_constraints',
        'solver_router', 'run_both_solvers', 'dame_solver',
        # 3-tier solver nodes (Phase 7: UI Integration)
        'tier3_solver', 'tier2_solver', 'tier1_solver', 'adhoc_solver',
        'generate_business_explanation', 'generate_data',
        # Clean Claude Agent SDK Workflow nodes
        'intent_discovery', 'claude_agent_solver', 'business_explanation',
        'intent_discovery_unified',  # Alternative name
    ]
    return node_name in step_complete_nodes

