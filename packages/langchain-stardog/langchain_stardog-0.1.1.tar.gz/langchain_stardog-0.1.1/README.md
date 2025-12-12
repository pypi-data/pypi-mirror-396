# Stardog LangChain Integration

[![PyPI version](https://badge.fury.io/py/langchain-stardog.svg)](https://badge.fury.io/py/langchain-stardog)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

LangChain integration for Stardog Voicebox - enabling natural language querying over your enterprise data using LangChain runnables and tools.

## Features

- **LangChain Tools**: Ready-to-use tools for LangChain agents
- **LCEL Runnables**: Composable runnables for building chains
- **Async & Sync**: Full support for both async and synchronous operations

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [Setup Environment Variables](#setup-environment-variables)
  - [Basic Usage with Tools](#basic-usage-with-tools)
  - [Using Runnables in LCEL Chains](#using-runnables-in-lcel-chains)
- [Class Reference](#class-reference)
  - [VoiceboxAskRunnable](#voiceboxaskrunnable)
  - [VoiceboxAskTool](#voiceboxasktool)
  - [VoiceboxClient](#voiceboxclient)
- [Examples](#examples)
- [Development](#development)
- [Contributing](#contributing)
- [General Support](#general-support)

## Requirements

- Python 3.10+ 
- A Stardog Cloud account with a Voicebox application
- Voicebox API token (process to obtain explained below)
- uv: a python package manager for development and contributions ([uv](https://github.com/astral-sh/uv))

## Installation

```bash
pip install langchain-stardog
```

## Quick Start

### Setup Environment Variables

The simplest way to get started is to set your API token as an environment variable:

```bash
export SD_VOICEBOX_API_TOKEN="your-voicebox-api-token"
```

**Getting Your API Token:**
1. Log in to [Stardog Cloud](https://cloud.stardog.com)
2. Click on your profile icon and select **Manage API Keys**.
3. Create a new application and generate a secret.
4. Copy the API token and keep it secure.
5. For more details, see [Stardog Voicebox API access](https://docs.stardog.com/voicebox/voicebox-dev-guide/#api-access).

**Optional Environment Variables:**
```bash
export SD_VOICEBOX_CLIENT_ID="my-app"                      # Client identifier (default: VBX-LANGCHAIN)
export SD_CLOUD_ENDPOINT="https://cloud.stardog.com/api"  # Custom endpoint (optional)
```

### Basic Usage with Tools

Tools are designed for agent workflows and automatically load credentials from environment variables:

```python
from langchain_stardog.voicebox import VoiceboxAskTool

# Tools automatically load credentials from SD_VOICEBOX_API_TOKEN
ask_tool = VoiceboxAskTool()

# Ask a question
result = await ask_tool._arun(question="What flights are delayed?")
print(result["answer"])
```

**Note**: Tools only support environment variable initialization to ensure consistent, secure configuration in agent workflows.

### Using Runnables in LCEL Chains

Runnables support two initialization patterns:

**Pattern 1: Auto-load from Environment (Simple)**

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_stardog.voicebox import VoiceboxAskRunnable

# Automatically loads from SD_VOICEBOX_API_TOKEN
chain = (
    RunnablePassthrough()
    | VoiceboxAskRunnable()
    | (lambda x: f"Answer: {x['answer']}")
)

result = await chain.ainvoke({"question": "Show me airports in Texas"})
```

**Pattern 2: Explicit Client (Advanced)**

```python
from langchain_core.runnables import RunnablePassthrough
from langchain_stardog.voicebox import VoiceboxClient, VoiceboxAskRunnable

# Create client for custom configuration
client = VoiceboxClient(
    api_token="your-token",
    client_id="my-app"
)

chain = (
    RunnablePassthrough()
    | VoiceboxAskRunnable(client=client)
    | (lambda x: f"Answer: {x['answer']}")
)

result = await chain.ainvoke({"question": "Show me airports in Texas"})
```

## Class Reference

The library provides the following main classes:

**Runnables** (for LCEL chains):
- `VoiceboxSettingsRunnable` - Retrieve app settings
- `VoiceboxAskRunnable` - Ask questions and get answers
- `VoiceboxGenerateQueryRunnable` - Generate SPARQL queries

**Tools** (for agent integration):
- `VoiceboxSettingsTool`
- `VoiceboxAskTool`
- `VoiceboxGenerateQueryTool`

**Client**:
- `VoiceboxClient` - Core client for Stardog Voicebox API

### VoiceboxAskRunnable

**Initialization:**

```python
# From environment variables (simple)
runnable = VoiceboxAskRunnable()

# With explicit client (advanced)
client = VoiceboxClient.from_env()
runnable = VoiceboxAskRunnable(client=client)
```

**Usage:**

```python
# Async
result = await runnable.ainvoke({
    "question": "Your question here",
    "conversation_id": "optional-conv-id"
})

# Sync
result = runnable.invoke({
    "question": "Your question here",
    "conversation_id": "optional-conv-id"
})
```

**Output:**
```python
{
    "answer": "Natural language answer",
    "sparql_query": "SELECT ...",
    "interpreted_question": "How Voicebox understood it",
    "conversation_id": "conv-123",
    "message_id": "msg-456"
}
```

### VoiceboxAskTool

**Initialization:**

Tools only support environment variable initialization for consistent, secure agent workflows:

```python
# Automatically loads from SD_VOICEBOX_API_TOKEN
tool = VoiceboxAskTool()
```

**Usage:**

```python
# Async
result = await tool._arun(
    question="Your question",
    conversation_id="optional"  # Optional: for multi-turn conversations
)

# Sync
result = tool._run(
    question="Your question",
    conversation_id="optional"
)
```

### VoiceboxClient

**Initialization:**

```python
# From environment variables (recommended)
client = VoiceboxClient.from_env()

# With custom configuration
client = VoiceboxClient.from_env(
    client_id="my-app",           # Optional: override default client ID
    endpoint="custom-endpoint"     # Optional: custom API endpoint
)

# Direct initialization (advanced)
client = VoiceboxClient(
    api_token="your-token",           # Required: Voicebox API token
    client_id="my-app",                # Optional: Client identifier (default: VBX-LANGCHAIN)
    endpoint="https://...",            # Optional: API endpoint
    auth_token_override="sso-token"    # Optional: SSO auth token
)
```

**Methods:**
- `async_get_settings()` / `get_settings()` - Get Voicebox app settings
- `async_ask(question, conversation_id=None)` / `ask(...)` - Ask a question
- `async_generate_query(question, conversation_id=None)` / `generate_query(...)` - Generate SPARQL query

## Examples

Check out the [`examples/`](https://github.com/stardog-union/stardog-langchain/tree/main/examples/) directory for basic examples on how to use the library:

- [`direct_tool_usage.py`](https://github.com/stardog-union/stardog-langchain/blob/main/examples/direct_tool_usage.py) - Direct tool usage and multi-turn conversations
- [`agent_integration.py`](https://github.com/stardog-union/stardog-langchain/blob/main/examples/agent_integration.py) - Agent integration using AWS Bedrock
- [`runnable_chains.py`](https://github.com/stardog-union/stardog-langchain/blob/main/examples/runnable_chains.py) - LCEL chains with runnables

## Development

### Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/stardog-union/stardog-langchain.git
cd stardog-langchain
make install-dev
```

Common development commands:

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Type checking
make type-check

# Linting
make lint

# Run all CI checks (format, type-check, lint, test)
make ci
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes, add tests and run `make test` to verify
4. Run `make ci` to verify all static code quality checks pass
5. Submit a pull request


## General Support

- **Documentation**: [Stardog Documentation](https://docs.stardog.com/)
- **Community**: [Stardog Community](https://community.stardog.com/)

