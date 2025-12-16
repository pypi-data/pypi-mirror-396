"""Base provider interface for Shepherd MCP.

This module defines the abstract base classes and common exceptions
for all provider implementations.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


def load_dotenv() -> None:
    """Load environment variables from .env file.

    Searches current directory and parent directories for a .env file.
    Only sets variables that aren't already in the environment.
    """
    for directory in [Path.cwd()] + list(Path.cwd().parents):
        env_file = directory / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and key not in os.environ:
                            os.environ[key] = value
            break


# Auto-load .env file on module import
load_dotenv()


# ============================================================================
# Common Exceptions
# ============================================================================


class ProviderError(Exception):
    """Base exception for provider errors."""

    pass


class AuthenticationError(ProviderError):
    """Authentication failed."""

    pass


class NotFoundError(ProviderError):
    """Resource not found."""

    pass


class RateLimitError(ProviderError):
    """Rate limit exceeded."""

    pass


# ============================================================================
# Base Provider Interface
# ============================================================================


class BaseProvider(ABC):
    """Abstract base class for observability providers.

    All provider implementations should inherit from this class and
    implement the required methods.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name (e.g., 'aiobs', 'langfuse')."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the provider client and release resources."""
        pass

    def __enter__(self) -> BaseProvider:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
