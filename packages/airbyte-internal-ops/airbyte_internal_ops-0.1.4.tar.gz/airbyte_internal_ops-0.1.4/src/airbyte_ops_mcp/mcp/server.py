# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Airbyte Admin MCP server implementation.

This module provides the main MCP server for Airbyte admin operations.
"""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP

from airbyte_ops_mcp.constants import MCP_SERVER_NAME
from airbyte_ops_mcp.mcp.cloud_connector_versions import (
    register_cloud_connector_version_tools,
)
from airbyte_ops_mcp.mcp.github import register_github_tools
from airbyte_ops_mcp.mcp.github_repo_ops import register_github_repo_ops_tools
from airbyte_ops_mcp.mcp.live_tests import register_live_tests_tools
from airbyte_ops_mcp.mcp.prerelease import register_prerelease_tools
from airbyte_ops_mcp.mcp.prompts import register_prompts
from airbyte_ops_mcp.mcp.server_info import register_server_info_resources

app: FastMCP = FastMCP(MCP_SERVER_NAME)


def register_server_assets(app: FastMCP) -> None:
    """Register all server assets (tools, prompts, resources) with the FastMCP app.

    This function registers assets for all domains:
    - SERVER_INFO: Server version and information resources
    - REPO: GitHub repository operations
    - CLOUD: Cloud connector version management
    - PROMPTS: Prompt templates for common workflows
    - LIVE_TESTS: Live connection validation and regression tests
    - REGISTRY: Connector registry operations (future)
    - METADATA: Connector metadata operations (future)
    - QA: Connector quality assurance (future)
    - INSIGHTS: Connector analysis and insights (future)

    Args:
        app: FastMCP application instance
    """
    register_server_info_resources(app)
    register_github_repo_ops_tools(app)
    register_github_tools(app)
    register_prerelease_tools(app)
    register_cloud_connector_version_tools(app)
    register_prompts(app)
    register_live_tests_tools(app)


register_server_assets(app)


def main() -> None:
    """Main entry point for the Airbyte Admin MCP server."""
    # Load environment variables from .env file in current working directory
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded environment from: {env_file}", flush=True, file=sys.stderr)

    print("=" * 60, flush=True, file=sys.stderr)
    print("Starting Airbyte Admin MCP server.", file=sys.stderr)
    try:
        asyncio.run(app.run_stdio_async(show_banner=False))
    except KeyboardInterrupt:
        print("Airbyte Admin MCP server interrupted by user.", file=sys.stderr)
    except Exception as ex:
        print(f"Error running Airbyte Admin MCP server: {ex}", file=sys.stderr)
        sys.exit(1)

    print("Airbyte Admin MCP server stopped.", file=sys.stderr)
    print("=" * 60, flush=True, file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
