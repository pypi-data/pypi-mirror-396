# Copilot Instructions for airbyte-ops-mcp

## Overview
MCP and API interfaces for Airbyte administrative operations. Python 3.11+ package using `uv` for dependency management.

**Key Info**: Package: `airbyte-internal-ops` | Module: `airbyte_ops_mcp` | Size: ~38 source files, ~29 tests | Coverage: 80% required

## Structure
- `src/airbyte_ops_mcp/` - Main source (`mcp/server.py` = MCP entry, `cli/app.py` = CLI entry)
  - `mcp/` - MCP server tools | `cli/` - CLI commands | `cloud_admin/` - API client | `airbyte_repo/` - Repo ops
  - `_legacy/` - **EXCLUDED** legacy code (issues #49-#56) - DO NOT modify
- `tests/` - Tests (pytest) | `legacy/` - **EXCLUDED** from test runs
- Config: `pyproject.toml`, `poe_tasks.toml`, `ruff.toml`, `pytest.ini`, `uv.lock` (committed)

## Critical Build/Test Commands

**ALWAYS run from repository root. All commands validated and timing documented.**

### Setup (Required First)
```bash
uv sync --group dev  # ~60s first run, ~5s after. Install dev deps. REQUIRED before any work.
```

### Pre-Commit Checks (Run before every commit)
```bash
uv run ruff format .              # ~5s - Auto-format code
uv run ruff check --fix .         # ~10s - Fix linting issues
uv run pytest --exitfirst --cov=airbyte_ops_mcp --cov-report=term  # ~15s - Run tests
```

**Shortcut**: `uv run poe fix && uv run poe test-fast` (~25s total)

### CI-Equivalent Checks
```bash
uv lock --check                   # ~5s - Verify lock file current
uv run ruff format --check .      # ~5s - Check format (no changes)
uv run ruff check .               # ~5s - Check linting
uv run deptry .                   # ~10s - Check dependencies (warnings normal)
uv run pytest --cov=airbyte_ops_mcp --cov-report=term  # ~20s - Full tests
uv build                          # ~10s - Build package
```

**Shortcut**: `uv run poe check` (runs format-check, lint, deps, test)

## CI/CD Workflows
All run on PRs and main pushes. **Must pass to merge**:

1. **Format Check**: `uv run ruff format --diff .` (~10s)
2. **Lint Check**: `uv run ruff check .` + `uv run deptry .` (~25s)
3. **Pytest Fast**: `uv lock --check` + `uv build` + pytest with `--exitfirst` on Python 3.11 (20min timeout)
4. **Pytest Matrix**: Tests on Python 3.11, 3.12, 3.13 (30min timeout)

**Known Issue**: CI uses wrong coverage path (`awesome_python_template` vs `airbyte_ops_mcp`) - tests still work correctly.

## Common Issues & Workarounds

### Legacy Code Exclusions
**CRITICAL**: `src/airbyte_ops_mcp/_legacy/` and `tests/legacy/` are EXCLUDED from all linting/testing. Configured in `ruff.toml` and `conftest.py`. **DO NOT modify** unless working on migration (issues #49-#56).

### Test Marker Warnings
`@pytest.mark.unit` and `@pytest.mark.integration` trigger warnings (known issue in pytest.ini) but work correctly.

### Environment Setup
Create `.env` from `.env.template` (NEVER commit `.env`):
- `AIRBYTE_CLOUD_CLIENT_ID/SECRET` - OAuth
- `AIRBYTE_INTERNAL_ADMIN_FLAG/USER` - Admin ops
- `AIRBYTE_CLOUD_TEST_WORKSPACE_ID` - Testing

### Coverage Requirements
80% minimum (pytest.ini). Current: ~40%. Add tests for new code.

## Development Workflow

**Standard sequence**:
1. `uv sync --group dev` (if dependencies changed)
2. Make changes
3. `uv run ruff format .` + `uv run ruff check --fix .`
4. `uv run pytest --exitfirst --cov=airbyte_ops_mcp --cov-report=term`
5. `uv build` (verify package builds)
6. Commit/push

**Fast iteration**: `uv run poe fix && uv run poe test-fast`

## Poe Task Reference
```bash
uv run poe fix           # Format + lint auto-fix
uv run poe test-fast     # Tests with --exitfirst
uv run poe check         # All checks (format, lint, deps, test)
uv run poe clean         # Remove artifacts
```

## Key Files & Patterns

**Config Files**:
- `pyproject.toml` - Dependencies (use `uv sync` to update), metadata
- `poe_tasks.toml` - Task definitions
- `ruff.toml` - Lint/format rules, legacy exclusions
- `pytest.ini` - Test config, 80% coverage, legacy exclusions

**Important Patterns**:
- Use `uv` exclusively (not pip/poetry)
- Run all commands from repo root
- Validate locally before pushing (all CI checks runnable locally)
- Package name: `airbyte-internal-ops` | Import name: `airbyte_ops_mcp`
- Entry points: `airbyte-ops-mcp` (MCP server), `airbyte-ops` (CLI)

## Repository Details

**Root Files**: `.env.template`, `.gitignore`, `.mcp.json.template`, `CONTRIBUTING.md`, `README.md`, `bin/`, `conftest.py`, `poe_tasks.toml`, `pyproject.toml`, `pytest.ini`, `ruff.toml`, `src/`, `tests/`, `uv.lock`

**Dependencies**: fastmcp (MCP), airbyte/airbyte-cdk (SDK), cyclopts/click (CLI), pydantic (validation), ruff/pytest/deptry (dev tools)

**Test Utilities**: `bin/test_mcp_tool.py` - Test MCP tools: `uv run poe mcp-tool-test <tool> '<json>'`

## Agent Guidelines

1. **Use `uv` only** - No pip/poetry
2. **Run `uv sync --group dev` first** - Always
3. **Test locally** - All CI checks available locally
4. **Avoid legacy code** - Don't touch `_legacy/` dirs
5. **Meet coverage** - 80% required
6. **Format/lint** - CI fails without
7. **Trust these instructions** - All validated. Search only if incomplete/incorrect.
