"""CLaRa integration for Context42 MCP server."""

# Import will work once files are created
try:
    from .config import CLaRaConfig
    from .manager import ModelManager
    from .generator import CLaRaGenerator

    CLARA_AVAILABLE = True
except ImportError:
    CLARA_AVAILABLE = False
    CLaRaConfig = None
    ModelManager = None
    CLaRaGenerator = None

__all__ = ["CLaRaConfig", "ModelManager", "CLaRaGenerator", "CLARA_AVAILABLE"]
