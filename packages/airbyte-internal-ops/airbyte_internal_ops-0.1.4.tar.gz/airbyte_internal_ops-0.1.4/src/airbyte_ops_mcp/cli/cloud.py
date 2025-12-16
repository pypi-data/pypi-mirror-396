# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""CLI commands for Airbyte Cloud operations.

Commands:
    airbyte-ops cloud connector get-version-info - Get connector version info
    airbyte-ops cloud connector set-version-override - Set connector version override
    airbyte-ops cloud connector clear-version-override - Clear connector version override
    airbyte-ops cloud connector live-test - Run live validation tests on a connector
    airbyte-ops cloud connector regression-test - Run regression tests comparing connector versions
    airbyte-ops cloud connector fetch-connection-config - Fetch connection config to local file
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Literal

from airbyte_cdk.models.connector_metadata import MetadataFile
from airbyte_cdk.utils.connector_paths import find_connector_root_from_name
from airbyte_cdk.utils.docker import build_connector_image, verify_docker_installation
from airbyte_protocol.models import ConfiguredAirbyteCatalog
from cyclopts import App, Parameter

from airbyte_ops_mcp.cli._base import app
from airbyte_ops_mcp.cli._shared import print_error, print_json, print_success
from airbyte_ops_mcp.cloud_admin.connection_config import fetch_connection_config
from airbyte_ops_mcp.live_tests.ci_output import (
    generate_regression_report,
    get_report_summary,
    write_github_output,
    write_github_outputs,
    write_github_summary,
    write_json_output,
    write_test_summary,
)
from airbyte_ops_mcp.live_tests.connection_fetcher import (
    fetch_connection_data,
    save_connection_data_to_files,
)
from airbyte_ops_mcp.live_tests.connector_runner import (
    ConnectorRunner,
    ensure_image_available,
)
from airbyte_ops_mcp.live_tests.http_metrics import (
    MitmproxyManager,
    parse_http_dump,
)
from airbyte_ops_mcp.live_tests.models import (
    Command,
    ConnectorUnderTest,
    ExecutionInputs,
    TargetOrControl,
)
from airbyte_ops_mcp.mcp.cloud_connector_versions import (
    get_cloud_connector_version,
    set_cloud_connector_version_override,
)

# Path to connectors directory within the airbyte repo
CONNECTORS_SUBDIR = Path("airbyte-integrations") / "connectors"

# Create the cloud sub-app
cloud_app = App(name="cloud", help="Airbyte Cloud operations.")
app.command(cloud_app)

# Create the connector sub-app under cloud
connector_app = App(
    name="connector", help="Deployed connector operations in Airbyte Cloud."
)
cloud_app.command(connector_app)


@connector_app.command(name="get-version-info")
def get_version_info(
    workspace_id: Annotated[
        str,
        Parameter(help="The Airbyte Cloud workspace ID."),
    ],
    connector_id: Annotated[
        str,
        Parameter(help="The ID of the deployed connector (source or destination)."),
    ],
    connector_type: Annotated[
        Literal["source", "destination"],
        Parameter(help="The type of connector."),
    ],
) -> None:
    """Get the current version information for a deployed connector."""
    result = get_cloud_connector_version(
        workspace_id=workspace_id,
        actor_id=connector_id,
        actor_type=connector_type,
    )
    print_json(result.model_dump())


@connector_app.command(name="set-version-override")
def set_version_override(
    workspace_id: Annotated[
        str,
        Parameter(help="The Airbyte Cloud workspace ID."),
    ],
    connector_id: Annotated[
        str,
        Parameter(help="The ID of the deployed connector (source or destination)."),
    ],
    connector_type: Annotated[
        Literal["source", "destination"],
        Parameter(help="The type of connector."),
    ],
    version: Annotated[
        str,
        Parameter(
            help="The semver version string to pin to (e.g., '2.1.5-dev.abc1234567')."
        ),
    ],
    reason: Annotated[
        str,
        Parameter(help="Explanation for the override (min 10 characters)."),
    ],
    reason_url: Annotated[
        str | None,
        Parameter(help="Optional URL with more context (e.g., issue link)."),
    ] = None,
) -> None:
    """Set a version override for a deployed connector.

    Requires admin authentication via AIRBYTE_INTERNAL_ADMIN_FLAG and
    AIRBYTE_INTERNAL_ADMIN_USER environment variables.
    """
    result = set_cloud_connector_version_override(
        workspace_id=workspace_id,
        actor_id=connector_id,
        actor_type=connector_type,
        version=version,
        unset=False,
        override_reason=reason,
        override_reason_reference_url=reason_url,
    )
    if result.success:
        print_success(result.message)
    else:
        print_error(result.message)
    print_json(result.model_dump())


@connector_app.command(name="clear-version-override")
def clear_version_override(
    workspace_id: Annotated[
        str,
        Parameter(help="The Airbyte Cloud workspace ID."),
    ],
    connector_id: Annotated[
        str,
        Parameter(help="The ID of the deployed connector (source or destination)."),
    ],
    connector_type: Annotated[
        Literal["source", "destination"],
        Parameter(help="The type of connector."),
    ],
) -> None:
    """Clear a version override from a deployed connector.

    Requires admin authentication via AIRBYTE_INTERNAL_ADMIN_FLAG and
    AIRBYTE_INTERNAL_ADMIN_USER environment variables.
    """
    result = set_cloud_connector_version_override(
        workspace_id=workspace_id,
        actor_id=connector_id,
        actor_type=connector_type,
        version=None,
        unset=True,
        override_reason=None,
        override_reason_reference_url=None,
    )
    if result.success:
        print_success(result.message)
    else:
        print_error(result.message)
    print_json(result.model_dump())


def _load_json_file(file_path: Path) -> dict | None:
    """Load a JSON file and return its contents.

    Returns None if the file doesn't exist or contains invalid JSON.
    """
    if not file_path.exists():
        return None
    try:
        return json.loads(file_path.read_text())
    except json.JSONDecodeError as e:
        print_error(f"Failed to parse JSON in file: {file_path}\nError: {e}")
        return None


def _run_connector_command(
    connector_image: str,
    command: Command,
    output_dir: Path,
    target_or_control: TargetOrControl,
    config_path: Path | None = None,
    catalog_path: Path | None = None,
    state_path: Path | None = None,
    proxy_url: str | None = None,
) -> dict:
    """Run a connector command and return results as a dict.

    Args:
        connector_image: Full connector image name with tag.
        command: The Airbyte command to run.
        output_dir: Directory to store output files.
        target_or_control: Whether this is target or control version.
        config_path: Path to connector config JSON file.
        catalog_path: Path to configured catalog JSON file.
        state_path: Path to state JSON file.
        proxy_url: Optional HTTP proxy URL for traffic capture.

    Returns:
        Dictionary with execution results.
    """
    connector = ConnectorUnderTest.from_image_name(connector_image, target_or_control)

    config = _load_json_file(config_path) if config_path else None
    state = _load_json_file(state_path) if state_path else None

    configured_catalog = None
    if catalog_path and catalog_path.exists():
        catalog_json = catalog_path.read_text()
        configured_catalog = ConfiguredAirbyteCatalog.parse_raw(catalog_json)

    execution_inputs = ExecutionInputs(
        connector_under_test=connector,
        command=command,
        output_dir=output_dir,
        config=config,
        configured_catalog=configured_catalog,
        state=state,
    )

    runner = ConnectorRunner(execution_inputs, proxy_url=proxy_url)
    result = runner.run()

    result.save_artifacts(output_dir)

    return {
        "connector": connector_image,
        "command": command.value,
        "success": result.success,
        "exit_code": result.exit_code,
        "stdout_file": str(result.stdout_file_path),
        "stderr_file": str(result.stderr_file_path),
        "message_counts": {
            k.value: v for k, v in result.get_message_count_per_type().items()
        },
        "record_counts_per_stream": result.get_record_count_per_stream(),
    }


def _build_connector_image_from_source(
    connector_name: str,
    repo_root: Path | None = None,
    tag: str = "dev",
) -> str | None:
    """Build a connector image from source code.

    Args:
        connector_name: Name of the connector (e.g., 'source-pokeapi').
        repo_root: Optional path to the airbyte repo root. If not provided,
            will attempt to auto-detect from current directory.
        tag: Tag to apply to the built image (default: 'dev').

    Returns:
        The full image name with tag if successful, None if build fails.
    """
    if not verify_docker_installation():
        print_error("Docker is not installed or not running")
        return None

    try:
        connector_directory = find_connector_root_from_name(connector_name)
    except FileNotFoundError:
        if repo_root:
            connector_directory = repo_root / CONNECTORS_SUBDIR / connector_name
            if not connector_directory.exists():
                print_error(f"Connector directory not found: {connector_directory}")
                return None
        else:
            print_error(
                f"Could not find connector '{connector_name}'. "
                "Try providing --repo-root to specify the airbyte repo location."
            )
            return None

    metadata_file_path = connector_directory / "metadata.yaml"
    if not metadata_file_path.exists():
        print_error(f"metadata.yaml not found at {metadata_file_path}")
        return None

    metadata = MetadataFile.from_file(metadata_file_path)
    print_success(f"Building image for connector: {connector_name}")

    built_image = build_connector_image(
        connector_name=connector_name,
        connector_directory=connector_directory,
        metadata=metadata,
        tag=tag,
        no_verify=False,
    )
    print_success(f"Successfully built image: {built_image}")
    return built_image


@connector_app.command(name="live-test")
def live_test(
    connector_image: Annotated[
        str | None,
        Parameter(
            help="Full connector image name with tag (e.g., airbyte/source-github:1.0.0). "
            "Optional if connector_name or connection_id is provided."
        ),
    ] = None,
    connector_name: Annotated[
        str | None,
        Parameter(
            help="Connector name to build from source (e.g., 'source-pokeapi'). "
            "If provided, builds the image locally with tag 'dev'."
        ),
    ] = None,
    repo_root: Annotated[
        str | None,
        Parameter(
            help="Path to the airbyte repo root. Required if connector_name is provided "
            "and the repo cannot be auto-detected."
        ),
    ] = None,
    command: Annotated[
        Literal["spec", "check", "discover", "read"],
        Parameter(help="The Airbyte command to run."),
    ] = "check",
    connection_id: Annotated[
        str | None,
        Parameter(
            help="Airbyte Cloud connection ID to fetch config/catalog from. "
            "Mutually exclusive with config-path/catalog-path. "
            "If provided, connector_image can be auto-detected."
        ),
    ] = None,
    config_path: Annotated[
        str | None,
        Parameter(help="Path to the connector config JSON file."),
    ] = None,
    catalog_path: Annotated[
        str | None,
        Parameter(help="Path to the configured catalog JSON file (required for read)."),
    ] = None,
    state_path: Annotated[
        str | None,
        Parameter(help="Path to the state JSON file (optional for read)."),
    ] = None,
    output_dir: Annotated[
        str,
        Parameter(help="Directory to store test artifacts."),
    ] = "/tmp/live_test_artifacts",
) -> None:
    """Run live validation tests on a connector.

    This command runs the specified Airbyte protocol command against a connector
    and validates the output. Results are written to the output directory and
    to GitHub Actions outputs if running in CI.

    You can provide the connector image in three ways:
    1. --connector-image: Use a pre-built image from Docker registry
    2. --connector-name: Build the image locally from source code
    3. --connection-id: Auto-detect from an Airbyte Cloud connection

    You can provide config/catalog either via file paths OR via a connection_id
    that fetches them from Airbyte Cloud.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cmd = Command(command)

    config_file: Path | None = None
    catalog_file: Path | None = None
    state_file = Path(state_path) if state_path else None
    resolved_connector_image: str | None = connector_image

    # If connector_name is provided, build the image from source
    if connector_name:
        if connector_image:
            print_error("Cannot specify both connector_image and connector_name")
            write_github_output("success", False)
            write_github_output(
                "error", "Cannot specify both connector_image and connector_name"
            )
            return

        repo_root_path = Path(repo_root) if repo_root else None
        built_image = _build_connector_image_from_source(
            connector_name=connector_name,
            repo_root=repo_root_path,
            tag="dev",
        )
        if not built_image:
            write_github_output("success", False)
            write_github_output("error", f"Failed to build image for {connector_name}")
            return
        resolved_connector_image = built_image

    if connection_id:
        if config_path or catalog_path:
            print_error(
                "Cannot specify both connection_id and config_path/catalog_path"
            )
            write_github_output("success", False)
            write_github_output(
                "error", "Cannot specify both connection_id and file paths"
            )
            return

        print_success(f"Fetching config/catalog from connection: {connection_id}")
        connection_data = fetch_connection_data(connection_id)
        config_file, catalog_file = save_connection_data_to_files(
            connection_data, output_path / "connection_data"
        )
        print_success(
            f"Fetched config for source: {connection_data.source_name} "
            f"with {len(connection_data.stream_names)} streams"
        )

        if not resolved_connector_image and connection_data.connector_image:
            resolved_connector_image = connection_data.connector_image
            print_success(f"Auto-detected connector image: {resolved_connector_image}")
    else:
        config_file = Path(config_path) if config_path else None
        catalog_file = Path(catalog_path) if catalog_path else None

    if not resolved_connector_image:
        print_error(
            "You must provide one of the following: a connector_image, a connector_name, "
            "or a connection_id for a connection that has an associated connector image. "
            "If using connection_id, ensure the connection has a connector image configured."
        )
        write_github_output("success", False)
        write_github_output("error", "Missing connector image")
        return

    # If connector_name was provided, we just built the image locally and it is already
    # available in Docker, so we skip the image availability check/pull. Only try to pull
    # if we didn't just build it (i.e., using a pre-built image from registry).
    if not connector_name and not ensure_image_available(resolved_connector_image):
        print_error(f"Failed to pull connector image: {resolved_connector_image}")
        write_github_output("success", False)
        write_github_output(
            "error", f"Failed to pull image: {resolved_connector_image}"
        )
        return

    result = _run_connector_command(
        connector_image=resolved_connector_image,
        command=cmd,
        output_dir=output_path,
        target_or_control=TargetOrControl.TARGET,
        config_path=config_file,
        catalog_path=catalog_file,
        state_path=state_file,
    )

    print_json(result)

    write_github_outputs(
        {
            "success": result["success"],
            "connector": resolved_connector_image,
            "command": command,
            "exit_code": result["exit_code"],
        }
    )

    write_test_summary(
        connector_image=resolved_connector_image,
        test_type="live-test",
        success=result["success"],
        results={
            "command": command,
            "exit_code": result["exit_code"],
            "output_dir": output_dir,
        },
    )

    if result["success"]:
        print_success(f"Live test passed for {resolved_connector_image}")
    else:
        print_error(f"Live test failed for {resolved_connector_image}")


def _run_with_optional_http_metrics(
    connector_image: str,
    command: Command,
    output_dir: Path,
    target_or_control: TargetOrControl,
    enable_http_metrics: bool,
    config_path: Path | None,
    catalog_path: Path | None,
    state_path: Path | None,
) -> dict:
    """Run a connector command with optional HTTP metrics capture.

    When enable_http_metrics is True, starts mitmproxy to capture HTTP traffic.
    If mitmproxy fails to start, falls back to running without metrics.

    Args:
        connector_image: Full connector image name with tag.
        command: The Airbyte command to run.
        output_dir: Directory to store output files.
        target_or_control: Whether this is target or control version.
        enable_http_metrics: Whether to capture HTTP metrics via mitmproxy.
        config_path: Path to connector config JSON file.
        catalog_path: Path to configured catalog JSON file.
        state_path: Path to state JSON file.

    Returns:
        Dictionary with execution results, optionally including http_metrics.
    """
    if not enable_http_metrics:
        return _run_connector_command(
            connector_image=connector_image,
            command=command,
            output_dir=output_dir,
            target_or_control=target_or_control,
            config_path=config_path,
            catalog_path=catalog_path,
            state_path=state_path,
        )

    with MitmproxyManager.start(output_dir) as session:
        if session is None:
            print_error("Mitmproxy unavailable, running without HTTP metrics")
            return _run_connector_command(
                connector_image=connector_image,
                command=command,
                output_dir=output_dir,
                target_or_control=target_or_control,
                config_path=config_path,
                catalog_path=catalog_path,
                state_path=state_path,
            )

        print_success(f"Started mitmproxy on {session.proxy_url}")
        result = _run_connector_command(
            connector_image=connector_image,
            command=command,
            output_dir=output_dir,
            target_or_control=target_or_control,
            config_path=config_path,
            catalog_path=catalog_path,
            state_path=state_path,
            proxy_url=session.proxy_url,
        )

        http_metrics = parse_http_dump(session.dump_file_path)
        result["http_metrics"] = {
            "flow_count": http_metrics.flow_count,
            "duplicate_flow_count": http_metrics.duplicate_flow_count,
        }
        print_success(
            f"Captured {http_metrics.flow_count} HTTP flows "
            f"({http_metrics.duplicate_flow_count} duplicates)"
        )
        return result


@connector_app.command(name="regression-test")
def regression_test(
    target_image: Annotated[
        str | None,
        Parameter(
            help="Target connector image (new version) with tag (e.g., airbyte/source-github:2.0.0). "
            "Optional if connector_name is provided."
        ),
    ] = None,
    control_image: Annotated[
        str | None,
        Parameter(
            help="Control connector image (baseline version) with tag (e.g., airbyte/source-github:1.0.0). "
            "Optional if connection_id is provided (auto-detected from connection)."
        ),
    ] = None,
    connector_name: Annotated[
        str | None,
        Parameter(
            help="Connector name to build target image from source (e.g., 'source-pokeapi'). "
            "If provided, builds the target image locally with tag 'dev'."
        ),
    ] = None,
    repo_root: Annotated[
        str | None,
        Parameter(
            help="Path to the airbyte repo root. Required if connector_name is provided "
            "and the repo cannot be auto-detected."
        ),
    ] = None,
    command: Annotated[
        Literal["spec", "check", "discover", "read"],
        Parameter(help="The Airbyte command to run."),
    ] = "check",
    connection_id: Annotated[
        str | None,
        Parameter(
            help="Airbyte Cloud connection ID to fetch config/catalog from. "
            "Mutually exclusive with config-path/catalog-path. "
            "If provided, control_image can be auto-detected."
        ),
    ] = None,
    config_path: Annotated[
        str | None,
        Parameter(help="Path to the connector config JSON file."),
    ] = None,
    catalog_path: Annotated[
        str | None,
        Parameter(help="Path to the configured catalog JSON file (required for read)."),
    ] = None,
    state_path: Annotated[
        str | None,
        Parameter(help="Path to the state JSON file (optional for read)."),
    ] = None,
    output_dir: Annotated[
        str,
        Parameter(help="Directory to store test artifacts."),
    ] = "/tmp/regression_test_artifacts",
    enable_http_metrics: Annotated[
        bool,
        Parameter(
            help="Capture HTTP traffic metrics via mitmproxy (experimental). "
            "Requires mitmdump to be installed."
        ),
    ] = False,
) -> None:
    """Run regression tests comparing two connector versions.

    This command runs the specified Airbyte protocol command against both the
    target (new) and control (baseline) connector versions, then compares the
    results. This helps identify regressions between versions.

    Results are written to the output directory and to GitHub Actions outputs
    if running in CI.

    You can provide the target image in two ways:
    1. --target-image: Use a pre-built image from Docker registry
    2. --connector-name: Build the target image locally from source code

    You can provide the control image in two ways:
    1. --control-image: Use a pre-built image from Docker registry
    2. --connection-id: Auto-detect from an Airbyte Cloud connection

    You can provide config/catalog either via file paths OR via a connection_id
    that fetches them from Airbyte Cloud.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cmd = Command(command)

    config_file: Path | None = None
    catalog_file: Path | None = None
    state_file = Path(state_path) if state_path else None
    resolved_target_image: str | None = target_image
    resolved_control_image: str | None = control_image

    # If connector_name is provided, build the target image from source
    if connector_name:
        if target_image:
            print_error("Cannot specify both target_image and connector_name")
            write_github_output("success", False)
            write_github_output(
                "error", "Cannot specify both target_image and connector_name"
            )
            return

        repo_root_path = Path(repo_root) if repo_root else None
        built_image = _build_connector_image_from_source(
            connector_name=connector_name,
            repo_root=repo_root_path,
            tag="dev",
        )
        if not built_image:
            write_github_output("success", False)
            write_github_output("error", f"Failed to build image for {connector_name}")
            return
        resolved_target_image = built_image

    if connection_id:
        if config_path or catalog_path:
            print_error(
                "Cannot specify both connection_id and config_path/catalog_path"
            )
            write_github_output("success", False)
            write_github_output(
                "error", "Cannot specify both connection_id and file paths"
            )
            return

        print_success(f"Fetching config/catalog from connection: {connection_id}")
        connection_data = fetch_connection_data(connection_id)
        config_file, catalog_file = save_connection_data_to_files(
            connection_data, output_path / "connection_data"
        )
        print_success(
            f"Fetched config for source: {connection_data.source_name} "
            f"with {len(connection_data.stream_names)} streams"
        )

        # Auto-detect control_image from connection if not provided
        if not resolved_control_image and connection_data.connector_image:
            resolved_control_image = connection_data.connector_image
            print_success(f"Auto-detected control image: {resolved_control_image}")
    else:
        config_file = Path(config_path) if config_path else None
        catalog_file = Path(catalog_path) if catalog_path else None

    # Validate that we have both images
    if not resolved_target_image:
        print_error(
            "You must provide one of the following: a target_image or a connector_name "
            "to build the target image from source."
        )
        write_github_output("success", False)
        write_github_output("error", "No target image specified")
        return

    if not resolved_control_image:
        print_error(
            "You must provide one of the following: a control_image or a connection_id "
            "for a connection that has an associated connector image."
        )
        write_github_output("success", False)
        write_github_output("error", "No control image specified")
        return

    # Pull images if they weren't just built locally
    # If connector_name was provided, we just built the target image locally
    if not connector_name and not ensure_image_available(resolved_target_image):
        print_error(f"Failed to pull target connector image: {resolved_target_image}")
        write_github_output("success", False)
        write_github_output("error", f"Failed to pull image: {resolved_target_image}")
        return

    if not ensure_image_available(resolved_control_image):
        print_error(f"Failed to pull control connector image: {resolved_control_image}")
        write_github_output("success", False)
        write_github_output("error", f"Failed to pull image: {resolved_control_image}")
        return

    target_output = output_path / "target"
    control_output = output_path / "control"

    target_result = _run_with_optional_http_metrics(
        connector_image=resolved_target_image,
        command=cmd,
        output_dir=target_output,
        target_or_control=TargetOrControl.TARGET,
        enable_http_metrics=enable_http_metrics,
        config_path=config_file,
        catalog_path=catalog_file,
        state_path=state_file,
    )

    control_result = _run_with_optional_http_metrics(
        connector_image=resolved_control_image,
        command=cmd,
        output_dir=control_output,
        target_or_control=TargetOrControl.CONTROL,
        enable_http_metrics=enable_http_metrics,
        config_path=config_file,
        catalog_path=catalog_file,
        state_path=state_file,
    )

    both_succeeded = target_result["success"] and control_result["success"]
    regression_detected = target_result["success"] != control_result["success"]

    combined_result = {
        "target": target_result,
        "control": control_result,
        "both_succeeded": both_succeeded,
        "regression_detected": regression_detected,
    }

    print_json(combined_result)

    write_github_outputs(
        {
            "success": both_succeeded and not regression_detected,
            "target_image": resolved_target_image,
            "control_image": resolved_control_image,
            "command": command,
            "target_exit_code": target_result["exit_code"],
            "control_exit_code": control_result["exit_code"],
            "regression_detected": regression_detected,
        }
    )

    write_json_output("regression_report", combined_result)

    report_path = generate_regression_report(
        target_image=resolved_target_image,
        control_image=resolved_control_image,
        command=command,
        target_result=target_result,
        control_result=control_result,
        output_dir=output_path,
    )
    print_success(f"Generated regression report: {report_path}")

    summary = get_report_summary(report_path)
    write_github_summary(summary)

    if regression_detected:
        print_error(
            f"Regression detected between {resolved_target_image} and {resolved_control_image}"
        )
    elif both_succeeded:
        print_success(
            f"Regression test passed for {resolved_target_image} vs {resolved_control_image}"
        )
    else:
        print_error(
            f"Both versions failed for {resolved_target_image} vs {resolved_control_image}"
        )


@connector_app.command(name="fetch-connection-config")
def fetch_connection_config_cmd(
    connection_id: Annotated[
        str,
        Parameter(help="The UUID of the Airbyte Cloud connection."),
    ],
    output_path: Annotated[
        str | None,
        Parameter(
            help="Path to output file or directory. "
            "If directory, writes connection-<id>-config.json. "
            "Default: ./connection-<id>-config.json"
        ),
    ] = None,
    with_secrets: Annotated[
        bool,
        Parameter(
            name="--with-secrets",
            negative="--no-secrets",
            help="If set, fetches unmasked secrets from the internal database. "
            "Requires GCP_PROD_DB_ACCESS_CREDENTIALS env var or `gcloud auth application-default login`. "
            "Must be used with --oc-issue-url.",
        ),
    ] = False,
    oc_issue_url: Annotated[
        str | None,
        Parameter(
            help="OC issue URL for audit logging. Required when using --with-secrets."
        ),
    ] = None,
) -> None:
    """Fetch connection configuration from Airbyte Cloud to a local file.

    This command retrieves the source configuration for a given connection ID
    and writes it to a local JSON file.

    Requires authentication via AIRBYTE_CLOUD_CLIENT_ID and
    AIRBYTE_CLOUD_CLIENT_SECRET environment variables.

    When --with-secrets is specified, the command fetches unmasked secrets from
    the internal database using the connection-retriever. This additionally requires:
    - An OC issue URL for audit logging (--oc-issue-url)
    - GCP credentials via `GCP_PROD_DB_ACCESS_CREDENTIALS` env var or `gcloud auth application-default login`
    - If `CI=true`: expects `cloud-sql-proxy` running on localhost, or
      direct network access to the Cloud SQL instance.
    """
    path = Path(output_path) if output_path else None
    result = fetch_connection_config(
        connection_id=connection_id,
        output_path=path,
        with_secrets=with_secrets,
        oc_issue_url=oc_issue_url,
    )
    if result.success:
        print_success(result.message)
    else:
        print_error(result.message)
    print_json(result.model_dump())
