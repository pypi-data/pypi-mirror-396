# TMCP Client

[![PyPI version](https://badge.fury.io/py/tmcp-client.svg)](https://badge.fury.io/py/tmcp-client)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Lightweight MCP client for TowardsAGI MCP servers**

A minimal, efficient client for connecting to TowardsAGI MCP servers via HTTP API. Designed for use with Claude, Cursor, VS Code, and other MCP-compatible applications.

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install tmcp-client

# Or use with uvx (no installation required)
uvx tmcp-client
```

### Usage with MCP Applications

Add to your MCP configuration file (e.g., `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "my-database": {
      "command": "uvx",
      "args": ["tmcp-client"],
      "env": {
        "TOWARDSMCP_SERVER_URL": "https://your-server.com/",
        "TOWARDSMCP_RESOURCE": "your-resource-name",
        "TOWARDSMCP_API_KEY": "tmcp_your-api-key"
      }
    }
  }
}
```

## 📋 Configuration

The client requires three environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `TOWARDSMCP_SERVER_URL` | Your TMCP server URL | `https://beta.towardsmcp.com/` |
| `TOWARDSMCP_RESOURCE` | Resource name to connect to | `my-database` |
| `TOWARDSMCP_API_KEY` | Your API key | `tmcp_abc123...` |

## 🔧 Installation Methods

### Method 1: UVX (Recommended)
No installation required - automatically downloads and runs:

```json
{
  "command": "uvx",
  "args": ["tmcp-client"],
  "env": { ... }
}
```

### Method 2: Global Installation
Install once, use everywhere:

```bash
pip install tmcp-client
```

```json
{
  "command": "tmcp-client",
  "env": { ... }
}
```

### Method 3: Python Module
Use with existing Python installation:

```json
{
  "command": "python",
  "args": ["-m", "tmcp_client"],
  "env": { ... }
}
```

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/JSON-RPC    ┌──────────────────┐
│   MCP Client    │ ◄─────────────────► │  TowardsAGI      │
│ (Claude/Cursor) │                     │  MCP Server      │
└─────────────────┘                     └──────────────────┘
         ▲                                        │
         │ stdio/JSON-RPC                         │
         ▼                                        ▼
┌─────────────────┐                     ┌──────────────────┐
│   tmcp-client   │                     │   Your Database  │
│     Bridge      │                     │   (PostgreSQL,   │
└─────────────────┘                     │   MongoDB, etc.) │
                                        └──────────────────┘
```

## 🛠️ Development

### Local Development

```bash
# Clone and install in development mode
git clone https://github.com/TowardsAGI-AI/tmcp-client.git
cd tmcp-client
pip install -e .

# Run tests
pytest

# Format code
black src/
isort src/
```

### Building

```bash
# Build package
python -m build

# Install locally
pip install dist/tmcp_client-*.whl
```

## 📚 Examples

### Basic Usage

```python
import asyncio
from tmcp_client import TMCPBridge

async def example():
    bridge = TMCPBridge()
    
    # List available tools
    tools = await bridge.list_tools()
    print(f"Available tools: {[t['name'] for t in tools]}")
    
    # Call a tool
    result = await bridge.call_tool("query", {"sql": "SELECT 1"})
    print(f"Result: {result}")
    
    await bridge.close()

# Run with environment variables set
asyncio.run(example())
```

### Multiple Resources

```json
{
  "mcpServers": {
    "production-db": {
      "command": "uvx",
      "args": ["tmcp-client"],
      "env": {
        "TOWARDSMCP_SERVER_URL": "https://prod.towardsmcp.com/",
        "TOWARDSMCP_RESOURCE": "prod-database",
        "TOWARDSMCP_API_KEY": "tmcp_prod_key"
      }
    },
    "analytics-db": {
      "command": "uvx", 
      "args": ["tmcp-client"],
      "env": {
        "TOWARDSMCP_SERVER_URL": "https://analytics.towardsmcp.com/",
        "TOWARDSMCP_RESOURCE": "analytics-warehouse",
        "TOWARDSMCP_API_KEY": "tmcp_analytics_key"
      }
    }
  }
}
```

## 🔍 Troubleshooting

### Common Issues

**"Missing required environment variables"**
- Ensure all three environment variables are set in your MCP config

**"Authentication failed (401)"**
- Check your `TOWARDSMCP_API_KEY` is correct and not expired

**"Resource not found (404)"**
- Verify the `TOWARDSMCP_RESOURCE` name matches your server configuration

**"Connection timeout"**
- Check your `TOWARDSMCP_SERVER_URL` is accessible and correct

### Debug Mode

Set `TMCP_DEBUG=1` environment variable for verbose logging:

```json
{
  "env": {
    "TOWARDSMCP_SERVER_URL": "...",
    "TOWARDSMCP_RESOURCE": "...",
    "TOWARDSMCP_API_KEY": "...",
    "TMCP_DEBUG": "1"
  }
}
```
## Publishing Build Artifact
```bash
cd tmcp-client
twine upload dist/*
Enter your API token: "provoid API tocken from pypi project (tmcp/api_tocken.txt)"
```
## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/TowardsAGI-AI/tmcp-client/issues)
- **Documentation**: [GitHub README](https://github.com/TowardsAGI-AI/tmcp-client#readme)
- **Email**: support@towardsagi.ai

---

**Made with ❤️ by [TowardsAGI.AI](https://towardsagi.ai)**
