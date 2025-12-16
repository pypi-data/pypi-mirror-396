# Root conftest.py for pytest configuration
# This file is used to exclude legacy modules from test collection.
# Each legacy subproject has a corresponding GitHub issue for tracking its migration:
#   - connector_erd_generator: https://github.com/airbytehq/airbyte-ops-mcp/issues/49
#   - connector_insights: https://github.com/airbytehq/airbyte-ops-mcp/issues/50
#   - connector_live_tests: https://github.com/airbytehq/airbyte-ops-mcp/issues/51
#   - connector_ops: https://github.com/airbytehq/airbyte-ops-mcp/issues/52
#   - connector_pipelines: https://github.com/airbytehq/airbyte-ops-mcp/issues/53
#   - connector_qa: https://github.com/airbytehq/airbyte-ops-mcp/issues/54
#   - metadata_models: https://github.com/airbytehq/airbyte-ops-mcp/issues/55
#   - metadata_service: https://github.com/airbytehq/airbyte-ops-mcp/issues/56

collect_ignore_glob = [
    # Legacy airbyte_ci source modules (recursive)
    "src/airbyte_ops_mcp/_legacy/**/*",
    # Legacy airbyte_ci test modules (recursive)
    "tests/legacy/**/*",
]
