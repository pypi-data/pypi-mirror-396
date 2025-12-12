"""Tests for Runnable implementations."""

import pytest

from langchain_stardog.voicebox import (
    ENV_VOICEBOX_API_TOKEN,
    VoiceboxAskRunnable,
    VoiceboxGenerateQueryRunnable,
    VoiceboxSettingsRunnable,
)


@pytest.fixture
def setup_env_vars(monkeypatch, mock_cloud_client):
    """Set up environment variables for runnable tests.

    Note: mock_cloud_client is passed to ensure mocks are active.
    """
    monkeypatch.setenv(ENV_VOICEBOX_API_TOKEN, "test-token")
    monkeypatch.setenv("SD_VOICEBOX_CLIENT_ID", "test-client")
    monkeypatch.setenv("SD_CLOUD_ENDPOINT", "https://test.stardog.com/api")


class TestVoiceboxSettingsRunnable:
    """Tests for VoiceboxSettingsRunnable."""

    @pytest.mark.asyncio
    async def test_ainvoke(self, voicebox_client):
        """Test async invocation of settings runnable."""
        runnable = VoiceboxSettingsRunnable(voicebox_client)
        result = await runnable.ainvoke({})

        assert result["name"] == "test-voicebox-app"
        assert result["database"] == "test-database"

    def test_invoke(self, voicebox_client):
        """Test sync invocation of settings runnable."""
        runnable = VoiceboxSettingsRunnable(voicebox_client)
        result = runnable.invoke({})

        assert result["name"] == "test-voicebox-app"
        assert result["database"] == "test-database"


class TestVoiceboxAskRunnable:
    """Tests for VoiceboxAskRunnable."""

    @pytest.mark.asyncio
    async def test_ainvoke(self, voicebox_client, sample_question):
        """Test async invocation of ask runnable."""
        runnable = VoiceboxAskRunnable(voicebox_client)
        result = await runnable.ainvoke({"question": sample_question})

        assert "answer" in result
        assert "conversation_id" in result

    @pytest.mark.asyncio
    async def test_ainvoke_with_conversation_id(
        self, voicebox_client, sample_question, sample_conversation_id
    ):
        """Test async invocation with conversation_id."""
        runnable = VoiceboxAskRunnable(voicebox_client)
        result = await runnable.ainvoke(
            {"question": sample_question, "conversation_id": sample_conversation_id}
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_ainvoke_missing_question(self, voicebox_client):
        """Test that missing question raises ValueError."""
        runnable = VoiceboxAskRunnable(voicebox_client)
        with pytest.raises(ValueError, match="Input must contain a 'question' key"):
            await runnable.ainvoke({})

    def test_invoke(self, voicebox_client, sample_question):
        """Test sync invocation of ask runnable."""
        runnable = VoiceboxAskRunnable(voicebox_client)
        result = runnable.invoke({"question": sample_question})

        assert "answer" in result
        assert "sparql_query" in result

    def test_invoke_missing_question(self, voicebox_client):
        """Test that missing question raises ValueError in sync mode."""
        runnable = VoiceboxAskRunnable(voicebox_client)
        with pytest.raises(ValueError, match="Input must contain a 'question' key"):
            runnable.invoke({"wrong_key": "value"})


class TestVoiceboxGenerateQueryRunnable:
    """Tests for VoiceboxGenerateQueryRunnable."""

    @pytest.mark.asyncio
    async def test_ainvoke(self, voicebox_client, sample_question):
        """Test async invocation of query runnable."""
        runnable = VoiceboxGenerateQueryRunnable(voicebox_client)
        result = await runnable.ainvoke({"question": sample_question})

        assert "sparql_query" in result
        assert "interpreted_question" in result
        assert "conversation_id" in result

    @pytest.mark.asyncio
    async def test_ainvoke_with_conversation_id(
        self, voicebox_client, sample_question, sample_conversation_id
    ):
        """Test async invocation with conversation_id."""
        runnable = VoiceboxGenerateQueryRunnable(voicebox_client)
        result = await runnable.ainvoke(
            {"question": sample_question, "conversation_id": sample_conversation_id}
        )

        assert result is not None

    @pytest.mark.asyncio
    async def test_ainvoke_missing_question(self, voicebox_client):
        """Test that missing question raises ValueError."""
        runnable = VoiceboxGenerateQueryRunnable(voicebox_client)
        with pytest.raises(ValueError, match="Input must contain a 'question' key"):
            await runnable.ainvoke({})

    def test_invoke(self, voicebox_client, sample_question):
        """Test sync invocation of query runnable."""
        runnable = VoiceboxGenerateQueryRunnable(voicebox_client)
        result = runnable.invoke({"question": sample_question})

        assert "sparql_query" in result
        assert "interpreted_question" in result


class TestRunnableEnvironmentVariableInitialization:
    """Tests for Runnable initialization from environment variables."""

    @pytest.mark.asyncio
    async def test_settings_runnable_from_env(self, setup_env_vars):
        """Test VoiceboxSettingsRunnable can be created from env vars."""
        runnable = VoiceboxSettingsRunnable()  # No client parameter
        result = await runnable.ainvoke({})

        assert result["name"] == "test-voicebox-app"
        assert result["database"] == "test-database"

    @pytest.mark.asyncio
    async def test_ask_runnable_from_env(self, setup_env_vars, sample_question):
        """Test VoiceboxAskRunnable can be created from env vars."""
        runnable = VoiceboxAskRunnable()  # No client parameter
        result = await runnable.ainvoke({"question": sample_question})
        assert "answer" in result

    @pytest.mark.asyncio
    async def test_query_runnable_from_env(self, setup_env_vars, sample_question):
        """Test VoiceboxGenerateQueryRunnable can be created from env vars."""
        runnable = VoiceboxGenerateQueryRunnable()  # No client parameter
        result = await runnable.ainvoke({"question": sample_question})

        assert "sparql_query" in result
        assert "interpreted_question" in result

    def test_runnable_requires_env_var_or_client(self, monkeypatch, mock_cloud_client):
        """Test that runnable raises error when neither env var nor client provided."""
        # Ensure env var is not set
        monkeypatch.delenv(ENV_VOICEBOX_API_TOKEN, raising=False)

        # Should raise error when trying to create runnable without client
        with pytest.raises(Exception) as exc_info:
            VoiceboxAskRunnable()

        assert ENV_VOICEBOX_API_TOKEN in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_explicit_client_takes_precedence(
        self, setup_env_vars, voicebox_client, sample_question
    ):
        """Test that explicit client parameter takes precedence over env vars."""
        # Both env vars and explicit client are available
        # Explicit client should be used
        runnable = VoiceboxAskRunnable(client=voicebox_client)
        result = await runnable.ainvoke({"question": sample_question})

        assert "answer" in result
