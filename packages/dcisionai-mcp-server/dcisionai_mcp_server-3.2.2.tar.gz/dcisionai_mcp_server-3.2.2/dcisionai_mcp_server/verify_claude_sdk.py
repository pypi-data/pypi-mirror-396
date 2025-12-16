#!/usr/bin/env python3
"""
Verification script to check if Claude Agent SDK is installed correctly.
This script can be run locally or in Railway to verify SDK availability.

Migration guide: https://platform.claude.com/docs/en/agent-sdk/migration-guide
"""

import sys

def check_claude_sdk():
    """Check if Claude Agent SDK is available."""
    print("=" * 60)
    print("🔍 Claude Agent SDK Verification")
    print("=" * 60)
    print()
    
    # Check Anthropic client (fallback)
    try:
        from anthropic import Anthropic
        print("✅ Anthropic client available (fallback)")
    except ImportError as e:
        print(f"❌ Anthropic client NOT available: {e}")
        return False
    
    # REQUIRED: Claude Agent SDK must be available (no fallback)
    try:
        from claude_agent_sdk.client import ClaudeSDKClient
        print("✅ Claude Agent SDK available (REQUIRED)")
        
        # Try to get version if available
        try:
            import claude_agent_sdk
            version = getattr(claude_agent_sdk, '__version__', 'unknown')
            print(f"   Version: {version}")
        except:
            pass
        
        return True
    except ImportError as e:
        print(f"❌ Claude Agent SDK REQUIRED but NOT available: {e}")
        print("   This is a required dependency for both dev and production")
        print("   Install with: pip install claude-agent-sdk")
        return False

def check_dcisionai_integration():
    """Check if dcisionai_graph integration works."""
    print()
    print("=" * 60)
    print("🔍 DcisionAI Integration Check")
    print("=" * 60)
    print()
    
    # Add project root to Python path for import
    import sys
    import os
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        from dcisionai_graph.core.agents.claude_sdk_adapter import (
            CLAUDE_AGENT_SDK_AVAILABLE,
            ANTHROPIC_AVAILABLE
        )
        print(f"✅ DcisionAI adapter imported successfully")
        print(f"   CLAUDE_AGENT_SDK_AVAILABLE: {CLAUDE_AGENT_SDK_AVAILABLE}")
        print(f"   ANTHROPIC_AVAILABLE: {ANTHROPIC_AVAILABLE}")
        
        if CLAUDE_AGENT_SDK_AVAILABLE:
            print("   ✅ Claude Agent SDK is available (REQUIRED)")
        else:
            print("   ❌ Claude Agent SDK REQUIRED but not available")
            print("   This will cause startup to fail")
        
        return True
    except ImportError as e:
        print(f"⚠️  DcisionAI adapter import failed: {e}")
        print("   This is OK if running outside project context")
        print("   The SDK check above is the critical one")
        return True  # Don't fail if dcisionai_graph not in path

if __name__ == "__main__":
    print()
    sdk_available = check_claude_sdk()
    integration_ok = check_dcisionai_integration()
    
    print()
    print("=" * 60)
    if sdk_available and integration_ok:
        print("✅ All checks passed! Claude Agent SDK is ready.")
        sys.exit(0)
    else:
        print("❌ Claude Agent SDK REQUIRED but not available")
        print("   Install with: pip install claude-agent-sdk")
        print("   This is a hard requirement - no fallback available")
        sys.exit(1)

