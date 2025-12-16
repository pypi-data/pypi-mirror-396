# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""MCP tools for cloud connector version management.

This module provides MCP tools for viewing and managing connector version
overrides (pins) in Airbyte Cloud. These tools enable admins to pin connectors
to specific versions for troubleshooting or stability purposes.

Uses PyAirbyte's CloudWorkspace, CloudSource, and CloudDestination classes
for all cloud operations.
"""

from __future__ import annotations

from typing import Annotated, Literal

from airbyte import constants
from airbyte.cloud import CloudWorkspace
from airbyte.cloud.auth import (
    resolve_cloud_client_id,
    resolve_cloud_client_secret,
)
from airbyte.exceptions import PyAirbyteInputError
from fastmcp import FastMCP
from pydantic import Field

from airbyte_ops_mcp.cloud_admin import api_client
from airbyte_ops_mcp.cloud_admin.auth import (
    CloudAuthError,
    get_admin_user_email,
    require_internal_admin,
)
from airbyte_ops_mcp.cloud_admin.models import (
    ConnectorVersionInfo,
    VersionOverrideOperationResult,
)
from airbyte_ops_mcp.mcp._mcp_utils import ToolDomain, mcp_tool, register_mcp_tools


def _get_workspace(workspace_id: str) -> CloudWorkspace:
    """Get a CloudWorkspace instance for the specified workspace.

    Args:
        workspace_id: The Airbyte Cloud workspace ID (required).

    Returns:
        CloudWorkspace instance configured for the specified workspace.

    Raises:
        CloudAuthError: If required environment variables are not set.
    """
    try:
        return CloudWorkspace(
            workspace_id=workspace_id,
            client_id=resolve_cloud_client_id(),
            client_secret=resolve_cloud_client_secret(),
            api_root=constants.CLOUD_API_ROOT,  # Used for workspace operations
        )
    except Exception as e:
        raise CloudAuthError(
            f"Failed to initialize CloudWorkspace. Ensure AIRBYTE_CLIENT_ID "
            f"and AIRBYTE_CLIENT_SECRET are set. Error: {e}"
        ) from e


@mcp_tool(
    ToolDomain.CLOUD_ADMIN,
    read_only=True,
    idempotent=True,
    open_world=True,
)
def get_cloud_connector_version(
    workspace_id: Annotated[
        str,
        Field(description="The Airbyte Cloud workspace ID."),
    ],
    actor_id: Annotated[
        str, "The ID of the deployed connector (source or destination)"
    ],
    actor_type: Annotated[
        Literal["source", "destination"],
        "The type of connector (source or destination)",
    ],
) -> ConnectorVersionInfo:
    """Get the current version information for a deployed connector.

    Returns version details including the current version string and whether
    an override (pin) is applied.

    The `AIRBYTE_CLIENT_ID`, `AIRBYTE_CLIENT_SECRET`, and `AIRBYTE_API_ROOT`
    environment variables will be used to authenticate with the Airbyte Cloud API.
    """
    try:
        workspace = _get_workspace(workspace_id)

        # Use vendored API client instead of connector.get_connector_version()
        # Use Config API root for version management operations
        version_data = api_client.get_connector_version(
            connector_id=actor_id,
            connector_type=actor_type,
            api_root=constants.CLOUD_CONFIG_API_ROOT,  # Use Config API, not public API
            client_id=workspace.client_id,
            client_secret=workspace.client_secret,
        )

        return ConnectorVersionInfo(
            connector_id=actor_id,
            connector_type=actor_type,
            version=version_data["dockerImageTag"],
            is_version_pinned=version_data["isVersionOverrideApplied"],
        )
    except CloudAuthError:
        raise
    except Exception as e:
        raise CloudAuthError(
            f"Failed to get connector version for {actor_type} {actor_id}: {e}"
        ) from e


@mcp_tool(
    ToolDomain.CLOUD_ADMIN,
    destructive=True,
    idempotent=False,
    open_world=True,
)
def set_cloud_connector_version_override(
    workspace_id: Annotated[
        str,
        Field(description="The Airbyte Cloud workspace ID."),
    ],
    actor_id: Annotated[
        str, "The ID of the deployed connector (source or destination)"
    ],
    actor_type: Annotated[
        Literal["source", "destination"],
        "The type of connector (source or destination)",
    ],
    version: Annotated[
        str | None,
        Field(
            description="The semver version string to pin to (e.g., '0.1.0'). "
            "Must be None if unset is True.",
            default=None,
        ),
    ],
    unset: Annotated[
        bool,
        Field(
            description="If True, removes any existing version override. "
            "Cannot be True if version is provided.",
            default=False,
        ),
    ],
    override_reason: Annotated[
        str | None,
        Field(
            description="Required when setting a version. "
            "Explanation for the override (min 10 characters).",
            default=None,
        ),
    ],
    override_reason_reference_url: Annotated[
        str | None,
        Field(
            description="Optional URL with more context (e.g., issue link).",
            default=None,
        ),
    ],
) -> VersionOverrideOperationResult:
    """Set or clear a version override for a deployed connector.

    **Admin-only operation** - Requires AIRBYTE_INTERNAL_ADMIN_FLAG=airbyte.io
    and AIRBYTE_INTERNAL_ADMIN_USER environment variables.

    You must specify EXACTLY ONE of `version` OR `unset=True`, but not both.
    When setting a version, `override_reason` is required.

    Business rules enforced:
    - Dev versions (-dev): Only creator can unpin their own dev version override
    - Production versions: Require strong justification mentioning customer/support/investigation
    - Release candidates (-rc): Any admin can pin/unpin RC versions

    The `AIRBYTE_CLIENT_ID`, `AIRBYTE_CLIENT_SECRET`, and `AIRBYTE_API_ROOT`
    environment variables will be used to authenticate with the Airbyte Cloud API.
    """
    # Validate admin access
    try:
        require_internal_admin()
        user_email = get_admin_user_email()
    except CloudAuthError as e:
        return VersionOverrideOperationResult(
            success=False,
            message=f"Admin authentication failed: {e}",
            connector_id=actor_id,
            connector_type=actor_type,
        )

    # Get workspace and current version info
    try:
        workspace = _get_workspace(workspace_id)

        # Get current version info before the operation
        current_version_data = api_client.get_connector_version(
            connector_id=actor_id,
            connector_type=actor_type,
            api_root=constants.CLOUD_CONFIG_API_ROOT,  # Use Config API
            client_id=workspace.client_id,
            client_secret=workspace.client_secret,
        )
        current_version = current_version_data["dockerImageTag"]
        was_pinned_before = current_version_data["isVersionOverrideApplied"]

    except CloudAuthError as e:
        return VersionOverrideOperationResult(
            success=False,
            message=f"Failed to initialize workspace or connector: {e}",
            connector_id=actor_id,
            connector_type=actor_type,
        )
    except Exception as e:
        return VersionOverrideOperationResult(
            success=False,
            message=f"Failed to get connector: {e}",
            connector_id=actor_id,
            connector_type=actor_type,
        )

    # Call vendored API client's set_connector_version_override method
    try:
        result = api_client.set_connector_version_override(
            connector_id=actor_id,
            connector_type=actor_type,
            api_root=constants.CLOUD_CONFIG_API_ROOT,  # Use Config API
            client_id=workspace.client_id,
            client_secret=workspace.client_secret,
            workspace_id=workspace_id,
            version=version,
            unset=unset,
            override_reason=override_reason,
            override_reason_reference_url=override_reason_reference_url,
            user_email=user_email,
        )

        # Get updated version info after the operation
        updated_version_data = api_client.get_connector_version(
            connector_id=actor_id,
            connector_type=actor_type,
            api_root=constants.CLOUD_CONFIG_API_ROOT,  # Use Config API
            client_id=workspace.client_id,
            client_secret=workspace.client_secret,
        )
        new_version = updated_version_data["dockerImageTag"] if not unset else None
        is_pinned_after = updated_version_data["isVersionOverrideApplied"]

        if unset:
            if result:
                message = "Successfully cleared version override. Connector will now use default version."
            else:
                message = "No version override was active (nothing to clear)"
        else:
            message = f"Successfully pinned connector to version {version}"

        return VersionOverrideOperationResult(
            success=True,
            message=message,
            connector_id=actor_id,
            connector_type=actor_type,
            previous_version=current_version,
            new_version=new_version,
            was_pinned_before=was_pinned_before,
            is_pinned_after=is_pinned_after,
        )

    except PyAirbyteInputError as e:
        # PyAirbyte raises this for validation errors and permission denials
        return VersionOverrideOperationResult(
            success=False,
            message=str(e),
            connector_id=actor_id,
            connector_type=actor_type,
            previous_version=current_version,
            was_pinned_before=was_pinned_before,
        )
    except Exception as e:
        return VersionOverrideOperationResult(
            success=False,
            message=f"Failed to {'clear' if unset else 'set'} version override: {e}",
            connector_id=actor_id,
            connector_type=actor_type,
            previous_version=current_version,
            was_pinned_before=was_pinned_before,
        )


def register_cloud_connector_version_tools(app: FastMCP) -> None:
    """Register cloud connector version management tools with the FastMCP app.

    Args:
        app: FastMCP application instance
    """
    register_mcp_tools(app, domain=ToolDomain.CLOUD_ADMIN)
