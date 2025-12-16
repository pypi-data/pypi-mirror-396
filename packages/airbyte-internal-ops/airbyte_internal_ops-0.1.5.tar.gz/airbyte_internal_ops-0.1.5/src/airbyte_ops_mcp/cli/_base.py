# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
"""Base CLI application instance.

This module contains the root App instance that all domain modules import from.
It should have no imports from other cli modules to avoid circular dependencies.
"""

from cyclopts import App

app = App(
    name="airbyte-ops",
    help="Airbyte operations CLI for managing connectors, cloud deployments, and workflows.",
)
