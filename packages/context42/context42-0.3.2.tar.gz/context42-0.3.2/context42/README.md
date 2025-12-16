# Context42 - MCP RAG Server

A FastMCP-based server for local text search with intelligent document compression and optional CLaRa semantic search.

## 🚀 Quick Start

```bash
# Install basic version (keyword search)
uvx context42

# Install with CLaRa semantic compression
pip install context42[clara]

# Run server
context42 serve
```

## 🛠️ MCP Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `load_documents` | Load text files from directory | `directory`, `extensions`, `max_files` |
| `chunk_documents` | Apply compression chunking | `compression_level: 1.0-128.0` |
| `search` | Search chunks (keyword or CLaRa) | `query`, `top_k`, `method` |
| `get_status` | Get server state | - |
| **CLaRa Tools** (requires `context42[clara]`) |
| `init_clara` | Initialize CLaRa model | `model`, `force_download` |
| `clara_status` | Get CLaRa model status | - |
| `unload_clara` | Unload model to free memory | - |
| `ask` | Ask questions about documents | `question`, `max_tokens` |

## 📚 MCP Resources

- `context42://status` - Server state with CLaRa status
- `context42://documents` - Loaded document metadata

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

## 🧠 CLaRa Models

| Model | Compression | Use Case |
|-------|-------------|----------|
| `clara-7b-instruct-16` | 16× | General Q&A (recommended) |
| `clara-7b-instruct-128` | 128× | Large corpus search |
| `clara-7b-base-16` | 16× | Custom fine-tuning |
| `clara-7b-e2e-16` | 16× | Multi-document RAG |

## ⚙️ Features

- FastMCP Framework with decorator-based tools
- Multi-format support: .md, .txt, .rst, .json, .yaml, .toml, .csv, .log
- Smart chunking with configurable compression (1×-128×)
- Optional CLaRa semantic search (Apple's neural compression)
- Automatic fallback to keyword search when CLaRa unavailable
- CLI for model management
- Type safe with full annotations

## 📄 License

MIT License