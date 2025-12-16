#!/usr/bin/env python3
"""
Configuration Management
Pydantic-based configuration with JSON persistence
Includes trial system integration
"""

import os
import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

from lmapp.utils.logging import logger


class LMAppConfig(BaseModel):
    """Configuration schema for lmapp"""

    model_config = ConfigDict(validate_assignment=True)

    backend: str = Field(
        default="auto", description="LLM backend: auto|ollama|llamafile|mock"
    )
    model: str = Field(default="tinyllama", description="Model name to use")
    temperature: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Temperature (0.0-1.0)"
    )
    debug: bool = Field(default=False, description="Enable debug logging")
    developer_mode: bool = Field(
        default=False,
        description="Enable advanced mode (verbose output, advanced options)",
    )
    advanced_mode: bool = Field(
        default=False,
        description="Enable Advanced Mode (access to RAG, plugins, batch, web UI)",
    )
    completed_setup: bool = Field(
        default=False,
        description="Whether first-run wizard has been completed",
    )
    default_model: Optional[str] = Field(
        default=None, description="Default model to use across sessions"
    )

    # Advanced settings (future)
    max_tokens: Optional[int] = Field(
        default=None, description="Maximum tokens in response"
    )
    timeout: int = Field(default=300, description="Request timeout in seconds")

    @field_validator("backend")
    @classmethod
    def validate_backend(cls, v):
        """Validate backend choice"""
        valid = ["auto", "ollama", "llamafile", "mock"]
        if v not in valid:
            raise ValueError(f"Backend must be one of {valid}")
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v):
        """Validate model name"""
        if not v or len(v.strip()) == 0:
            raise ValueError("Model name cannot be empty")
        return v.strip()


class ConfigManager:
    """Manages configuration persistence"""

    CONFIG_DIR = Path.home() / ".config" / "lmapp"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    def __init__(self):
        """Initialize config manager"""
        self.config_dir = self.CONFIG_DIR
        self.config_file = self.CONFIG_FILE
        self._config: Optional[LMAppConfig] = None

    def load(self) -> LMAppConfig:
        """Load configuration from file or environment"""
        logger.debug(f"Loading configuration from {self.config_file}")

        # Try to load from file first
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                logger.debug(f"Loaded config from {self.config_file}")
                self._config = LMAppConfig(**data)
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}, using defaults")
                self._config = self._from_env()
        else:
            # Load from environment
            self._config = self._from_env()

        return self._config

    def save(self, config: Optional[LMAppConfig] = None) -> bool:
        """Save configuration to file"""
        if config:
            self._config = config

        if not self._config:
            logger.error("No configuration to save")
            return False

        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(self._config.model_dump(), f, indent=2)
            logger.debug(f"Saved config to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    def _from_env(self) -> LMAppConfig:
        """Load configuration from environment variables"""
        logger.debug("Loading configuration from environment variables")

        return LMAppConfig(
            backend=os.getenv("LMAPP_BACKEND", "auto"),
            model=os.getenv("LMAPP_MODEL", "tinyllama"),
            temperature=float(os.getenv("LMAPP_TEMP", "0.7")),
            debug=os.getenv("LMAPP_DEBUG", "0") == "1",
            developer_mode=os.getenv("LMAPP_DEV_MODE", "0") == "1",
        )

    def get(self) -> LMAppConfig:
        """Get current configuration (never returns None)"""
        if not self._config:
            try:
                self.load()
            except Exception:
                # Fallback to default config if loading fails
                self._config = LMAppConfig()
        if not self._config:
            self._config = LMAppConfig()
        
        # Enforce trial gating: if no active trial/paid, force Advanced Mode OFF
        # (This ensures free tier users don't accidentally have advanced features)
        from lmapp.core.trial import is_trial_active
        if self._config.advanced_mode and not is_trial_active():
            logger.debug("Trial inactive, enforcing free tier (Advanced Mode OFF)")
            self._config.advanced_mode = False
        
        return self._config

    def update(self, **kwargs) -> bool:
        """Update configuration and save"""
        if not self._config:
            self.load()

        try:
            if not self._config:
                raise RuntimeError("Config not loaded")

            # Update fields
            for key, value in kwargs.items():
                if hasattr(self._config, key):
                    setattr(self._config, key, value)

            # Validate and save
            self._config = LMAppConfig(**self._config.model_dump())
            return self.save()
        except Exception as e:
            logger.error(f"Failed to update config: {e}")
            return False

    def show(self) -> str:
        """Get configuration as formatted string"""
        if not self._config:
            self.load()

        if not self._config:
            return "Error: Configuration could not be loaded"

        lines = ["Current Configuration:"]
        for key, value in self._config.model_dump().items():
            lines.append(f"  {key}: {value}")

        return "\n".join(lines)


# Global config instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get or create global config manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> LMAppConfig:
    """Get current configuration"""
    return get_config_manager().get()
