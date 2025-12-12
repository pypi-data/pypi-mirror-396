"""Example demonstrating Voicebox tools integration with LangChain agents using AWS Bedrock.

This example shows how to use Voicebox tools with a LangChain agent
and AWS Bedrock as the LLM provider to enable the agent to query a knowledge graph.

Tools automatically load credentials from environment variables.
This is the recommended pattern for agent workflows.

Required Environment Variables:
    SD_VOICEBOX_API_TOKEN: Your Voicebox application API token
    AWS_ACCESS_KEY_ID: Your AWS access key
    AWS_SECRET_ACCESS_KEY: Your AWS secret key
    AWS_REGION: Your AWS region (e.g., us-east-1)

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

# Note: This example requires langchain and langchain-aws
# Install with: uv pip install langchain-aws
try:
    from langchain.agents import create_agent
    from langchain_aws import ChatBedrock
except ImportError as error:
    print(f"Error ==> {error}")
    print("This example requires langchain and langchain-aws:")
    print("pip install langchain langchain-aws")
    exit(1)

from langchain_stardog.voicebox import (
    VoiceboxAskTool,
    VoiceboxSettingsTool,
)


async def main():
    """Main example function."""
    if not os.getenv("SD_VOICEBOX_API_TOKEN"):
        print("Please set SD_VOICEBOX_API_TOKEN environment variable")
        return
    if (
        not os.getenv("AWS_ACCESS_KEY_ID")
        or not os.getenv("AWS_SECRET_ACCESS_KEY")
        or not os.getenv("AWS_REGION")
    ):
        print(
            "Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION environment variables"
        )
        return

    print("=== Voicebox Agent Example (using AWS Bedrock) ===\n")

    # Create Voicebox tools (Reads SD_VOICEBOX_API_TOKEN)
    tools = [
        VoiceboxSettingsTool(),
        VoiceboxAskTool(),
    ]
    print("Tools initialized\n")

    # Initialize LLM
    llm = ChatBedrock(
        model_id="us.meta.llama4-maverick-17b-instruct-v1:0",
        region_name=os.getenv("AWS_REGION"),
        temperature=0,
        beta_use_converse_api=True,
    )

    # Create agent graph with Voicebox tools
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="You are a helpful assistant that can answer questions using Voicebox tools.",
        debug=True,
    )

    # Example 1: Query Voicebox configuration
    print("Example 1: Query Voicebox configuration")
    result1 = await agent.ainvoke(
        {
            "messages": [
                {"role": "user", "content": "What are the current Voicebox settings?"}
            ]
        }
    )
    print(f"Result: {result1['messages'][-1].content}\n")

    # Example 2: Query knowledge graph data
    print("\nExample 2: Query knowledge graph data")
    result2 = await agent.ainvoke(
        {
            "messages": [
                {"role": "user", "content": "How many aerodromes are there in FL?"}
            ]
        }
    )
    print(f"Result: {result2['messages'][-1].content}\n")

    print("=== Examples Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
