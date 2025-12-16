from fastmcp import FastMCP, Context
from context42.processor import DocumentProcessor
from context42.chunker import Chunker
from context42.search import SearchEngine

# CLaRa integration (optional)
CLARA_AVAILABLE = False
ModelManager = None
CLaRaGenerator = None
CLaRaConfig = None

try:
    from context42.clara import ModelManager, CLaRaGenerator, CLaRaConfig

    CLARA_AVAILABLE = True
except ImportError:
    pass

mcp = FastMCP("context42")

# Configuration
if CLARA_AVAILABLE:
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
def load_documents(
    directory: str,
    extensions: list[str] = [
        ".md",
        ".txt",
        ".rst",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".csv",
        ".log",
    ],
    max_files: int = 100,
) -> dict:
    """Load text documents from a directory.

    Args:
        directory: Path to directory containing text files
        extensions: File extensions to include (default: .md, .txt, .rst, .json, .yaml, .yml, .toml, .csv, .log)
        max_files: Maximum number of files to load

    Returns:
        Summary of loaded documents
    """
    processor = DocumentProcessor()
    state["documents"] = processor.load(directory, extensions, max_files)
    state["directory"] = directory
    return {
        "loaded": len(state["documents"]),
        "directory": directory,
        "extensions": extensions,
    }


@mcp.tool
def chunk_documents(compression_level: float = 1.0) -> dict:
    """Chunk loaded documents with specified compression.

    Args:
        compression_level: Compression ratio (1.0-128.0). Higher = smaller chunks.

    Returns:
        Chunking summary
    """
    if not state["documents"]:
        return {"error": "No documents loaded. Call load_documents first."}

    chunker = Chunker()
    state["chunks"] = chunker.chunk(state["documents"], compression_level)
    state["compression_level"] = compression_level
    return {
        "chunks": len(state["chunks"]),
        "compression_level": compression_level,
        "chunk_size": chunker.get_chunk_size(compression_level),
    }


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
    use_clara = method == "clara" or (
        method == "auto" and CLARA_AVAILABLE and model_manager.is_loaded()
    )

    if use_clara and CLARA_AVAILABLE and model_manager.is_loaded():
        return clara_generator.search(query, state["documents"], top_k)

    # Fallback to keyword search
    if not state["chunks"]:
        return [{"error": "No chunks available. Call chunk_documents first."}]

    engine = SearchEngine()
    results = engine.search(state["chunks"], query, top_k)
    for r in results:
        r["method"] = "keyword"
    return results


@mcp.tool
def get_status() -> dict:
    """Get current server state."""
    status = {
        "documents_loaded": len(state["documents"]),
        "chunks_created": len(state["chunks"]),
        "compression_level": state["compression_level"],
        "directory": state["directory"],
        "clara_available": CLARA_AVAILABLE,
    }

    if CLARA_AVAILABLE:
        status["clara"] = model_manager.get_status()

    return status


# CLaRa-specific tools
if CLARA_AVAILABLE:

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
            question: Question to ask about documents
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


@mcp.resource("context42://status")
def status_resource() -> dict:
    """Current server state."""
    return get_status()


@mcp.resource("context42://documents")
def documents_resource() -> list[dict]:
    """List of loaded documents."""
    return [
        {"filename": d["filename"], "size": d["size"], "path": d["path"]}
        for d in state["documents"]
    ]


def main():
    """Main entry point for MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
