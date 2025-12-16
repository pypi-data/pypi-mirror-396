"""CLaRa configuration management."""

from dataclasses import dataclass, field
from pathlib import Path
import os


def _default_model_path() -> Path:
    """Get default model path from env or default location."""
    env_path = os.environ.get("CONTEXT42_MODEL_PATH")
    if env_path:
        return Path(env_path)
    return Path.home() / ".cache/context42/models"


@dataclass
class CLaRaConfig:
    """Configuration for CLaRa model management."""

    model_path: Path = field(default_factory=_default_model_path)
    default_model: str = field(
        default_factory=lambda: os.environ.get("CONTEXT42_MODEL", "clara-7b-instruct-16")
    )
    device: str = field(
        default_factory=lambda: os.environ.get("CONTEXT42_DEVICE", "auto")
    )
    lazy_load: bool = field(
        default_factory=lambda: os.environ.get("CONTEXT42_LAZY_LOAD", "true").lower() == "true"
    )

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
