"""LangChain standard unit tests for Voicebox tools."""

from langchain_tests.unit_tests.tools import ToolsUnitTests

from langchain_stardog.voicebox import (
    VoiceboxAskTool,
    VoiceboxGenerateQueryTool,
    VoiceboxSettingsTool,
)


class TestVoiceboxAskToolUnit(ToolsUnitTests):
    """Standard unit tests for VoiceboxAskTool."""

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
        """Example parameters for invoking the tool."""
        return {"question": "What is the capital of France?"}

    @property
    def init_from_env_params(self):
        """Environment variable initialization test parameters."""
        env_vars = {
            "SD_VOICEBOX_API_TOKEN": "test-token-123",
            "SD_VOICEBOX_CLIENT_ID": "test-client",
        }
        init_args = {}
        expected_attrs = {}
        return env_vars, init_args, expected_attrs


class TestVoiceboxSettingsToolUnit(ToolsUnitTests):
    """Standard unit tests for VoiceboxSettingsTool."""

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

    @property
    def init_from_env_params(self):
        """Environment variable initialization test parameters."""
        env_vars = {
            "SD_VOICEBOX_API_TOKEN": "test-token-123",
            "SD_VOICEBOX_CLIENT_ID": "test-client",
        }
        init_args = {}
        expected_attrs = {}
        return env_vars, init_args, expected_attrs


class TestVoiceboxGenerateQueryToolUnit(ToolsUnitTests):
    """Standard unit tests for VoiceboxGenerateQueryTool."""

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
        """Example parameters for invoking the tool."""
        return {"question": "Show me all airports in California"}

    @property
    def init_from_env_params(self):
        """Environment variable initialization test parameters."""
        env_vars = {
            "SD_VOICEBOX_API_TOKEN": "test-token-123",
            "SD_VOICEBOX_CLIENT_ID": "test-client",
        }
        init_args = {}
        expected_attrs = {}
        return env_vars, init_args, expected_attrs
