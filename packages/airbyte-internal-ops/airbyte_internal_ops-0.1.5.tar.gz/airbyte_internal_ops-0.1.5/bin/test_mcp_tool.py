#!/usr/bin/env python3
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""One-liner CLI tool for testing airbyte-ops-mcp MCP tools directly with JSON arguments.

Usage:
    poe mcp-tool-test <tool_name> '<json_args>'

Examples:
    poe mcp-tool-test publish_connector_to_airbyte_registry \
        '{"connector_name": "destination-pinecone", "pr_number": 70202}'
    poe mcp-tool-test check_workflow_status \
        '{"workflow_url": "https://github.com/airbytehq/airbyte/actions/runs/12345"}'
    poe mcp-tool-test get_docker_image_info \
        '{"image": "airbyte/destination-pinecone", "tag": "0.1.0-dev.abc1234567"}'
"""

import asyncio
import json
import sys
import traceback
from typing import Any

from fastmcp import Client

from airbyte_ops_mcp.mcp.server import app

MIN_ARGS = 3


async def call_mcp_tool(tool_name: str, args: dict[str, Any]) -> object:
    """Call an MCP tool using the FastMCP client."""
    async with Client(app) as client:
        return await client.call_tool(tool_name, args)


def main() -> None:
    """Main entry point for the MCP tool tester."""
    if len(sys.argv) < MIN_ARGS:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    tool_name = sys.argv[1]
    json_args = sys.argv[2]

    try:
        args: dict[str, Any] = json.loads(json_args)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON arguments: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        result = asyncio.run(call_mcp_tool(tool_name, args))

        if hasattr(result, "text"):
            print(result.text)
        else:
            print(str(result))

    except Exception as e:
        print(f"Error executing tool '{tool_name}': {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
