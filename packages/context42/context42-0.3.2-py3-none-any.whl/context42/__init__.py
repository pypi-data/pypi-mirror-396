"""MCP RAG Server - Document chunking with compression"""

from .processor import DocumentProcessor
from .chunker import Chunker
from .search import SearchEngine

# CLaRa integration (optional)
CLARA_AVAILABLE = False
ModelManager = None
CLaRaGenerator = None
CLaRaConfig = None

try:
    from .clara import ModelManager, CLaRaGenerator, CLaRaConfig

    CLARA_AVAILABLE = True
except ImportError:
    pass

__version__ = "0.3.0"
