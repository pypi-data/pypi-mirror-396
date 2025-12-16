# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Constants for the Airbyte Admin MCP server."""

from __future__ import annotations

MCP_SERVER_NAME = "airbyte-internal-ops"
"""The name of the MCP server."""

# Environment variable names for internal admin authentication
ENV_AIRBYTE_INTERNAL_ADMIN_FLAG = "AIRBYTE_INTERNAL_ADMIN_FLAG"
ENV_AIRBYTE_INTERNAL_ADMIN_USER = "AIRBYTE_INTERNAL_ADMIN_USER"

# Expected values for internal admin authentication
EXPECTED_ADMIN_FLAG_VALUE = "airbyte.io"
EXPECTED_ADMIN_EMAIL_DOMAIN = "@airbyte.io"
