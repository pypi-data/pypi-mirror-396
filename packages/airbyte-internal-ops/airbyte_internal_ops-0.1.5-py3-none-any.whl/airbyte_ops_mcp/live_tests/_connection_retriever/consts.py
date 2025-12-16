# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Constants for vendored connection-retriever.

Vendored from: airbyte-platform-internal/tools/connection-retriever/src/connection_retriever/consts.py
"""

from enum import Enum

GCP_PROJECT_NAME = "prod-ab-cloud-proj"

CLOUD_REGISTRY_URL = (
    "https://connectors.airbyte.com/files/registries/v0/cloud_registry.json"
)

CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS_SECRET_ID = (
    "projects/587336813068/secrets/CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS"
)


class ConnectionObject(Enum):
    """Types of connection objects that can be retrieved."""

    CONNECTION = "connection"
    SOURCE_ID = "source-id"
    DESTINATION_ID = "destination-id"
    DESTINATION_CONFIG = "destination-config"
    SOURCE_CONFIG = "source-config"
    CATALOG = "catalog"
    CONFIGURED_CATALOG = "configured-catalog"
    STATE = "state"
    WORKSPACE_ID = "workspace-id"
    DESTINATION_DOCKER_IMAGE = "destination-docker-image"
    SOURCE_DOCKER_IMAGE = "source-docker-image"
