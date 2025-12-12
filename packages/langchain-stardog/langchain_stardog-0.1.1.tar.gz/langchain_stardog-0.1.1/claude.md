# Claude Session Documentation

This file documents the project state and recent changes for future Claude sessions.

## Project Overview

**Stardog LangChain Integration** - A Python library that provides LangChain integrations for Stardog products. Currently includes Voicebox integration for natural language querying of knowledge graphs.

### Package Structure

```
langchain_stardog/                 # Main package
├── __init__.py                    # Top-level exports (re-exports from submodules)
└── voicebox/                      # Voicebox subpackage
    ├── __init__.py               # Voicebox exports
    ├── client.py                 # VoiceboxClient (formerly voicebox_client.py)
    ├── runnables.py              # Voicebox runnables
    ├── tools.py                  # Voicebox tools
    ├── constants.py              # Constants and defaults
    └── exceptions.py             # Custom exceptions
```

### Key Components

1. **VoiceboxClient** (`langchain_stardog.voicebox.client`)
   - Core client for Stardog Voicebox API
   - Handles authentication and API communication
   - Provides both sync and async methods

2. **Runnables** (`langchain_stardog.voicebox.runnables`)
   - `VoiceboxSettingsRunnable` - Retrieve app settings
   - `VoiceboxAskRunnable` - Ask questions (with answers)
   - `VoiceboxGenerateQueryRunnable` - Generate SPARQL queries
   - Core implementation layer supporting LCEL composition

3. **Tools** (`langchain_stardog.voicebox.tools`)
   - `VoiceboxSettingsTool`
   - `VoiceboxAskTool`
   - `VoiceboxGenerateQueryTool`
   - LangChain BaseTool wrappers around Runnables for agent integration

## Recent Changes (Latest Session - 2025-10-26)

### 1. Environment Variable Naming and Unified Client Creation

**What Changed:**
- Changed environment variable names to use `SD_` prefix for consistency:
  - `STARDOG_VOICEBOX_API_TOKEN` → `SD_VOICEBOX_API_TOKEN`
  - Added `SD_VOICEBOX_CLIENT_ID` (optional, defaults to `VBX-LANGCHAIN`)
  - Added `SD_CLOUD_ENDPOINT` (optional, defaults to `https://cloud.stardog.com/api`)

- Added `VoiceboxClient.from_env()` class method for unified client creation from environment variables

**Implementation:**
- Updated `constants.py` with new environment variable name constants
- Added `VoiceboxClient.from_env()` class method that:
  - Loads credentials from environment variables
  - Accepts optional overrides for `client_id` and `endpoint`
  - Properly resolves Optional types to avoid mypy errors
- Used property pattern with runtime checks to ensure type safety

**Files Modified:**
- `langchain_stardog/constants.py` - Added new env var name constants
- `langchain_stardog/voicebox_client.py` - Added `from_env()` class method

### 2. Simplified Tools to Environment-Only Pattern

**Critical Design Decision:**
- **Tools**: Now ONLY accept environment variables (no client parameter)
  - Designed for agent workflows where consistent, secure configuration is essential
  - Simplified initialization: `VoiceboxAskTool()`

- **Runnables**: Support BOTH patterns (env vars OR explicit client)
  - Provides flexibility for advanced use cases
  - Defaults to loading from env vars if no client provided
  - Accepts optional client parameter for custom configurations

**Implementation:**
- Tools use `PrivateAttr()` for private `_runnable` field (avoids Pydantic naming restrictions)
- Tools create client via `VoiceboxClient.from_env()` in `__init__`
- Runnables accept optional `client` parameter with env fallback
- Used property pattern for type-safe access to client/runnable

**Files Modified:**
- `langchain_stardog/tools.py` - Removed client parameter, env-only initialization
- `langchain_stardog/runnables.py` - Added optional client parameter with env fallback

### 3. Comprehensive Test Updates

**What Changed:**
- Completely rewrote `tests/test_tools.py` to use environment variables only
- Updated `tests/test_runnables.py` to test both initialization patterns
- Added `setup_env_vars` fixture using monkeypatch for consistent env var setup

**Test Coverage:**
- 51 tests passing (up from 50)
- 95% code coverage (exceeds 90% requirement)
- All initialization patterns tested:
  - Tools: Environment variable loading only
  - Runnables: Both env vars and explicit client
  - Explicit client takes precedence over env vars
  - Missing credentials error handling

**Files Modified:**
- `tests/test_tools.py` - Complete rewrite for env-only pattern
- `tests/test_runnables.py` - Added tests for both patterns
- `tests/conftest.py` - Updated fixtures as needed

### 4. Updated Examples

**Files Modified:**
- `examples/basic_tool_usage.py` - Simplified to show env var pattern for tools only
- `examples/agent_integration.py` - Shows agent workflow with env-only tools
- `examples/runnable_chains.py` - Demonstrates both patterns for runnables

**Key Changes:**
- Tools examples use simplified pattern: `VoiceboxAskTool()` (no parameters)
- Runnable examples show both env var and explicit client patterns
- All examples updated with new `SD_VOICEBOX_API_TOKEN` variable name
- Added clear environment variable setup checks and instructions

### 5. Documentation Updates

**README.md Updates:**
- Updated all environment variable names from `STARDOG_VOICEBOX_*` to `SD_VOICEBOX_*`
- Updated "Setup Environment Variables" section with new variable names and optional variables
- Simplified "Basic Usage with Tools" to show env-only pattern
- Updated "Using Runnables in LCEL Chains" to show both patterns
- Completely rewrote "Configuration" section to explain:
  - Tools: Environment Variables Only (with rationale)
  - Runnables: Both Patterns Supported (with use cases)
- Updated environment variables table with all three variables
- Updated API Reference sections:
  - VoiceboxClient: Added `from_env()` class method documentation
  - VoiceboxAskRunnable: Shows both initialization patterns
  - VoiceboxAskTool: Shows env-only pattern with explanation
- Updated all code examples throughout to use new env var names
- Updated Security Best Practices section with new env var names

**__init__.py Updates:**
- Updated docstrings to reflect new patterns
- Exported new environment variable constants from `constants.py`

**claude.md Updates:**
- This file! Documented all changes from this session

## Initialization Patterns

### Tools: Environment Variables Only

Tools are designed for agent workflows and only support environment variable initialization:

```python
from langchain_stardog import VoiceboxAskTool

# Automatically loads from SD_VOICEBOX_API_TOKEN
tool = VoiceboxAskTool()
```

**Why environment-only?**
- Ensures consistent, secure configuration in agent workflows
- Simplifies agent integration
- Follows security best practices

### Runnables: Two Patterns

Runnables offer flexibility with two initialization patterns:

**Pattern 1: Auto-load from Environment (Simple)**
```python
from langchain_stardog import VoiceboxAskRunnable

# Automatically loads from SD_VOICEBOX_API_TOKEN
runnable = VoiceboxAskRunnable()
```

**Pattern 2: Explicit Client (Advanced)**
```python
from langchain_stardog import VoiceboxClient, VoiceboxAskRunnable

# Create client for custom configuration
client = VoiceboxClient.from_env(client_id="my-app")
runnable = VoiceboxAskRunnable(client=client)
```

**Use cases for explicit client:**
- Custom endpoint configurations
- Multiple Voicebox applications in one script
- Advanced authentication scenarios (SSO)
- Fine-grained client management

## Project Structure

```
langchain-stardog/
├── langchain_stardog/
│   ├── __init__.py              # Package exports
│   ├── constants.py              # Constants and defaults
│   ├── exceptions.py             # Custom exceptions
│   ├── voicebox_client.py       # Core API client
│   ├── runnables.py             # LangChain Runnables (core)
│   └── tools.py                 # LangChain Tools (wrappers)
├── examples/
│   ├── basic_tool_usage.py      # Basic usage, both patterns
│   ├── agent_integration.py     # ReAct agent example
│   └── runnable_chains.py       # LCEL chain examples
├── tests/
│   ├── test_client.py           # Client tests
│   ├── test_runnables.py        # Runnable tests
│   └── test_tools.py            # Tool tests (incl. env var)
├── README.md                     # Main documentation
├── pyproject.toml               # Project config
├── Makefile                     # Common commands
└── claude.md                    # This file
```

## Common Commands

```bash
# Development setup
make install-dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Type checking
make type-check

# Lint
make lint

# Run all CI checks
make ci

# Run examples
export SD_VOICEBOX_API_TOKEN="your-token"
python examples/direct_tool_usage.py
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SD_VOICEBOX_API_TOKEN` | Voicebox API token | Yes* | None |
| `SD_VOICEBOX_CLIENT_ID` | Client identifier | No | `VBX-LANGCHAIN` |
| `SD_CLOUD_ENDPOINT` | Custom API endpoint | No | `https://cloud.stardog.com/api` |
| `OPENAI_API_KEY` | For agent examples | No | None |

\* Required when using auto-load pattern

## Security Best Practices

1. **Never commit tokens** - Add `.env` to `.gitignore`
2. **Use .env files** - For local development with `python-dotenv`
3. **Secrets management** - Use AWS Secrets Manager, Azure Key Vault, etc. in production
4. **Rotate tokens** - Generate new tokens periodically
5. **Least privilege** - Separate tokens for different environments

## Getting Your API Token

1. Log in to [Stardog Cloud](https://cloud.stardog.com)
2. Navigate to your Voicebox application
3. Go to Settings → API Token
4. Copy your application API token

## Known Issues / Future Work

None currently. All tests pass with 95% coverage.

## Important Notes for Future Sessions

1. **Tools vs Runnables - Critical Design Pattern:**
   - **Runnables** are the core implementation layer
   - **Tools** wrap Runnables for agent integration
   - **Tools** ONLY support environment variables (no client parameter)
   - **Runnables** support BOTH env vars and explicit client (flexible)
   - This separation ensures agent workflows are simple and secure, while advanced use cases remain flexible

2. **Environment Variable Names:**
   - Use `SD_` prefix for all Stardog-related env vars
   - `SD_VOICEBOX_API_TOKEN` (required)
   - `SD_VOICEBOX_CLIENT_ID` (optional, default: VBX-LANGCHAIN)
   - `SD_CLOUD_ENDPOINT` (optional, default: https://cloud.stardog.com/api)

3. **VoiceboxClient.from_env():**
   - Unified way to create client from environment variables
   - Used internally by both Tools and Runnables
   - Accepts optional overrides for `client_id` and `endpoint`
   - Properly handles Optional types for mypy compliance

4. **Pydantic Private Fields:**
   - Use `PrivateAttr()` for private fields in Pydantic models (not `Field(exclude=True)`)
   - Example: `_runnable: VoiceboxAskRunnable = PrivateAttr()`
   - Required because Pydantic doesn't allow Field with underscore-prefixed names

5. **Type Safety Pattern:**
   - Store Optional values in private fields (`_client: Optional[VoiceboxClient]`)
   - Expose non-Optional via `@property` with runtime checks
   - This ensures type safety while allowing deferred initialization

6. **Test Coverage:**
   - Always run `make test-cov` before committing
   - Maintain >= 90% coverage (currently at 95%)
   - Use monkeypatch fixtures for testing environment variables
   - New features should include tests for all initialization patterns

7. **Documentation:**
   - Keep README.md, docstrings, examples, and claude.md in sync
   - Update claude.md for significant changes
   - Document both Tools and Runnables patterns separately

## Related Documentation

- [Stardog Documentation](https://docs.stardog.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Stardog Community](https://community.stardog.com/)

## Recent Changes (Latest Session - 2025-11-06)

### Package Restructuring

**What Changed:**
- Renamed project from `stardog-voicebox-langchain` → `langchain-stardog`
- Restructured package to support future Stardog integrations beyond Voicebox
- Created subpackage structure: `langchain_stardog.voicebox`

**New Structure:**
```
langchain_stardog/              # Main package
├── __init__.py                 # Re-exports from voicebox for convenience
└── voicebox/                   # Voicebox subpackage
    ├── __init__.py
    ├── client.py               # Renamed from voicebox_client.py
    ├── runnables.py
    ├── tools.py
    ├── constants.py
    └── exceptions.py
```

**Import Patterns:**
- **Recommended**: `from langchain_stardog.voicebox import VoiceboxAskTool`
- **Also works**: `from langchain_stardog import VoiceboxAskTool` (re-exported)

**Files Updated:**
- `pyproject.toml` - Changed name, description, URLs, coverage target
- `Makefile` - Updated source directories and type-check target
- All test files - Updated imports to `langchain_stardog.voicebox`
- All example files - Updated imports to `langchain_stardog.voicebox`
- `README.md` - Updated all package names and URLs
- `stardog_voicebox.mdx` → `langchain_stardog.mdx` - Renamed and updated
- `CLAUDE.md` - Updated project overview and structure

**Rationale:**
- Allows future expansion with other Stardog tools (schema, KG, etc.)
- Clean separation of concerns with subpackages
- Package name better reflects broader scope
- No breaking changes since not yet released

**Test Results:**
- ✅ 69 tests passing, 15 skipped
- ✅ 97% code coverage
- ✅ Package builds successfully as `langchain-stardog`

## Last Updated

2025-11-06 - Restructured package to langchain-stardog with voicebox subpackage, preparing for future Stardog integrations
