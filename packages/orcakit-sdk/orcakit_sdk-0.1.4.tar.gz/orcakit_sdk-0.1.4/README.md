# OrcaKit SDK

A public SDK package for AI Agent development based on LangGraph, providing common utilities, MCP adapters, and compatible LLM service support.

## Features

- 🔧 **MCP Adapter**: Integrated Model Context Protocol (MCP) client with multi-server configuration support
- 🤖 **Compatible Models**: Support for OpenAI-compatible LLM services (e.g., DeepSeek)
- 🛠️ **Utility Functions**: Message handling, model loading, and other common utilities
- 📦 **Lightweight**: Minimal core dependencies for easy integration

## Installation

```bash
pip install orcakit-sdk
```

Or using uv:

```bash
uv add orcakit-sdk
```

## Quick Start

### Using OpenAI-Compatible Models

```python
from orcakit_sdk import create_compatible_openai_client

# Create client (requires OPENAI_API_KEY and OPENAI_BASE_URL environment variables)
client = create_compatible_openai_client(model_name="gpt-4")

# Or use default model (read from OPENAI_MODEL_NAME environment variable)
client = create_compatible_openai_client()
```

### Using MCP Adapter

```python
import asyncio
from orcakit_sdk import get_mcp_client, get_mcp_tools

async def main():
    # MCP server configuration (JSON format)
    server_configs = '''
    {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
            }
        }
    }
    '''
    
    # Get MCP client
    client = await get_mcp_client(server_configs)
    
    # Get available tools
    tools = await get_mcp_tools(server_configs)
    print(f"Loaded {len(tools)} tools")

asyncio.run(main())
```

### Loading Chat Models

```python
from orcakit_sdk import load_chat_model

# Load model from fully qualified name
model = load_chat_model("openai/gpt-4")

# Or use OpenAI-compatible model
model = load_chat_model("compatible_openai/deepseek-chat")
```

### Processing Message Content

```python
from orcakit_sdk import get_message_text
from langchain_core.messages import HumanMessage

msg = HumanMessage(content="Hello, world!")
text = get_message_text(msg)
print(text)  # Output: Hello, world!
```

## Environment Variables

The SDK supports the following environment variable configurations:

- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_BASE_URL`: OpenAI API base URL (for compatible services)
- `OPENAI_MODEL_NAME`: Default model name

Example `.env` file:

```bash
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL_NAME=deepseek-chat
```

## API Reference

### MCP Adapter

#### `get_mcp_client(server_configs: str) -> MultiServerMCPClient | None`

Get or initialize the global MCP client.

**Parameters:**
- `server_configs`: JSON-formatted server configuration string

**Returns:**
- `MultiServerMCPClient` instance or `None` (if initialization fails)

#### `get_mcp_tools(server_configs: str) -> list[Callable[..., object]]`

Get the list of tools provided by the MCP server.

**Parameters:**
- `server_configs`: JSON-formatted server configuration string

**Returns:**
- List of tool functions

#### `clear_mcp_cache() -> None`

Clear the MCP client and tools cache (mainly for testing).

### Model Tools

#### `create_compatible_openai_client(model_name: str | None = None) -> ChatOpenAI`

Create an OpenAI-compatible chat model client.

**Parameters:**
- `model_name`: Model name (optional, defaults to environment variable)

**Returns:**
- `ChatOpenAI` client instance

#### `load_chat_model(fully_specified_name: str) -> BaseChatModel`

Load a chat model from a fully qualified name.

**Parameters:**
- `fully_specified_name`: String in the format `provider/model`

**Returns:**
- `BaseChatModel` instance

### Utility Functions

#### `get_message_text(msg: BaseMessage) -> str`

Extract text content from a message object.

**Parameters:**
- `msg`: LangChain message object

**Returns:**
- Extracted text content

## Development

### Install Development Dependencies

```bash
make install-dev
```

### Run Tests

```bash
make test
```

### Code Formatting

```bash
make format
```

### Code Linting

```bash
make lint
```

## Project Structure

```
orcakit-sdk/
├── src/
│   └── orcakit_sdk/
│       ├── __init__.py          # Package entry point
│       ├── mcp_adapter.py       # MCP adapter
│       ├── model.py             # Model utilities
│       └── utils.py             # Utility functions
├── tests/
│   ├── unit_tests/
│   │   ├── test_utils.py
│   │   └── test_model.py
│   └── integration_tests/
├── pyproject.toml               # Project configuration
├── Makefile                     # Development commands
└── README.md                    # Project documentation
```

## Dependencies

Core dependencies:
- `langgraph >= 0.6.6`: LangGraph framework
- `langchain >= 0.2.14`: LangChain core library
- `langchain-openai >= 0.1.22`: OpenAI integration
- `langchain-mcp-adapters >= 0.1.9`: MCP adapter
- `python-dotenv >= 1.0.1`: Environment variable management

## License

MIT License

## Contributing

Issues and Pull Requests are welcome!

## Author

William Fu-Hinthorn (jubaoliang@gmail.com)
