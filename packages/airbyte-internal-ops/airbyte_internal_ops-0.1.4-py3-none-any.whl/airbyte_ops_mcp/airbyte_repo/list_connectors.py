# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Detect changed connectors in the Airbyte monorepo.

This module provides functionality to detect which connectors have been modified
by comparing git diffs between branches.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from pathlib import Path

CONNECTOR_PATH_PREFIX = "airbyte-integrations/connectors"
METADATA_FILE_NAME = "metadata.yaml"


class ConnectorLanguage(StrEnum):
    """Supported connector implementation languages."""

    PYTHON = "python"
    JAVA = "java"
    LOW_CODE = "low-code"
    MANIFEST_ONLY = "manifest-only"


def get_modified_connectors(
    repo_path: str | Path,
    base_ref: str = "origin/main",
    head_ref: str = "HEAD",
) -> list[str]:
    """Get list of connector IDs that have been modified.

    This function compares the git diff between base_ref and head_ref to determine
    which connectors have been modified. A connector is considered modified if any
    files within its directory have changed.

    Args:
        repo_path: Path to the Airbyte monorepo
        base_ref: Base git reference to compare against (default: "origin/main")
        head_ref: Head git reference to compare (default: "HEAD")

    Returns:
        List of connector technical names (e.g., ["source-faker", "destination-postgres"])

    Example:
        >>> connectors = get_changed_connectors("/path/to/airbyte", "origin/main")
        >>> print(connectors)
        ['source-faker', 'destination-postgres']
    """
    repo_path = Path(repo_path)

    # Get list of changed files using git diff
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base_ref, head_ref],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        changed_files = result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get git diff: {e.stderr}") from e
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("Git diff command timed out after 30 seconds") from e

    # Filter for connector files and extract connector names
    changed_connectors = set()
    for file_path in changed_files:
        if file_path.startswith(CONNECTOR_PATH_PREFIX + "/"):
            # Extract connector name from path
            # e.g., "airbyte-integrations/connectors/source-faker/..." -> "source-faker"
            path_parts = file_path.split("/")
            if len(path_parts) >= 3:
                connector_name = path_parts[2]
                changed_connectors.add(connector_name)

    return sorted(changed_connectors)


@lru_cache(maxsize=128)
def get_certified_connectors(repo_path: str | Path) -> set[str]:
    """Get set of all certified connector IDs from metadata.

    This function reads the metadata.yaml file for each connector to determine
    which connectors have "certified" support level.

    Args:
        repo_path: Path to the Airbyte monorepo

    Returns:
        Set of certified connector technical names

    Example:
        >>> certified = get_certified_connectors("/path/to/airbyte")
        >>> "source-postgres" in certified
        True
    """
    repo_path = Path(repo_path)
    connectors_dir = repo_path / CONNECTOR_PATH_PREFIX

    if not connectors_dir.exists():
        raise ValueError(f"Connectors directory not found: {connectors_dir}")

    certified_connectors = set()

    # Iterate through all connector directories
    for connector_dir in connectors_dir.iterdir():
        if not connector_dir.is_dir():
            continue

        metadata_file = connector_dir / METADATA_FILE_NAME
        if not metadata_file.exists():
            continue

        # Read metadata to check support level
        try:
            import yaml

            with open(metadata_file) as f:
                metadata = yaml.safe_load(f)

            support_level = metadata.get("data", {}).get("supportLevel")
            if support_level == "certified":
                certified_connectors.add(connector_dir.name)
        except Exception:
            # Skip connectors with invalid metadata
            continue

    return certified_connectors


def get_all_connectors(repo_path: str | Path) -> set[str]:
    """Get set of all connector IDs in the repository.

    Args:
        repo_path: Path to the Airbyte monorepo

    Returns:
        Set of all connector technical names

    Example:
        >>> all_connectors = get_all_connectors("/path/to/airbyte")
        >>> "source-faker" in all_connectors
        True
    """
    repo_path = Path(repo_path)
    connectors_dir = repo_path / CONNECTOR_PATH_PREFIX

    if not connectors_dir.exists():
        raise ValueError(f"Connectors directory not found: {connectors_dir}")

    return {p.name for p in connectors_dir.iterdir() if p.is_dir()}


def get_connectors_by_language(
    repo_path: str | Path,
    language: ConnectorLanguage,
) -> set[str]:
    """Get set of all connector IDs for a specific language.

    This function reads connector directories to determine which connectors
    use the specified language.

    Args:
        repo_path: Path to the Airbyte monorepo
        language: Language to filter by

    Returns:
        Set of connector technical names using the specified language

    Example:
        >>> python_connectors = get_connectors_by_language(
        ...     "/path/to/airbyte", ConnectorLanguage.PYTHON
        ... )
        >>> "source-faker" in python_connectors
        True
    """
    repo_path = Path(repo_path)
    connectors_dir = repo_path / CONNECTOR_PATH_PREFIX

    if not connectors_dir.exists():
        raise ValueError(f"Connectors directory not found: {connectors_dir}")

    language_value = language.value
    connectors_by_language = set()

    # Iterate through all connector directories
    for connector_dir in connectors_dir.iterdir():
        if not connector_dir.is_dir():
            continue

        # Determine language based on file structure
        connector_name = connector_dir.name
        detected_language = _detect_connector_language(connector_dir, connector_name)

        if detected_language == language_value:
            connectors_by_language.add(connector_dir.name)

    return connectors_by_language


@lru_cache(maxsize=1024)
def _detect_connector_language(connector_dir: Path, connector_name: str) -> str | None:
    """Detect the language of a connector based on its file structure.

    Args:
        connector_dir: Path to the connector directory
        connector_name: Technical name of the connector

    Returns:
        Language string (python, java, low-code, manifest-only) or None
    """
    # Check for manifest-only (manifest.yaml at root)
    if (connector_dir / "manifest.yaml").is_file():
        return "manifest-only"

    # Check for low-code (manifest.yaml in source directory)
    source_dir = connector_dir / connector_name.replace("-", "_")
    if (source_dir / "manifest.yaml").is_file():
        return "low-code"

    # Check for Python (setup.py or pyproject.toml)
    if (connector_dir / "setup.py").is_file() or (
        connector_dir / "pyproject.toml"
    ).is_file():
        return "python"

    # Check for Java/Kotlin (src/main/java or src/main/kotlin)
    if (connector_dir / "src" / "main" / "java").exists() or (
        connector_dir / "src" / "main" / "kotlin"
    ).exists():
        return "java"

    return None


@lru_cache(maxsize=128)
def get_connectors_with_local_cdk(repo_path: str | Path) -> set[str]:
    """Get set of connectors using local CDK reference instead of published version.

    This function detects connectors that are configured to use a local CDK
    checkout rather than a published CDK version. The detection method differs
    by connector language:
    - Python: Checks for path-based dependency in pyproject.toml
    - Java/Kotlin: Checks for useLocalCdk=true in build.gradle files

    Args:
        repo_path: Path to the Airbyte monorepo

    Returns:
        Set of connector technical names using local CDK reference

    Example:
        >>> local_cdk_connectors = get_connectors_with_local_cdk("/path/to/airbyte")
        >>> "destination-motherduck" in local_cdk_connectors
        True
    """
    repo_path = Path(repo_path)
    connectors_dir = repo_path / CONNECTOR_PATH_PREFIX

    if not connectors_dir.exists():
        raise ValueError(f"Connectors directory not found: {connectors_dir}")

    local_cdk_connectors = set()

    # Iterate through all connector directories
    for connector_dir in connectors_dir.iterdir():
        if not connector_dir.is_dir():
            continue

        connector_name = connector_dir.name
        detected_language = _detect_connector_language(connector_dir, connector_name)

        # Check for local CDK based on language
        if detected_language in ("python", "low-code") and _has_local_cdk_python(
            connector_dir
        ):
            # Python connectors: check pyproject.toml for path-based CDK dependency
            local_cdk_connectors.add(connector_name)
        elif detected_language == "java" and _has_local_cdk_java(connector_dir):
            # Java/Kotlin connectors: check build.gradle for useLocalCdk=true
            local_cdk_connectors.add(connector_name)

    return local_cdk_connectors


def _has_local_cdk_python(connector_dir: Path) -> bool:
    """Check if a Python connector uses local CDK reference.

    Args:
        connector_dir: Path to the connector directory

    Returns:
        True if connector uses local CDK reference
    """
    pyproject_file = connector_dir / "pyproject.toml"
    if not pyproject_file.exists():
        return False

    try:
        content = pyproject_file.read_text()
        # Look for path-based airbyte-cdk dependency
        # Pattern: airbyte-cdk = { path = "..." } or airbyte-cdk = {path = "..."}
        return bool(re.search(r"airbyte-cdk\s*=\s*\{[^}]*path\s*=", content))
    except Exception:
        return False


def _has_local_cdk_java(connector_dir: Path) -> bool:
    """Check if a Java/Kotlin connector uses local CDK reference.

    Mirrors the implementation from airbyte-ci/connectors/connector_ops/connector_ops/utils.py

    Args:
        connector_dir: Path to the connector directory

    Returns:
        True if connector uses local CDK reference
    """
    # Check both build.gradle and build.gradle.kts
    for build_file_name in ("build.gradle", "build.gradle.kts"):
        build_file = connector_dir / build_file_name
        if not build_file.exists():
            continue

        try:
            # Read file and strip inline comments
            contents = "\n".join(
                [
                    line.split("//")[0]  # Remove inline comments
                    for line in build_file.read_text().split("\n")
                ]
            )
            # Remove spaces and check for useLocalCdk=true
            contents = contents.replace(" ", "")
            if "useLocalCdk=true" in contents:
                return True
        except Exception:
            continue

    return False


@dataclass
class ConnectorListResult:
    """Result of listing connectors with filters."""

    connectors: list[str]
    count: int


def list_connectors(
    repo_path: str | Path,
    certified: bool | None = None,
    modified: bool | None = None,
    language_filter: set[str] | None = None,
    language_exclude: set[str] | None = None,
    base_ref: str | None = None,
    head_ref: str | None = None,
) -> ConnectorListResult:
    """List connectors in the Airbyte monorepo with flexible filtering.

    This is the core capability function that encapsulates all filtering logic.
    Both CLI and MCP layers should use this function.

    Args:
        repo_path: Path to the Airbyte monorepo
        certified: Filter by certification status (True=certified only,
            False=non-certified only, None=all)
        modified: Filter by modification status (True=modified only,
            False=not-modified only, None=all)
        language_filter: Set of languages to include (python, java, low-code, manifest-only)
        language_exclude: Set of languages to exclude (mutually exclusive with language_filter)
        base_ref: Base git reference for modification detection (default: "origin/main")
        head_ref: Head git reference for modification detection (default: "HEAD")

    Returns:
        ConnectorListResult with sorted list of connector names and count

    Raises:
        ValueError: If both language_filter and language_exclude are provided
    """
    # Validate mutual exclusivity of language filters
    if language_filter is not None and language_exclude is not None:
        raise ValueError(
            "Cannot specify both language_filter and language_exclude. "
            "Only one language filter parameter is accepted."
        )

    # Start with all connectors
    result = get_all_connectors(repo_path)

    # Apply certified filter
    if certified is not None:
        certified_set = get_certified_connectors(repo_path)
        if certified:
            # Include only certified
            result &= certified_set
        else:
            # Include only non-certified
            result -= certified_set

    # Apply modified filter
    if modified is not None:
        base = base_ref if base_ref is not None else "origin/main"
        head = head_ref if head_ref is not None else "HEAD"
        changed_set = set(get_modified_connectors(repo_path, base, head))
        if modified:
            # Include only modified
            result &= changed_set
        else:
            # Include only not-modified
            result -= changed_set

    # Apply language include filter
    if language_filter:
        # Get connectors for all specified languages and union them
        lang_result: set[str] = set()
        for lang in language_filter:
            lang_result |= get_connectors_by_language(
                repo_path, ConnectorLanguage(lang)
            )
        result &= lang_result

    # Apply language exclude filter
    if language_exclude:
        # Get connectors for all specified languages and exclude them
        for lang in language_exclude:
            excluded = get_connectors_by_language(repo_path, ConnectorLanguage(lang))
            result -= excluded

    return ConnectorListResult(
        connectors=sorted(result),
        count=len(result),
    )
