# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""CLI commands for GitHub operations.

Commands:
    airbyte-ops gh workflow status - Check GitHub Actions workflow status
"""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from airbyte_ops_mcp.cli._base import app
from airbyte_ops_mcp.cli._shared import exit_with_error, print_json
from airbyte_ops_mcp.mcp.github import check_workflow_status

# Create the gh sub-app
gh_app = App(name="gh", help="GitHub operations.")
app.command(gh_app)

# Create the workflow sub-app under gh
workflow_app = App(name="workflow", help="GitHub Actions workflow operations.")
gh_app.command(workflow_app)


@workflow_app.command(name="status")
def workflow_status(
    url: Annotated[
        str | None,
        Parameter(
            help="Full GitHub Actions workflow run URL "
            "(e.g., 'https://github.com/owner/repo/actions/runs/12345')."
        ),
    ] = None,
    owner: Annotated[
        str | None,
        Parameter(help="Repository owner (e.g., 'airbytehq')."),
    ] = None,
    repo: Annotated[
        str | None,
        Parameter(help="Repository name (e.g., 'airbyte')."),
    ] = None,
    run_id: Annotated[
        int | None,
        Parameter(help="Workflow run ID."),
    ] = None,
) -> None:
    """Check the status of a GitHub Actions workflow run.

    Provide either --url OR all of (--owner, --repo, --run-id).
    """
    # Validate input parameters
    if url:
        if owner or repo or run_id:
            exit_with_error(
                "Cannot specify --url together with --owner/--repo/--run-id. "
                "Use either --url OR the component parts."
            )
    elif not (owner and repo and run_id):
        exit_with_error(
            "Must provide either --url OR all of (--owner, --repo, --run-id)."
        )

    result = check_workflow_status(
        workflow_url=url,
        owner=owner,
        repo=repo,
        run_id=run_id,
    )
    print_json(result.model_dump())
