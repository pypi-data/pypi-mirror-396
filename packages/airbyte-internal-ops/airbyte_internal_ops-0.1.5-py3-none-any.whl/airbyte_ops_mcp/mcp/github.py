# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""MCP tools for GitHub workflow and Docker operations.

This module provides MCP tools for checking GitHub Actions workflow status,
Docker image availability, and other related operations.
"""

from __future__ import annotations

import os
import re
from typing import Annotated

import requests
from fastmcp import FastMCP
from pydantic import BaseModel, Field

from airbyte_ops_mcp.mcp._mcp_utils import ToolDomain, mcp_tool, register_mcp_tools

GITHUB_API_BASE = "https://api.github.com"
DOCKERHUB_API_BASE = "https://hub.docker.com/v2"


class WorkflowRunStatus(BaseModel):
    """Response model for check_workflow_status MCP tool."""

    run_id: int
    status: str
    conclusion: str | None
    workflow_name: str
    head_branch: str
    head_sha: str
    html_url: str
    created_at: str
    updated_at: str
    run_started_at: str | None = None
    jobs_url: str


def _get_github_token() -> str:
    """Get GitHub token from environment.

    Returns:
        GitHub token string.

    Raises:
        ValueError: If GITHUB_TOKEN environment variable is not set.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_TOKEN environment variable is required. "
            "Please set it to a GitHub personal access token."
        )
    return token


def _parse_workflow_url(url: str) -> tuple[str, str, int]:
    """Parse a GitHub Actions workflow run URL into components.

    Args:
        url: GitHub Actions workflow run URL
            (e.g., "https://github.com/owner/repo/actions/runs/12345")

    Returns:
        Tuple of (owner, repo, run_id)

    Raises:
        ValueError: If URL format is invalid.
    """
    pattern = r"https://github\.com/([^/]+)/([^/]+)/actions/runs/(\d+)"
    match = re.match(pattern, url)
    if not match:
        raise ValueError(
            f"Invalid workflow URL format: {url}. "
            "Expected format: https://github.com/owner/repo/actions/runs/12345"
        )
    return match.group(1), match.group(2), int(match.group(3))


def _get_workflow_run(
    owner: str,
    repo: str,
    run_id: int,
    token: str,
) -> dict:
    """Get workflow run details from GitHub API.

    Args:
        owner: Repository owner (e.g., "airbytehq")
        repo: Repository name (e.g., "airbyte")
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


@mcp_tool(
    ToolDomain.REPO,
    read_only=True,
    idempotent=True,
    open_world=True,
)
def check_workflow_status(
    workflow_url: Annotated[
        str | None,
        Field(
            description="Full GitHub Actions workflow run URL (e.g., 'https://github.com/owner/repo/actions/runs/12345')"
        ),
    ] = None,
    owner: Annotated[
        str | None,
        Field(description="Repository owner (e.g., 'airbytehq')"),
    ] = None,
    repo: Annotated[
        str | None,
        Field(description="Repository name (e.g., 'airbyte')"),
    ] = None,
    run_id: Annotated[
        int | None,
        Field(description="Workflow run ID"),
    ] = None,
) -> WorkflowRunStatus:
    """Check the status of a GitHub Actions workflow run.

    You can provide either:
    - A full workflow URL (workflow_url parameter), OR
    - The component parts (owner, repo, run_id parameters)

    Returns the current status, conclusion, and other details about the workflow run.

    Requires GITHUB_TOKEN environment variable.
    """
    # Guard: Validate input parameters
    if workflow_url:
        # Parse URL to get components
        owner, repo, run_id = _parse_workflow_url(workflow_url)
    elif owner and repo and run_id:
        # Use provided components
        pass
    else:
        raise ValueError(
            "Must provide either workflow_url OR all of (owner, repo, run_id)"
        )

    # Guard: Check for required token
    token = _get_github_token()

    # Get workflow run details
    run_data = _get_workflow_run(owner, repo, run_id, token)

    return WorkflowRunStatus(
        run_id=run_data["id"],
        status=run_data["status"],
        conclusion=run_data["conclusion"],
        workflow_name=run_data["name"],
        head_branch=run_data["head_branch"],
        head_sha=run_data["head_sha"],
        html_url=run_data["html_url"],
        created_at=run_data["created_at"],
        updated_at=run_data["updated_at"],
        run_started_at=run_data.get("run_started_at"),
        jobs_url=run_data["jobs_url"],
    )


class DockerImageInfo(BaseModel):
    """Response model for get_docker_image_info MCP tool."""

    exists: bool
    image: str
    tag: str
    full_name: str
    digest: str | None = None
    last_updated: str | None = None
    size_bytes: int | None = None
    architecture: str | None = None
    os: str | None = None


def _check_dockerhub_image(
    image: str,
    tag: str,
) -> dict | None:
    """Check if a Docker image tag exists on DockerHub.

    Args:
        image: Docker image name (e.g., "airbyte/source-github")
        tag: Image tag (e.g., "2.1.5-dev.abc1234567")

    Returns:
        Tag data dictionary if found, None if not found.
    """
    # DockerHub API endpoint for tag info
    url = f"{DOCKERHUB_API_BASE}/repositories/{image}/tags/{tag}"

    response = requests.get(url, timeout=30)
    if response.status_code == 404:
        return None
    response.raise_for_status()

    return response.json()


@mcp_tool(
    ToolDomain.REPO,
    read_only=True,
    idempotent=True,
    open_world=True,
)
def get_docker_image_info(
    image: Annotated[
        str,
        Field(description="Docker image name (e.g., 'airbyte/source-github')"),
    ],
    tag: Annotated[
        str,
        Field(description="Image tag (e.g., '2.1.5-dev.abc1234567')"),
    ],
) -> DockerImageInfo:
    """Check if a Docker image exists on DockerHub.

    Returns information about the image if it exists, or indicates if it doesn't exist.
    This is useful for confirming that a pre-release connector was successfully published.
    """
    full_name = f"{image}:{tag}"
    tag_data = _check_dockerhub_image(image, tag)

    if not tag_data:
        return DockerImageInfo(
            exists=False,
            image=image,
            tag=tag,
            full_name=full_name,
        )

    # Extract image details from the first image in the list (if available)
    images = tag_data.get("images", [])
    first_image = images[0] if images else {}

    return DockerImageInfo(
        exists=True,
        image=image,
        tag=tag,
        full_name=full_name,
        digest=tag_data.get("digest"),
        last_updated=tag_data.get("last_updated"),
        size_bytes=first_image.get("size"),
        architecture=first_image.get("architecture"),
        os=first_image.get("os"),
    )


def register_github_tools(app: FastMCP) -> None:
    """Register GitHub tools with the FastMCP app.

    Args:
        app: FastMCP application instance
    """
    register_mcp_tools(app, domain=ToolDomain.REPO)
