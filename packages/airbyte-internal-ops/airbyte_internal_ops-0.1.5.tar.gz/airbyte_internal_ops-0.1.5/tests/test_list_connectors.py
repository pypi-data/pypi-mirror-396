# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Unit tests for the list_connectors module."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import pytest

from airbyte_ops_mcp.airbyte_repo.list_connectors import (
    CONNECTOR_PATH_PREFIX,
    get_connector_metadata,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    "metadata_yaml_content,expected_result",
    [
        pytest.param(
            """data:
  name: source-faker
  supportLevel: certified
  dockerImageTag: "1.0.0"
""",
            {
                "name": "source-faker",
                "supportLevel": "certified",
                "dockerImageTag": "1.0.0",
            },
            id="basic_metadata",
        ),
        pytest.param(
            """data:
  name: source-postgres
  supportLevel: community
  dockerImageTag: "2.1.0"
  ab_internal:
    ql: 200
    sl: 100
""",
            {
                "name": "source-postgres",
                "supportLevel": "community",
                "dockerImageTag": "2.1.0",
                "ab_internal": {"ql": 200, "sl": 100},
            },
            id="metadata_with_ab_internal",
        ),
        pytest.param(
            """data:
  name: destination-s3
  supportLevel: certified
  dockerImageTag: "0.5.0"
  connectorSubtype: file
  connectorType: destination
""",
            {
                "name": "destination-s3",
                "supportLevel": "certified",
                "dockerImageTag": "0.5.0",
                "connectorSubtype": "file",
                "connectorType": "destination",
            },
            id="destination_connector",
        ),
        pytest.param(
            """data:
  name: source-empty
""",
            {"name": "source-empty"},
            id="minimal_metadata",
        ),
        pytest.param(
            """data:
  name: source-complex
  supportLevel: certified
  dockerImageTag: "1.2.3"
  releases:
    breakingChanges:
      1.0.0:
        message: "Breaking change"
        upgradeDeadline: "2025-01-01"
""",
            {
                "name": "source-complex",
                "supportLevel": "certified",
                "dockerImageTag": "1.2.3",
                "releases": {
                    "breakingChanges": {
                        "1.0.0": {
                            "message": "Breaking change",
                            "upgradeDeadline": "2025-01-01",
                        }
                    }
                },
            },
            id="metadata_with_releases",
        ),
        pytest.param(
            """data:
  name: source-with-tags
  supportLevel: community
  dockerImageTag: "0.1.0"
  tags:
    - database
    - sql
    - postgres
""",
            {
                "name": "source-with-tags",
                "supportLevel": "community",
                "dockerImageTag": "0.1.0",
                "tags": ["database", "sql", "postgres"],
            },
            id="metadata_with_list_field",
        ),
        pytest.param(
            """data:
  name: source-archived
  supportLevel: archived
  dockerImageTag: "0.0.1"
""",
            {
                "name": "source-archived",
                "supportLevel": "archived",
                "dockerImageTag": "0.0.1",
            },
            id="archived_connector",
        ),
        pytest.param(
            """data: {}
""",
            {},
            id="empty_data_section",
        ),
    ],
)
def test_get_connector_metadata(
    metadata_yaml_content: str,
    expected_result: dict[str, Any],
) -> None:
    """Test get_connector_metadata with various metadata.yaml contents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        connector_name = "source-test"
        connector_dir = Path(tmpdir) / CONNECTOR_PATH_PREFIX / connector_name
        connector_dir.mkdir(parents=True)

        (connector_dir / "metadata.yaml").write_text(metadata_yaml_content)

        result = get_connector_metadata(tmpdir, connector_name)
        assert result == expected_result


@pytest.mark.unit
def test_get_connector_metadata_no_file() -> None:
    """Test get_connector_metadata returns None when metadata.yaml doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        connector_name = "source-nonexistent"
        connector_dir = Path(tmpdir) / CONNECTOR_PATH_PREFIX / connector_name
        connector_dir.mkdir(parents=True)

        result = get_connector_metadata(tmpdir, connector_name)
        assert result is None


@pytest.mark.unit
def test_get_connector_metadata_connector_not_found() -> None:
    """Test get_connector_metadata returns None when connector directory doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = get_connector_metadata(tmpdir, "source-nonexistent")
        assert result is None


@pytest.mark.unit
def test_get_connector_metadata_invalid_yaml() -> None:
    """Test get_connector_metadata returns None for invalid YAML."""
    with tempfile.TemporaryDirectory() as tmpdir:
        connector_name = "source-invalid"
        connector_dir = Path(tmpdir) / CONNECTOR_PATH_PREFIX / connector_name
        connector_dir.mkdir(parents=True)

        # Write invalid YAML
        (connector_dir / "metadata.yaml").write_text("data: [invalid: yaml: content")

        result = get_connector_metadata(tmpdir, connector_name)
        assert result is None


@pytest.mark.unit
def test_get_connector_metadata_no_data_key() -> None:
    """Test get_connector_metadata returns empty dict when 'data' key is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        connector_name = "source-no-data"
        connector_dir = Path(tmpdir) / CONNECTOR_PATH_PREFIX / connector_name
        connector_dir.mkdir(parents=True)

        (connector_dir / "metadata.yaml").write_text("other_key: value\n")

        result = get_connector_metadata(tmpdir, connector_name)
        assert result == {}
