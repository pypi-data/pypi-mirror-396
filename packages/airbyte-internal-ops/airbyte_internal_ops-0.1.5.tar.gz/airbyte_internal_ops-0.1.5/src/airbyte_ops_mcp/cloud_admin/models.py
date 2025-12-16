# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Pydantic models for cloud connector version operations.

This module defines the data models used for connector version management
and pinning operations in Airbyte Cloud.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ConnectorVersionInfo(BaseModel):
    """Information about a cloud connector's version.

    This model represents the current version state of a deployed connector,
    including whether a version override (pin) is active.
    """

    connector_id: str = Field(description="The ID of the deployed connector")
    connector_type: Literal["source", "destination"] = Field(
        description="The type of connector (source or destination)"
    )
    version: str = Field(description="The current version string (e.g., '0.1.0')")
    is_version_pinned: bool = Field(
        description="Whether a version override is active for this connector"
    )

    def __str__(self) -> str:
        """Return a string representation of the version."""
        pinned_suffix = " (pinned)" if self.is_version_pinned else ""
        return (
            f"{self.connector_type} {self.connector_id}: {self.version}{pinned_suffix}"
        )


class VersionOverrideOperationResult(BaseModel):
    """Result of a version override operation (set or clear).

    This model provides detailed information about the outcome of a version
    pinning or unpinning operation.
    """

    success: bool = Field(description="Whether the operation succeeded")
    message: str = Field(description="Human-readable message describing the result")
    connector_id: str = Field(description="The ID of the connector that was modified")
    connector_type: Literal["source", "destination"] = Field(
        description="The type of connector (source or destination)"
    )
    previous_version: str | None = Field(
        default=None,
        description="The version before the operation (None if not available)",
    )
    new_version: str | None = Field(
        default=None,
        description="The version after the operation (None if cleared or failed)",
    )
    was_pinned_before: bool | None = Field(
        default=None,
        description="Whether a pin was active before the operation",
    )
    is_pinned_after: bool | None = Field(
        default=None,
        description="Whether a pin is active after the operation",
    )

    def __str__(self) -> str:
        """Return a string representation of the operation result."""
        if self.success:
            return f"✓ {self.message}"
        return f"✗ {self.message}"
