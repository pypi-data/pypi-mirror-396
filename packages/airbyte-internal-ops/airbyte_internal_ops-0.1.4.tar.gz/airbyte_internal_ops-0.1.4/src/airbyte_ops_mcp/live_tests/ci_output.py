# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""CI-friendly output helpers for GitHub Actions integration.

This module provides utilities for writing structured output to GitHub Actions
environment files (GITHUB_OUTPUT and GITHUB_STEP_SUMMARY), and for generating
regression test reports modeled on the legacy connector_live_tests HTML reports.
"""

from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
from typing import Any


def is_ci() -> bool:
    """Check if running in a CI environment."""
    return bool(os.getenv("CI"))


def is_github_actions() -> bool:
    """Check if running in GitHub Actions."""
    return bool(os.getenv("GITHUB_ACTIONS"))


def write_github_output(key: str, value: str | int | bool | None) -> None:
    """Write a single key-value pair to GITHUB_OUTPUT.

    Args:
        key: The output variable name.
        value: The value to write. None values are skipped.
    """
    if value is None:
        return

    github_output = os.getenv("GITHUB_OUTPUT")
    if not github_output:
        return

    with open(github_output, "a", encoding="utf-8") as f:
        if isinstance(value, bool):
            value = str(value).lower()
        f.write(f"{key}={value}\n")


def write_github_outputs(outputs: dict[str, Any]) -> None:
    """Write multiple key-value pairs to GITHUB_OUTPUT.

    Args:
        outputs: Dictionary of output variables. None values are skipped.
    """
    for key, value in outputs.items():
        write_github_output(key, value)


def write_github_summary(content: str) -> None:
    """Write content to GITHUB_STEP_SUMMARY.

    Args:
        content: Markdown content to append to the step summary.
    """
    github_summary = os.getenv("GITHUB_STEP_SUMMARY")
    if not github_summary:
        return

    with open(github_summary, "a", encoding="utf-8") as f:
        f.write(content)
        if not content.endswith("\n"):
            f.write("\n")


def write_test_summary(
    connector_image: str,
    test_type: str,
    success: bool,
    results: dict[str, Any],
    details: str | None = None,
) -> None:
    """Write a formatted test summary to GITHUB_STEP_SUMMARY.

    Args:
        connector_image: The connector image being tested.
        test_type: Type of test (e.g., "live-test", "regression-test").
        success: Whether the test passed.
        results: Dictionary of test results to display.
        details: Optional additional details in markdown format.
    """
    status_emoji = "✅" if success else "❌"
    status_text = "PASSED" if success else "FAILED"

    summary = f"""## {status_emoji} {test_type.title()} Results

**Connector:** `{connector_image}`
**Status:** {status_text}

### Results

| Metric | Value |
|--------|-------|
"""

    for key, value in results.items():
        display_key = key.replace("_", " ").title()
        summary += f"| {display_key} | {value} |\n"

    if details:
        summary += f"\n### Details\n\n{details}\n"

    write_github_summary(summary)


def write_json_output(key: str, data: dict[str, Any] | list[Any]) -> None:
    """Write JSON data to GITHUB_OUTPUT using multiline format.

    For complex data structures, GitHub Actions requires multiline output format.

    Args:
        key: The output variable name.
        data: The data to serialize as JSON.
    """
    github_output = os.getenv("GITHUB_OUTPUT")
    if not github_output:
        return

    json_str = json.dumps(data, separators=(",", ":"))

    with open(github_output, "a", encoding="utf-8") as f:
        delimiter = "EOF"
        f.write(f"{key}<<{delimiter}\n")
        f.write(json_str)
        f.write(f"\n{delimiter}\n")


def _format_delta(delta: int) -> str:
    """Format a delta value with +/- prefix and highlight if non-zero."""
    if delta > 0:
        return f"**+{delta}**"
    elif delta < 0:
        return f"**{delta}**"
    return "0"


def generate_regression_report(
    target_image: str,
    control_image: str,
    command: str,
    target_result: dict[str, Any],
    control_result: dict[str, Any],
    output_dir: Path,
) -> Path:
    """Generate a markdown regression test report modeled on legacy HTML reports.

    This creates a comprehensive report with context, message counts comparison,
    and record counts per stream (for read commands). The structure mirrors the
    legacy connector_live_tests HTML report.

    Args:
        target_image: The target (new version) connector image.
        control_image: The control (baseline version) connector image.
        command: The Airbyte command that was run.
        target_result: Results dict from running target connector.
        control_result: Results dict from running control connector.
        output_dir: Directory to write the report to.

    Returns:
        Path to the generated report.md file.
    """
    both_succeeded = target_result["success"] and control_result["success"]
    regression_detected = target_result["success"] != control_result["success"]

    target_counts = target_result.get("message_counts", {})
    control_counts = control_result.get("message_counts", {})
    target_record_counts = target_result.get("record_counts_per_stream", {})
    control_record_counts = control_result.get("record_counts_per_stream", {})

    run_id = os.getenv("GITHUB_RUN_ID", "")
    artifact_name = (
        f"regression-test-artifacts-{run_id}" if run_id else "regression-test-artifacts"
    )

    target_version = (
        target_image.rsplit(":", 1)[-1] if ":" in target_image else "unknown"
    )
    control_version = (
        control_image.rsplit(":", 1)[-1] if ":" in control_image else "unknown"
    )
    connector_name = (
        target_image.rsplit(":", 1)[0] if ":" in target_image else target_image
    )

    lines: list[str] = [
        "# Regression Test Report",
        "",
        "## Context",
        "",
        f"- **Test Date:** {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"- **Connector:** `{connector_name}`",
        f"- **Control Version:** `{control_version}`",
        f"- **Target Version:** `{target_version}`",
        f"- **Command:** `{command.upper()}`",
        f"- **Artifacts:** `{artifact_name}`",
        "",
        "## Summary",
        "",
    ]

    if regression_detected:
        if target_result["success"] and not control_result["success"]:
            lines.append("**Result:** Target succeeded, control failed (improvement)")
        else:
            lines.append(
                "**Result:** Target FAILED, control succeeded (**REGRESSION DETECTED**)"
            )
    elif both_succeeded:
        lines.append("**Result:** Both versions succeeded (no regression)")
    else:
        lines.append("**Result:** Both versions failed")

    lines.extend(
        [
            "",
            "| Version | Exit Code | Success |",
            "|---------|-----------|---------|",
            f"| Control ({control_version}) | {control_result['exit_code']} | {control_result['success']} |",
            f"| Target ({target_version}) | {target_result['exit_code']} | {target_result['success']} |",
            "",
        ]
    )

    lines.extend(
        [
            "## Command Execution Metrics",
            "",
        ]
    )

    if target_counts or control_counts:
        lines.extend(
            [
                "### Message Types",
                "",
                "| Type | Control | Target | Delta |",
                "|------|---------|--------|-------|",
            ]
        )
        all_types = sorted(set(target_counts) | set(control_counts))
        for msg_type in all_types:
            control_count = control_counts.get(msg_type, 0)
            target_count = target_counts.get(msg_type, 0)
            delta = target_count - control_count
            lines.append(
                f"| {msg_type} | {control_count} | {target_count} | {_format_delta(delta)} |"
            )
        lines.append("")

    if target_record_counts or control_record_counts:
        lines.extend(
            [
                "### Record Count per Stream",
                "",
                "| Stream | Control | Target | Delta |",
                "|--------|---------|--------|-------|",
            ]
        )
        all_streams = sorted(set(target_record_counts) | set(control_record_counts))
        total_control = 0
        total_target = 0
        for stream in all_streams:
            control_count = control_record_counts.get(stream, 0)
            target_count = target_record_counts.get(stream, 0)
            total_control += control_count
            total_target += target_count
            delta = target_count - control_count
            lines.append(
                f"| {stream} | {control_count} | {target_count} | {_format_delta(delta)} |"
            )
        total_delta = total_target - total_control
        lines.append(
            f"| **Total** | **{total_control}** | **{total_target}** | {_format_delta(total_delta)} |"
        )
        lines.append("")

    control_http = control_result.get("http_metrics") or {}
    target_http = target_result.get("http_metrics") or {}
    if control_http or target_http:
        lines.extend(
            [
                "### HTTP Metrics",
                "",
                "| Version | Flow Count | Duplicate Flows |",
                "|---------|------------|-----------------|",
                f"| Control | {control_http.get('flow_count', 0)} | {control_http.get('duplicate_flow_count', 0)} |",
                f"| Target | {target_http.get('flow_count', 0)} | {target_http.get('duplicate_flow_count', 0)} |",
                "",
            ]
        )

    lines.extend(
        [
            "## Execution Details",
            "",
            "### Control",
            "",
            f"- **Image:** `{control_image}`",
            f"- **Exit Code:** {control_result['exit_code']}",
            f"- **Success:** {control_result['success']}",
            f"- **Stdout:** `{control_result.get('stdout_file', 'N/A')}`",
            f"- **Stderr:** `{control_result.get('stderr_file', 'N/A')}`",
            "",
            "### Target",
            "",
            f"- **Image:** `{target_image}`",
            f"- **Exit Code:** {target_result['exit_code']}",
            f"- **Success:** {target_result['success']}",
            f"- **Stdout:** `{target_result.get('stdout_file', 'N/A')}`",
            f"- **Stderr:** `{target_result.get('stderr_file', 'N/A')}`",
            "",
        ]
    )

    report_content = "\n".join(lines)
    report_path = output_dir / "report.md"
    report_path.write_text(report_content)

    return report_path


def get_report_summary(report_path: Path) -> str:
    """Get a brief summary pointing to the full report.

    Args:
        report_path: Path to the full report.md file.

    Returns:
        Brief markdown summary for GITHUB_STEP_SUMMARY.
    """
    run_id = os.getenv("GITHUB_RUN_ID", "")
    artifact_name = (
        f"regression-test-artifacts-{run_id}" if run_id else "regression-test-artifacts"
    )

    return f"""## Regression Test Report

Full report available in the **Regression Test Report** check or in artifact `{artifact_name}`.

See the Checks tab for the complete report with message counts and execution details.
"""
