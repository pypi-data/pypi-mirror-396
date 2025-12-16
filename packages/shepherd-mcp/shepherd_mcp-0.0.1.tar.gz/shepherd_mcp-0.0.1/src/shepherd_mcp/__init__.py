"""Shepherd MCP - Debug your AI agents like you debug your code.

Supports multiple observability providers:
- AIOBS (Shepherd backend)
- Langfuse
"""

__version__ = "0.1.0"

# Re-export providers for programmatic use
from shepherd_mcp.providers import AIOBSClient, LangfuseClient
from shepherd_mcp.providers.base import (
    AuthenticationError,
    NotFoundError,
    ProviderError,
    RateLimitError,
)
from shepherd_mcp.server import main

__all__ = [
    "main",
    "__version__",
    # Providers
    "AIOBSClient",
    "LangfuseClient",
    # Exceptions
    "AuthenticationError",
    "NotFoundError",
    "ProviderError",
    "RateLimitError",
]
