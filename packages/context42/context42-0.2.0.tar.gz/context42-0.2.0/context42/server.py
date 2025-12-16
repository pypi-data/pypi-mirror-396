from fastmcp import FastMCP, Context
from context42.processor import DocumentProcessor
from context42.chunker import Chunker
from context42.search import SearchEngine

mcp = FastMCP("context42")

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
        extensions: File extensions to include (default: .md, .txt, .rst, .json)
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
def search(query: str, top_k: int = 5) -> list[dict]:
    """Search document chunks by keyword relevance.

    Args:
        query: Search query (keywords)
        top_k: Number of results to return

    Returns:
        List of matching chunks with scores
    """
    if not state["chunks"]:
        return [{"error": "No chunks available. Call chunk_documents first."}]

    engine = SearchEngine()
    return engine.search(state["chunks"], query, top_k)


@mcp.tool
def get_status() -> dict:
    """Get current server state."""
    return {
        "documents_loaded": len(state["documents"]),
        "chunks_created": len(state["chunks"]),
        "compression_level": state["compression_level"],
        "directory": state["directory"],
    }


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
    mcp.run()


if __name__ == "__main__":
    main()
