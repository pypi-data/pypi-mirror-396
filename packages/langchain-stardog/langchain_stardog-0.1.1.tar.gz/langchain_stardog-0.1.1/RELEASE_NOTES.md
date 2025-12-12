# LangChain Stardog v0.1.0 - Initial Release

## Features

### Voicebox Integration
Query your knowledge graphs using natural language with Stardog Voicebox:

- **LangChain Tools** - Ready-to-use tools for agent workflows
  - `VoiceboxAskTool` - Ask questions and get natural language answers
  - `VoiceboxSettingsTool` - Retrieve Voicebox application settings
  - `VoiceboxGenerateQueryTool` - Generate SPARQL queries from natural language

- **LCEL Runnables** - Composable runnables for building custom chains
  - `VoiceboxAskRunnable`
  - `VoiceboxSettingsRunnable`
  - `VoiceboxGenerateQueryRunnable`

## Installation
```bash
pip install langchain-stardog
```

## Documentation

- **GitHub**: https://github.com/stardog-union/stardog-langchain
- **PyPI**: https://pypi.org/project/langchain-stardog/
- **Examples**: See the `/examples` directory in the repository
- **Stardog Docs**: https://docs.stardog.com/

**Full Changelog**: https://github.com/stardog-union/stardog-langchain/commits/v0.1.0
