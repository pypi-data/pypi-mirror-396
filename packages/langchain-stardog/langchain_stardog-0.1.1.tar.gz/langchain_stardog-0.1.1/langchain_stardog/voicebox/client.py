import os
from typing import Any, Optional

from stardog.cloud.client import AsyncClient as StardogAsyncClient
from stardog.cloud.client import Client as StardogClient

from .constants import (
    DEFAULT_CLIENT_ID,
    DEFAULT_STARDOG_CLOUD_ENDPOINT,
    ENV_CLOUD_ENDPOINT,
    ENV_VOICEBOX_API_TOKEN,
    ENV_VOICEBOX_CLIENT_ID,
)
from .exceptions import (
    VoiceboxAPIError,
    VoiceboxAuthenticationError,
    VoiceboxValidationError,
)


class VoiceboxClient:
    """Client for interacting with Stardog Voicebox API.

    This client provides both synchronous and asynchronous methods for
    interacting with the Voicebox API. It wraps the pystardog library
    and provides a clean interface for LangChain integration.

    Args:
        api_token: Voicebox application API token
        client_id: Optional client identifier (default: "VBX-LANGCHAIN")
        endpoint: Stardog Cloud API endpoint (default: https://cloud.stardog.com/api)
        auth_token_override: Optional auth token override for SSO scenarios
    """

    def __init__(
        self,
        api_token: str,
        client_id: Optional[str] = None,
        endpoint: str = DEFAULT_STARDOG_CLOUD_ENDPOINT,
        auth_token_override: Optional[str] = None,
    ) -> None:
        """Initialize the Voicebox client."""
        if not api_token:
            raise VoiceboxAuthenticationError("API token is required")

        self.api_token = api_token
        self.client_id = client_id or DEFAULT_CLIENT_ID
        self.endpoint = endpoint
        self.auth_token_override = auth_token_override

    @classmethod
    def from_env(
        cls,
        client_id: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> "VoiceboxClient":
        """Create a VoiceboxClient from environment variables.

        This is a convenience method for creating a client using configuration
        from environment variables. Useful for agent workflows and production
        deployments.

        Environment Variables:
            SD_VOICEBOX_API_TOKEN: Required. Voicebox application API token
            SD_VOICEBOX_CLIENT_ID: Optional. Client identifier (default: VBX-LANGCHAIN)
            SD_CLOUD_ENDPOINT: Optional. Stardog Cloud endpoint (default: https://cloud.stardog.com/api)

        Args:
            client_id: Override for client ID (takes precedence over env var)
            endpoint: Override for endpoint (takes precedence over env var)

        Returns:
            VoiceboxClient instance configured from environment

        Raises:
            VoiceboxAuthenticationError: If SD_VOICEBOX_API_TOKEN is not set

        Example:
            >>> client = VoiceboxClient.from_env()
            >>> # With overrides
            >>> client = VoiceboxClient.from_env(client_id="my-app")
        """
        api_token = os.getenv(ENV_VOICEBOX_API_TOKEN)
        if not api_token:
            raise VoiceboxAuthenticationError(
                f"Environment variable {ENV_VOICEBOX_API_TOKEN} is not set. "
                f"Please set it to your Voicebox application API token."
            )

        # Resolve client_id with fallback to env var and default
        resolved_client_id = (
            client_id
            if client_id is not None
            else os.getenv(ENV_VOICEBOX_CLIENT_ID, DEFAULT_CLIENT_ID)
        )

        # Resolve endpoint with fallback to env var and default
        resolved_endpoint = (
            endpoint
            if endpoint is not None
            else os.getenv(ENV_CLOUD_ENDPOINT, DEFAULT_STARDOG_CLOUD_ENDPOINT)
        )

        return cls(
            api_token=api_token,
            client_id=resolved_client_id,
            endpoint=resolved_endpoint,
        )

    def _validate_question(self, question: str) -> None:
        """Validate that question is not empty.

        Args:
            question: Question to validate

        Raises:
            VoiceboxValidationError: If question is empty
        """
        if not question or not question.strip():
            raise VoiceboxValidationError("Question cannot be empty")

    # Async methods
    async def async_get_settings(self) -> dict[str, Any]:
        """Get Voicebox application settings asynchronously.

        Returns:
            Dictionary containing Voicebox app settings

        Raises:
            VoiceboxAPIError: If the API request fails
        """
        try:
            async_client = StardogAsyncClient(base_url=self.endpoint)
            voicebox_app = async_client.voicebox_app(
                app_api_token=self.api_token, client_id=self.client_id
            )
            settings = await voicebox_app.async_settings()
            return {
                "name": settings.name,
                "database": settings.database,
                "model": settings.model,
                "named_graphs": settings.named_graphs,
                "reasoning": settings.reasoning,
            }
        except Exception as e:
            raise VoiceboxAPIError(
                f"Failed to retrieve Voicebox settings: {str(e)}", exception=e
            ) from e

    async def async_ask(
        self,
        question: str,
        conversation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Ask a question to Voicebox asynchronously.

        Args:
            question: Natural language question
            conversation_id: Optional conversation ID for multi-turn conversations

        Returns:
            Dictionary containing the answer, query, and conversation metadata

        Raises:
            VoiceboxValidationError: If the question is empty
            VoiceboxAPIError: If the API request fails
        """
        self._validate_question(question)

        try:
            async_client = StardogAsyncClient(base_url=self.endpoint)
            voicebox_app = async_client.voicebox_app(
                app_api_token=self.api_token, client_id=self.client_id
            )
            answer = await voicebox_app.async_ask(
                question=question,
                conversation_id=conversation_id,
                client_id=self.client_id,
                stardog_auth_token_override=self.auth_token_override,
            )
            return {
                "answer": answer.content,
                "interpreted_question": answer.interpreted_question,
                "sparql_query": answer.sparql_query,
                "conversation_id": answer.conversation_id,
                "message_id": answer.message_id,
            }
        except VoiceboxValidationError:
            raise
        except Exception as e:
            raise VoiceboxAPIError(
                f"Failed to ask question: {str(e)}", exception=e
            ) from e

    async def async_generate_query(
        self,
        question: str,
        conversation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Generate a SPARQL query from a natural language question asynchronously.

        Args:
            question: Natural language question
            conversation_id: Optional conversation ID for context

        Returns:
            Dictionary containing the generated query and metadata

        Raises:
            VoiceboxValidationError: If the question is empty
            VoiceboxAPIError: If the API request fails
        """
        self._validate_question(question)

        try:
            async_client = StardogAsyncClient(base_url=self.endpoint)
            voicebox_app = async_client.voicebox_app(
                app_api_token=self.api_token, client_id=self.client_id
            )
            response = await voicebox_app.async_generate_query(
                question=question,
                conversation_id=conversation_id,
                client_id=self.client_id,
                stardog_auth_token_override=self.auth_token_override,
            )
            return {
                "sparql_query": response.sparql_query,
                "interpreted_question": response.interpreted_question,
                "conversation_id": response.conversation_id,
                "message_id": response.message_id,
            }
        except VoiceboxValidationError:
            raise
        except Exception as e:
            raise VoiceboxAPIError(
                f"Failed to generate query: {str(e)}", exception=e
            ) from e

    # Synchronous methods
    def get_settings(self) -> dict[str, Any]:
        """Get Voicebox application settings synchronously.

        Returns:
            Dictionary containing Voicebox app settings

        Raises:
            VoiceboxAPIError: If the API request fails
        """
        try:
            sync_client = StardogClient(base_url=self.endpoint)
            voicebox_app = sync_client.voicebox_app(
                app_api_token=self.api_token, client_id=self.client_id
            )
            settings = voicebox_app.settings()
            return {
                "name": settings.name,
                "database": settings.database,
                "model": settings.model,
                "named_graphs": settings.named_graphs,
                "reasoning": settings.reasoning,
            }
        except Exception as e:
            raise VoiceboxAPIError(
                f"Failed to retrieve Voicebox settings: {str(e)}", exception=e
            ) from e

    def ask(
        self,
        question: str,
        conversation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Ask a question to Voicebox synchronously.

        Args:
            question: Natural language question
            conversation_id: Optional conversation ID for multi-turn conversations

        Returns:
            Dictionary containing the answer, query, and conversation metadata

        Raises:
            VoiceboxValidationError: If the question is empty
            VoiceboxAPIError: If the API request fails
        """
        self._validate_question(question)

        try:
            sync_client = StardogClient(base_url=self.endpoint)
            voicebox_app = sync_client.voicebox_app(
                app_api_token=self.api_token, client_id=self.client_id
            )
            answer = voicebox_app.ask(
                question=question,
                conversation_id=conversation_id,
                client_id=self.client_id,
                stardog_auth_token_override=self.auth_token_override,
            )
            return {
                "answer": answer.content,
                "interpreted_question": answer.interpreted_question,
                "sparql_query": answer.sparql_query,
                "conversation_id": answer.conversation_id,
                "message_id": answer.message_id,
            }
        except VoiceboxValidationError:
            raise
        except Exception as e:
            raise VoiceboxAPIError(
                f"Failed to ask question: {str(e)}", exception=e
            ) from e

    def generate_query(
        self,
        question: str,
        conversation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Generate a SPARQL query from a natural language question synchronously.

        Args:
            question: Natural language question
            conversation_id: Optional conversation ID for context

        Returns:
            Dictionary containing the generated query and metadata

        Raises:
            VoiceboxValidationError: If the question is empty
            VoiceboxAPIError: If the API request fails
        """
        self._validate_question(question)

        try:
            sync_client = StardogClient(base_url=self.endpoint)
            voicebox_app = sync_client.voicebox_app(
                app_api_token=self.api_token, client_id=self.client_id
            )
            response = voicebox_app.generate_query(
                question=question,
                conversation_id=conversation_id,
                client_id=self.client_id,
                stardog_auth_token_override=self.auth_token_override,
            )
            return {
                "sparql_query": response.sparql_query,
                "interpreted_question": response.interpreted_question,
                "conversation_id": response.conversation_id,
                "message_id": response.message_id,
            }
        except VoiceboxValidationError:
            raise
        except Exception as e:
            raise VoiceboxAPIError(
                f"Failed to generate query: {str(e)}", exception=e
            ) from e
