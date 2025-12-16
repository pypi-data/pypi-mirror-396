# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""CLI commands for connector registry operations.

Commands:
    airbyte-ops registry connector publish-prerelease - Publish connector prerelease
    airbyte-ops registry image inspect - Inspect Docker image on DockerHub
"""

from __future__ import annotations

from typing import Annotated

from cyclopts import App, Parameter

from airbyte_ops_mcp.cli._base import app
from airbyte_ops_mcp.cli._shared import print_error, print_json, print_success
from airbyte_ops_mcp.mcp.github import get_docker_image_info
from airbyte_ops_mcp.mcp.prerelease import publish_connector_to_airbyte_registry

# Create the registry sub-app
registry_app = App(
    name="registry", help="Connector registry and Docker image operations."
)
app.command(registry_app)

# Create the connector sub-app under registry
connector_app = App(name="connector", help="Registry-facing connector operations.")
registry_app.command(connector_app)

# Create the image sub-app under registry
image_app = App(name="image", help="Docker image operations.")
registry_app.command(image_app)


@connector_app.command(name="publish-prerelease")
def publish_prerelease(
    connector_name: Annotated[
        str,
        Parameter(
            help="The connector name to publish (e.g., 'source-github', 'destination-postgres')."
        ),
    ],
    pr: Annotated[
        int,
        Parameter(help="The pull request number containing the connector changes."),
    ],
) -> None:
    """Publish a connector prerelease to the Airbyte registry.

    Triggers the publish-connectors-prerelease workflow in the airbytehq/airbyte
    repository. Pre-release versions are tagged with format: {version}-dev.{git-sha}

    Requires GITHUB_CONNECTOR_PUBLISHING_PAT or GITHUB_TOKEN environment variable
    with 'actions:write' permission.
    """
    result = publish_connector_to_airbyte_registry(
        connector_name=connector_name,
        pr_number=pr,
        prerelease=True,
    )
    if result.success:
        print_success(result.message)
    else:
        print_error(result.message)
    print_json(result.model_dump())


@image_app.command(name="inspect")
def inspect_image(
    image: Annotated[
        str,
        Parameter(help="Docker image name (e.g., 'airbyte/source-github')."),
    ],
    tag: Annotated[
        str,
        Parameter(help="Image tag (e.g., '2.1.5-dev.abc1234567')."),
    ],
) -> None:
    """Check if a Docker image exists on DockerHub.

    Returns information about the image if it exists, or indicates if it doesn't exist.
    Useful for confirming that a pre-release connector was successfully published.
    """
    result = get_docker_image_info(
        image=image,
        tag=tag,
    )
    if result.exists:
        print_success(f"Image {result.full_name} exists.")
    else:
        print_error(f"Image {result.full_name} not found.")
    print_json(result.model_dump())
