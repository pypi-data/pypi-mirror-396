# airbyte-ops-mcp

MCP and API interfaces that let the agents do the admin work.

## Installing Ops MCP in your Client

This config example will help you add the MCP server to your client:

```json
{
  "mcpServers": {
    "airbyte-ops-mcp": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--project=/Users/aj.steers/repos/airbyte-ops-mcp/",
        "airbyte-ops-mcp"
      ],
      "env": {
        "AIRBYTE_MCP_ENV_FILE": "/Users/{user-id}/.mcp/airbyte_mcp.env"
      }
    },
    "airbyte-coral-mcp": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--python=3.11",
        "--from=airbyte@latest",
        "airbyte-mcp"
      ],
      "env": {
        "AIRBYTE_MCP_ENV_FILE": "/Users/{user-id}/.mcp/airbyte_mcp.env"
      }
    }
  }
}
```

Your `.env` file should include the following values:

```ini
# Creds for Airbyte Cloud OAuth
AIRBYTE_CLOUD_CLIENT_ID="..."
AIRBYTE_CLOUD_CLIENT_SECRET="..."

# Required for elevated admin operations
AIRBYTE_INTERNAL_ADMIN_FLAG=airbyte.io
AIRBYTE_INTERNAL_ADMIN_USER={my-id}@airbyte.io

# Workspace ID for Testing
AIRBYTE_CLOUD_TEST_WORKSPACE_ID="..."
```

## Getting Started

Once configured, use the `test_my_tools` prompt by typing "/test" into your agent and selecting the auto-complete option for the `test_my_tools` prompt.

This prompt will step through all the tools, demoing their capabilities.
