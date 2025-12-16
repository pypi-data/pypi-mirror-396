# Context42 - MCP RAG Server

A FastMCP-based server for local text search with intelligent document compression.

## 🚀 Quick Start

```bash
# Install basic version (keyword search)
uvx install context42

# Install with CLaRa semantic compression
pip install context42[clara]

# Run directly
uvx context42

# Or via uv
uv run context42

# Download CLaRa model (optional)
context42 download
```

## 🛠️ MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `load_documents` | Load text files from directory | `directory: str`, `extensions: list[str]`, `max_files: int` |
| `chunk_documents` | Apply compression chunking | `compression_level: float (1.0-128.0)` |
| `search` | Search in chunks (keyword or CLaRa) | `query: str`, `top_k: int`, `method: str (auto\|clara\|keyword)` |
| `get_status` | Get server state | - |
| **CLaRa Tools** (requires `pip install context42[clara]`) |
| `init_clara` | Initialize CLaRa model for semantic search | `model: str`, `force_download: bool` |
| `clara_status` | Get CLaRa model status | - |
| `unload_clara` | Unload CLaRa model to free memory | - |
| `ask` | Ask questions about documents using CLaRa | `question: str`, `max_tokens: int` |

## 📚 MCP Resources

- `context42://status` - Current server state (docs loaded, chunks, compression, CLaRa status)
- `context42://documents` - List of loaded document metadata

## 🧠 CLaRa Semantic Compression

**Optional Feature** - Install with `pip install context42[clara]` to enable Apple's CLaRa model for semantic document compression and intelligent search.

### CLaRa Models Available

| Model | Compression | Size | Use Case |
|-------|-------------|------|----------|
| `clara-7b-instruct-16` | 16× | ~14GB | General Q&A, **recommended** |
| `clara-7b-instruct-128` | 128× | ~14GB | Large corpus search |
| `clara-7b-base-16` | 16× | ~14GB | Custom fine-tuning |
| `clara-7b-e2e-16` | 16× | ~14GB | Multi-document RAG |

### CLaRa Workflow

```bash
# 1. Initialize CLaRa (downloads model if needed)
tools/call init_clara {"model": "clara-7b-instruct-16"}

# 2. Load documents
tools/call load_documents {"directory": "./docs"}

# 3. Ask semantic questions
tools/call ask {"question": "What is the main topic of these documents?"}

# 4. Search with CLaRa (auto-enabled when loaded)
tools/call search {"query": "machine learning", "method": "clara"}

# 5. Check model status
tools/call clara_status {}
```

### Fallback Behavior

| CLaRa Status | Search Behavior | Ask Behavior |
|---------------|----------------|---------------|
| Not installed | Keyword search | Error message |
| Installed, not loaded | Keyword search | Error message |
| Loaded | CLaRa semantic search | CLaRa generation |

## 🎯 Example Usage

```bash
# 1. Load documents
tools/call load_documents {"directory": "./docs", "extensions": [".md", ".txt"]}

# 2. Apply 16x compression (100-char chunks)
tools/call chunk_documents {"compression_level": 16.0}

# 3. Search for content
tools/call search {"query": "machine learning", "top_k": 5}
```

## 📊 File Formats Supported

| Extension | Description |
|-----------|-------------|
| `.md` | Markdown |
| `.txt` | Plain text |
| `.rst` | reStructuredText |
| `.json` | JSON (as text) |
| `.yaml`, `.yml` | YAML configs |
| `.toml` | TOML configs |
| `.csv` | CSV data |
| `.log` | Log files |

## 📊 Compression Levels

| Level | Chunk Size | Use Case |
|-------|------------|----------|
| 1.0x  | 1000 chars | Large context, detailed analysis |
| 4.0x  | 250 chars  | Medium context, balanced search |
| 16.0x | 100 chars  | Small context, fast search |
| 64.0x | 100 chars  | Maximum compression |

## 🔧 MCP Integration

### Quick CLI Setup

Add Context42 to any MCP-compatible tool with this one-liner:

```bash
# Claude Desktop
echo '{"mcpServers":{"context42":{"command":"uvx","args":["context42"]}}' >> ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Cursor Editor
echo '{"mcpServers":{"context42":{"command":"uvx","args":["context42"]}}' > ~/.cursor/mcp_settings.json

# Continue.dev
echo '{"mcpServers":{"context42":{"command":"uvx","args":["context42"]}}' > ~/.continue/config.json
```

### MCP Configuration Standards

Context42 follows official MCP configuration patterns and works with all major tools:

#### Standard Configuration Format
```json
{
  "mcpServers": {
    "context42": {
      "command": "uvx",
      "args": ["context42"]
    }
  }
}
```

#### Claude Code (Recommended)
```bash
# Add to user scope (cross-project)
claude mcp add --transport stdio context42 -- uvx context42

# Add to project scope (team-shared)
claude mcp add --transport stdio context42 --scope project -- uvx context42

# Add with environment variables
claude mcp add --transport stdio context42 --env CONTEXT42_DOCS_PATH=/path/to/docs -- uvx context42
```

#### VS Code
```json
{
  "mcp": {
    "servers": {
      "context42": {
        "type": "stdio",
        "command": "uvx",
        "args": ["context42"]
      }
    }
  }
}
```

#### Cursor/Windsurf
```json
{
  "mcpServers": {
    "context42": {
      "command": "uvx",
      "args": ["context42"]
    }
  }
}
```

#### Zed Editor
```json
{
  "context_servers": {
    "Context42": {
      "source": "custom",
      "command": "uvx",
      "args": ["context42"]
    }
  }
}
```

#### Cline/Roo Code
```json
{
  "mcpServers": {
    "context42": {
      "type": "stdio",
      "command": "uvx",
      "args": ["context42"]
    }
  }
}
```

### Configuration Scopes

MCP servers can be configured at different levels:

| Scope | Location | Use Case | Command |
|-------|----------|-----------|---------|
| **Local** | `~/.claude.json` (project-specific) | Personal, project-only servers | `claude mcp add --scope local` |
| **Project** | `.mcp.json` (version controlled) | Team-shared servers | `claude mcp add --scope project` |
| **User** | `~/.claude.json` (global) | Cross-project personal servers | `claude mcp add --scope user` |

### Environment Variable Expansion

Use environment variables in `.mcp.json` for flexible configurations:

```json
{
  "mcpServers": {
    "context42": {
      "command": "uvx",
      "args": ["context42"],
      "env": {
        "CONTEXT42_DOCS_PATH": "${DOCS_PATH:-./docs}",
        "CONTEXT42_COMPRESSION": "${COMPRESSION_LEVEL:-4.0}"
      }
    }
  }
}
```

### Windows Compatibility

For Windows users, use the `cmd /c` wrapper:

```json
{
  "mcpServers": {
    "context42": {
      "command": "cmd",
      "args": ["/c", "uvx", "context42"]
    }
  }
}
```

### Supported Tools

Context42 works with all major MCP-compatible tools:

**AI Coding Assistants:**
- Claude Desktop, Claude Code, Cursor, Windsurf
- Cline, Roo Code, Continue.dev, Codeium
- GitHub Copilot, OpenCode, Aider, Supermaven
- Sourcegraph Cody, Tabnine, Perplexity

**IDEs & Editors:**
- VS Code, JetBrains IDEs (IntelliJ, PyCharm, etc.)
- Zed, Neovim, Emacs, Sublime Text

**CLI Tools:**
- Amp, BoltAI, Crush, Factory (droid)
- Kilo Code, LM Studio, Warp Terminal

**Enterprise Platforms:**
- Google Antigravity, Amazon Q Developer CLI
- Microsoft Copilot CLI, Qwen Coder

### MCP Resources & Prompts

Context42 exposes MCP resources that can be referenced with `@`:

```bash
# Reference server status
@context42://status

# Reference loaded documents
@context42://documents
```

Available slash commands (if supported by client):
```bash
/mcp__context42__load_docs
/mcp__context42__search
/mcp__context42__status
```

### Authentication & Security

- **No authentication required** - Context42 is a local server
- **File system access** - Respects your user permissions
- **No network calls** - All processing happens locally (except CLaRa model download)
- **Enterprise ready** - Can be deployed via managed MCP configurations
- **CLaRa Privacy** - Models downloaded from official HuggingFace repositories

### Memory Requirements

| Configuration | RAM Required | GPU VRAM |
|---------------|--------------|----------|
| Fallback (keyword only) | ~100MB | None |
| CLaRa on CPU | ~16GB | None |
| CLaRa on MPS (Mac) | ~16GB unified | Shared |
| CLaRa on CUDA | ~8GB | ~14GB |

### Python Client
```python
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession

async def use_context42():
    server_params = StdioServerParameters(
        command="uvx", args=["context42"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("load_documents", {
                "directory": "./documents"
            })
            
            # Use CLaRa if available
            clara_result = await session.call_tool("init_clara", {
                "model": "clara-7b-instruct-16"
            })
            
            # Ask semantic questions
            answer = await session.call_tool("ask", {
                "question": "What is the main topic?",
                "max_tokens": 128
            })
```

### CLI Commands

```bash
# Model management (requires context42[clara])
context42 download                    # Download default CLaRa model
context42 models --local               # List downloaded models
context42 info clara-7b-instruct-16   # Show model details
context42 remove clara-7b-instruct-128  # Remove model

# Server management
context42 serve                       # Start MCP server
context42 serve --model clara-7b-instruct-128  # Use specific model
context42 serve --preload              # Preload model at startup
context42 serve --fallback             # Keyword-only mode
```

### MCP Server Management

```bash
# List all configured MCP servers
claude mcp list

# Get Context42 server details
claude mcp get context42

# Remove Context42 server
claude mcp remove context42

# Check server status in Claude Code
/mcp

# Use Claude Code as MCP server (for testing)
claude mcp serve
```

### Enterprise Configuration

For enterprise deployments, use managed MCP configuration:

```json
// managed-mcp.json
{
  "mcpServers": {
    "context42": {
      "command": "uvx",
      "args": ["context42"],
      "env": {
        "CONTEXT42_DOCS_PATH": "/company/docs",
        "CONTEXT42_MAX_FILES": "10000",
        "CONTEXT42_MODEL": "clara-7b-instruct-16",
        "CONTEXT42_DEVICE": "cuda"
      }
    }
  },
  "allowedMcpServers": [
    {"serverName": "context42"}
  ]
}
```

## 🧪 Development

```bash
# Install dev dependencies
uv sync

# Run server for testing
uv run context42

# Test via FastMCP inspector
fastmcp dev context42/server.py
```

## 📁 Project Structure

```
context42/
├── __init__.py          # Package exports, CLARA_AVAILABLE flag
├── server.py            # FastMCP server with MCP tools
├── cli.py               # CLI: serve, download, models, remove, info
├── processor.py         # DocumentProcessor class
├── chunker.py           # Chunker class
├── search.py            # SearchEngine (keyword fallback)
└── clara/               # Optional CLaRa integration
    ├── __init__.py      # CLaRa exports
    ├── config.py        # CLaRaConfig with model registry
    ├── manager.py       # ModelManager (download/load/unload/remove)
    └── generator.py     # CLaRaGenerator (ask/search)
```

## ⚙️ Features

- ✅ **FastMCP Framework**: Modern decorator-based MCP server
- ✅ **Multi-format Support**: .md, .txt, .rst, .json, .yaml, .toml, .csv, .log
- ✅ **Smart Chunking**: Configurable compression (1x-128x) with overlap
- ✅ **Keyword Search**: Relevance-based scoring with previews
- ✅ **CLaRa Integration**: Optional semantic compression with Apple's CLaRa model
- ✅ **Hybrid Search**: Auto-switches between CLaRa semantic and keyword search
- ✅ **Model Management**: Download, load, and manage multiple CLaRa models
- ✅ **Memory Management**: Lazy loading and unloading for resource efficiency
- ✅ **uvx Ready**: Installable globally via uvx
- ✅ **Type Safe**: Full type annotations
- ✅ **Error Handling**: Comprehensive exception management
- ✅ **CLI Tool Compatible**: Works with all major CLI tools and editors

## 🐛 Troubleshooting

### Server Issues

**Server won't start:**
```bash
uv sync  # Install dependencies
uvx --install context42  # Ensure global installation
```

**Connection errors:**
- Windows: Use `cmd /c` wrapper in configuration
- macOS/Linux: Check `uvx` is in PATH
- Verify MCP client supports stdio transport

**Permission errors:**
- Ensure Context42 has read access to document directories
- Check file permissions on target files

### Document Loading Issues

**No documents found:**
- Check directory path contains supported file types
- Use absolute paths if needed
- Verify directory exists and is accessible

**Large file processing:**
- Use compression levels 4.0x-16.0x for better performance
- Consider splitting very large files (>10MB)

### Search Issues

**Search returns no results:**
- Ensure documents are loaded and chunked first
- Try different search terms or partial matches
- Check compression level isn't too high (reduces context)

**Slow search performance:**
- Use higher compression levels (16.0x-64.0x)
- Limit search with `top_k` parameter
- Consider reducing document corpus size

### MCP Client Issues

**Server not appearing in client:**
- Restart MCP client after configuration
- Check configuration JSON syntax
- Verify server name matches exactly

**Tools not available:**
- Use `/mcp` command in Claude Code to check status
- Ensure server initialized successfully
- Check client logs for connection errors

**Resource references not working:**
- Verify client supports MCP resources
- Use format: `@context42://status` or `@context42://documents`
- Check server has loaded documents first

## 📄 License

MIT License - see LICENSE file for details.