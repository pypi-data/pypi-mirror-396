# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""CLI commands for local Airbyte monorepo operations.

Commands:
    airbyte-ops repo connector list - List connectors in the monorepo
    airbyte-ops repo connector info - Get metadata for a single connector
    airbyte-ops repo connector bump-version - Bump connector version
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Literal

import yaml
from cyclopts import App, Parameter
from rich.console import Console

from airbyte_ops_mcp.airbyte_repo.bump_version import (
    ConnectorNotFoundError,
    InvalidVersionError,
    VersionNotFoundError,
    bump_connector_version,
)
from airbyte_ops_mcp.airbyte_repo.list_connectors import (
    CONNECTOR_PATH_PREFIX,
    METADATA_FILE_NAME,
    _detect_connector_language,
    get_connectors_with_local_cdk,
)
from airbyte_ops_mcp.cli._base import app
from airbyte_ops_mcp.cli._shared import exit_with_error, print_json
from airbyte_ops_mcp.mcp.github_repo_ops import list_connectors_in_repo

console = Console()

OutputFormat = Literal["csv", "lines", "json-gh-matrix"]

# Support level mapping: keyword -> integer value
# Higher values indicate higher support/quality levels
SUPPORT_LEVEL_MAP: dict[str, int] = {
    "archived": 100,
    "community": 200,
    "certified": 300,
}

# Reverse mapping for input parsing
SUPPORT_LEVEL_KEYWORDS = set(SUPPORT_LEVEL_MAP.keys())


def _parse_support_level(value: str) -> int:
    """Parse a support level string to an integer.

    Accepts either an integer string ("200") or a keyword ("certified").
    """
    value = value.strip().lower()
    if value in SUPPORT_LEVEL_MAP:
        return SUPPORT_LEVEL_MAP[value]
    try:
        return int(value)
    except ValueError:
        raise ValueError(
            f"Invalid support level: {value}. "
            f"Use an integer or one of: {', '.join(SUPPORT_LEVEL_KEYWORDS)}"
        ) from None


def _get_connector_support_level(connector_dir: Path) -> int | None:
    """Read support level from connector's metadata.yaml and return as integer."""
    metadata_file = connector_dir / METADATA_FILE_NAME
    if not metadata_file.exists():
        return None
    metadata = yaml.safe_load(metadata_file.read_text())
    support_level_str = metadata.get("data", {}).get("supportLevel")
    if support_level_str and support_level_str.lower() in SUPPORT_LEVEL_MAP:
        return SUPPORT_LEVEL_MAP[support_level_str.lower()]
    return None


def _parse_connector_types(value: str) -> set[str]:
    """Parse connector types from CSV or newline-delimited string."""
    types = set()
    for item in value.replace(",", "\n").split("\n"):
        item = item.strip().lower()
        if item:
            if item not in ("source", "destination"):
                raise ValueError(
                    f"Invalid connector type: {item}. Must be 'source' or 'destination'."
                )
            types.add(item)
    return types


def _get_connector_type(connector_name: str) -> str:
    """Derive connector type from name prefix."""
    if connector_name.startswith("source-"):
        return "source"
    elif connector_name.startswith("destination-"):
        return "destination"
    return "unknown"


def _parse_connector_names(value: str) -> set[str]:
    """Parse connector names from CSV or newline-delimited string."""
    names = set()
    for item in value.replace(",", "\n").split("\n"):
        item = item.strip()
        if item:
            names.add(item)
    return names


def _get_connector_version(connector_dir: Path) -> str | None:
    """Read connector version (dockerImageTag) from metadata.yaml."""
    metadata_file = connector_dir / METADATA_FILE_NAME
    if not metadata_file.exists():
        return None
    metadata = yaml.safe_load(metadata_file.read_text())
    return metadata.get("data", {}).get("dockerImageTag")


def _get_connector_info(
    connector_name: str, connector_dir: Path
) -> dict[str, str | int | None]:
    """Get full connector metadata as a dict with connector_ prefixed keys.

    This is shared between the `list --output-format json-gh-matrix` and `info` commands.
    """
    return {
        "connector": connector_name,
        "connector_type": _get_connector_type(connector_name),
        "connector_language": _detect_connector_language(connector_dir, connector_name)
        or "unknown",
        "connector_support_level": _get_connector_support_level(connector_dir),
        "connector_version": _get_connector_version(connector_dir),
        "connector_dir": f"{CONNECTOR_PATH_PREFIX}/{connector_name}",
    }


# Create the repo sub-app
repo_app = App(name="repo", help="Local Airbyte monorepo operations.")
app.command(repo_app)

# Create the connector sub-app under repo
connector_app = App(name="connector", help="Connector operations in the monorepo.")
repo_app.command(connector_app)


@connector_app.command(name="list")
def list_connectors(
    repo_path: Annotated[
        str,
        Parameter(help="Absolute path to the Airbyte monorepo."),
    ],
    certified_only: Annotated[
        bool,
        Parameter(help="Include only certified connectors."),
    ] = False,
    modified_only: Annotated[
        bool,
        Parameter(help="Include only modified connectors (requires PR context)."),
    ] = False,
    local_cdk: Annotated[
        bool,
        Parameter(
            help=(
                "Include connectors using local CDK reference. "
                "When combined with --modified-only, adds local-CDK connectors to the modified set."
            )
        ),
    ] = False,
    language: Annotated[
        list[str] | None,
        Parameter(help="Languages to include (python, java, low-code, manifest-only)."),
    ] = None,
    exclude_language: Annotated[
        list[str] | None,
        Parameter(help="Languages to exclude."),
    ] = None,
    connector_type: Annotated[
        str | None,
        Parameter(
            help=(
                "Connector types to include (source, destination). "
                "Accepts CSV or newline-delimited values."
            )
        ),
    ] = None,
    min_support_level: Annotated[
        str | None,
        Parameter(
            help=(
                "Minimum support level (inclusive). "
                "Accepts integer (100, 200, 300) or keyword (archived, community, certified)."
            )
        ),
    ] = None,
    max_support_level: Annotated[
        str | None,
        Parameter(
            help=(
                "Maximum support level (inclusive). "
                "Accepts integer (100, 200, 300) or keyword (archived, community, certified)."
            )
        ),
    ] = None,
    pr: Annotated[
        str | None,
        Parameter(help="PR number or GitHub URL for modification detection."),
    ] = None,
    exclude_connectors: Annotated[
        list[str] | None,
        Parameter(
            help=(
                "Connectors to exclude from results. "
                "Accepts CSV or newline-delimited values. Can be specified multiple times."
            )
        ),
    ] = None,
    force_include_connectors: Annotated[
        list[str] | None,
        Parameter(
            help=(
                "Connectors to force-include regardless of other filters. "
                "Accepts CSV or newline-delimited values. Can be specified multiple times."
            )
        ),
    ] = None,
    output_format: Annotated[
        OutputFormat,
        Parameter(
            help=(
                'Output format: "csv" (comma-separated), '
                '"lines" (one connector per line), '
                '"json-gh-matrix" (GitHub Actions matrix JSON).'
            )
        ),
    ] = "lines",
) -> None:
    """List connectors in the Airbyte monorepo with filtering options."""
    # Validate mutually exclusive flags
    if language and exclude_language:
        exit_with_error("Cannot specify both --language and --exclude-language.")

    # Map CLI flags to MCP tool parameters
    certified: bool | None = True if certified_only else None
    modified: bool | None = True if modified_only else None

    language_filter: set[str] | None = set(language) if language else None
    language_exclude: set[str] | None = (
        set(exclude_language) if exclude_language else None
    )

    # Parse connector type filter
    connector_type_filter: set[str] | None = None
    if connector_type:
        try:
            connector_type_filter = _parse_connector_types(connector_type)
        except ValueError as e:
            exit_with_error(str(e))

    # Parse support level filters
    min_level: int | None = None
    max_level: int | None = None
    if min_support_level:
        try:
            min_level = _parse_support_level(min_support_level)
        except ValueError as e:
            exit_with_error(str(e))
    if max_support_level:
        try:
            max_level = _parse_support_level(max_support_level)
        except ValueError as e:
            exit_with_error(str(e))

    # Parse exclude/force-include connector lists (merge multiple flag values)
    exclude_set: set[str] = set()
    if exclude_connectors:
        for value in exclude_connectors:
            exclude_set.update(_parse_connector_names(value))

    force_include_set: set[str] = set()
    if force_include_connectors:
        for value in force_include_connectors:
            force_include_set.update(_parse_connector_names(value))

    result = list_connectors_in_repo(
        repo_path=repo_path,
        certified=certified,
        modified=modified,
        language_filter=language_filter,
        language_exclude=language_exclude,
        pr_num_or_url=pr,
    )
    connectors = list(result.connectors)
    repo_path_obj = Path(repo_path)

    # Add connectors with local CDK reference if --local-cdk flag is set
    if local_cdk:
        local_cdk_connectors = get_connectors_with_local_cdk(repo_path)
        connectors = sorted(set(connectors) | local_cdk_connectors)

    # Apply connector type filter
    if connector_type_filter:
        connectors = [
            name
            for name in connectors
            if _get_connector_type(name) in connector_type_filter
        ]

    # Apply support level filters (requires reading metadata)
    if min_level is not None or max_level is not None:
        filtered_connectors = []
        for name in connectors:
            connector_dir = repo_path_obj / CONNECTOR_PATH_PREFIX / name
            level = _get_connector_support_level(connector_dir)
            if level is None:
                continue  # Skip connectors without support level
            if min_level is not None and level < min_level:
                continue
            if max_level is not None and level > max_level:
                continue
            filtered_connectors.append(name)
        connectors = filtered_connectors

    # Apply exclude filter
    if exclude_set:
        connectors = [name for name in connectors if name not in exclude_set]

    # Apply force-include (union, overrides all other filters)
    if force_include_set:
        connectors_set = set(connectors)
        connectors_set.update(force_include_set)
        connectors = sorted(connectors_set)

    if output_format == "csv":
        console.print(",".join(connectors))
    elif output_format == "lines":
        for name in connectors:
            console.print(name)
    elif output_format == "json-gh-matrix":
        # Build matrix with full connector metadata
        include_list = []
        for name in connectors:
            connector_dir = repo_path_obj / CONNECTOR_PATH_PREFIX / name
            include_list.append(_get_connector_info(name, connector_dir))
        matrix = {"include": include_list}
        print_json(matrix)


def _write_github_step_outputs(outputs: dict[str, str | int | None]) -> None:
    """Write outputs to GitHub Actions step output file if running in CI."""
    github_output = os.getenv("GITHUB_OUTPUT")
    if not (os.getenv("CI") and github_output):
        return

    with open(github_output, "a", encoding="utf-8") as f:
        for key, value in outputs.items():
            if value is None:
                continue
            f.write(f"{key}={value}\n")


@connector_app.command(name="info")
def connector_info(
    connector_name: Annotated[
        str,
        Parameter(help="Name of the connector (e.g., source-github)."),
    ],
    repo_path: Annotated[
        str | None,
        Parameter(help="Path to the Airbyte monorepo. Can be inferred from context."),
    ] = None,
) -> None:
    """Get metadata for a single connector.

    Prints JSON output with connector metadata. When running in GitHub Actions
    (CI env var set), also writes each field to GitHub step outputs.
    """
    # Infer repo_path from current directory if not provided
    if repo_path is None:
        # Check if we're in an airbyte repo by looking for the connectors directory
        cwd = Path.cwd()
        # Walk up to find airbyte-integrations/connectors
        for parent in [cwd, *cwd.parents]:
            if (parent / CONNECTOR_PATH_PREFIX).exists():
                repo_path = str(parent)
                break
        if repo_path is None:
            exit_with_error(
                "Could not infer repo path. Please provide --repo-path or run from within the Airbyte monorepo."
            )

    repo_path_obj = Path(repo_path)
    connector_dir = repo_path_obj / CONNECTOR_PATH_PREFIX / connector_name

    if not connector_dir.exists():
        exit_with_error(f"Connector directory not found: {connector_dir}")

    info = _get_connector_info(connector_name, connector_dir)

    # Print JSON output
    print_json(info)

    # Write to GitHub step outputs if in CI
    _write_github_step_outputs(info)


BumpType = Literal["patch", "minor", "major"]


@connector_app.command(name="bump-version")
def bump_version(
    name: Annotated[
        str,
        Parameter(help="Connector technical name (e.g., source-github)."),
    ],
    repo_path: Annotated[
        str,
        Parameter(help="Absolute path to the Airbyte monorepo."),
    ],
    bump_type: Annotated[
        BumpType | None,
        Parameter(help="Version bump type: patch, minor, or major."),
    ] = None,
    new_version: Annotated[
        str | None,
        Parameter(help="Explicit new version (overrides --bump-type if provided)."),
    ] = None,
    changelog_message: Annotated[
        str | None,
        Parameter(help="Message to add to changelog."),
    ] = None,
    pr_number: Annotated[
        int | None,
        Parameter(help="PR number for changelog entry."),
    ] = None,
    dry_run: Annotated[
        bool,
        Parameter(help="Show what would be changed without modifying files."),
    ] = False,
) -> None:
    """Bump a connector's version across all relevant files.

    Updates version in metadata.yaml (always), pyproject.toml (if exists),
    and documentation changelog (if --changelog-message provided).

    Either --bump-type or --new-version must be provided.
    """
    # Call capability function and handle specific errors
    try:
        result = bump_connector_version(
            repo_path=repo_path,
            connector_name=name,
            bump_type=bump_type,
            new_version=new_version,
            changelog_message=changelog_message,
            pr_number=pr_number,
            dry_run=dry_run,
        )
    except ConnectorNotFoundError as e:
        exit_with_error(str(e))
    except VersionNotFoundError as e:
        exit_with_error(str(e))
    except InvalidVersionError as e:
        exit_with_error(str(e))
    except ValueError as e:
        exit_with_error(str(e))

    # Build output matching the issue spec
    output = {
        "connector": result.connector,
        "previous_version": result.previous_version,
        "new_version": result.new_version,
        "files_modified": result.files_modified,
        "dry_run": result.dry_run,
    }
    print_json(output)

    # Write to GitHub step outputs if in CI
    _write_github_step_outputs(
        {
            "connector": result.connector,
            "previous_version": result.previous_version,
            "new_version": result.new_version,
        }
    )
