"""Tests for CLaRa integration module."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestCLaRaConfig:
    """Test CLaRaConfig functionality."""

    def test_config_defaults(self):
        """Test default configuration values."""
        from context42.clara.config import CLaRaConfig

        config = CLaRaConfig()

        assert config.default_model == "clara-7b-instruct-16"
        assert config.device == "auto"
        assert config.lazy_load is True
        assert config.model_path == Path.home() / ".cache/context42/models"

    def test_config_env_override(self, monkeypatch):
        """Test environment variable overrides."""
        from context42.clara.config import CLaRaConfig

        monkeypatch.setenv("CONTEXT42_MODEL", "clara-7b-base-16")
        monkeypatch.setenv("CONTEXT42_DEVICE", "cpu")
        monkeypatch.setenv("CONTEXT42_LAZY_LOAD", "false")

        # Need to reimport to pick up env changes
        import importlib
        import context42.clara.config
        importlib.reload(context42.clara.config)
        from context42.clara.config import CLaRaConfig

        config = CLaRaConfig()

        assert config.default_model == "clara-7b-base-16"
        assert config.device == "cpu"
        assert config.lazy_load is False

    def test_models_registry(self):
        """Test model registry contains expected models."""
        from context42.clara.config import CLaRaConfig

        config = CLaRaConfig()
        expected_models = [
            "clara-7b-instruct-16",
            "clara-7b-instruct-128",
            "clara-7b-base-16",
            "clara-7b-e2e-16",
        ]

        for model in expected_models:
            assert model in config.MODELS
            assert "hf_path" in config.MODELS[model]
            assert "subfolder" in config.MODELS[model]
            assert "compression" in config.MODELS[model]


class TestModelManager:
    """Test ModelManager functionality."""

    def test_manager_initialization(self):
        """Test ModelManager initializes correctly."""
        from context42.clara.config import CLaRaConfig
        from context42.clara.manager import ModelManager

        config = CLaRaConfig()
        manager = ModelManager(config)

        assert manager.model is None
        assert manager.current_model_name is None
        assert manager.config == config

    def test_is_loaded_false(self):
        """Test is_loaded returns False when no model loaded."""
        from context42.clara.config import CLaRaConfig
        from context42.clara.manager import ModelManager

        config = CLaRaConfig()
        manager = ModelManager(config)

        assert manager.is_loaded() is False

    def test_get_status(self):
        """Test get_status returns correct info."""
        from context42.clara.config import CLaRaConfig
        from context42.clara.manager import ModelManager

        config = CLaRaConfig()
        manager = ModelManager(config)

        status = manager.get_status()

        assert status["loaded"] is False
        assert status["model"] is None
        assert "clara-7b-instruct-16" in status["available_models"]
        assert status["device"] in ["auto", "cuda", "mps", "cpu"]

    def test_download_unknown_model(self):
        """Test download returns error for unknown model."""
        from context42.clara.config import CLaRaConfig
        from context42.clara.manager import ModelManager

        config = CLaRaConfig()
        manager = ModelManager(config)

        result = manager.download("nonexistent-model")

        assert "error" in result
        assert "Unknown model" in result["error"]

    def test_load_unknown_model(self):
        """Test load returns error for unknown model."""
        from context42.clara.config import CLaRaConfig
        from context42.clara.manager import ModelManager

        config = CLaRaConfig()
        manager = ModelManager(config)

        result = manager.load("nonexistent-model")

        assert "error" in result
        assert "Unknown model" in result["error"]

    def test_unload_when_not_loaded(self):
        """Test unload when no model loaded."""
        from context42.clara.config import CLaRaConfig
        from context42.clara.manager import ModelManager

        config = CLaRaConfig()
        manager = ModelManager(config)

        result = manager.unload()

        assert result["status"] == "not_loaded"

    def test_remove_unknown_model(self):
        """Test remove returns error for unknown model."""
        from context42.clara.config import CLaRaConfig
        from context42.clara.manager import ModelManager

        config = CLaRaConfig()
        manager = ModelManager(config)

        result = manager.remove("nonexistent-model")

        assert "error" in result
        assert "Unknown model" in result["error"]

    def test_remove_not_downloaded_model(self):
        """Test remove returns not_found for non-downloaded model."""
        from context42.clara.config import CLaRaConfig
        from context42.clara.manager import ModelManager

        with tempfile.TemporaryDirectory() as temp_dir:
            config = CLaRaConfig()
            config.model_path = Path(temp_dir)
            manager = ModelManager(config)

            result = manager.remove("clara-7b-instruct-16")

            assert result["status"] == "not_found"


class TestCLaRaGenerator:
    """Test CLaRaGenerator functionality."""

    def test_generator_initialization(self):
        """Test CLaRaGenerator initializes correctly."""
        from context42.clara.generator import CLaRaGenerator

        mock_manager = MagicMock()
        generator = CLaRaGenerator(mock_manager)

        assert generator.manager == mock_manager

    def test_ask_not_loaded(self):
        """Test ask returns error when model not loaded."""
        from context42.clara.generator import CLaRaGenerator

        mock_manager = MagicMock()
        mock_manager.is_loaded.return_value = False

        generator = CLaRaGenerator(mock_manager)
        result = generator.ask("test question", ["doc1", "doc2"])

        assert "error" in result
        assert "not loaded" in result["error"]

    def test_search_not_loaded(self):
        """Test search returns error when model not loaded."""
        from context42.clara.generator import CLaRaGenerator

        mock_manager = MagicMock()
        mock_manager.is_loaded.return_value = False

        generator = CLaRaGenerator(mock_manager)
        result = generator.search("test query", [{"content": "doc"}])

        assert len(result) == 1
        assert "error" in result[0]
        assert "not loaded" in result[0]["error"]

    def test_ask_with_loaded_model(self):
        """Test ask calls model correctly when loaded."""
        from context42.clara.generator import CLaRaGenerator

        mock_manager = MagicMock()
        mock_manager.is_loaded.return_value = True
        mock_manager.current_model_name = "clara-7b-instruct-16"
        mock_manager.model.generate_from_text.return_value = ["Test answer"]

        generator = CLaRaGenerator(mock_manager)
        result = generator.ask("What is AI?", ["AI is artificial intelligence."])

        assert result["answer"] == "Test answer"
        assert result["method"] == "clara"
        assert result["model"] == "clara-7b-instruct-16"
        mock_manager.model.generate_from_text.assert_called_once()


class TestCLaRaAvailability:
    """Test CLaRa availability detection."""

    def test_clara_module_imports(self):
        """Test CLaRa module can be imported."""
        from context42.clara import CLARA_AVAILABLE, CLaRaConfig, ModelManager, CLaRaGenerator

        # Should be available since transformers is installed
        assert CLARA_AVAILABLE is True
        assert CLaRaConfig is not None
        assert ModelManager is not None
        assert CLaRaGenerator is not None

    def test_main_module_exports_clara(self):
        """Test main module exports CLaRa components."""
        from context42 import CLARA_AVAILABLE

        assert CLARA_AVAILABLE is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
