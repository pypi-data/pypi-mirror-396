"""
Configuration management for DcisionAI MCP Server 2.0
"""

import os
from typing import Optional


class MCPConfig:
    """Configuration for MCP Server 2.0"""
    
    # Server Configuration
    SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "8080"))
    
    # dcisionai_graph Configuration
    DOMAIN_FILTER: str = os.getenv("DCISIONAI_DOMAIN_FILTER", "all").lower()
    
    # Anthropic Claude API Configuration
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", None)
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
    
    # Logging
    LOG_LEVEL: str = os.getenv("DCISIONAI_LOG_LEVEL", "INFO")
    
    # Transport Configuration
    ENABLE_HTTP: bool = os.getenv("MCP_ENABLE_HTTP", "true").lower() == "true"
    ENABLE_WEBSOCKET: bool = os.getenv("MCP_ENABLE_WEBSOCKET", "true").lower() == "true"
    ENABLE_SSE: bool = os.getenv("MCP_ENABLE_SSE", "true").lower() == "true"
    
    # CORS Configuration (for web clients)
    # Production: Allow Vercel domains and platform domain
    # Development: Allow localhost
    _default_cors_origins = (
        "http://localhost:3000,"
        "https://platform.dcisionai.com,"
        "https://*.vercel.app"  # Vercel preview and production deployments
    )
    CORS_ORIGINS: list[str] = os.getenv(
        "MCP_CORS_ORIGINS",
        _default_cors_origins
    ).split(",")
    
    # Authentication (for remote clients)
    API_KEY: Optional[str] = os.getenv("MCP_API_KEY", None)
    OAUTH_ENABLED: bool = os.getenv("MCP_OAUTH_ENABLED", "false").lower() == "true"
    
    @classmethod
    def get_domain_filter(cls) -> str:
        """Get domain filter setting"""
        return cls.DOMAIN_FILTER
    
    @classmethod
    def get_anthropic_api_key(cls) -> Optional[str]:
        """Get Anthropic API key for Claude"""
        return cls.ANTHROPIC_API_KEY
    
    @classmethod
    def get_claude_model(cls) -> str:
        """Get Claude model name"""
        return cls.CLAUDE_MODEL

