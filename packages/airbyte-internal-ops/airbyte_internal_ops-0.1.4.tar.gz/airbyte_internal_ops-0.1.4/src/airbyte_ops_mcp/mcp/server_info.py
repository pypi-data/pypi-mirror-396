# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""MCP resources for the Airbyte Admin MCP server.

This module provides read-only resources that can be accessed by MCP clients.
"""

import importlib.metadata as md
import subprocess
from functools import lru_cache

from fastmcp import FastMCP

from airbyte_ops_mcp.constants import MCP_SERVER_NAME
from airbyte_ops_mcp.mcp._mcp_utils import (
    ToolDomain,
    mcp_resource,
    register_mcp_resources,
)


@lru_cache(maxsize=1)
def _get_version_info() -> dict[str, str | None]:
    """Get version information for the MCP server.

    Returns:
        Dictionary with version information including package version,
        git SHA, and FastMCP version
    """
    package_name = "airbyte-internal-ops"

    try:
        version = md.version(package_name)
    except md.PackageNotFoundError:
        version = "0.1.0+dev"

    try:
        fastmcp_version = md.version("fastmcp")
    except md.PackageNotFoundError:
        fastmcp_version = None

    try:
        git_sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        ).stdout.strip()
    except Exception:
        git_sha = None

    return {
        "name": package_name,
        "docs_url": "https://github.com/airbytehq/airbyte-ops-mcp",
        "release_history_url": "https://github.com/airbytehq/airbyte-ops-mcp/releases",
        "version": version,
        "git_sha": git_sha,
        "fastmcp_version": fastmcp_version,
        "domains": ["registry", "metadata", "qa", "insights", "repo"],
    }


@mcp_resource(
    uri=f"{MCP_SERVER_NAME}://server/info",
    description="Server information for the Airbyte Admin MCP server",
    mime_type="application/json",
    domain=ToolDomain.SERVER_INFO,
)
def mcp_server_info() -> dict[str, str | None]:
    """Resource that returns information for the MCP server.

    This includes package version, release history, help URLs, as well as other information.

    Returns:
        Dictionary with version information
    """
    return _get_version_info()


def register_server_info_resources(app: FastMCP) -> None:
    """Register server info resources with the FastMCP app.

    Args:
        app: FastMCP application instance
    """
    register_mcp_resources(app, domain=ToolDomain.SERVER_INFO)
