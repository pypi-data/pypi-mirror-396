from typing import Any, Optional, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

from .client import VoiceboxClient
from .runnables import (
    VoiceboxAskRunnable,
    VoiceboxGenerateQueryRunnable,
    VoiceboxSettingsRunnable,
)


# Input schemas for tools
class VoiceboxSettingsInput(BaseModel):
    """Input schema for VoiceboxSettingsTool (no inputs required)."""

    pass


class VoiceboxAskInput(BaseModel):
    """Input schema for VoiceboxAskTool."""

    question: str = Field(description="Natural language question to ask Voicebox")
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation ID for multi-turn conversations",
    )


class VoiceboxGenerateQueryInput(BaseModel):
    """Input schema for VoiceboxGenerateQueryTool."""

    question: str = Field(
        description="Natural language question to convert to a SPARQL query"
    )
    conversation_id: Optional[str] = Field(
        default=None, description="Optional conversation ID for context"
    )


class VoiceboxSettingsTool(BaseTool):
    """Tool for retrieving Voicebox application settings.

    This tool retrieves the configuration and metadata for a Voicebox application.
    It can be used in LangChain agents to understand the available data sources.

    Credentials are loaded from environment variables:
        - SD_VOICEBOX_API_TOKEN (required)
        - SD_VOICEBOX_CLIENT_ID (optional, defaults to VBX-LANGCHAIN)
        - SD_CLOUD_ENDPOINT (optional, defaults to https://cloud.stardog.com/api)

    Example:
        >>> tool = VoiceboxSettingsTool()
        >>> settings = await tool._arun()
        >>> print(settings["database"])
    """

    name: str = "voicebox_settings"
    description: str = (
        "Retrieve Voicebox application settings like database name, "
        "model name, named graphs, and reasoning configuration"
    )
    args_schema: Type[BaseModel] = VoiceboxSettingsInput

    _runnable: VoiceboxSettingsRunnable = PrivateAttr()

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the tool from environment variables."""
        super().__init__(**kwargs)
        client = VoiceboxClient.from_env()
        self._runnable = VoiceboxSettingsRunnable(client)

    def _run(self) -> dict[str, Any]:
        """Execute the tool synchronously."""
        return self._runnable.invoke({})

    async def _arun(self) -> dict[str, Any]:
        """Execute the tool asynchronously."""
        return await self._runnable.ainvoke({})


class VoiceboxAskTool(BaseTool):
    """Tool for asking questions to Voicebox.

    This tool asks natural language questions and receives answers
    from Stardog Voicebox. It's ideal for question-answering tasks in agents.

    Credentials are loaded from environment variables:
        - SD_VOICEBOX_API_TOKEN (required)
        - SD_VOICEBOX_CLIENT_ID (optional, defaults to VBX-LANGCHAIN)
        - SD_CLOUD_ENDPOINT (optional, defaults to https://cloud.stardog.com/api)

    Example:
        >>> tool = VoiceboxAskTool()
        >>> result = await tool._arun(question="What flights are delayed?")
        >>> print(result["answer"])
    """

    name: str = "voicebox_ask"
    description: str = (
        "Ask a natural language question to Stardog Voicebox and get an answer. "
        "Conversation_id is to be left blank for new conversation (system creates one automatically) "
        "but needs to be supplied for multi-turn conversations to maintain the same conversation history/thread"
    )
    args_schema: Type[BaseModel] = VoiceboxAskInput

    _runnable: VoiceboxAskRunnable = PrivateAttr()

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the tool from environment variables."""
        super().__init__(**kwargs)
        client = VoiceboxClient.from_env()
        self._runnable = VoiceboxAskRunnable(client)

    def _run(
        self,
        question: str,
        conversation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute the tool synchronously."""
        return self._runnable.invoke(
            {"question": question, "conversation_id": conversation_id}
        )

    async def _arun(
        self,
        question: str,
        conversation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute the tool asynchronously."""
        return await self._runnable.ainvoke(
            {"question": question, "conversation_id": conversation_id}
        )


class VoiceboxGenerateQueryTool(BaseTool):
    """Tool for generating SPARQL queries from natural language.

    This tool generates SPARQL queries from natural language questions
    without executing them.

    Credentials are loaded from environment variables:
        - SD_VOICEBOX_API_TOKEN (required)
        - SD_VOICEBOX_CLIENT_ID (optional, defaults to VBX-LANGCHAIN)
        - SD_CLOUD_ENDPOINT (optional, defaults to https://cloud.stardog.com/api)

    Example:
        >>> tool = VoiceboxGenerateQueryTool()
        >>> result = await tool._arun(question="Show me all airports")
        >>> print(result["sparql_query"])
    """

    name: str = "voicebox_generate_query"
    description: str = (
        "Generate a SPARQL query from a natural language question without executing it. "
        "Conversation_id is to be left blank for new conversation (system creates one automatically) "
        "but needs to be supplied for multi-turn conversations to maintain the same conversation history/thread"
    )
    args_schema: Type[BaseModel] = VoiceboxGenerateQueryInput

    _runnable: VoiceboxGenerateQueryRunnable = PrivateAttr()

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the tool from environment variables."""
        super().__init__(**kwargs)
        client = VoiceboxClient.from_env()
        self._runnable = VoiceboxGenerateQueryRunnable(client)

    def _run(
        self,
        question: str,
        conversation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute the tool synchronously."""
        return self._runnable.invoke(
            {"question": question, "conversation_id": conversation_id}
        )

    async def _arun(
        self,
        question: str,
        conversation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute the tool asynchronously."""
        return await self._runnable.ainvoke(
            {"question": question, "conversation_id": conversation_id}
        )
