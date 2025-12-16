#!/usr/bin/env python3
"""
Configuration Management Tests
Tests for config module with pydantic integration
"""

import pytest
import tempfile
import os
from pathlib import Path

from lmapp.core.config import LMAppConfig, ConfigManager, get_config


class TestLMAppConfig:
    """Test LMAppConfig schema"""

    def test_config_creation_defaults(self):
        """Test creating config with defaults"""
        cfg = LMAppConfig()
        assert cfg.backend == "auto"
        assert cfg.model == "tinyllama"
        assert cfg.temperature == 0.7
        assert cfg.debug is False

    def test_config_creation_custom(self):
        """Test creating config with custom values"""
        cfg = LMAppConfig(
            backend="ollama", model="mistral", temperature=0.5, debug=True
        )
        assert cfg.backend == "ollama"
        assert cfg.model == "mistral"
        assert cfg.temperature == 0.5
        assert cfg.debug is True

    def test_backend_validation(self):
        """Test backend validation"""
        with pytest.raises(ValueError):
            LMAppConfig(backend="invalid_backend")

    def test_temperature_validation(self):
        """Test temperature range validation"""
        with pytest.raises(ValueError):
            LMAppConfig(temperature=1.5)

        with pytest.raises(ValueError):
            LMAppConfig(temperature=-0.5)

    def test_model_validation(self):
        """Test model name validation"""
        with pytest.raises(ValueError):
            LMAppConfig(model="")

    def test_config_to_dict(self):
        """Test converting config to dictionary"""
        cfg = LMAppConfig(backend="ollama", model="tinyllama", temperature=0.7)
        data = cfg.model_dump()
        assert data["backend"] == "ollama"
        assert data["model"] == "tinyllama"


class TestConfigManager:
    """Test ConfigManager"""

    def test_config_manager_initialization(self):
        """Test ConfigManager initialization"""
        manager = ConfigManager()
        assert manager.config_dir == Path.home() / ".config" / "lmapp"
        assert manager.config_file == manager.config_dir / "config.json"

    def test_load_config_from_env(self):
        """Test loading config from environment variables"""
        manager = ConfigManager()

        # Set environment variables
        os.environ["LMAPP_BACKEND"] = "ollama"
        os.environ["LMAPP_MODEL"] = "mistral"
        os.environ["LMAPP_TEMP"] = "0.5"
        os.environ["LMAPP_DEBUG"] = "1"

        cfg = manager._from_env()

        assert cfg.backend == "ollama"
        assert cfg.model == "mistral"
        assert cfg.temperature == 0.5
        assert cfg.debug is True

        # Clean up
        del os.environ["LMAPP_BACKEND"]
        del os.environ["LMAPP_MODEL"]
        del os.environ["LMAPP_TEMP"]
        del os.environ["LMAPP_DEBUG"]

    def test_save_and_load_config(self):
        """Test saving and loading config"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ConfigManager()
            manager.config_dir = Path(tmpdir)
            manager.config_file = manager.config_dir / "test_config.json"

            # Create and save config
            cfg = LMAppConfig(backend="ollama", model="mistral", temperature=0.3)
            manager.save(cfg)

            # Verify file exists
            assert manager.config_file.exists()

            # Load and verify
            loaded_cfg = manager.load()
            assert loaded_cfg.backend == "ollama"
            assert loaded_cfg.model == "mistral"
            assert loaded_cfg.temperature == 0.3

    def test_update_config(self):
        """Test updating config"""
        manager = ConfigManager()
        manager.load()

        # Update fields
        result = manager.update(model="llama2", temperature=0.8)

        assert result is True
        assert manager.get().model == "llama2"
        assert manager.get().temperature == 0.8

    def test_get_config(self):
        """Test getting current config"""
        manager = ConfigManager()
        cfg = manager.get()

        assert isinstance(cfg, LMAppConfig)
        assert cfg.backend in ["auto", "ollama", "llamafile", "mock"]

    def test_show_config(self):
        """Test showing config as string"""
        manager = ConfigManager()
        manager.load()

        output = manager.show()

        assert "Current Configuration:" in output
        assert "backend:" in output
        assert "model:" in output


class TestConfigGlobalInstance:
    """Test global config instance"""

    def test_get_config_function(self):
        """Test global get_config function"""
        cfg = get_config()

        assert isinstance(cfg, LMAppConfig)
        assert cfg.backend in ["auto", "ollama", "llamafile", "mock"]
        assert isinstance(cfg.model, str) and len(cfg.model) > 0
        assert 0.0 <= cfg.temperature <= 1.0
