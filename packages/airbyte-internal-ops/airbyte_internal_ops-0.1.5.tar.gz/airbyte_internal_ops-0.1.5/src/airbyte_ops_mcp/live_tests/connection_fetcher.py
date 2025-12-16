# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Fetch connection configuration and catalog from Airbyte Cloud.

This module provides utilities for fetching source configuration and connection
catalog from Airbyte Cloud using the public API.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests
from airbyte import constants
from airbyte.cloud import CloudWorkspace
from airbyte.exceptions import PyAirbyteInputError


@dataclass
class ConnectionData:
    """Data fetched from an Airbyte Cloud connection."""

    connection_id: str
    source_id: str
    source_name: str
    source_definition_id: str
    config: dict[str, Any]
    catalog: dict[str, Any]
    stream_names: list[str]
    docker_repository: str | None = None
    docker_image_tag: str | None = None
    state: list[dict[str, Any]] | None = field(default=None)

    @property
    def connector_image(self) -> str | None:
        """Get the full connector image name with tag."""
        if self.docker_repository and self.docker_image_tag:
            return f"{self.docker_repository}:{self.docker_image_tag}"
        return None


def _get_access_token(
    client_id: str,
    client_secret: str,
) -> str:
    """Get an access token for Airbyte Cloud API."""
    auth_url = f"{constants.CLOUD_API_ROOT}/applications/token"
    response = requests.post(
        auth_url,
        json={
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise PyAirbyteInputError(
            message=f"Failed to authenticate with Airbyte Cloud: {response.status_code}",
            context={"response": response.text},
        )

    return response.json()["access_token"]


def fetch_connection_data(
    connection_id: str,
    client_id: str | None = None,
    client_secret: str | None = None,
) -> ConnectionData:
    """Fetch connection configuration and catalog from Airbyte Cloud.

    Args:
        connection_id: The connection ID to fetch data for.
        client_id: Airbyte Cloud client ID (defaults to env var).
        client_secret: Airbyte Cloud client secret (defaults to env var).

    Returns:
        ConnectionData with config and catalog.

    Raises:
        PyAirbyteInputError: If the API request fails.
    """
    client_id = client_id or os.getenv("AIRBYTE_CLOUD_CLIENT_ID")
    client_secret = client_secret or os.getenv("AIRBYTE_CLOUD_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise PyAirbyteInputError(
            message="Missing Airbyte Cloud credentials",
            context={
                "hint": "Set AIRBYTE_CLOUD_CLIENT_ID and AIRBYTE_CLOUD_CLIENT_SECRET env vars"
            },
        )

    access_token = _get_access_token(client_id, client_secret)
    api_root = constants.CLOUD_API_ROOT
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Get connection details
    conn_response = requests.get(
        f"{api_root}/connections/{connection_id}",
        headers=headers,
        timeout=30,
    )

    if conn_response.status_code != 200:
        raise PyAirbyteInputError(
            message=f"Failed to get connection: {conn_response.status_code}",
            context={"connection_id": connection_id, "response": conn_response.text},
        )

    conn_data = conn_response.json()
    source_id = conn_data["sourceId"]

    # Get source details (includes config)
    source_response = requests.get(
        f"{api_root}/sources/{source_id}",
        headers=headers,
        timeout=30,
    )

    if source_response.status_code != 200:
        raise PyAirbyteInputError(
            message=f"Failed to get source: {source_response.status_code}",
            context={"source_id": source_id, "response": source_response.text},
        )

    source_data = source_response.json()
    source_definition_id = source_data.get("definitionId", "")

    # Try to get docker repository and image tag from source definition version
    docker_repository = None
    docker_image_tag = None
    if source_definition_id:
        try:
            # Use the Config API to get version info for the source
            config_api_root = constants.CLOUD_CONFIG_API_ROOT
            version_response = requests.post(
                f"{config_api_root}/actor_definition_versions/get_for_source",
                json={"sourceId": source_id},
                headers=headers,
                timeout=30,
            )
            if version_response.status_code == 200:
                version_data = version_response.json()
                docker_repository = version_data.get("dockerRepository")
                docker_image_tag = version_data.get("dockerImageTag")
        except Exception:
            # Non-fatal: we can still proceed without docker info
            pass

    # Build configured catalog from connection streams
    streams_config = conn_data.get("configurations", {}).get("streams", [])
    stream_names = [s["name"] for s in streams_config]

    # Build Airbyte protocol catalog format
    catalog = _build_configured_catalog(streams_config, source_id, headers, api_root)

    return ConnectionData(
        connection_id=connection_id,
        source_id=source_id,
        source_name=source_data.get("name", ""),
        source_definition_id=source_definition_id,
        config=source_data.get("configuration", {}),
        catalog=catalog,
        stream_names=stream_names,
        docker_repository=docker_repository,
        docker_image_tag=docker_image_tag,
    )


def _build_configured_catalog(
    streams_config: list[dict[str, Any]],
    source_id: str,
    headers: dict[str, str],
    api_root: str,
) -> dict[str, Any]:
    """Build a configured catalog from connection stream configuration.

    This creates a catalog in the Airbyte protocol format that can be used
    with connector commands.
    """
    # For now, create a minimal catalog structure
    # A full implementation would fetch the source's discovered catalog
    # and merge it with the connection's stream configuration
    configured_streams = []

    for stream in streams_config:
        stream_name = stream.get("name", "")
        sync_mode = stream.get("syncMode", "full_refresh")

        # Map API sync modes to protocol sync modes
        destination_sync_mode = "append"
        if "incremental" in sync_mode.lower():
            source_sync_mode = "incremental"
        else:
            source_sync_mode = "full_refresh"

        configured_stream = {
            "stream": {
                "name": stream_name,
                "json_schema": {},  # Schema would come from discover
                "supported_sync_modes": ["full_refresh", "incremental"],
            },
            "sync_mode": source_sync_mode,
            "destination_sync_mode": destination_sync_mode,
        }

        cursor_field = stream.get("cursorField")
        if cursor_field:
            configured_stream["cursor_field"] = (
                cursor_field if isinstance(cursor_field, list) else [cursor_field]
            )

        primary_key = stream.get("primaryKey")
        if primary_key:
            configured_stream["primary_key"] = primary_key

        configured_streams.append(configured_stream)

    return {"streams": configured_streams}


def save_connection_data_to_files(
    connection_data: ConnectionData,
    output_dir: Path,
) -> tuple[Path, Path]:
    """Save connection config and catalog to JSON files.

    Args:
        connection_data: The connection data to save.
        output_dir: Directory to save files to.

    Returns:
        Tuple of (config_path, catalog_path).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    config_path = output_dir / "config.json"
    catalog_path = output_dir / "catalog.json"

    config_path.write_text(json.dumps(connection_data.config, indent=2))
    catalog_path.write_text(json.dumps(connection_data.catalog, indent=2))

    return config_path, catalog_path


def fetch_connection_artifacts(
    connection_id: str,
    workspace_id: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]] | None]:
    """Fetch catalog and state artifacts using PyAirbyte's CloudConnection.

    This uses the Config API endpoints via PyAirbyte to get the actual
    configured catalog (with full schemas) and state artifacts without
    requiring direct database access.

    Args:
        connection_id: The connection ID to fetch artifacts for.
        workspace_id: Airbyte Cloud workspace ID (defaults to env var).
        client_id: Airbyte Cloud client ID (defaults to env var).
        client_secret: Airbyte Cloud client secret (defaults to env var).

    Returns:
        Tuple of (catalog, state) where:
        - catalog: The configured catalog dict with full schemas, or None
        - state: List of state dicts for each stream, or None if no state
    """
    workspace_id = workspace_id or os.getenv("AIRBYTE_CLOUD_WORKSPACE_ID")
    client_id = client_id or os.getenv("AIRBYTE_CLOUD_CLIENT_ID")
    client_secret = client_secret or os.getenv("AIRBYTE_CLOUD_CLIENT_SECRET")

    if not workspace_id:
        raise PyAirbyteInputError(
            message="Missing Airbyte Cloud workspace ID",
            context={"hint": "Set AIRBYTE_CLOUD_WORKSPACE_ID env var"},
        )

    workspace = CloudWorkspace(
        workspace_id=workspace_id,
        client_id=client_id,
        client_secret=client_secret,
    )
    connection = workspace.get_connection(connection_id)

    catalog = connection.get_catalog_artifact()
    state = connection.get_state_artifacts()

    return catalog, state


def enrich_connection_data_with_artifacts(
    connection_data: ConnectionData,
    workspace_id: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
) -> ConnectionData:
    """Enrich ConnectionData with full catalog and state from PyAirbyte.

    This replaces the minimal catalog (with empty schemas) with the actual
    configured catalog from the Config API, and adds state artifacts.

    Args:
        connection_data: The connection data to enrich.
        workspace_id: Airbyte Cloud workspace ID (defaults to env var).
        client_id: Airbyte Cloud client ID (defaults to env var).
        client_secret: Airbyte Cloud client secret (defaults to env var).

    Returns:
        ConnectionData with enriched catalog and state.
    """
    catalog, state = fetch_connection_artifacts(
        connection_id=connection_data.connection_id,
        workspace_id=workspace_id,
        client_id=client_id,
        client_secret=client_secret,
    )

    if catalog is not None:
        # Convert syncCatalog format to ConfiguredAirbyteCatalog format
        connection_data.catalog = _convert_sync_catalog_to_configured(catalog)

    connection_data.state = state
    return connection_data


def _convert_sync_catalog_to_configured(sync_catalog: dict[str, Any]) -> dict[str, Any]:
    """Convert syncCatalog format to ConfiguredAirbyteCatalog format.

    The Config API returns syncCatalog in a slightly different format than
    the Airbyte protocol's ConfiguredAirbyteCatalog. This function converts
    between the two formats.
    """
    configured_streams = []

    for stream_config in sync_catalog.get("streams", []):
        stream_info = stream_config.get("stream", {})
        config_info = stream_config.get("config", {})

        configured_stream = {
            "stream": {
                "name": stream_info.get("name", ""),
                "json_schema": stream_info.get("jsonSchema", {}),
                "supported_sync_modes": stream_info.get("supportedSyncModes", []),
                "source_defined_cursor": stream_info.get("sourceDefinedCursor", False),
                "default_cursor_field": stream_info.get("defaultCursorField", []),
                "source_defined_primary_key": stream_info.get(
                    "sourceDefinedPrimaryKey", []
                ),
            },
            "sync_mode": config_info.get("syncMode", "full_refresh"),
            "destination_sync_mode": config_info.get("destinationSyncMode", "append"),
        }

        cursor_field = config_info.get("cursorField")
        if cursor_field:
            configured_stream["cursor_field"] = cursor_field

        primary_key = config_info.get("primaryKey")
        if primary_key:
            configured_stream["primary_key"] = primary_key

        configured_streams.append(configured_stream)

    return {"streams": configured_streams}
