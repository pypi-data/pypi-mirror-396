# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MCP RAG Server - A Model Context Protocol (MCP) server for document chunking with configurable compression levels and keyword-based search functionality.

## Commands

```bash
# Install dependencies
uv sync

# Run the MCP server (stdio mode)
uv run python -m mcp_rag_server.server

# Run as CLI entry point
uv run mcp-rag-server
```

## Architecture

### Core Components

**mcp_rag_server/server.py** - Main MCP server implementation containing:
- `DocumentProcessor` - Static methods for document loading, chunking, and keyword search
- `MCPRAGServer` - MCP protocol handler exposing tools and resources

### MCP Tools Exposed

| Tool | Purpose |
|------|---------|
| `load_documents` | Load markdown files from a directory |
| `chunk_documents` | Apply compression-level chunking (1.0x-128.0x) |
| `search_chunks` | Keyword-based relevance search |
| `get_compression_info` | Return server state |

### Compression System

Chunk size = `1000 / compression_level` (minimum 100 chars). Higher compression = smaller chunks.

## Integration

Claude Desktop config example:
```json
{
  "mcpServers": {
    "mcp-rag-server": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_rag_server.server"],
      "cwd": "/path/to/project"
    }
  }
}
```
