"""Tests for VoiceboxClient."""

import pytest

from langchain_stardog.voicebox import (
    VoiceboxAuthenticationError,
    VoiceboxClient,
    VoiceboxValidationError,
)


class TestVoiceboxClientInit:
    """Tests for VoiceboxClient initialization."""

    def test_init_with_required_params(self, mock_cloud_client):
        """Test client initialization with required parameters."""
        client = VoiceboxClient(api_token="test-token")
        assert client.api_token == "test-token"
        assert client.client_id == "VBX-LANGCHAIN"
        assert client.endpoint == "https://cloud.stardog.com/api"

    def test_init_with_all_params(self, mock_cloud_client):
        """Test client initialization with all parameters."""
        client = VoiceboxClient(
            api_token="test-token",
            client_id="custom-client",
            endpoint="https://custom.stardog.com/api",
            auth_token_override="override-token",
        )
        assert client.api_token == "test-token"
        assert client.client_id == "custom-client"
        assert client.endpoint == "https://custom.stardog.com/api"
        assert client.auth_token_override == "override-token"

    def test_init_without_api_token(self, mock_cloud_client):
        """Test that initialization fails without API token."""
        with pytest.raises(VoiceboxAuthenticationError):
            VoiceboxClient(api_token="")


class TestVoiceboxClientAsyncMethods:
    """Tests for async methods of VoiceboxClient."""

    @pytest.mark.asyncio
    async def test_async_get_settings(self, voicebox_client):
        """Test async_get_settings method."""
        settings = await voicebox_client.async_get_settings()

        assert settings["name"] == "test-voicebox-app"
        assert settings["database"] == "test-database"
        assert settings["model"] == "test-model"
        assert len(settings["named_graphs"]) == 2
        assert settings["reasoning"] is True

    @pytest.mark.asyncio
    async def test_async_ask(self, voicebox_client, sample_question):
        """Test async_ask method."""
        result = await voicebox_client.async_ask(sample_question)

        assert "answer" in result
        assert "sparql_query" in result
        assert "interpreted_question" in result
        assert "conversation_id" in result
        assert "message_id" in result
        assert result["conversation_id"] == "conv-123"

    @pytest.mark.asyncio
    async def test_async_ask_with_conversation_id(
        self, voicebox_client, sample_question, sample_conversation_id
    ):
        """Test async_ask with conversation_id."""
        result = await voicebox_client.async_ask(
            sample_question, sample_conversation_id
        )

        assert result is not None
        assert "answer" in result
        assert "conversation_id" in result

    @pytest.mark.asyncio
    async def test_async_ask_empty_question(self, voicebox_client):
        """Test async_ask with empty question raises validation error."""
        with pytest.raises(VoiceboxValidationError):
            await voicebox_client.async_ask("")

    @pytest.mark.asyncio
    async def test_async_generate_query(self, voicebox_client, sample_question):
        """Test async_generate_query method."""
        result = await voicebox_client.async_generate_query(sample_question)

        assert "sparql_query" in result
        assert "interpreted_question" in result
        assert "conversation_id" in result
        assert result["conversation_id"] == "conv-789"

    @pytest.mark.asyncio
    async def test_async_generate_query_empty_question(self, voicebox_client):
        """Test async_generate_query with empty question raises validation error."""
        with pytest.raises(VoiceboxValidationError):
            await voicebox_client.async_generate_query("   ")

    @pytest.mark.asyncio
    async def test_async_get_settings_api_error(
        self, voicebox_client, mock_cloud_client
    ):
        """Test async_get_settings raises VoiceboxAPIError on failure."""
        from unittest.mock import AsyncMock

        from langchain_stardog.voicebox import VoiceboxAPIError

        # Make the async client raise an exception
        mock_sync, mock_async = mock_cloud_client
        mock_voicebox_app = AsyncMock()
        mock_voicebox_app.async_settings = AsyncMock(side_effect=Exception("API Error"))
        mock_async.return_value.voicebox_app.return_value = mock_voicebox_app

        with pytest.raises(VoiceboxAPIError):
            await voicebox_client.async_get_settings()

    @pytest.mark.asyncio
    async def test_async_ask_api_error(
        self, voicebox_client, sample_question, mock_cloud_client
    ):
        """Test async_ask raises VoiceboxAPIError on failure."""
        from unittest.mock import AsyncMock

        from langchain_stardog.voicebox import VoiceboxAPIError

        # Make the async client raise an exception
        mock_sync, mock_async = mock_cloud_client
        mock_voicebox_app = AsyncMock()
        mock_voicebox_app.async_ask = AsyncMock(side_effect=Exception("API Error"))
        mock_async.return_value.voicebox_app.return_value = mock_voicebox_app

        with pytest.raises(VoiceboxAPIError):
            await voicebox_client.async_ask(sample_question)

    @pytest.mark.asyncio
    async def test_async_generate_query_api_error(
        self, voicebox_client, sample_question, mock_cloud_client
    ):
        """Test async_generate_query raises VoiceboxAPIError on failure."""
        from unittest.mock import AsyncMock

        from langchain_stardog.voicebox import VoiceboxAPIError

        # Make the async client raise an exception
        mock_sync, mock_async = mock_cloud_client
        mock_voicebox_app = AsyncMock()
        mock_voicebox_app.async_generate_query = AsyncMock(
            side_effect=Exception("API Error")
        )
        mock_async.return_value.voicebox_app.return_value = mock_voicebox_app

        with pytest.raises(VoiceboxAPIError):
            await voicebox_client.async_generate_query(sample_question)


class TestVoiceboxClientSyncMethods:
    """Tests for synchronous methods of VoiceboxClient."""

    def test_get_settings(self, voicebox_client):
        """Test get_settings method (sync wrapper)."""
        settings = voicebox_client.get_settings()

        assert settings["name"] == "test-voicebox-app"
        assert settings["database"] == "test-database"

    def test_ask(self, voicebox_client, sample_question):
        """Test ask method (sync wrapper)."""
        result = voicebox_client.ask(sample_question)

        assert "answer" in result
        assert "sparql_query" in result
        assert "interpreted_question" in result
        assert "conversation_id" in result
        assert "message_id" in result

    def test_generate_query(self, voicebox_client, sample_question):
        """Test generate_query method (sync wrapper)."""
        result = voicebox_client.generate_query(sample_question)

        assert "sparql_query" in result
        assert "interpreted_question" in result

    def test_get_settings_api_error(self, voicebox_client, mock_cloud_client):
        """Test get_settings raises VoiceboxAPIError on failure."""
        from unittest.mock import MagicMock

        from langchain_stardog.voicebox import VoiceboxAPIError

        # Make the sync client raise an exception
        mock_sync, mock_async = mock_cloud_client
        mock_voicebox_app = MagicMock()
        mock_voicebox_app.settings = MagicMock(side_effect=Exception("API Error"))
        mock_sync.return_value.voicebox_app.return_value = mock_voicebox_app

        with pytest.raises(VoiceboxAPIError):
            voicebox_client.get_settings()

    def test_ask_api_error(self, voicebox_client, sample_question, mock_cloud_client):
        """Test ask raises VoiceboxAPIError on failure."""
        from unittest.mock import MagicMock

        from langchain_stardog.voicebox import VoiceboxAPIError

        # Make the sync client raise an exception
        mock_sync, mock_async = mock_cloud_client
        mock_voicebox_app = MagicMock()
        mock_voicebox_app.ask = MagicMock(side_effect=Exception("API Error"))
        mock_sync.return_value.voicebox_app.return_value = mock_voicebox_app

        with pytest.raises(VoiceboxAPIError):
            voicebox_client.ask(sample_question)

    def test_generate_query_api_error(
        self, voicebox_client, sample_question, mock_cloud_client
    ):
        """Test generate_query raises VoiceboxAPIError on failure."""
        from unittest.mock import MagicMock

        from langchain_stardog.voicebox import VoiceboxAPIError

        # Make the sync client raise an exception
        mock_sync, mock_async = mock_cloud_client
        mock_voicebox_app = MagicMock()
        mock_voicebox_app.generate_query = MagicMock(side_effect=Exception("API Error"))
        mock_sync.return_value.voicebox_app.return_value = mock_voicebox_app

        with pytest.raises(VoiceboxAPIError):
            voicebox_client.generate_query(sample_question)
