# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Retrieve unmasked connection secrets via vendored connection-retriever.

This module provides a focused utility for enriching connection config with
unmasked secrets from the vendored connection-retriever code. It is designed
to work alongside the existing connection_fetcher module, which handles all
other connection data via the public Cloud API.

The secret retriever requires:
- GCP credentials with appropriate permissions
- Cloud SQL Proxy running to internal Postgres (or CI environment)

Usage:
    from airbyte_ops_mcp.live_tests.connection_fetcher import fetch_connection_data
    from airbyte_ops_mcp.live_tests.connection_secret_retriever import (
        enrich_config_with_secrets,
        should_use_secret_retriever,
    )

    # Fetch connection data via public API (config will have masked secrets)
    connection_data = fetch_connection_data(connection_id)

    # Enrich with unmasked secrets if enabled
    if should_use_secret_retriever():
        connection_data = enrich_config_with_secrets(
            connection_data,
            retrieval_reason="MCP live test",
        )
"""

from __future__ import annotations

import logging
import os
from dataclasses import replace
from typing import TYPE_CHECKING

from airbyte_ops_mcp.live_tests._connection_retriever import (
    ConnectionObject,
    retrieve_objects,
)

if TYPE_CHECKING:
    from airbyte_ops_mcp.live_tests.connection_fetcher import ConnectionData

logger = logging.getLogger(__name__)

# Environment variable to enable secret retrieval
ENV_USE_SECRET_RETRIEVER = "USE_CONNECTION_SECRET_RETRIEVER"

# GCP credential environment variables
ENV_GOOGLE_APPLICATION_CREDENTIALS = "GOOGLE_APPLICATION_CREDENTIALS"
ENV_GCP_PROD_DB_ACCESS_CREDENTIALS = "GCP_PROD_DB_ACCESS_CREDENTIALS"


def _ensure_gcp_credentials_env() -> None:
    """Ensure GCP credentials are available via standard env var.

    If GOOGLE_APPLICATION_CREDENTIALS is not set but GCP_PROD_DB_ACCESS_CREDENTIALS is,
    copy the value to GOOGLE_APPLICATION_CREDENTIALS. This provides a fallback
    for internal employees who use GCP_PROD_DB_ACCESS_CREDENTIALS as their standard
    credential path for prod database access.

    This function is idempotent and safe to call multiple times.
    """
    if ENV_GOOGLE_APPLICATION_CREDENTIALS not in os.environ:
        gsm_creds = os.getenv(ENV_GCP_PROD_DB_ACCESS_CREDENTIALS)
        if gsm_creds:
            os.environ[ENV_GOOGLE_APPLICATION_CREDENTIALS] = gsm_creds
            logger.debug(
                f"Using {ENV_GCP_PROD_DB_ACCESS_CREDENTIALS} as fallback for "
                f"{ENV_GOOGLE_APPLICATION_CREDENTIALS}"
            )


def is_secret_retriever_enabled() -> bool:
    """Check if secret retrieval is enabled via environment variable.

    Returns:
        True if USE_CONNECTION_SECRET_RETRIEVER is set to a truthy value.
    """
    value = os.getenv(ENV_USE_SECRET_RETRIEVER, "").lower()
    return value in ("true", "1", "yes")


def should_use_secret_retriever() -> bool:
    """Check if secret retrieval should be used.

    Returns:
        True if USE_CONNECTION_SECRET_RETRIEVER env var is set to a truthy value.
    """
    return is_secret_retriever_enabled()


def retrieve_unmasked_config(
    connection_id: str,
    retrieval_reason: str = "MCP live tests",
) -> dict | None:
    """Retrieve unmasked source config from vendored connection-retriever.

    This function directly queries the internal Postgres database to get
    the source configuration with unmasked secrets.

    Args:
        connection_id: The Airbyte Cloud connection ID.
        retrieval_reason: Reason for retrieval (for audit logging).

    Returns:
        The unmasked source config dict, or None if retrieval fails.
    """
    # Ensure GCP credentials are available (supports GCP_PROD_DB_ACCESS_CREDENTIALS fallback)
    _ensure_gcp_credentials_env()

    # Only request the source config - that's all we need for secrets
    requested_objects = [ConnectionObject.SOURCE_CONFIG]

    candidates = retrieve_objects(
        connection_objects=requested_objects,
        retrieval_reason=retrieval_reason,
        connection_id=connection_id,
    )

    if not candidates:
        logger.warning(
            f"No connection data found for connection ID {connection_id} "
            "via connection-retriever"
        )
        return None

    candidate = candidates[0]
    if candidate.source_config:
        return dict(candidate.source_config)

    return None


def enrich_config_with_secrets(
    connection_data: ConnectionData,
    retrieval_reason: str = "MCP live tests",
) -> ConnectionData:
    """Enrich connection data with unmasked secrets from internal retriever.

    This function takes a ConnectionData object (typically from the public
    Cloud API with masked secrets) and replaces the config with unmasked
    secrets from the internal connection-retriever.

    Args:
        connection_data: The connection data to enrich.
        retrieval_reason: Reason for retrieval (for audit logging).

    Returns:
        A new ConnectionData with unmasked config, or the original if
        retrieval fails or is not available.
    """
    unmasked_config = retrieve_unmasked_config(
        connection_id=connection_data.connection_id,
        retrieval_reason=retrieval_reason,
    )

    if unmasked_config is None:
        logger.info(
            f"Could not retrieve unmasked config for {connection_data.connection_id}, "
            "using masked config from Cloud API"
        )
        return connection_data

    logger.info(
        f"Successfully enriched config with unmasked secrets for "
        f"{connection_data.connection_id}"
    )

    # Return a new ConnectionData with the unmasked config
    return replace(connection_data, config=unmasked_config)
