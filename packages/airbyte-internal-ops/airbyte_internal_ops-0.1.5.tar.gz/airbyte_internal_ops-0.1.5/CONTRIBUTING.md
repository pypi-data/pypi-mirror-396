# Contributing

First clone the repo, then use something like the following MCP config.

```json
{
  "mcpServers": {
    "airbyte-ops-mcp": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--project=/Users/{my-user-id}/repos/airbyte-ops-mcp/",
        "airbyte-ops-mcp"
      ],
      "env": {
        "AIRBYTE_MCP_ENV_FILE": "/path/to/airbyte-ops-mcp/.env"
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

## Internal Secrets for Live Tests

The live tests feature can retrieve unmasked connection secrets from Airbyte Cloud's internal database. This requires:

- **GCP_PROD_DB_ACCESS_CREDENTIALS** - Access to prod Cloud SQL and Google Secret Manager for DB connection details

To test locally:

1. Set up GCP Application Default Credentials: `gcloud auth application-default login`
2. Ensure you have access to the `prod-ab-cloud-proj` project
3. Connect to Tailscale (required for private network access)

In CI, these secrets are available at the org level and a Cloud SQL Auth Proxy handles connectivity.
