# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Low-level API client for Airbyte Cloud operations.

This module provides direct HTTP access to Airbyte Cloud APIs that are not
yet available in PyAirbyte. This is vendored functionality from PyAirbyte PR #838.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

import requests
from airbyte import constants
from airbyte.exceptions import PyAirbyteInputError

# Internal enums for scoped configuration API "magic strings"
# These values caused issues during development and are now centralized here


class _ScopedConfigKey(str, Enum):
    """Configuration keys used in scoped configuration API."""

    CONNECTOR_VERSION = "connector_version"


class _ResourceType(str, Enum):
    """Resource types for scoped configuration."""

    ACTOR_DEFINITION = "actor_definition"
    WORKSPACE = "workspace"
    ORGANIZATION = "organization"


class _ScopeType(str, Enum):
    """Scope types for scoped configuration."""

    ACTOR = "actor"
    WORKSPACE = "workspace"
    ORGANIZATION = "organization"


class _OriginType(str, Enum):
    """Origin types for scoped configuration."""

    USER = "user"
    SYSTEM = "system"


def _get_access_token(
    client_id: str,
    client_secret: str,
) -> str:
    """Get an access token for Airbyte Cloud API.

    Args:
        client_id: The Airbyte Cloud client ID
        client_secret: The Airbyte Cloud client secret

    Returns:
        Access token string

    Raises:
        PyAirbyteInputError: If authentication fails
    """
    # Always authenticate via the public API endpoint
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
            message=f"Failed to authenticate with Airbyte Cloud: {response.status_code} {response.text}",
            context={
                "status_code": response.status_code,
                "response": response.text,
            },
        )

    data = response.json()
    return data["access_token"]


def get_user_id_by_email(
    email: str,
    api_root: str,
    client_id: str,
    client_secret: str,
) -> str:
    """Get user ID from email address.

    Args:
        email: The user's email address
        api_root: The API root URL
        client_id: The Airbyte Cloud client ID
        client_secret: The Airbyte Cloud client secret

    Returns:
        User ID (UUID string)

    Raises:
        PyAirbyteInputError: If user not found or API request fails
    """
    access_token = _get_access_token(client_id, client_secret)

    endpoint = f"{api_root}/users/list_instance_admin"
    response = requests.post(
        endpoint,
        json={},
        headers={
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "PyAirbyte Client",
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise PyAirbyteInputError(
            message=f"Failed to list users: {response.status_code} {response.text}",
            context={
                "endpoint": endpoint,
                "status_code": response.status_code,
                "response": response.text,
            },
        )

    data = response.json()
    users = data.get("users", [])

    for user in users:
        if user.get("email") == email:
            return user["userId"]

    raise PyAirbyteInputError(
        message=f"No user found with email: {email}",
        context={
            "email": email,
            "available_users": len(users),
        },
    )


def resolve_connector_version_id(
    actor_definition_id: str,
    connector_type: Literal["source", "destination"],
    version: str,
    api_root: str,
    client_id: str,
    client_secret: str,
) -> str:
    """Resolve a version string to an actor_definition_version_id.

    Args:
        actor_definition_id: The actor definition ID
        connector_type: Either "source" or "destination"
        version: The version string (e.g., "0.1.47-dev.abe7cb4ddb")
        api_root: The API root URL
        client_id: The Airbyte Cloud client ID
        client_secret: The Airbyte Cloud client secret

    Returns:
        Version ID (UUID string)

    Raises:
        PyAirbyteInputError: If version cannot be resolved or API request fails
    """
    access_token = _get_access_token(client_id, client_secret)

    endpoint = f"{api_root}/actor_definition_versions/resolve"
    payload = {
        "actorDefinitionId": actor_definition_id,
        "actorType": connector_type,
        "dockerImageTag": version,
    }

    response = requests.post(
        endpoint,
        json=payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "PyAirbyte Client",
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise PyAirbyteInputError(
            message=f"Failed to resolve version: {response.status_code} {response.text}",
            context={
                "endpoint": endpoint,
                "payload": payload,
                "status_code": response.status_code,
                "response": response.text,
            },
        )

    data = response.json()
    version_id = data.get("versionId")

    if not version_id:
        raise PyAirbyteInputError(
            message=f"Could not resolve version '{version}' for connector",
            context={
                "actor_definition_id": actor_definition_id,
                "connector_type": connector_type,
                "version": version,
                "response": data,
            },
        )

    return version_id


def get_connector_version(
    connector_id: str,
    connector_type: Literal["source", "destination"],
    api_root: str,
    client_id: str,
    client_secret: str,
) -> dict[str, Any]:
    """Get version information for a deployed connector.

    Args:
        connector_id: The ID of the deployed connector (source or destination)
        connector_type: Either "source" or "destination"
        api_root: The API root URL
        client_id: The Airbyte Cloud client ID
        client_secret: The Airbyte Cloud client secret

    Returns:
        Dictionary containing:
        - dockerImageTag: The current version string
        - isVersionOverrideApplied: Boolean indicating if override is active

    Raises:
        PyAirbyteInputError: If the API request fails
    """
    access_token = _get_access_token(client_id, client_secret)

    # Determine endpoint based on connector type
    # api_root already includes /v1
    if connector_type == "source":
        endpoint = f"{api_root}/actor_definition_versions/get_for_source"
        payload = {"sourceId": connector_id}
    else:
        endpoint = f"{api_root}/actor_definition_versions/get_for_destination"
        payload = {"destinationId": connector_id}

    response = requests.post(
        endpoint,
        json=payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "PyAirbyte Client",
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    if response.status_code != 200:
        raise PyAirbyteInputError(
            message=f"Failed to get connector version: {response.status_code} {response.text}",
            context={
                "connector_id": connector_id,
                "connector_type": connector_type,
                "endpoint": endpoint,
                "payload": payload,
                "api_root": api_root,
                "status_code": response.status_code,
                "response": response.text,
            },
        )

    data = response.json()

    # Defensively check for both possible field names
    return {
        "dockerImageTag": data.get("dockerImageTag", "unknown"),
        "isVersionOverrideApplied": data.get(
            "isVersionOverrideApplied", data.get("isOverrideApplied", False)
        ),
    }


def set_connector_version_override(
    connector_id: str,
    connector_type: Literal["source", "destination"],
    api_root: str,
    client_id: str,
    client_secret: str,
    workspace_id: str,
    version: str | None = None,
    unset: bool = False,
    override_reason: str | None = None,
    override_reason_reference_url: str | None = None,
    user_email: str | None = None,
) -> bool:
    """Set or clear a version override for a deployed connector.

    Args:
        connector_id: The ID of the deployed connector
        connector_type: Either "source" or "destination"
        api_root: The API root URL
        client_id: The Airbyte Cloud client ID
        client_secret: The Airbyte Cloud client secret
        workspace_id: The workspace ID
        version: The version to pin to (e.g., "0.1.0"), or None to unset
        unset: If True, removes any existing override
        override_reason: Required when setting. Explanation for the override
        override_reason_reference_url: Optional URL with more context
        user_email: Email of user creating the override

    Returns:
        True if operation succeeded, False if no override existed (unset only)

    Raises:
        PyAirbyteInputError: If the API request fails or parameters are invalid
    """
    # Input validation
    if (version is None) == (not unset):
        raise PyAirbyteInputError(
            message="Must specify EXACTLY ONE of version (to set) OR unset=True (to clear), but not both",
        )

    if not unset and (not override_reason or len(override_reason.strip()) < 10):
        raise PyAirbyteInputError(
            message="override_reason is required when setting a version and must be at least 10 characters",
        )

    access_token = _get_access_token(client_id, client_secret)

    # Build the scoped configuration
    scope_type = _ScopeType.ACTOR

    if unset:
        # To unset, we need to delete the scoped configuration
        # First, get the actor_definition_id for the connector
        get_endpoint: str = f"{api_root}/{connector_type}s/get"
        get_payload: dict[str, str] = {f"{connector_type}Id": connector_id}
        definition_id_key = f"{connector_type}DefinitionId"

        get_response = requests.post(
            get_endpoint,
            json=get_payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "PyAirbyte Client",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        if get_response.status_code != 200:
            raise PyAirbyteInputError(
                message=f"Failed to get {connector_type} info: {get_response.status_code} {get_response.text}",
            )

        connector_info = get_response.json()
        actor_definition_id = connector_info.get(definition_id_key)

        if not actor_definition_id:
            raise PyAirbyteInputError(
                message=f"Could not find {definition_id_key} in {connector_type} info",
            )

        # Now get the scoped configuration context
        endpoint = f"{api_root}/scoped_configuration/get_context"
        context_payload = {
            "config_key": _ScopedConfigKey.CONNECTOR_VERSION,
            "resource_type": _ResourceType.ACTOR_DEFINITION,
            "resource_id": actor_definition_id,
            "scope_type": _ScopeType.ACTOR,
            "scope_id": connector_id,
        }

        response = requests.post(
            endpoint,
            json=context_payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "PyAirbyte Client",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        if response.status_code != 200:
            raise PyAirbyteInputError(
                message=f"Failed to get scoped configuration context: {response.status_code} {response.text}",
                context={
                    "endpoint": endpoint,
                    "payload": context_payload,
                    "workspace_id": workspace_id,
                    "connector_id": connector_id,
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )

        context_data = response.json()
        active_config = context_data.get("activeConfiguration")

        if not active_config:
            # No override exists, nothing to do
            return False

        # Delete the active configuration
        delete_endpoint = f"{api_root}/scoped_configuration/delete"
        delete_payload = {"scopedConfigurationId": active_config["id"]}

        response = requests.post(
            delete_endpoint,
            json=delete_payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "PyAirbyte Client",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        if response.status_code not in (200, 204):
            raise PyAirbyteInputError(
                message=f"Failed to delete version override: {response.status_code} {response.text}",
                context={
                    "delete_endpoint": delete_endpoint,
                    "config_id": active_config["id"],
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )

        return True

    else:
        # Set a new override
        # First, get the actor_definition_id for the connector
        get_endpoint = f"{api_root}/{connector_type}s/get"
        get_payload: dict[str, str] = {f"{connector_type}Id": connector_id}
        definition_id_key = f"{connector_type}DefinitionId"

        get_response = requests.post(
            get_endpoint,
            json=get_payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "PyAirbyte Client",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        if get_response.status_code != 200:
            raise PyAirbyteInputError(
                message=f"Failed to get {connector_type} info: {get_response.status_code} {get_response.text}",
            )

        connector_info = get_response.json()
        actor_definition_id = connector_info.get(definition_id_key)

        if not actor_definition_id:
            raise PyAirbyteInputError(
                message=f"Could not find {definition_id_key} in {connector_type} info",
            )

        # Resolve version string to version ID
        version_id = resolve_connector_version_id(
            actor_definition_id=actor_definition_id,
            connector_type=connector_type,
            version=version,
            api_root=api_root,
            client_id=client_id,
            client_secret=client_secret,
        )

        # Get user ID from email if provided
        origin = None
        if user_email:
            origin = get_user_id_by_email(
                email=user_email,
                api_root=api_root,
                client_id=client_id,
                client_secret=client_secret,
            )

        # Create the override with correct schema
        endpoint = f"{api_root}/scoped_configuration/create"

        payload: dict[str, Any] = {
            "config_key": _ScopedConfigKey.CONNECTOR_VERSION,
            "resource_type": _ResourceType.ACTOR_DEFINITION,
            "resource_id": actor_definition_id,
            "scope_type": scope_type,
            "scope_id": connector_id,
            "value": version_id,  # Use version ID, not version string
            "description": override_reason,
            "origin_type": _OriginType.USER,
        }

        # Add origin (user ID) if available
        if origin:
            payload["origin"] = origin

        if override_reason_reference_url:
            payload["reference_url"] = override_reason_reference_url

        response = requests.post(
            endpoint,
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "PyAirbyte Client",
                "Content-Type": "application/json",
            },
            timeout=30,
        )

        if response.status_code not in (200, 201):
            raise PyAirbyteInputError(
                message=f"Failed to set version override: {response.status_code} {response.text}",
                context={
                    "connector_id": connector_id,
                    "connector_type": connector_type,
                    "version": version,
                    "version_id": version_id,
                    "endpoint": endpoint,
                    "payload": payload,
                    "actor_definition_id": actor_definition_id,
                    "status_code": response.status_code,
                    "response": response.text,
                },
            )

        return True
