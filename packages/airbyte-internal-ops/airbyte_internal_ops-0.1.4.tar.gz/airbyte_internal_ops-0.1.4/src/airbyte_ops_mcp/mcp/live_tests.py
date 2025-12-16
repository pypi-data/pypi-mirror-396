# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""MCP tools for live connection tests.

This module provides MCP tools for triggering live validation and regression tests
on Airbyte Cloud connections via GitHub Actions workflows. Tests run asynchronously
in GitHub Actions and results can be polled via workflow status.
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime
from enum import Enum
from typing import Annotated, Any

import requests
from airbyte.cloud import CloudWorkspace
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from airbyte_ops_mcp.mcp._mcp_utils import ToolDomain, mcp_tool, register_mcp_tools

logger = logging.getLogger(__name__)

# =============================================================================
# GitHub Workflow Configuration
# =============================================================================

GITHUB_API_BASE = "https://api.github.com"
LIVE_TEST_REPO_OWNER = "airbytehq"
LIVE_TEST_REPO_NAME = "airbyte-ops-mcp"
LIVE_TEST_DEFAULT_BRANCH = "main"
LIVE_TEST_WORKFLOW_FILE = "connector-live-test.yml"
REGRESSION_TEST_WORKFLOW_FILE = "connector-regression-test.yml"


# =============================================================================
# GitHub API Helper Functions
# =============================================================================


def _get_github_token() -> str:
    """Get GitHub token from environment.

    Checks for tokens in order of specificity:
    1. GITHUB_CI_WORKFLOW_TRIGGER_PAT (general workflow triggering)
    2. GITHUB_TOKEN (fallback)

    Returns:
        GitHub token string.

    Raises:
        ValueError: If no GitHub token environment variable is set.
    """
    token = os.getenv("GITHUB_CI_WORKFLOW_TRIGGER_PAT") or os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "No GitHub token found. Set GITHUB_CI_WORKFLOW_TRIGGER_PAT or GITHUB_TOKEN "
            "environment variable with 'actions:write' permission."
        )
    return token


def _trigger_workflow_dispatch(
    owner: str,
    repo: str,
    workflow_file: str,
    ref: str,
    inputs: dict[str, Any],
    token: str,
) -> str:
    """Trigger a GitHub Actions workflow via workflow_dispatch.

    Args:
        owner: Repository owner (e.g., "airbytehq")
        repo: Repository name (e.g., "airbyte-ops-mcp")
        workflow_file: Workflow file name (e.g., "connector-live-test.yml")
        ref: Git ref to run the workflow on (branch name)
        inputs: Workflow inputs dictionary
        token: GitHub API token

    Returns:
        URL to view workflow runs.

    Raises:
        requests.HTTPError: If API request fails.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/workflows/{workflow_file}/dispatches"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {
        "ref": ref,
        "inputs": inputs,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()

    # workflow_dispatch returns 204 No Content on success
    # Return URL to view workflow runs
    return f"https://github.com/{owner}/{repo}/actions/workflows/{workflow_file}"


def _get_workflow_run_status(
    owner: str,
    repo: str,
    run_id: int,
    token: str,
) -> dict[str, Any]:
    """Get workflow run details from GitHub API.

    Args:
        owner: Repository owner (e.g., "airbytehq")
        repo: Repository name (e.g., "airbyte-ops-mcp")
        run_id: Workflow run ID
        token: GitHub API token

    Returns:
        Workflow run data dictionary.

    Raises:
        ValueError: If workflow run not found.
        requests.HTTPError: If API request fails.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/actions/runs/{run_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 404:
        raise ValueError(f"Workflow run {owner}/{repo}/actions/runs/{run_id} not found")
    response.raise_for_status()

    return response.json()


# =============================================================================
# Pydantic Models for Test Results
# =============================================================================


class TestRunStatus(str, Enum):
    """Status of a test run."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class TestPhaseStatus(str, Enum):
    """Status of a test phase (live or regression)."""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ValidationResultModel(BaseModel):
    """Result of a single validation check."""

    name: str = Field(description="Name of the validation check")
    passed: bool = Field(description="Whether the validation passed")
    message: str = Field(description="Human-readable result message")
    errors: list[str] = Field(
        default_factory=list,
        description="List of error messages if validation failed",
    )


class StreamComparisonResultModel(BaseModel):
    """Result of comparing a single stream between control and target."""

    stream_name: str = Field(description="Name of the stream")
    passed: bool = Field(description="Whether all comparisons passed")
    control_record_count: int = Field(description="Number of records in control")
    target_record_count: int = Field(description="Number of records in target")
    missing_pks: list[str] = Field(
        default_factory=list,
        description="Primary keys present in control but missing in target",
    )
    differing_records: int = Field(
        default=0,
        description="Number of records that differ between control and target",
    )
    message: str = Field(description="Human-readable comparison summary")


class LivePhaseResult(BaseModel):
    """Results from the live test phase."""

    status: TestPhaseStatus = Field(description="Status of the live phase")
    catalog_validations: list[ValidationResultModel] = Field(
        default_factory=list,
        description="Results of catalog validation checks",
    )
    record_validations: list[ValidationResultModel] = Field(
        default_factory=list,
        description="Results of record validation checks",
    )
    record_count: int = Field(
        default=0,
        description="Total number of records read",
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if the phase failed",
    )


class RegressionPhaseResult(BaseModel):
    """Results from the regression test phase."""

    status: TestPhaseStatus = Field(description="Status of the regression phase")
    baseline_version: str | None = Field(
        default=None,
        description="Version of the baseline (control) connector",
    )
    stream_comparisons: list[StreamComparisonResultModel] = Field(
        default_factory=list,
        description="Per-stream comparison results",
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if the phase failed",
    )


class LiveConnectionTestResult(BaseModel):
    """Complete result of a live connection test run."""

    run_id: str = Field(description="Unique identifier for this test run")
    connection_id: str = Field(description="The connection being tested")
    workspace_id: str = Field(description="The workspace containing the connection")
    status: TestRunStatus = Field(description="Overall status of the test run")
    target_version: str | None = Field(
        default=None,
        description="Version of the target connector being tested",
    )
    baseline_version: str | None = Field(
        default=None,
        description="Version of the baseline connector (if regression ran)",
    )
    evaluation_mode: str = Field(
        default="diagnostic",
        description="Evaluation mode used (diagnostic or strict)",
    )
    skip_regression_tests: bool = Field(
        default=False,
        description="Whether regression tests were skipped by request",
    )
    live_phase: LivePhaseResult | None = Field(
        default=None,
        description="Results from the live test phase",
    )
    regression_phase: RegressionPhaseResult | None = Field(
        default=None,
        description="Results from the regression test phase",
    )
    artifacts: dict[str, str] = Field(
        default_factory=dict,
        description="Paths to generated artifacts (JSONL, DuckDB, HAR files)",
    )
    human_summary: str = Field(
        default="",
        description="Human-readable summary of the test results",
    )
    started_at: datetime | None = Field(
        default=None,
        description="When the test run started",
    )
    completed_at: datetime | None = Field(
        default=None,
        description="When the test run completed",
    )
    test_description: str | None = Field(
        default=None,
        description="Optional description/context for this test run",
    )


class RunLiveConnectionTestsResponse(BaseModel):
    """Response from starting a live connection test via GitHub Actions workflow."""

    run_id: str = Field(description="Unique identifier for the test run")
    status: TestRunStatus = Field(description="Initial status of the test run")
    message: str = Field(description="Human-readable status message")
    workflow_url: str | None = Field(
        default=None,
        description="URL to view the GitHub Actions workflow runs",
    )


# =============================================================================
# MCP Tools
# =============================================================================


@mcp_tool(
    ToolDomain.LIVE_TESTS,
    read_only=False,
    idempotent=False,
    open_world=True,
)
def run_live_connection_tests(
    connection_id: Annotated[str, "The Airbyte Cloud connection ID to test"],
    command: Annotated[
        str,
        "Airbyte command to run: 'spec', 'check', 'discover', or 'read'",
    ] = "check",
    workspace_id: Annotated[
        str | None,
        "Optional Airbyte Cloud workspace ID. If provided, validates that the connection "
        "belongs to this workspace before triggering tests. If omitted, no validation is done.",
    ] = None,
    skip_regression_tests: Annotated[
        bool,
        "If True, run only live tests (connector-live-test workflow). "
        "If False, run regression tests comparing target vs control versions "
        "(connector-regression-test workflow).",
    ] = True,
    connector_image: Annotated[
        str | None,
        "Optional connector image with tag for live tests (e.g., 'airbyte/source-github:1.0.0'). "
        "If not provided, auto-detected from connection. Only used when skip_regression_tests=True.",
    ] = None,
    target_image: Annotated[
        str | None,
        "Target connector image (new version) with tag for regression tests "
        "(e.g., 'airbyte/source-github:2.0.0'). Optional if connector_name is provided. "
        "Only used when skip_regression_tests=False.",
    ] = None,
    control_image: Annotated[
        str | None,
        "Control connector image (baseline version) with tag for regression tests "
        "(e.g., 'airbyte/source-github:1.0.0'). Optional if connection_id is provided "
        "(auto-detected from connection). Only used when skip_regression_tests=False.",
    ] = None,
    connector_name: Annotated[
        str | None,
        "Connector name to build target image from source for regression tests "
        "(e.g., 'source-pokeapi'). If provided, builds the target image locally. "
        "Only used when skip_regression_tests=False.",
    ] = None,
) -> RunLiveConnectionTestsResponse:
    """Start a live connection test run via GitHub Actions workflow.

    This tool triggers either the live-test or regression-test workflow depending
    on the skip_regression_tests parameter:

    - skip_regression_tests=True (default): Triggers connector-live-test workflow.
      Runs the specified command against the connection and validates the output.

    - skip_regression_tests=False: Triggers connector-regression-test workflow.
      Compares the target connector version against a control (baseline) version.
      For regression tests, provide either target_image or connector_name to specify
      the target version.

    Returns immediately with a run_id and workflow URL. Check the workflow URL
    to monitor progress and view results.

    Requires GITHUB_CI_WORKFLOW_TRIGGER_PAT or GITHUB_TOKEN environment variable
    with 'actions:write' permission.
    """
    # Generate a unique run ID for tracking
    run_id = str(uuid.uuid4())

    # Get GitHub token
    try:
        token = _get_github_token()
    except ValueError as e:
        return RunLiveConnectionTestsResponse(
            run_id=run_id,
            status=TestRunStatus.FAILED,
            message=str(e),
            workflow_url=None,
        )

    # Validate workspace membership if workspace_id is provided
    if workspace_id:
        try:
            workspace = CloudWorkspace(workspace_id=workspace_id)
            # This will raise an exception if the connection doesn't belong to the workspace
            workspace.get_connection(connection_id)
        except Exception as e:
            return RunLiveConnectionTestsResponse(
                run_id=run_id,
                status=TestRunStatus.FAILED,
                message=f"Connection {connection_id} validation failed for workspace {workspace_id}: {e}",
                workflow_url=None,
            )

    if skip_regression_tests:
        # Live test workflow
        workflow_inputs: dict[str, str] = {
            "connection_id": connection_id,
            "command": command,
        }
        if connector_image:
            workflow_inputs["connector_image"] = connector_image

        try:
            workflow_url = _trigger_workflow_dispatch(
                owner=LIVE_TEST_REPO_OWNER,
                repo=LIVE_TEST_REPO_NAME,
                workflow_file=LIVE_TEST_WORKFLOW_FILE,
                ref=LIVE_TEST_DEFAULT_BRANCH,
                inputs=workflow_inputs,
                token=token,
            )
        except Exception as e:
            logger.exception("Failed to trigger live test workflow")
            return RunLiveConnectionTestsResponse(
                run_id=run_id,
                status=TestRunStatus.FAILED,
                message=f"Failed to trigger live-test workflow: {e}",
                workflow_url=None,
            )

        return RunLiveConnectionTestsResponse(
            run_id=run_id,
            status=TestRunStatus.QUEUED,
            message=f"Live-test workflow triggered for connection {connection_id}. "
            f"View progress at: {workflow_url}",
            workflow_url=workflow_url,
        )

    # Regression test workflow (skip_regression_tests=False)
    # Validate that we have enough info to run regression tests
    if not target_image and not connector_name:
        return RunLiveConnectionTestsResponse(
            run_id=run_id,
            status=TestRunStatus.FAILED,
            message=(
                "For regression tests (skip_regression_tests=False), provide either "
                "target_image or connector_name so the workflow can determine the target image."
            ),
            workflow_url=None,
        )

    workflow_inputs = {
        "connection_id": connection_id,
        "command": command,
    }
    if target_image:
        workflow_inputs["target_image"] = target_image
    if control_image:
        workflow_inputs["control_image"] = control_image
    if connector_name:
        workflow_inputs["connector_name"] = connector_name

    try:
        workflow_url = _trigger_workflow_dispatch(
            owner=LIVE_TEST_REPO_OWNER,
            repo=LIVE_TEST_REPO_NAME,
            workflow_file=REGRESSION_TEST_WORKFLOW_FILE,
            ref=LIVE_TEST_DEFAULT_BRANCH,
            inputs=workflow_inputs,
            token=token,
        )
    except Exception as e:
        logger.exception("Failed to trigger regression test workflow")
        return RunLiveConnectionTestsResponse(
            run_id=run_id,
            status=TestRunStatus.FAILED,
            message=f"Failed to trigger regression-test workflow: {e}",
            workflow_url=None,
        )

    return RunLiveConnectionTestsResponse(
        run_id=run_id,
        status=TestRunStatus.QUEUED,
        message=f"Regression-test workflow triggered for connection {connection_id}. "
        f"View progress at: {workflow_url}",
        workflow_url=workflow_url,
    )


# =============================================================================
# Registration
# =============================================================================


def register_live_tests_tools(app: FastMCP) -> None:
    """Register live tests tools with the FastMCP app.

    Args:
        app: FastMCP application instance
    """
    register_mcp_tools(app, domain=ToolDomain.LIVE_TESTS)
