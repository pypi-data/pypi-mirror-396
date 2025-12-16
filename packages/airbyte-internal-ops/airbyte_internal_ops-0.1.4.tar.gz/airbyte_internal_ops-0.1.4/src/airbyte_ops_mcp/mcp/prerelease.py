# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""MCP tools for triggering connector pre-release workflows.

This module provides MCP tools for triggering the publish-connectors-prerelease
workflow in the airbytehq/airbyte repository via GitHub's workflow dispatch API.
"""

from __future__ import annotations

import base64
import os
from typing import Annotated, Literal

import requests
import yaml
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from airbyte_ops_mcp.mcp._mcp_utils import ToolDomain, mcp_tool, register_mcp_tools

GITHUB_API_BASE = "https://api.github.com"
DEFAULT_REPO_OWNER = "airbytehq"
DEFAULT_REPO_NAME = "airbyte"
DEFAULT_BRANCH = "master"
PRERELEASE_WORKFLOW_FILE = "publish-connectors-prerelease-command.yml"
CONNECTOR_PATH_PREFIX = "airbyte-integrations/connectors"


class PRHeadInfo(BaseModel):
    """Information about a PR's head commit."""

    ref: str
    sha: str
    short_sha: str


class PrereleaseWorkflowResult(BaseModel):
    """Response model for publish_connector_to_airbyte_registry MCP tool."""

    success: bool
    message: str
    workflow_url: str | None = None
    connector_name: str | None = None
    pr_number: int | None = None
    docker_image: str | None = None
    docker_image_tag: str | None = None


def _get_github_token() -> str:
    """Get GitHub token from environment.

    Checks for tokens in order of specificity:
    1. GITHUB_CONNECTOR_PUBLISHING_PAT (most specific)
    2. GITHUB_CI_WORKFLOW_TRIGGER_PAT (general workflow triggering)
    3. GITHUB_TOKEN (fallback)

    Returns:
        GitHub token string.

    Raises:
        ValueError: If no GitHub token environment variable is set.
    """
    token = (
        os.getenv("GITHUB_CONNECTOR_PUBLISHING_PAT")
        or os.getenv("GITHUB_CI_WORKFLOW_TRIGGER_PAT")
        or os.getenv("GITHUB_TOKEN")
    )
    if not token:
        raise ValueError(
            "No GitHub token found. Set GITHUB_CONNECTOR_PUBLISHING_PAT, "
            "GITHUB_CI_WORKFLOW_TRIGGER_PAT, or GITHUB_TOKEN environment variable "
            "with 'actions:write' permission."
        )
    return token


def _get_pr_head_info(
    owner: str,
    repo: str,
    pr_number: int,
    token: str,
) -> PRHeadInfo:
    """Get the head ref and SHA for a PR.

    Args:
        owner: Repository owner (e.g., "airbytehq")
        repo: Repository name (e.g., "airbyte")
        pr_number: Pull request number
        token: GitHub API token

    Returns:
        PRHeadInfo with ref, sha, and short_sha.

    Raises:
        ValueError: If PR not found or API error.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 404:
        raise ValueError(f"PR {owner}/{repo}#{pr_number} not found")
    response.raise_for_status()

    pr_data = response.json()
    sha = pr_data["head"]["sha"]
    return PRHeadInfo(
        ref=pr_data["head"]["ref"],
        sha=sha,
        short_sha=sha[:10],
    )


def _get_connector_metadata(
    owner: str,
    repo: str,
    connector_name: str,
    ref: str,
    token: str,
) -> dict | None:
    """Fetch and parse connector metadata.yaml from the repository.

    Args:
        owner: Repository owner (e.g., "airbytehq")
        repo: Repository name (e.g., "airbyte")
        connector_name: Connector name (e.g., "source-github")
        ref: Git ref to fetch from (branch name or SHA)
        token: GitHub API token

    Returns:
        Parsed metadata dictionary, or None if not found.
    """
    metadata_path = f"{CONNECTOR_PATH_PREFIX}/{connector_name}/metadata.yaml"
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{metadata_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    params = {"ref": ref}

    response = requests.get(url, headers=headers, params=params, timeout=30)

    # Guard: Return None if metadata file not found
    if response.status_code == 404:
        return None

    response.raise_for_status()

    content_data = response.json()

    # Guard: Return None if content is not base64 encoded
    if content_data.get("encoding") != "base64":
        return None

    content = base64.b64decode(content_data["content"]).decode("utf-8")
    return yaml.safe_load(content)


def _trigger_workflow_dispatch(
    owner: str,
    repo: str,
    workflow_file: str,
    ref: str,
    inputs: dict,
    token: str,
) -> str:
    """Trigger a GitHub Actions workflow via workflow_dispatch.

    Args:
        owner: Repository owner (e.g., "airbytehq")
        repo: Repository name (e.g., "airbyte")
        workflow_file: Workflow file name (e.g., "publish-connectors-prerelease-command.yml")
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


@mcp_tool(
    ToolDomain.REPO,
    read_only=False,
    destructive=False,
    idempotent=False,
    open_world=True,
)
def publish_connector_to_airbyte_registry(
    connector_name: Annotated[
        str,
        Field(
            description="The connector name to publish (e.g., 'source-github', 'destination-postgres')"
        ),
    ],
    pr_number: Annotated[
        int,
        Field(description="The pull request number containing the connector changes"),
    ],
    prerelease: Annotated[
        Literal[True],
        Field(
            default=True,
            description="Must be True. Only prerelease publishing is supported at this time.",
        ),
    ],
) -> PrereleaseWorkflowResult:
    """Publish a connector to the Airbyte registry.

    Currently only supports pre-release publishing. This tool triggers the
    publish-connectors-prerelease workflow in the airbytehq/airbyte repository,
    which publishes a pre-release version of the specified connector from the PR branch.

    Pre-release versions are tagged with the format: {version}-dev.{10-char-git-sha}
    These versions are available for version pinning via the scoped_configuration API.

    Requires GITHUB_CONNECTOR_PUBLISHING_PAT or GITHUB_TOKEN environment variable
    with 'actions:write' permission.
    """
    # Guard: Only prerelease publishing is supported
    if prerelease is not True:
        raise NotImplementedError(
            "Non-prerelease publishing is not implemented yet. Set prerelease=True."
        )

    # Guard: Check for required token
    token = _get_github_token()

    # Get the PR's head ref and SHA
    head_info = _get_pr_head_info(
        DEFAULT_REPO_OWNER, DEFAULT_REPO_NAME, pr_number, token
    )

    # Prepare workflow inputs
    # The workflow expects these inputs from slash-command-dispatch
    # Note: The workflow auto-detects modified connectors from the PR
    workflow_inputs = {
        "repo": f"{DEFAULT_REPO_OWNER}/{DEFAULT_REPO_NAME}",
        "gitref": head_info.ref,
        "pr": str(pr_number),
    }

    # Trigger the workflow on the default branch
    # The workflow will checkout the PR branch via inputs.gitref
    workflow_url = _trigger_workflow_dispatch(
        owner=DEFAULT_REPO_OWNER,
        repo=DEFAULT_REPO_NAME,
        workflow_file=PRERELEASE_WORKFLOW_FILE,
        ref=DEFAULT_BRANCH,
        inputs=workflow_inputs,
        token=token,
    )

    # Try to compute docker_image and docker_image_tag from connector metadata
    docker_image: str | None = None
    docker_image_tag: str | None = None
    metadata = _get_connector_metadata(
        DEFAULT_REPO_OWNER,
        DEFAULT_REPO_NAME,
        connector_name,
        head_info.sha,
        token,
    )
    if metadata and "data" in metadata:
        data = metadata["data"]
        docker_image = data.get("dockerRepository")
        base_version = data.get("dockerImageTag")
        if base_version:
            docker_image_tag = f"{base_version}-dev.{head_info.short_sha}"

    return PrereleaseWorkflowResult(
        success=True,
        message=f"Successfully triggered pre-release workflow for {connector_name} from PR #{pr_number}",
        workflow_url=workflow_url,
        connector_name=connector_name,
        pr_number=pr_number,
        docker_image=docker_image,
        docker_image_tag=docker_image_tag,
    )


def register_prerelease_tools(app: FastMCP) -> None:
    """Register pre-release workflow tools with the FastMCP app.

    Args:
        app: FastMCP application instance
    """
    register_mcp_tools(app, domain=ToolDomain.REPO)
