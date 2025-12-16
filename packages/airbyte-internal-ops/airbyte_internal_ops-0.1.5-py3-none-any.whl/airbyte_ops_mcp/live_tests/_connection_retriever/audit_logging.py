# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Audit logging for vendored connection-retriever.

Vendored from: airbyte-platform-internal/tools/connection-retriever/src/connection_retriever/audit_logging.py
"""

from __future__ import annotations

import logging
import subprocess
from typing import TYPE_CHECKING, Any, Callable

from google.cloud import logging as gcloud_logging

from airbyte_ops_mcp.live_tests._connection_retriever.consts import (
    GCP_PROJECT_NAME,
)

if TYPE_CHECKING:
    from airbyte_ops_mcp.live_tests._connection_retriever.retrieval import (
        RetrievalMetadata,
    )

LOGGER = logging.getLogger(__name__)

# Lazy-initialized to avoid import-time GCP calls
_logging_client: gcloud_logging.Client | None = None
_airbyte_gcloud_logger: Any = None


def _get_logger() -> Any:
    """Get the GCP Cloud Logger, initializing lazily on first use."""
    global _logging_client, _airbyte_gcloud_logger

    if _airbyte_gcloud_logger is not None:
        return _airbyte_gcloud_logger

    _logging_client = gcloud_logging.Client(project=GCP_PROJECT_NAME)
    _airbyte_gcloud_logger = _logging_client.logger(
        "airbyte-cloud-connection-retriever"
    )
    return _airbyte_gcloud_logger


def get_user_email() -> str:
    """Get the email of the currently authenticated GCP user."""
    # This is a bit hacky - should use service account impersonation
    # https://cloud.google.com/iam/docs/impersonating-service-accounts
    command = [
        "gcloud",
        "auth",
        "list",
        "--filter=status:ACTIVE",
        "--format=value(account)",
    ]
    output = subprocess.run(command, capture_output=True, text=True, check=True)
    return output.stdout.strip()


def get_audit_log_message(
    retrieval_metadata: RetrievalMetadata,
) -> dict:
    """Build an audit log message for a retrieval operation."""
    user_email = get_user_email()
    return {
        "message": (
            f"{user_email} is accessing {retrieval_metadata.connection_object.value} "
            f"for connection_id {retrieval_metadata.connection_id} "
            f"for {retrieval_metadata.retrieval_reason}"
        ),
        "retrieval_reason": retrieval_metadata.retrieval_reason,
        "connection_object_type": retrieval_metadata.connection_object.value,
        "user": user_email,
        "connection_id": retrieval_metadata.connection_id,
    }


def audit(function_to_audit: Callable) -> Callable:
    """Decorator to audit function calls to GCP Cloud Logging."""

    def wrapper(
        retrieval_metadata: RetrievalMetadata, *args: Any, **kwargs: Any
    ) -> Callable:
        audit_log_message = get_audit_log_message(retrieval_metadata)
        _get_logger().log_struct(audit_log_message)
        return function_to_audit(*args, **kwargs)

    return wrapper
