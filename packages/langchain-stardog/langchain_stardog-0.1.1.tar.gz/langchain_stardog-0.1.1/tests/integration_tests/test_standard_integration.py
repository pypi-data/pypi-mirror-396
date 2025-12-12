"""LangChain standard integration tests for Voicebox tools"""

import os

import pytest
from langchain_tests.integration_tests.tools import ToolsIntegrationTests

from langchain_stardog.voicebox import (
    VoiceboxAskTool,
    VoiceboxGenerateQueryTool,
    VoiceboxSettingsTool,
)

pytestmark = pytest.mark.skipif(
    not os.environ.get("SD_VOICEBOX_API_TOKEN"),
    reason="SD_VOICEBOX_API_TOKEN not set - skipping integration tests",
)


class TestVoiceboxAskToolIntegration(ToolsIntegrationTests):
    """Standard integration tests for VoiceboxAskTool."""

    @property
    def tool_constructor(self):
        """Returns the VoiceboxAskTool class."""
        return VoiceboxAskTool

    @property
    def tool_constructor_params(self):
        """No params needed - tools load from env."""
        return {}

    @property
    def tool_invoke_params_example(self):
        """Example parameters for invoking the tool.

        Note: This example assumes the Flight Planning knowledge kit.
        Modify the question if using a different data source.
        """
        return {"question": "What airports are in California?"}


class TestVoiceboxSettingsToolIntegration(ToolsIntegrationTests):
    """Standard integration tests for VoiceboxSettingsTool."""

    @property
    def tool_constructor(self):
        """Returns the VoiceboxSettingsTool class."""
        return VoiceboxSettingsTool

    @property
    def tool_constructor_params(self):
        """No params needed - tools load from env."""
        return {}

    @property
    def tool_invoke_params_example(self):
        """Example parameters for invoking the tool."""
        return {}


class TestVoiceboxGenerateQueryToolIntegration(ToolsIntegrationTests):
    """Standard integration tests for VoiceboxGenerateQueryTool."""

    @property
    def tool_constructor(self):
        """Returns the VoiceboxGenerateQueryTool class."""
        return VoiceboxGenerateQueryTool

    @property
    def tool_constructor_params(self):
        """No params needed - tools load from env."""
        return {}

    @property
    def tool_invoke_params_example(self):
        """Example parameters for invoking the tool.

        Note: This example assumes the Flight Planning knowledge kit.
        Modify the question if using a different data source.
        """
        return {"question": "List all flights departing from San Francisco"}
