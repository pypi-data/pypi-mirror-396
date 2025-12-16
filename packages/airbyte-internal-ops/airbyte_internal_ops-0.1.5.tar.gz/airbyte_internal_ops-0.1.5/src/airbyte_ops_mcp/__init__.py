"""Airbyte Admin MCP - MCP and API interfaces that let the agents do the admin work."""

__version__ = "0.1.0"


def hello() -> str:
    """Return a friendly greeting."""
    return "Hello from airbyte-internal-ops!"


def get_version() -> str:
    """Return the current version."""
    return __version__


__all__ = ["__version__", "get_version", "hello"]
