# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Version bumping utilities for Airbyte connectors.

This module provides pure Python functionality to bump connector versions
across metadata.yaml, pyproject.toml, and changelog files.
"""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from enum import StrEnum
from operator import attrgetter
from pathlib import Path
from typing import Literal

import semver
import yaml

from airbyte_ops_mcp.airbyte_repo.list_connectors import (
    CONNECTOR_PATH_PREFIX,
    METADATA_FILE_NAME,
)

PYPROJECT_FILE_NAME = "pyproject.toml"
AIRBYTE_GITHUB_REPO = "airbytehq/airbyte"


class BumpType(StrEnum):
    """Supported version bump types."""

    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


class ConnectorVersionError(Exception):
    """Base exception for connector version operations."""

    pass


class ConnectorNotFoundError(ConnectorVersionError):
    """Raised when a connector is not found."""

    pass


class VersionNotFoundError(ConnectorVersionError):
    """Raised when version cannot be found in a file."""

    pass


class InvalidVersionError(ConnectorVersionError):
    """Raised when a version string is invalid."""

    pass


class ChangelogParsingError(ConnectorVersionError):
    """Raised when changelog cannot be parsed."""

    pass


@dataclass
class VersionBumpResult:
    """Result of a version bump operation."""

    connector: str
    previous_version: str
    new_version: str
    files_modified: list[str]
    dry_run: bool


@dataclass(frozen=True)
class ChangelogEntry:
    """A single changelog entry."""

    date: datetime.date
    version: semver.Version
    pr_number: int | str
    comment: str

    def to_markdown(self, github_repo: str = AIRBYTE_GITHUB_REPO) -> str:
        """Convert entry to markdown table row."""
        return (
            f"| {self.version} | {self.date.strftime('%Y-%m-%d')} | "
            f"[{self.pr_number}](https://github.com/{github_repo}/pull/{self.pr_number}) | "
            f"{self.comment} |"
        )


def get_connector_path(repo_path: str | Path, connector_name: str) -> Path:
    """Get the path to a connector directory.

    Args:
        repo_path: Path to the Airbyte monorepo
        connector_name: Technical name of the connector (e.g., "source-github")

    Returns:
        Path to the connector directory

    Raises:
        ConnectorNotFoundError: If the connector directory doesn't exist
    """
    repo_path = Path(repo_path)
    connector_path = repo_path / CONNECTOR_PATH_PREFIX / connector_name

    if not connector_path.exists():
        raise ConnectorNotFoundError(
            f"Connector '{connector_name}' not found at {connector_path}"
        )

    return connector_path


def get_current_version(connector_path: Path) -> str:
    """Get the current version from metadata.yaml.

    Args:
        connector_path: Path to the connector directory

    Returns:
        Current version string

    Raises:
        VersionNotFoundError: If version cannot be found
    """
    metadata_file = connector_path / METADATA_FILE_NAME

    if not metadata_file.exists():
        raise VersionNotFoundError(f"Metadata file not found: {metadata_file}")

    with open(metadata_file) as f:
        metadata = yaml.safe_load(f)

    try:
        version = metadata["data"]["dockerImageTag"]
    except KeyError as e:
        raise VersionNotFoundError("dockerImageTag not found in metadata.yaml") from e

    return version


def calculate_new_version(
    current_version: str,
    bump_type: BumpType | None = None,
    new_version: str | None = None,
) -> str:
    """Calculate the new version based on bump type or explicit version.

    Args:
        current_version: Current version string
        bump_type: Type of version bump (patch, minor, major)
        new_version: Explicit new version (overrides bump_type)

    Returns:
        New version string

    Raises:
        InvalidVersionError: If version is invalid
        ValueError: If neither bump_type nor new_version is provided
    """
    if new_version is not None:
        # Validate the explicit version
        if not semver.Version.is_valid(new_version):
            raise InvalidVersionError(f"Invalid version format: {new_version}")
        return new_version

    if bump_type is None:
        raise ValueError("Either bump_type or new_version must be provided")

    try:
        version = semver.Version.parse(current_version)
    except ValueError as e:
        raise InvalidVersionError(
            f"Cannot parse current version: {current_version}"
        ) from e

    if bump_type == BumpType.PATCH:
        return str(version.bump_patch())
    elif bump_type == BumpType.MINOR:
        return str(version.bump_minor())
    elif bump_type == BumpType.MAJOR:
        return str(version.bump_major())
    else:
        raise ValueError(f"Unknown bump type: {bump_type}")


def update_metadata_version(
    connector_path: Path,
    new_version: str,
    dry_run: bool = False,
) -> bool:
    """Update version in metadata.yaml.

    Args:
        connector_path: Path to the connector directory
        new_version: New version string
        dry_run: If True, don't actually modify the file

    Returns:
        True if file was (or would be) modified
    """
    metadata_file = connector_path / METADATA_FILE_NAME

    if not metadata_file.exists():
        return False

    content = metadata_file.read_text()
    current_version = get_current_version(connector_path)

    # Use string replacement to preserve comments and formatting
    new_content = content.replace(
        f"dockerImageTag: {current_version}",
        f"dockerImageTag: {new_version}",
    )

    if new_content == content:
        # Also try with quotes
        new_content = content.replace(
            f'dockerImageTag: "{current_version}"',
            f'dockerImageTag: "{new_version}"',
        )

    if new_content != content and not dry_run:
        metadata_file.write_text(new_content)

    return new_content != content


def update_pyproject_version(
    connector_path: Path,
    new_version: str,
    dry_run: bool = False,
) -> bool:
    """Update version in pyproject.toml.

    Args:
        connector_path: Path to the connector directory
        new_version: New version string
        dry_run: If True, don't actually modify the file

    Returns:
        True if file was (or would be) modified
    """
    pyproject_file = connector_path / PYPROJECT_FILE_NAME

    if not pyproject_file.exists():
        return False

    content = pyproject_file.read_text()

    # Match version in [tool.poetry] or [project] section
    # Pattern matches: version = "x.y.z" or version = 'x.y.z'
    version_pattern = r'(version\s*=\s*["\'])([^"\']+)(["\'])'

    def replace_version(match: re.Match) -> str:
        return f"{match.group(1)}{new_version}{match.group(3)}"

    new_content = re.sub(version_pattern, replace_version, content, count=1)

    if new_content != content and not dry_run:
        pyproject_file.write_text(new_content)

    return new_content != content


def get_connector_doc_path(
    repo_path: Path,
    connector_name: str,
) -> Path | None:
    """Get the path to the connector's documentation file.

    Args:
        repo_path: Path to the Airbyte monorepo
        connector_name: Technical name of the connector

    Returns:
        Path to the documentation file, or None if not found
    """
    # Determine connector type (source or destination)
    if connector_name.startswith("source-"):
        connector_type = "sources"
        doc_name = connector_name.replace("source-", "")
    elif connector_name.startswith("destination-"):
        connector_type = "destinations"
        doc_name = connector_name.replace("destination-", "")
    else:
        return None

    doc_path = repo_path / "docs" / "integrations" / connector_type / f"{doc_name}.md"

    if doc_path.exists():
        return doc_path

    return None


def parse_changelog(
    markdown_lines: list[str],
    github_repo: str = AIRBYTE_GITHUB_REPO,
) -> tuple[int, set[ChangelogEntry]]:
    """Parse changelog entries from markdown.

    Args:
        markdown_lines: Lines of the markdown file
        github_repo: GitHub repository for PR links

    Returns:
        Tuple of (start_line_index, set of entries)

    Raises:
        ChangelogParsingError: If changelog table cannot be found or parsed
    """
    changelog_entry_re = (
        r"^\| *(?P<version>[0-9]+\.[0-9]+\.[0-9]+) *\| *"
        r"(?P<day>[0-9]{4}-[0-9]{2}-[0-9]{2}) *\| *"
        r"\[?(?P<pr_number1>[0-9]+)\]? ?\(https://github.com/"
        + re.escape(github_repo)
        + r"/pull/(?P<pr_number2>[0-9]+)\) *\| *"
        r"(?P<comment>[^ ].*[^ ]) *\| *$"
    )

    changelog_header_line_index = -1
    changelog_line_enumerator = enumerate(markdown_lines)

    for line_index, line in changelog_line_enumerator:
        if re.search(r"\| *Version *\| *Date *\| *Pull Request *\| *Subject *\|", line):
            changelog_header_line_index = line_index
            break

    if changelog_header_line_index == -1:
        raise ChangelogParsingError(
            "Could not find the changelog section table in the documentation file."
        )

    # Skip the header delimiter line
    try:
        next(changelog_line_enumerator)
    except StopIteration as e:
        raise ChangelogParsingError(
            "The changelog table is missing the header delimiter."
        ) from e

    changelog_entries_start_line_index = changelog_header_line_index + 2

    entries: set[ChangelogEntry] = set()
    for _line_index, line in changelog_line_enumerator:
        changelog_entry_match = re.search(changelog_entry_re, line)
        if not changelog_entry_match:
            break
        if changelog_entry_match.group("pr_number1") != changelog_entry_match.group(
            "pr_number2"
        ):
            break

        entry_version = semver.Version.parse(changelog_entry_match.group("version"))
        entry_date = datetime.datetime.strptime(
            changelog_entry_match.group("day"), "%Y-%m-%d"
        ).date()
        entry_pr_number = int(changelog_entry_match.group("pr_number1"))
        entry_comment = changelog_entry_match.group("comment")

        entries.add(
            ChangelogEntry(entry_date, entry_version, entry_pr_number, entry_comment)
        )

    return changelog_entries_start_line_index, entries


def update_changelog(
    doc_path: Path,
    new_version: str,
    changelog_message: str,
    pr_number: int | str | None = None,
    dry_run: bool = False,
    github_repo: str = AIRBYTE_GITHUB_REPO,
) -> bool:
    """Update the changelog in the documentation file.

    Args:
        doc_path: Path to the documentation file
        new_version: New version string
        changelog_message: Message for the changelog entry
        pr_number: PR number for the entry (uses placeholder if None)
        dry_run: If True, don't actually modify the file
        github_repo: GitHub repository for PR links

    Returns:
        True if file was (or would be) modified
    """
    if not doc_path.exists():
        return False

    content = doc_path.read_text()
    markdown_lines = content.splitlines()

    try:
        start_line_index, original_entries = parse_changelog(
            markdown_lines, github_repo
        )
    except ChangelogParsingError:
        # If we can't parse the changelog, skip updating it
        return False

    # Create new entry
    version = semver.Version.parse(new_version)
    pr_num = pr_number if pr_number is not None else "*PR_NUMBER_PLACEHOLDER*"
    new_entry = ChangelogEntry(
        date=datetime.date.today(),
        version=version,
        pr_number=pr_num,
        comment=changelog_message,
    )

    # Combine and sort entries
    all_entries = original_entries | {new_entry}
    sorted_entries = sorted(
        sorted(all_entries, key=attrgetter("date"), reverse=True),
        key=attrgetter("version"),
        reverse=True,
    )

    # Rebuild the markdown
    new_lines = (
        markdown_lines[:start_line_index]
        + [entry.to_markdown(github_repo) for entry in sorted_entries]
        + markdown_lines[start_line_index + len(original_entries) :]
    )

    new_content = "\n".join(new_lines) + "\n"

    if new_content != content and not dry_run:
        doc_path.write_text(new_content)

    return new_content != content


def bump_connector_version(
    repo_path: str | Path,
    connector_name: str,
    bump_type: Literal["patch", "minor", "major"] | None = None,
    new_version: str | None = None,
    changelog_message: str | None = None,
    pr_number: int | str | None = None,
    dry_run: bool = False,
) -> VersionBumpResult:
    """Bump a connector's version across all relevant files.

    This function updates the version in:
    - metadata.yaml (always)
    - pyproject.toml (if exists, for Python connectors)
    - Documentation changelog (if changelog_message provided and doc exists)

    Args:
        repo_path: Path to the Airbyte monorepo
        connector_name: Technical name of the connector (e.g., "source-github")
        bump_type: Type of version bump (patch, minor, major)
        new_version: Explicit new version (overrides bump_type)
        changelog_message: Message to add to changelog (optional)
        pr_number: PR number for changelog entry (optional)
        dry_run: If True, don't actually modify files

    Returns:
        VersionBumpResult with details of the operation

    Raises:
        ConnectorNotFoundError: If connector doesn't exist
        VersionNotFoundError: If current version cannot be found
        InvalidVersionError: If version format is invalid
        ValueError: If neither bump_type nor new_version is provided
    """
    repo_path = Path(repo_path)
    connector_path = get_connector_path(repo_path, connector_name)

    # Get current version
    current_version = get_current_version(connector_path)

    # Calculate new version
    bump_type_enum = BumpType(bump_type) if bump_type else None
    calculated_version = calculate_new_version(
        current_version, bump_type_enum, new_version
    )

    files_modified: list[str] = []

    # Update metadata.yaml
    if update_metadata_version(connector_path, calculated_version, dry_run):
        files_modified.append(
            f"{CONNECTOR_PATH_PREFIX}/{connector_name}/{METADATA_FILE_NAME}"
        )

    # Update pyproject.toml if it exists
    if update_pyproject_version(connector_path, calculated_version, dry_run):
        files_modified.append(
            f"{CONNECTOR_PATH_PREFIX}/{connector_name}/{PYPROJECT_FILE_NAME}"
        )

    # Update changelog if message provided
    if changelog_message:
        doc_path = get_connector_doc_path(repo_path, connector_name)
        if doc_path and update_changelog(
            doc_path,
            calculated_version,
            changelog_message,
            pr_number,
            dry_run,
        ):
            files_modified.append(str(doc_path.relative_to(repo_path)))

    return VersionBumpResult(
        connector=connector_name,
        previous_version=current_version,
        new_version=calculated_version,
        files_modified=files_modified,
        dry_run=dry_run,
    )
