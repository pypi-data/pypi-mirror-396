# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
from airbyte_ops_mcp._legacy.airbyte_ci.connector_qa.checks.documentation.documentation import (
    CheckChangelogEntry,
    CheckChangelogSectionContent,
    CheckDocumentationExists,
    CheckDocumentationHeadersOrder,
    CheckDocumentationLinks,
    CheckForAirbyteCloudSectionContent,
    CheckForAirbyteOpenSectionContent,
    CheckMigrationGuide,
    CheckPrerequisitesSectionDescribesRequiredFieldsFromSpec,
    CheckSourceSectionContent,
    CheckSupportedSyncModesSectionContent,
    CheckTutorialsSectionContent,
)

ENABLED_CHECKS = [
    CheckMigrationGuide(),
    CheckDocumentationExists(),
    CheckDocumentationLinks(),
    CheckDocumentationHeadersOrder(),
    CheckPrerequisitesSectionDescribesRequiredFieldsFromSpec(),
    CheckSourceSectionContent(),
    CheckForAirbyteCloudSectionContent(),
    CheckForAirbyteOpenSectionContent(),
    CheckSupportedSyncModesSectionContent(),
    CheckTutorialsSectionContent(),
    CheckChangelogSectionContent(),
    CheckChangelogEntry(),
]
