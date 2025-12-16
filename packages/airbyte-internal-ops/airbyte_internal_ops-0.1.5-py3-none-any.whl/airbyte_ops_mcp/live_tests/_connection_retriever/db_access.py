# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Database access for vendored connection-retriever.

Vendored from: airbyte-platform-internal/tools/connection-retriever/src/connection_retriever/db_access.py
"""

from __future__ import annotations

import json
import os
import traceback
from typing import Any, Callable

import sqlalchemy
from google.cloud import secretmanager
from google.cloud.sql.connector import Connector
from google.cloud.sql.connector.enums import IPTypes

from airbyte_ops_mcp.live_tests._connection_retriever.consts import (
    CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS_SECRET_ID,
)
from airbyte_ops_mcp.live_tests._connection_retriever.secrets_resolution import (
    get_secret_value,
)

PG_DRIVER = "pg8000"

# Lazy-initialized to avoid import-time GCP auth
_connector: Connector | None = None


def _get_connector() -> Connector:
    """Get the Cloud SQL connector, initializing lazily on first use."""
    global _connector
    if _connector is None:
        _connector = Connector()
    return _connector


def get_database_creator(pg_connection_details: dict) -> Callable:
    """Create a database connection creator function."""

    def creator() -> Any:
        return _get_connector().connect(
            pg_connection_details["database_address"],
            PG_DRIVER,
            user=pg_connection_details["pg_user"],
            password=pg_connection_details["pg_password"],
            db=pg_connection_details["database_name"],
            ip_type=IPTypes.PRIVATE,
        )

    return creator


def get_pool(
    secret_manager_client: secretmanager.SecretManagerServiceClient,
) -> sqlalchemy.Engine:
    """Get a SQLAlchemy connection pool for the Airbyte Cloud database."""
    pg_connection_details = json.loads(
        get_secret_value(
            secret_manager_client, CONNECTION_RETRIEVER_PG_CONNECTION_DETAILS_SECRET_ID
        )
    )

    if os.getenv("CI"):
        # In CI we connect via Cloud SQL Auth Proxy, running on localhost
        host = "127.0.0.1"
        try:
            return sqlalchemy.create_engine(
                f"postgresql+{PG_DRIVER}://{pg_connection_details['pg_user']}:{pg_connection_details['pg_password']}@127.0.0.1/{pg_connection_details['database_name']}",
            )
        except Exception as e:
            raise AssertionError(
                f"sqlalchemy.create_engine exception; could not connect to the proxy at {host}. "
                f"Error: {traceback.format_exception(e)}"
            ) from e
    else:
        return sqlalchemy.create_engine(
            f"postgresql+{PG_DRIVER}://",
            creator=get_database_creator(pg_connection_details),
        )
