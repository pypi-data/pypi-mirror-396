"""Configuration manager for git-reporter."""

import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import ValidationError

from ..models import Config


class ConfigManager:
    """Manages configuration loading and saving."""

    DEFAULT_CONFIG_PATH = Path.home() / ".git-reporter" / "config.yaml"
    LOCAL_CONFIG_NAMES = [
        "git-reporter.yaml",
        "git-reporter.yml",
        ".git-reporter.yaml",
        ".git-reporter.yml",
    ]

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the configuration manager.

        Args:
            config_path: Path to configuration file (uses default if None)
        """
        if config_path:
            self.config_path = config_path
        else:
            # Check for local config files first
            for config_name in self.LOCAL_CONFIG_NAMES:
                local_config = Path.cwd() / config_name
                if local_config.exists():
                    self.config_path = local_config
                    break
            else:
                # Fall back to default config path
                self.config_path = self.DEFAULT_CONFIG_PATH

    def load(self) -> Config:
        """Load configuration from file.

        Returns:
            Configuration object

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValidationError: If config file is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Run 'git-reporter init' to create a configuration file."
            )

        with open(self.config_path) as f:
            data = yaml.safe_load(f)

        # Load environment variables for API keys if not in config
        if data is None:
            data = {}

        if "openai_api_key" not in data or not data["openai_api_key"]:
            data["openai_api_key"] = os.environ.get("OPENAI_API_KEY")

        if "gemini_api_key" not in data or not data["gemini_api_key"]:
            data["gemini_api_key"] = os.environ.get("GEMINI_API_KEY")

        try:
            return Config(**data)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e}") from e

    def save(self, config: Config) -> None:
        """Save configuration to file.

        Args:
            config: Configuration object to save
        """
        # Create directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict and remove None values and API keys (store in env instead)
        data = config.model_dump(exclude_none=True, mode="python", by_alias=True)

        # Don't save API keys to file for security
        if "openai_api_key" in data:
            data.pop("openai_api_key")
        if "gemini_api_key" in data:
            data.pop("gemini_api_key")

        # Convert enum to string value
        if "ai_provider" in data:
            data["ai_provider"] = (
                data["ai_provider"].value
                if hasattr(data["ai_provider"], "value")
                else data["ai_provider"]
            )
        if "default_period" in data:
            data["default_period"] = (
                data["default_period"].value
                if hasattr(data["default_period"], "value")
                else data["default_period"]
            )

        with open(self.config_path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

    def create_default(self) -> Config:
        """Create and save a default configuration.

        Returns:
            Default configuration object
        """
        config = Config()
        self.save(config)
        return config
