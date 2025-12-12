"""Tests for Tool implementations."""

import pytest

from langchain_stardog.voicebox import (
    ENV_VOICEBOX_API_TOKEN,
    VoiceboxAskTool,
    VoiceboxGenerateQueryTool,
    VoiceboxSettingsTool,
)


@pytest.fixture
def setup_env_vars(monkeypatch, mock_cloud_client):
    """Set up environment variables for tool tests.

    Note: mock_cloud_client is passed to ensure mocks are active.
    """
    monkeypatch.setenv(ENV_VOICEBOX_API_TOKEN, "test-token")
    monkeypatch.setenv("SD_VOICEBOX_CLIENT_ID", "test-client")
    monkeypatch.setenv("SD_CLOUD_ENDPOINT", "https://test.stardog.com/api")


class TestVoiceboxSettingsTool:
    """Tests for VoiceboxSettingsTool."""

    def test_tool_metadata(self, setup_env_vars):
        """Test tool has correct metadata."""
        tool = VoiceboxSettingsTool()

        assert tool.name == "voicebox_settings"
        assert "Voicebox application settings" in tool.description

    def test_run(self, setup_env_vars):
        """Test synchronous tool execution."""
        tool = VoiceboxSettingsTool()
        result = tool._run()

        assert result["name"] == "test-voicebox-app"
        assert result["database"] == "test-database"

    @pytest.mark.asyncio
    async def test_arun(self, setup_env_vars):
        """Test asynchronous tool execution."""
        tool = VoiceboxSettingsTool()
        result = await tool._arun()

        assert result["name"] == "test-voicebox-app"
        assert result["database"] == "test-database"


class TestVoiceboxAskTool:
    """Tests for VoiceboxAskTool."""

    def test_tool_metadata(self, setup_env_vars):
        """Test tool has correct metadata."""
        tool = VoiceboxAskTool()

        assert tool.name == "voicebox_ask"
        assert "natural language question" in tool.description.lower()
        assert tool.args_schema is not None

    def test_run(self, setup_env_vars, sample_question):
        """Test synchronous tool execution."""
        tool = VoiceboxAskTool()
        result = tool._run(question=sample_question)

        assert "answer" in result
        assert "sparql_query" in result
        assert "conversation_id" in result

    def test_run_with_conversation_id(
        self, setup_env_vars, sample_question, sample_conversation_id
    ):
        """Test synchronous tool execution with conversation_id."""
        tool = VoiceboxAskTool()
        result = tool._run(
            question=sample_question, conversation_id=sample_conversation_id
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_arun(self, setup_env_vars, sample_question):
        """Test asynchronous tool execution."""
        tool = VoiceboxAskTool()
        result = await tool._arun(question=sample_question)
        assert "answer" in result

    @pytest.mark.asyncio
    async def test_arun_with_conversation_id(
        self, setup_env_vars, sample_question, sample_conversation_id
    ):
        """Test asynchronous tool execution with conversation_id."""
        tool = VoiceboxAskTool()
        result = await tool._arun(
            question=sample_question, conversation_id=sample_conversation_id
        )

        assert result is not None

    def test_tool_schema_validation(self, setup_env_vars):
        """Test tool input schema validation."""
        tool = VoiceboxAskTool()
        schema = tool.args_schema

        # Check that question field is required
        assert "question" in schema.model_fields
        assert schema.model_fields["question"].is_required()


class TestVoiceboxGenerateQueryTool:
    """Tests for VoiceboxGenerateQueryTool."""

    def test_tool_metadata(self, setup_env_vars):
        """Test tool has correct metadata."""
        tool = VoiceboxGenerateQueryTool()

        assert tool.name == "voicebox_generate_query"
        assert "SPARQL query" in tool.description
        assert tool.args_schema is not None

    def test_run(self, setup_env_vars, sample_question):
        """Test synchronous tool execution."""
        tool = VoiceboxGenerateQueryTool()
        result = tool._run(question=sample_question)

        assert "sparql_query" in result
        assert "interpreted_question" in result

    def test_run_with_conversation_id(
        self, setup_env_vars, sample_question, sample_conversation_id
    ):
        """Test synchronous tool execution with conversation_id."""
        tool = VoiceboxGenerateQueryTool()
        result = tool._run(
            question=sample_question, conversation_id=sample_conversation_id
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_arun(self, setup_env_vars, sample_question):
        """Test asynchronous tool execution."""
        tool = VoiceboxGenerateQueryTool()
        result = await tool._arun(question=sample_question)

        assert "sparql_query" in result
        assert "interpreted_question" in result

    @pytest.mark.asyncio
    async def test_arun_with_conversation_id(
        self, setup_env_vars, sample_question, sample_conversation_id
    ):
        """Test asynchronous tool execution with conversation_id."""
        tool = VoiceboxGenerateQueryTool()
        result = await tool._arun(
            question=sample_question, conversation_id=sample_conversation_id
        )

        assert result is not None


class TestToolEnvironmentVariableInitialization:
    """Tests for environment variable initialization."""

    def test_tool_requires_env_var(self, monkeypatch, mock_cloud_client):
        """Test that tool raises error when env var not set."""
        # Ensure env var is not set
        monkeypatch.delenv(ENV_VOICEBOX_API_TOKEN, raising=False)

        # Should raise error when trying to create tool
        with pytest.raises(Exception) as exc_info:
            VoiceboxAskTool()

        assert ENV_VOICEBOX_API_TOKEN in str(exc_info.value)

    def test_tool_from_env(self, setup_env_vars):
        """Test tool initialization from environment variables."""
        tool = VoiceboxAskTool()

        # Tool should be created successfully
        assert tool is not None
        assert tool.name == "voicebox_ask"

    def test_all_tools_from_env(self, setup_env_vars):
        """Test that all tool types can be initialized from env."""
        settings_tool = VoiceboxSettingsTool()
        ask_tool = VoiceboxAskTool()
        query_tool = VoiceboxGenerateQueryTool()

        assert settings_tool is not None
        assert ask_tool is not None
        assert query_tool is not None
