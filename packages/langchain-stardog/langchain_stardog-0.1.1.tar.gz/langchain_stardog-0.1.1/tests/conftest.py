"""Pytest fixtures for Stardog Voicebox LangChain tests."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from langchain_stardog.voicebox import VoiceboxClient


@pytest.fixture
def mock_voicebox_settings():
    """Mock Voicebox settings response."""
    settings = MagicMock()
    settings.name = "test-voicebox-app"
    settings.database = "test-database"
    settings.model = "test-model"
    settings.named_graphs = ["http://example.org/graph1", "http://example.org/graph2"]
    settings.reasoning = True
    return settings


@pytest.fixture
def mock_voicebox_answer():
    """Mock Voicebox answer response."""
    answer = MagicMock()
    answer.content = (
        "There are 5 delayed flights: AA101, UA202, DL303, BA404, and LH505."
    )
    answer.interpreted_question = "Which flights are currently delayed?"
    answer.query = (
        "SELECT ?flight WHERE { ?flight rdf:type :Flight ; :status :Delayed }"
    )
    answer.conversation_id = "conv-123"
    answer.message_id = "msg-456"
    return answer


@pytest.fixture
def mock_voicebox_query_response():
    """Mock Voicebox generate_query response."""
    response = MagicMock()
    response.query = "SELECT ?airport WHERE { ?airport rdf:type :Airport }"
    response.interpreted_question = "List all airports"
    response.conversation_id = "conv-789"
    response.message_id = "msg-012"
    return response


@pytest.fixture
def mock_cloud_client(
    mock_voicebox_settings, mock_voicebox_answer, mock_voicebox_query_response
):
    """Mock pystardog cloud client."""
    with (
        patch("langchain_stardog.voicebox.client.StardogClient") as mock_sync_client,
        patch(
            "langchain_stardog.voicebox.client.StardogAsyncClient"
        ) as mock_async_client,
    ):
        # Create mock Voicebox app for async client
        mock_async_voicebox_app = MagicMock()
        mock_async_voicebox_app.async_settings = AsyncMock(
            return_value=mock_voicebox_settings
        )
        mock_async_voicebox_app.async_ask = AsyncMock(return_value=mock_voicebox_answer)
        mock_async_voicebox_app.async_generate_query = AsyncMock(
            return_value=mock_voicebox_query_response
        )

        # Create mock Voicebox app for sync client
        mock_sync_voicebox_app = MagicMock()
        mock_sync_voicebox_app.settings = MagicMock(return_value=mock_voicebox_settings)
        mock_sync_voicebox_app.ask = MagicMock(return_value=mock_voicebox_answer)
        mock_sync_voicebox_app.generate_query = MagicMock(
            return_value=mock_voicebox_query_response
        )

        # Configure async client instance to return async voicebox app
        mock_async_client_instance = MagicMock()
        mock_async_client_instance.voicebox_app = MagicMock(
            return_value=mock_async_voicebox_app
        )
        mock_async_client.return_value = mock_async_client_instance

        # Configure sync client instance to return sync voicebox app
        mock_sync_client_instance = MagicMock()
        mock_sync_client_instance.voicebox_app = MagicMock(
            return_value=mock_sync_voicebox_app
        )
        mock_sync_client.return_value = mock_sync_client_instance

        yield (mock_sync_client, mock_async_client)


@pytest.fixture
def voicebox_client(mock_cloud_client):
    """Create a VoiceboxClient with mocked backend"""
    return VoiceboxClient(
        api_token="test-token",
        client_id="test-client",
        endpoint="https://test.stardog.com/api",
    )


@pytest.fixture
def sample_question():
    """Sample question for testing."""
    return "What flights are delayed?"


@pytest.fixture
def sample_conversation_id():
    """Sample conversation ID for testing."""
    return "conv-test-123"


@pytest.fixture(autouse=True)
def setup_env_for_standard_tests(mock_cloud_client, monkeypatch):
    """Setup environment variables for LangChain standard tests."""
    monkeypatch.setenv("SD_VOICEBOX_API_TOKEN", "test-token-for-standard-tests")
    monkeypatch.setenv("SD_VOICEBOX_CLIENT_ID", "test-client-standard")
    yield
