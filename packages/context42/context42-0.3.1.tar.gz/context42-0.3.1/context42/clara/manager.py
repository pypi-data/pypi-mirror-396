"""CLaRa model download and lifecycle management."""

from pathlib import Path
from typing import Optional, Dict, Any
import shutil
import gc

try:
    from transformers import AutoModel
    from huggingface_hub import snapshot_download

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    AutoModel = None
    snapshot_download = None

from .config import CLaRaConfig


class ModelManager:
    """Manage CLaRa model download, loading, and lifecycle."""

    def __init__(self, config: CLaRaConfig):
        self.config = config
        self.model = None
        self.current_model_name: Optional[str] = None

    def download(self, model_name: str, force: bool = False) -> Dict[str, Any]:
        """Download model from HuggingFace."""
        if not TRANSFORMERS_AVAILABLE:
            return {
                "error": "transformers not installed. Install with: pip install context42[clara]"
            }

        if model_name not in self.config.MODELS:
            return {"error": f"Unknown model: {model_name}"}

        model_info = self.config.MODELS[model_name]
        local_path = self.config.model_path / model_name

        if local_path.exists() and not force:
            return {"status": "already_downloaded", "path": str(local_path)}

        # Create model directory
        local_path.mkdir(parents=True, exist_ok=True)

        try:
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
        except Exception as e:
            return {"error": f"Download failed: {str(e)}"}

    def load(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Load model into memory."""
        if not TRANSFORMERS_AVAILABLE:
            return {
                "error": "transformers not installed. Install with: pip install context42[clara]"
            }

        model_name = model_name or self.config.default_model

        if self.model and self.current_model_name == model_name:
            return {"status": "already_loaded", "model": model_name}

        if model_name not in self.config.MODELS:
            return {"error": f"Unknown model: {model_name}"}

        model_info = self.config.MODELS[model_name]
        local_path = self.config.model_path / model_name / model_info["subfolder"]

        if not local_path.exists():
            # Auto-download if not present
            download_result = self.download(model_name)
            if "error" in download_result:
                return download_result

        # Determine device
        device = self._get_device()

        try:
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
        except Exception as e:
            return {"error": f"Model loading failed: {str(e)}"}

    def unload(self) -> Dict[str, Any]:
        """Unload model from memory."""
        if self.model:
            del self.model
            self.model = None
            self.current_model_name = None

            # Force garbage collection
            gc.collect()

            # Clear CUDA cache if available
            try:
                import torch

                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass

            return {"status": "unloaded"}
        return {"status": "not_loaded"}

    def remove(self, model_name: str) -> Dict[str, Any]:
        """Remove downloaded model from disk."""
        if model_name not in self.config.MODELS:
            return {"error": f"Unknown model: {model_name}"}

        local_path = self.config.model_path / model_name

        if not local_path.exists():
            return {"status": "not_found", "model": model_name}

        # Unload if this model is currently loaded
        if self.current_model_name == model_name:
            self.unload()

        try:
            shutil.rmtree(local_path)
            return {"status": "removed", "model": model_name, "path": str(local_path)}
        except Exception as e:
            return {"error": f"Failed to remove: {str(e)}"}

    def _get_device(self) -> str:
        """Determine best available device."""
        if self.config.device != "auto":
            return self.config.device

        # Check for CUDA first
        try:
            import torch

            if torch.cuda.is_available():
                return "cuda"
        except ImportError:
            pass

        # Check for MPS (Apple Silicon)
        try:
            import torch

            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass

        return "cpu"

    def is_loaded(self) -> bool:
        """Check if model is currently loaded."""
        return self.model is not None

    def get_status(self) -> Dict[str, Any]:
        """Get current model manager status."""
        return {
            "loaded": self.is_loaded(),
            "model": self.current_model_name,
            "available_models": list(self.config.MODELS.keys()),
            "device": self._get_device(),
            "transformers_available": TRANSFORMERS_AVAILABLE,
        }
