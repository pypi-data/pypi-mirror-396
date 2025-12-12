"""Basic example demonstrating Voicebox Tools usage.

This example shows how to use Voicebox tools directly for simple
question-answering tasks.

Tools automatically load credentials from environment variables.
This is the recommended pattern for agent workflows and production usage.

Required Environment Variables:
    SD_VOICEBOX_API_TOKEN: Your Voicebox application API token

Note:
    This example uses questions from the Flight Planning knowledge kit.
    To run this example successfully, you need to either:
    1. Install the Flight Planning kit to your Stardog instance:
       https://cloud.stardog.com/kits/default:flight_planning:1.0
    2. Modify the questions to match your configured database domain. To create an api token for a database,
       refer to 'Getting your API token' under the 'Quick Start' section of the README
"""

import asyncio
import os

from langchain_stardog.voicebox import (
    VoiceboxAskTool,
    VoiceboxGenerateQueryTool,
    VoiceboxSettingsTool,
)


async def main():

    # Check if environment variable is set
    api_token = os.getenv("SD_VOICEBOX_API_TOKEN")
    if not api_token:
        print("Please set SD_VOICEBOX_API_TOKEN environment variable")
        print("Example: export SD_VOICEBOX_API_TOKEN='your-token-here'")
        print("\nOptional environment variables:")
        print("  SD_VOICEBOX_CLIENT_ID - Client identifier (default: VBX-LANGCHAIN)")
        print(
            "  SD_CLOUD_ENDPOINT - API endpoint (default: https://cloud.stardog.com/api)"
        )
        return

    print("=== Voicebox Tools Example ===\n")

    # Tools automatically load keys from environment variables
    print("Initializing tools...")
    setting_tool = VoiceboxSettingsTool()
    ask_tool = VoiceboxAskTool()
    query_tool = VoiceboxGenerateQueryTool()
    print("✓ Tools initialized successfully\n")

    # Example 1: Fetch the application settings
    print("Example 1: Fetching Voicebox settings")
    settings = await setting_tool._arun()
    print(f"Voicebox settings: {settings}\n")

    # Example 2: Ask a question and get an answer
    print("Example 2: Asking a question")
    question = "How many aerodromes are there in FL?"
    result = await ask_tool._arun(question=question)

    print(f"Question: {question}")
    print(f"Answer: {result['answer']}")
    print(f"Conversation ID: {result['conversation_id']}\n")

    # Example 3: Generate the sparql query corresponding to the natural language question
    print("Example 3: Generating a SPARQL query")
    question2 = "List the airports in California?"
    query_result = await query_tool._arun(question=question2)

    print(f"Question: {question2}")
    print(f"Generated Query: {query_result['sparql_query']}")
    print(f"Interpreted as: {query_result['interpreted_question']}\n")

    # Example 4: Multi-turn conversation
    print("Example 4: Multi-turn conversation")
    first_question = "What flights depart from SFO?"
    first_result = await ask_tool._arun(question=first_question)

    print(f"Question 1: {first_question}")
    print(f"Answer 1: {first_result['answer']}\n")

    # Use the conversation_id for follow-up
    conversation_id = first_result["conversation_id"]
    followup_question = "Which of those are going to New York?"
    followup_result = await ask_tool._arun(
        question=followup_question, conversation_id=conversation_id
    )

    print(f"Question 2: {followup_question}")
    print(f"Answer 2: {followup_result['answer']}\n")

    print("=== Example Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
