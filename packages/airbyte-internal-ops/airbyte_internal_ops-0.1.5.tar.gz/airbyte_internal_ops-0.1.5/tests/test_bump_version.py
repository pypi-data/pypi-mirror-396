# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Unit tests for the bump_version module."""

from __future__ import annotations

import datetime
import tempfile
from pathlib import Path

import pytest
import semver

from airbyte_ops_mcp.airbyte_repo.bump_version import (
    BumpType,
    ChangelogEntry,
    ChangelogParsingError,
    ConnectorNotFoundError,
    InvalidVersionError,
    VersionNotFoundError,
    bump_connector_version,
    calculate_new_version,
    get_connector_path,
    get_current_version,
    parse_changelog,
    update_metadata_version,
    update_pyproject_version,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    "current_version,bump_type,new_version,expected",
    [
        pytest.param("1.0.0", BumpType.PATCH, None, "1.0.1", id="patch_bump"),
        pytest.param("1.0.0", BumpType.MINOR, None, "1.1.0", id="minor_bump"),
        pytest.param("1.0.0", BumpType.MAJOR, None, "2.0.0", id="major_bump"),
        pytest.param("1.2.3", BumpType.PATCH, None, "1.2.4", id="patch_bump_complex"),
        pytest.param(
            "0.1.0", BumpType.MINOR, None, "0.2.0", id="minor_bump_zero_major"
        ),
        pytest.param("1.0.0", None, "2.0.0", "2.0.0", id="explicit_version"),
        pytest.param("1.0.0", None, "1.5.0", "1.5.0", id="explicit_version_minor"),
    ],
)
def test_calculate_new_version(
    current_version: str,
    bump_type: BumpType | None,
    new_version: str | None,
    expected: str,
):
    """Test version calculation with various bump types and explicit versions."""
    result = calculate_new_version(current_version, bump_type, new_version)
    assert result == expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "current_version,new_version,error_type",
    [
        pytest.param(
            "1.0.0", "invalid", InvalidVersionError, id="invalid_explicit_version"
        ),
        pytest.param(
            "invalid", BumpType.PATCH, InvalidVersionError, id="invalid_current_version"
        ),
    ],
)
def test_calculate_new_version_errors(
    current_version: str,
    new_version: str | BumpType,
    error_type: type,
):
    """Test version calculation error cases."""
    if isinstance(new_version, BumpType):
        with pytest.raises(error_type):
            calculate_new_version(current_version, new_version, None)
    else:
        with pytest.raises(error_type):
            calculate_new_version(current_version, None, new_version)


@pytest.mark.unit
def test_calculate_new_version_missing_args():
    """Test that ValueError is raised when neither bump_type nor new_version is provided."""
    with pytest.raises(
        ValueError, match="Either bump_type or new_version must be provided"
    ):
        calculate_new_version("1.0.0", None, None)


@pytest.mark.unit
def test_get_connector_path_not_found():
    """Test that ConnectorNotFoundError is raised for non-existent connector."""
    with tempfile.TemporaryDirectory() as tmpdir, pytest.raises(ConnectorNotFoundError):
        get_connector_path(tmpdir, "source-nonexistent")


@pytest.mark.unit
def test_get_connector_path_exists():
    """Test that get_connector_path returns correct path for existing connector."""
    with tempfile.TemporaryDirectory() as tmpdir:
        connector_dir = (
            Path(tmpdir) / "airbyte-integrations" / "connectors" / "source-test"
        )
        connector_dir.mkdir(parents=True)

        result = get_connector_path(tmpdir, "source-test")
        assert result == connector_dir


@pytest.mark.unit
def test_get_current_version():
    """Test getting current version from metadata.yaml."""
    with tempfile.TemporaryDirectory() as tmpdir:
        connector_dir = (
            Path(tmpdir) / "airbyte-integrations" / "connectors" / "source-test"
        )
        connector_dir.mkdir(parents=True)

        metadata_content = """data:
  dockerImageTag: "1.2.3"
  name: source-test
"""
        (connector_dir / "metadata.yaml").write_text(metadata_content)

        version = get_current_version(connector_dir)
        assert version == "1.2.3"


@pytest.mark.unit
def test_get_current_version_not_found():
    """Test that VersionNotFoundError is raised when metadata.yaml doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        connector_dir = Path(tmpdir) / "source-test"
        connector_dir.mkdir(parents=True)

        with pytest.raises(VersionNotFoundError):
            get_current_version(connector_dir)


@pytest.mark.unit
def test_get_current_version_missing_tag():
    """Test that VersionNotFoundError is raised when dockerImageTag is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        connector_dir = Path(tmpdir) / "source-test"
        connector_dir.mkdir(parents=True)

        metadata_content = """data:
  name: source-test
"""
        (connector_dir / "metadata.yaml").write_text(metadata_content)

        with pytest.raises(VersionNotFoundError):
            get_current_version(connector_dir)


@pytest.mark.unit
def test_update_metadata_version():
    """Test updating version in metadata.yaml."""
    with tempfile.TemporaryDirectory() as tmpdir:
        connector_dir = Path(tmpdir)

        metadata_content = """data:
  dockerImageTag: 1.0.0
  name: source-test
"""
        (connector_dir / "metadata.yaml").write_text(metadata_content)

        result = update_metadata_version(connector_dir, "1.1.0")
        assert result is True

        updated_content = (connector_dir / "metadata.yaml").read_text()
        assert "dockerImageTag: 1.1.0" in updated_content
        assert "dockerImageTag: 1.0.0" not in updated_content


@pytest.mark.unit
def test_update_metadata_version_dry_run():
    """Test that dry_run doesn't modify the file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        connector_dir = Path(tmpdir)

        metadata_content = """data:
  dockerImageTag: 1.0.0
  name: source-test
"""
        (connector_dir / "metadata.yaml").write_text(metadata_content)

        result = update_metadata_version(connector_dir, "1.1.0", dry_run=True)
        assert result is True

        # File should not be modified
        content = (connector_dir / "metadata.yaml").read_text()
        assert "dockerImageTag: 1.0.0" in content


@pytest.mark.unit
def test_update_pyproject_version():
    """Test updating version in pyproject.toml."""
    with tempfile.TemporaryDirectory() as tmpdir:
        connector_dir = Path(tmpdir)

        pyproject_content = """[tool.poetry]
name = "source-test"
version = "1.0.0"
"""
        (connector_dir / "pyproject.toml").write_text(pyproject_content)

        result = update_pyproject_version(connector_dir, "1.1.0")
        assert result is True

        updated_content = (connector_dir / "pyproject.toml").read_text()
        assert 'version = "1.1.0"' in updated_content


@pytest.mark.unit
def test_update_pyproject_version_no_file():
    """Test that update_pyproject_version returns False when file doesn't exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        connector_dir = Path(tmpdir)

        result = update_pyproject_version(connector_dir, "1.1.0")
        assert result is False


@pytest.mark.unit
def test_parse_changelog_valid():
    """Test parsing a valid changelog table."""
    markdown_lines = [
        "# Changelog",
        "",
        "| Version | Date | Pull Request | Subject |",
        "|---------|------|--------------|---------|",
        "| 1.0.0 | 2025-01-01 | [123](https://github.com/airbytehq/airbyte/pull/123) | Initial release |",
    ]

    start_index, entries = parse_changelog(markdown_lines)
    assert start_index == 4
    assert len(entries) == 1

    entry = next(iter(entries))
    assert str(entry.version) == "1.0.0"
    assert entry.pr_number == 123
    assert entry.comment == "Initial release"


@pytest.mark.unit
def test_parse_changelog_no_table():
    """Test that ChangelogParsingError is raised when no changelog table exists."""
    markdown_lines = [
        "# Changelog",
        "",
        "No table here",
    ]

    with pytest.raises(ChangelogParsingError):
        parse_changelog(markdown_lines)


@pytest.mark.unit
def test_changelog_entry_to_markdown():
    """Test ChangelogEntry.to_markdown() output."""
    entry = ChangelogEntry(
        date=datetime.date(2025, 1, 15),
        version=semver.Version.parse("1.2.3"),
        pr_number=456,
        comment="Fix bug",
    )

    markdown = entry.to_markdown()
    assert "1.2.3" in markdown
    assert "2025-01-15" in markdown
    assert "456" in markdown
    assert "Fix bug" in markdown


@pytest.mark.unit
def test_bump_connector_version_full():
    """Test full bump_connector_version workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create connector directory structure
        connector_dir = (
            Path(tmpdir) / "airbyte-integrations" / "connectors" / "source-test"
        )
        connector_dir.mkdir(parents=True)

        # Create metadata.yaml
        metadata_content = """data:
  dockerImageTag: 1.0.0
  name: source-test
"""
        (connector_dir / "metadata.yaml").write_text(metadata_content)

        # Create pyproject.toml
        pyproject_content = """[tool.poetry]
name = "source-test"
version = "1.0.0"
"""
        (connector_dir / "pyproject.toml").write_text(pyproject_content)

        # Run bump
        result = bump_connector_version(
            repo_path=tmpdir,
            connector_name="source-test",
            bump_type="patch",
        )

        assert result.connector == "source-test"
        assert result.previous_version == "1.0.0"
        assert result.new_version == "1.0.1"
        assert len(result.files_modified) == 2
        assert result.dry_run is False

        # Verify files were updated
        metadata = (connector_dir / "metadata.yaml").read_text()
        assert "dockerImageTag: 1.0.1" in metadata

        pyproject = (connector_dir / "pyproject.toml").read_text()
        assert 'version = "1.0.1"' in pyproject


@pytest.mark.unit
def test_bump_connector_version_dry_run():
    """Test bump_connector_version with dry_run=True."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create connector directory structure
        connector_dir = (
            Path(tmpdir) / "airbyte-integrations" / "connectors" / "source-test"
        )
        connector_dir.mkdir(parents=True)

        # Create metadata.yaml
        metadata_content = """data:
  dockerImageTag: 1.0.0
  name: source-test
"""
        (connector_dir / "metadata.yaml").write_text(metadata_content)

        # Run bump with dry_run
        result = bump_connector_version(
            repo_path=tmpdir,
            connector_name="source-test",
            bump_type="minor",
            dry_run=True,
        )

        assert result.connector == "source-test"
        assert result.previous_version == "1.0.0"
        assert result.new_version == "1.1.0"
        assert result.dry_run is True

        # Verify file was NOT updated
        metadata = (connector_dir / "metadata.yaml").read_text()
        assert "dockerImageTag: 1.0.0" in metadata


@pytest.mark.unit
def test_bump_connector_version_connector_not_found():
    """Test bump_connector_version with non-existent connector."""
    with tempfile.TemporaryDirectory() as tmpdir, pytest.raises(ConnectorNotFoundError):
        bump_connector_version(
            repo_path=tmpdir,
            connector_name="source-nonexistent",
            bump_type="patch",
        )
