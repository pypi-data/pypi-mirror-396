# CLaRa Integration Design for Context42

## Overview

Integrate Apple's CLaRa (Continuous Latent Reasoning) model into Context42 MCP server for semantic document compression and intelligent RAG search.

---

## Architecture

### Current vs CLaRa-Enhanced

```
CURRENT (Keyword Search)              CLaRa-ENHANCED (Semantic Search)
────────────────────────              ─────────────────────────────────
load_documents                        load_documents
      ↓                                     ↓
chunk_documents (char-based)          compress_documents (CLaRa neural)
      ↓                                     ↓
search (keyword count)                search (CLaRa generate_from_text)
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Context42 MCP Server                         │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────────┐│
│  │  @mcp.tool   │  │  @mcp.tool   │  │      @mcp.tool             ││
│  │ init_clara() │  │ load_docs()  │  │ search() / ask()           ││
│  └──────┬───────┘  └──────┬───────┘  └─────────────┬──────────────┘│
│         │                 │                        │               │
│  ┌──────▼─────────────────▼────────────────────────▼──────────────┐│
│  │                      Server State                               ││
│  │  - clara_model: CLaRaModel | None                               ││
│  │  - documents: List[Document]                                    ││
│  │  - compressed_docs: List[CompressedDoc]                         ││
│  │  - config: CLaRaConfig                                          ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        CLaRa Backend                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐ │
│  │  ModelManager   │  │  Compressor     │  │  Generator          │ │
│  │  - download()   │  │  - compress()   │  │  - generate()       │ │
│  │  - load()       │  │  - batch()      │  │  - stream()         │ │
│  │  - unload()     │  │                 │  │                     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Package Structure

```
context42/
├── __init__.py
├── server.py              # FastMCP server (updated)
├── processor.py           # DocumentProcessor (unchanged)
├── chunker.py             # Chunker (fallback, unchanged)
├── search.py              # SearchEngine (fallback, unchanged)
├── clara/                 # NEW: CLaRa integration
│   ├── __init__.py
│   ├── manager.py         # Model download/load/unload
│   ├── compressor.py      # Document compression
│   ├── generator.py       # Answer generation
│   └── config.py          # Configuration
└── cli.py                 # NEW: CLI for model management
```

---

## Model Management

### Available Models

| Model | Compression | Size | Use Case |
|-------|-------------|------|----------|
| `apple/CLaRa-7B-Instruct/compression-16` | 16× | ~14GB | Balanced quality/speed |
| `apple/CLaRa-7B-Instruct/compression-128` | 128× | ~14GB | Maximum compression |
| `apple/CLaRa-7B-Base/compression-16` | 16× | ~14GB | Base model (no instruction tuning) |
| `apple/CLaRa-7B-E2E/compression-16` | 16× | ~14GB | End-to-end trained |

### Model Storage

```
~/.cache/context42/
├── models/
│   ├── clara-7b-instruct-16/    # Default model
│   │   ├── config.json
│   │   ├── model.safetensors
│   │   └── tokenizer/
│   └── clara-7b-instruct-128/
└── config.json                   # User preferences
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CONTEXT42_MODEL_PATH` | `~/.cache/context42/models` | Model storage location |
| `CONTEXT42_MODEL` | `clara-7b-instruct-16` | Default model to load |
| `CONTEXT42_DEVICE` | `auto` | Device: `auto`, `cuda`, `mps`, `cpu` |
| `CONTEXT42_LAZY_LOAD` | `true` | Load model on first use vs startup |

---

## CLI Commands

### Model Management

```bash
# Download default model (CLaRa-7B-Instruct compression-16)
context42 download

# Download specific model
context42 download --model clara-7b-instruct-128

# List available models
context42 models

# List downloaded models
context42 models --local

# Remove a model
context42 remove clara-7b-instruct-128

# Show model info
context42 info clara-7b-instruct-16
```

### Server Management

```bash
# Start server (lazy loads model on first use)
context42 serve

# Start with specific model
context42 serve --model clara-7b-instruct-128

# Start with model preloaded
context42 serve --preload

# Start in fallback mode (keyword search only, no CLaRa)
context42 serve --fallback
```

---

## MCP Tools API

### New Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `init_clara` | Initialize/download CLaRa model | `model: str`, `force_download: bool` |
| `clara_status` | Get CLaRa model status | - |
| `ask` | Ask question about documents (CLaRa) | `question: str`, `max_tokens: int` |
| `compress_documents` | Compress docs with CLaRa | `compression: int (16\|128)` |

### Updated Tools

| Tool | Change |
|------|--------|
| `search` | Auto-uses CLaRa if loaded, falls back to keyword |
| `get_status` | Includes CLaRa model status |

---

## Implementation Spec

### clara/config.py

```python
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class CLaRaConfig:
    model_path: Path = Path(os.environ.get(
        "CONTEXT42_MODEL_PATH",
        Path.home() / ".cache/context42/models"
    ))
    default_model: str = os.environ.get(
        "CONTEXT42_MODEL",
        "clara-7b-instruct-16"
    )
    device: str = os.environ.get("CONTEXT42_DEVICE", "auto")
    lazy_load: bool = os.environ.get("CONTEXT42_LAZY_LOAD", "true").lower() == "true"

    # Model registry
    MODELS = {
        "clara-7b-instruct-16": {
            "hf_path": "apple/CLaRa-7B-Instruct",
            "subfolder": "compression-16",
            "compression": 16,
            "size_gb": 14,
        },
        "clara-7b-instruct-128": {
            "hf_path": "apple/CLaRa-7B-Instruct",
            "subfolder": "compression-128",
            "compression": 128,
            "size_gb": 14,
        },
        "clara-7b-base-16": {
            "hf_path": "apple/CLaRa-7B-Base",
            "subfolder": "compression-16",
            "compression": 16,
            "size_gb": 14,
        },
        "clara-7b-e2e-16": {
            "hf_path": "apple/CLaRa-7B-E2E",
            "subfolder": "compression-16",
            "compression": 16,
            "size_gb": 14,
        },
    }
```

### clara/manager.py

```python
from pathlib import Path
from typing import Optional
from transformers import AutoModel
from .config import CLaRaConfig

class ModelManager:
    """Manage CLaRa model download, loading, and lifecycle."""

    def __init__(self, config: CLaRaConfig):
        self.config = config
        self.model = None
        self.current_model_name: Optional[str] = None

    def download(self, model_name: str, force: bool = False) -> dict:
        """Download model from HuggingFace."""
        if model_name not in self.config.MODELS:
            return {"error": f"Unknown model: {model_name}"}

        model_info = self.config.MODELS[model_name]
        local_path = self.config.model_path / model_name

        if local_path.exists() and not force:
            return {"status": "already_downloaded", "path": str(local_path)}

        from huggingface_hub import snapshot_download

        snapshot_download(
            repo_id=model_info["hf_path"],
            local_dir=local_path,
            allow_patterns=[f"{model_info['subfolder']}/*"],
        )

        return {
            "status": "downloaded",
            "model": model_name,
            "path": str(local_path),
            "size_gb": model_info["size_gb"],
        }

    def load(self, model_name: Optional[str] = None) -> dict:
        """Load model into memory."""
        model_name = model_name or self.config.default_model

        if self.model and self.current_model_name == model_name:
            return {"status": "already_loaded", "model": model_name}

        if model_name not in self.config.MODELS:
            return {"error": f"Unknown model: {model_name}"}

        model_info = self.config.MODELS[model_name]
        local_path = self.config.model_path / model_name / model_info["subfolder"]

        if not local_path.exists():
            # Auto-download if not present
            self.download(model_name)

        # Determine device
        device = self._get_device()

        self.model = AutoModel.from_pretrained(
            str(local_path),
            trust_remote_code=True,
            device_map=device,
        )
        self.current_model_name = model_name

        return {
            "status": "loaded",
            "model": model_name,
            "device": device,
            "compression": model_info["compression"],
        }

    def unload(self) -> dict:
        """Unload model from memory."""
        if self.model:
            del self.model
            self.model = None
            self.current_model_name = None

            import gc
            import torch
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            return {"status": "unloaded"}
        return {"status": "not_loaded"}

    def _get_device(self) -> str:
        """Determine best available device."""
        if self.config.device != "auto":
            return self.config.device

        import torch
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def is_loaded(self) -> bool:
        return self.model is not None

    def get_status(self) -> dict:
        return {
            "loaded": self.is_loaded(),
            "model": self.current_model_name,
            "available_models": list(self.config.MODELS.keys()),
            "device": self._get_device(),
        }
```

### clara/generator.py

```python
from typing import Optional

class CLaRaGenerator:
    """Generate answers using CLaRa model."""

    def __init__(self, manager):
        self.manager = manager

    def ask(
        self,
        question: str,
        documents: list[str],
        max_new_tokens: int = 64,
    ) -> dict:
        """Ask a question about documents."""
        if not self.manager.is_loaded():
            return {"error": "Model not loaded. Call init_clara first."}

        try:
            output = self.manager.model.generate_from_text(
                questions=[question],
                documents=[documents],
                max_new_tokens=max_new_tokens,
            )

            return {
                "answer": output[0] if output else "",
                "model": self.manager.current_model_name,
                "documents_used": len(documents),
            }
        except Exception as e:
            return {"error": str(e)}

    def search(
        self,
        query: str,
        documents: list[dict],
        top_k: int = 5,
    ) -> list[dict]:
        """Search documents using CLaRa's latent space."""
        if not self.manager.is_loaded():
            return [{"error": "Model not loaded. Call init_clara first."}]

        # Extract content from documents
        doc_texts = [d["content"] for d in documents]

        # Use CLaRa for retrieval
        output, topk_indices = self.manager.model.generate_from_questions(
            questions=[query],
            documents=[doc_texts],
            max_new_tokens=1,  # Just retrieval, minimal generation
        )

        # Map indices to documents
        results = []
        for idx in topk_indices[0][:top_k]:
            if idx < len(documents):
                results.append({
                    **documents[idx],
                    "score": 1.0 - (results.index(documents[idx]) * 0.1 if documents[idx] in results else 0),
                    "method": "clara",
                })

        return results
```

### server.py (Updated)

```python
from fastmcp import FastMCP
from context42.processor import DocumentProcessor
from context42.chunker import Chunker
from context42.search import SearchEngine
from context42.clara import ModelManager, CLaRaGenerator, CLaRaConfig

mcp = FastMCP("context42")

# Configuration
clara_config = CLaRaConfig()
model_manager = ModelManager(clara_config)
clara_generator = CLaRaGenerator(model_manager)

# Server state
state = {
    "documents": [],
    "chunks": [],
    "compression_level": 1.0,
    "directory": None,
}


@mcp.tool
def init_clara(
    model: str = "clara-7b-instruct-16",
    force_download: bool = False,
) -> dict:
    """Initialize CLaRa model for semantic search.

    Args:
        model: Model to use (clara-7b-instruct-16, clara-7b-instruct-128, etc.)
        force_download: Re-download even if model exists

    Returns:
        Initialization status
    """
    if force_download or not (clara_config.model_path / model).exists():
        download_result = model_manager.download(model, force=force_download)
        if "error" in download_result:
            return download_result

    return model_manager.load(model)


@mcp.tool
def clara_status() -> dict:
    """Get CLaRa model status."""
    return model_manager.get_status()


@mcp.tool
def unload_clara() -> dict:
    """Unload CLaRa model to free memory."""
    return model_manager.unload()


@mcp.tool
def ask(question: str, max_tokens: int = 128) -> dict:
    """Ask a question about loaded documents using CLaRa.

    Args:
        question: Question to ask about the documents
        max_tokens: Maximum tokens in response

    Returns:
        Generated answer based on documents
    """
    if not state["documents"]:
        return {"error": "No documents loaded. Call load_documents first."}

    if not model_manager.is_loaded():
        return {"error": "CLaRa not initialized. Call init_clara first."}

    doc_contents = [d["content"] for d in state["documents"]]
    return clara_generator.ask(question, doc_contents, max_tokens)


@mcp.tool
def search(query: str, top_k: int = 5, method: str = "auto") -> list[dict]:
    """Search document chunks.

    Args:
        query: Search query
        top_k: Number of results to return
        method: Search method (auto, clara, keyword)

    Returns:
        List of matching chunks with scores
    """
    if not state["documents"]:
        return [{"error": "No documents loaded. Call load_documents first."}]

    # Determine method
    use_clara = (
        method == "clara" or
        (method == "auto" and model_manager.is_loaded())
    )

    if use_clara and model_manager.is_loaded():
        return clara_generator.search(query, state["documents"], top_k)

    # Fallback to keyword search
    if not state["chunks"]:
        return [{"error": "No chunks available. Call chunk_documents first."}]

    engine = SearchEngine()
    results = engine.search(state["chunks"], query, top_k)
    for r in results:
        r["method"] = "keyword"
    return results


# ... existing tools unchanged ...


@mcp.tool
def get_status() -> dict:
    """Get current server state."""
    return {
        "documents_loaded": len(state["documents"]),
        "chunks_created": len(state["chunks"]),
        "compression_level": state["compression_level"],
        "directory": state["directory"],
        "clara": model_manager.get_status(),
    }
```

### cli.py

```python
import argparse
import sys
from context42.clara import ModelManager, CLaRaConfig

def main():
    parser = argparse.ArgumentParser(description="Context42 MCP Server")
    subparsers = parser.add_subparsers(dest="command")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Start MCP server")
    serve_parser.add_argument("--model", default=None, help="Model to use")
    serve_parser.add_argument("--preload", action="store_true", help="Preload model")
    serve_parser.add_argument("--fallback", action="store_true", help="Keyword-only mode")

    # download command
    download_parser = subparsers.add_parser("download", help="Download model")
    download_parser.add_argument("--model", default="clara-7b-instruct-16")
    download_parser.add_argument("--force", action="store_true")

    # models command
    models_parser = subparsers.add_parser("models", help="List models")
    models_parser.add_argument("--local", action="store_true", help="Show downloaded only")

    # remove command
    remove_parser = subparsers.add_parser("remove", help="Remove model")
    remove_parser.add_argument("model", help="Model to remove")

    # info command
    info_parser = subparsers.add_parser("info", help="Show model info")
    info_parser.add_argument("model", help="Model name")

    args = parser.parse_args()

    config = CLaRaConfig()
    manager = ModelManager(config)

    if args.command == "serve" or args.command is None:
        from context42.server import main as serve_main
        serve_main()

    elif args.command == "download":
        result = manager.download(args.model, force=args.force)
        print(result)

    elif args.command == "models":
        if args.local:
            downloaded = [m for m in config.MODELS if (config.model_path / m).exists()]
            for m in downloaded:
                print(f"  ✓ {m}")
        else:
            for name, info in config.MODELS.items():
                local = (config.model_path / name).exists()
                status = "✓" if local else " "
                print(f"  {status} {name} ({info['compression']}× compression, ~{info['size_gb']}GB)")

    elif args.command == "remove":
        import shutil
        path = config.model_path / args.model
        if path.exists():
            shutil.rmtree(path)
            print(f"Removed {args.model}")
        else:
            print(f"Model not found: {args.model}")

    elif args.command == "info":
        if args.model in config.MODELS:
            info = config.MODELS[args.model]
            local = (config.model_path / args.model).exists()
            print(f"Model: {args.model}")
            print(f"  HuggingFace: {info['hf_path']}/{info['subfolder']}")
            print(f"  Compression: {info['compression']}×")
            print(f"  Size: ~{info['size_gb']}GB")
            print(f"  Downloaded: {'Yes' if local else 'No'}")
        else:
            print(f"Unknown model: {args.model}")

if __name__ == "__main__":
    main()
```

---

## pyproject.toml (Updated)

```toml
[project]
name = "context42"
version = "0.3.0"
description = "MCP RAG Server with CLaRa semantic compression"
authors = [{name = "Aleksandr Beshkenadze", email = "beshkenadze@gmail.com"}]
requires-python = ">=3.10"
dependencies = [
    "fastmcp>=2.0.0",
]

[project.optional-dependencies]
clara = [
    "torch>=2.0.0",
    "transformers>=4.20.0",
    "accelerate>=0.20.0",
    "huggingface-hub>=0.20.0",
]
dev = [
    "pytest>=7.0.0",
]
all = [
    "context42[clara,dev]",
]

[project.scripts]
context42 = "context42.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["context42"]
```

---

## Usage Workflow

### First-Time Setup

```bash
# Install with CLaRa support
pip install context42[clara]

# Download default model (~14GB)
context42 download

# Or download specific model
context42 download --model clara-7b-instruct-128
```

### MCP Server Usage

```bash
# Start server (model loads on first use)
context42 serve

# Or preload model at startup
context42 serve --preload

# Or use keyword-only mode (no CLaRa, low memory)
context42 serve --fallback
```

### MCP Tool Workflow

```python
# 1. Initialize CLaRa (downloads if needed)
init_clara(model="clara-7b-instruct-16")

# 2. Load documents
load_documents(directory="./docs")

# 3. Ask questions (uses CLaRa)
ask(question="What is the main topic of these documents?")

# 4. Search (auto-uses CLaRa if loaded)
search(query="machine learning", top_k=5)

# 5. Unload to free memory
unload_clara()
```

---

## Fallback Behavior

| CLaRa Status | `search()` Behavior | `ask()` Behavior |
|--------------|---------------------|------------------|
| Not installed | Keyword search | Error message |
| Installed, not loaded | Keyword search | Error message |
| Loaded | CLaRa semantic search | CLaRa generation |

---

## Model Comparison

### Training Pipeline

CLaRa uses a three-stage training approach:

```
Stage 1: Compression Pretraining (Base)
    ↓
Stage 2: Instruction Tuning (Instruct)
    ↓
Stage 3: End-to-End Fine-tuning (E2E)
```

### Model Variants

| Model | Training Stage | Best For | Description |
|-------|----------------|----------|-------------|
| **CLaRa-7B-Base** | Stage 1 | Fine-tuning, custom tasks | Foundational compression + generation. Raw capability without instruction tuning. |
| **CLaRa-7B-Instruct** | Stage 2 | General Q&A, chat | Instruction-tuned for Q&A tasks. Follows instructions well. **Recommended for most users.** |
| **CLaRa-7B-E2E** | Stage 3 | Multi-document RAG | End-to-end optimized retrieval + generation. Best when searching across many documents. |

### Compression Variants

| Compression | Chunk Ratio | Quality | Speed | Use Case |
|-------------|-------------|---------|-------|----------|
| **16×** | 1 token per 16 chars | Higher | Slower | Detailed analysis, complex questions |
| **128×** | 1 token per 128 chars | Lower | Faster | Quick search, large document sets |

### Recommended Configurations

| Use Case | Model | Compression |
|----------|-------|-------------|
| **General Q&A** | `clara-7b-instruct-16` | 16× |
| **Large corpus search** | `clara-7b-instruct-128` | 128× |
| **Custom fine-tuning** | `clara-7b-base-16` | 16× |
| **Multi-hop reasoning** | `clara-7b-e2e-16` | 16× |

### Performance Benchmarks (from paper)

| Model | NQ | HotpotQA | MuSiQue | 2WikiMHQA | Avg |
|-------|-----|----------|---------|-----------|-----|
| CLaRa (16×) | 42.1% | 38.2% | 35.8% | 43.4% | 39.9% |
| CLaRa (128×) | 38.5% | 35.1% | 32.4% | 40.2% | 36.6% |

*Higher compression = faster but slightly lower accuracy*

---

## Memory Requirements

| Configuration | RAM Required | GPU VRAM |
|---------------|--------------|----------|
| Fallback (keyword only) | ~100MB | None |
| CLaRa on CPU | ~16GB | None |
| CLaRa on MPS (Mac) | ~16GB unified | Shared |
| CLaRa on CUDA | ~8GB | ~14GB |

---

## Future: MLX Support

When Apple releases MLX version:

```python
# clara/manager.py - add MLX backend
def _get_device(self) -> str:
    if self.config.device != "auto":
        return self.config.device

    # Check for MLX first (fastest on Apple Silicon)
    try:
        import mlx
        return "mlx"
    except ImportError:
        pass

    # Then CUDA, MPS, CPU
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"
```

---

## Summary

| Feature | Description |
|---------|-------------|
| **Model Download** | `context42 download` or auto on first `init_clara()` |
| **Model Selection** | 4 variants: instruct/base × 16/128 compression |
| **Lazy Loading** | Model loads on first use (configurable) |
| **Fallback** | Keyword search when CLaRa unavailable |
| **Memory Management** | `unload_clara()` to free resources |
| **Device Selection** | Auto-detects CUDA > MPS > CPU |
