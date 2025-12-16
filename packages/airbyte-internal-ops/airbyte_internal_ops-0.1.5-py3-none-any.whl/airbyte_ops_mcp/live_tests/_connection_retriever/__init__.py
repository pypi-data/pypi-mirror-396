# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Vendored subset of connection-retriever from airbyte-platform-internal.

This module contains a minimal subset of the connection-retriever tool,
vendored to avoid depending on an unpublished internal package. It provides
functionality to retrieve unmasked source configuration from Airbyte Cloud's
internal database.

Original source: airbyte-platform-internal/tools/connection-retriever
Vendored: 2025-01-XX

Only the following functionality is included:
- Retrieve unmasked source config for a given connection ID
- Secret resolution from GCP Secret Manager
- Audit logging to GCP Cloud Logging

NOT included (see issue #91 for future work):
- retrieve_testing_candidates() - BigQuery-based candidate discovery
- Destination config retrieval
- CLI interface
"""

from airbyte_ops_mcp.live_tests._connection_retriever.consts import (
    ConnectionObject,
)
from airbyte_ops_mcp.live_tests._connection_retriever.retrieval import (
    TestingCandidate,
    retrieve_objects,
)

__all__ = [
    "ConnectionObject",
    "TestingCandidate",
    "retrieve_objects",
]
