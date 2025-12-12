"""Example demonstrating Voicebox Runnables and Chains usage.

This example shows how to use Voicebox runnables in LangChain Expression Language (LCEL)
chains for building custom workflows.

Runnables support two initialization patterns:
1. From environment variables (simple, recommended)
2. With explicit VoiceboxClient (for custom configuration)

Required Environment Variables:
    SD_VOICEBOX_API_TOKEN: Your Voicebox application API token

Note:
    This example uses questions from the Flight Planning knowledge kit.
    To run this example successfully, you need to either:
    1. Install the Flight Planning kit to your Stardog instance:
       https://cloud.stardog.com/kits/default:flight_planning:1.0
    2. Modify the questions to match your configured database domain. To create an API token for a database,
       refer to 'Getting your API token' under the 'Quick Start' section of the README
"""

import asyncio
import os

from langchain_core.runnables import RunnablePassthrough

from langchain_stardog.voicebox import (
    VoiceboxAskRunnable,
    VoiceboxClient,
)


async def example_basic_runnable():
    """Example 1: Basic runnable usage loading keys from environment vars."""
    print("=== Example 1: Basic Runnable (environment vars) ===\n")

    # Pattern 1: Runnables can auto-load from environment vars
    if not os.getenv("SD_VOICEBOX_API_TOKEN"):
        print("Please set SD_VOICEBOX_API_TOKEN environment variable")
        return

    # Simple initialization - reads from SD_VOICEBOX_API_TOKEN
    ask_runnable = VoiceboxAskRunnable()

    # Use it directly
    result = await ask_runnable.ainvoke(
        {"question": "How many aerodromes are there in FL?"}
    )

    if result["answer"]:
        print(f"Answer: {result['answer']}")
    else:
        print("Answer not found, please debug your application setup.")


async def example_explicit_client():
    """Example 2: Using explicit client (programmatic configuration)."""
    print("=== Example 2: Runnable with Explicit Client (advanced) ===\n")

    # Pattern 2: For custom configuration, create explicit client
    api_token = os.getenv("SD_VOICEBOX_API_TOKEN")
    client = VoiceboxClient(
        api_token=api_token,
        client_id="custom-app",
    )

    # Pass client to runnable
    ask_runnable = VoiceboxAskRunnable(client=client)
    result = await ask_runnable.ainvoke({"question": "Which airports are in Texas?"})
    if result["answer"]:
        print(f"Answer: {result['answer']}")
    else:
        print("Answer not found, please debug your application setup.")


async def example_lcel_chain():
    """Example 3: Composing runnables with LCEL."""
    print("=== Example 3: LCEL Chain Composition ===\n")

    # Build a chain: input -> Voicebox -> extract answer
    chain = (
        RunnablePassthrough()
        | VoiceboxAskRunnable()  # Reads from environment
        | (
            lambda x: f"Answer: {x['answer']}\n\nInternal Conversation ID: {x['conversation_id']}"
        )
    )

    result = await chain.ainvoke({"question": "Show me airports in Texas"})
    print(result)


async def main():
    """Run all examples."""
    api_token = os.getenv("SD_VOICEBOX_API_TOKEN")
    if not api_token:
        print("Please set SD_VOICEBOX_API_TOKEN environment variable")
        print("Example: export SD_VOICEBOX_API_TOKEN='your-token-here'")
        return

    await example_basic_runnable()
    await example_explicit_client()
    await example_lcel_chain()

    print("=== All Examples Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
