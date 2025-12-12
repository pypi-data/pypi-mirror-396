from dataclasses import dataclass
from typing import Optional

from baicai_base.configs import ConfigManager


@dataclass
class LLMConfig:
    """Configuration for LLM settings."""

    provider: str = "groq"
    model_name: str = "qwen/qwen3-32b"
    base_url: Optional[str] = None
    temperature: float = 0.0

    def __post_init__(self):
        """Set default base_url based on provider if not specified."""
        if self.base_url is None and self.provider == "openai兼容":
            self.base_url = "https://api.deepseek.com/"

    @classmethod
    def load(cls, config_id: str = "default") -> "LLMConfig":
        """Load configuration from disk.

        Configuration hierarchy:
        1. If config_id is specified and exists, use that
        2. If global config exists, use that
        3. Otherwise, use default config
        """
        config_manager = ConfigManager()

        # Try to load specific config first
        if config_id != "default":
            loaded_config = config_manager.load_config(config_id, cls)
            if loaded_config is not None:
                return loaded_config

        # If no specific config or config_id is "default", try global
        global_config = config_manager.load_global_config()
        if global_config:
            provider = global_config.get("provider", "groq")
            base_url = global_config.get("base_url")
            # Set default base_url for openai兼容 provider if not specified
            if base_url is None and provider == "openai兼容":
                base_url = "https://api.deepseek.com/"
            return cls(
                provider=provider,
                model_name=global_config.get("model", "qwen/qwen3-32b"),
                base_url=base_url,
                temperature=float(global_config.get("temperature", 0.0)),
            )

        # If no global config, use default
        return cls.load_default()

    def save(self, config_id: str = "global"):
        """Save configuration to disk.

        Args:
            config_id: The ID to save the config under. Use "global" for global settings.
                      Cannot save as "default" as it's immutable.
        """
        if config_id == "default":
            raise ValueError("Cannot modify default configuration")

        config_manager = ConfigManager()
        config_manager.save_config(config_id, self)

    @classmethod
    def load_default(cls) -> "LLMConfig":
        """Load default configuration."""
        config_manager = ConfigManager()
        default_config = config_manager.load_default_config()
        provider = default_config.get("provider", "groq")
        base_url = default_config.get("base_url")
        # Set default base_url for openai兼容 provider if not specified
        if base_url is None and provider == "openai兼容":
            base_url = "https://api.deepseek.com/"
        return cls(
            provider=provider,
            model_name=default_config.get("model", "qwen/qwen3-32b"),
            base_url=base_url,
            temperature=float(default_config.get("temperature", 0.0)),
        )

    def save_global(self):
        """Save current configuration as global settings."""
        config_manager = ConfigManager()
        global_config = {
            "provider": self.provider,
            "model": self.model_name,
            "base_url": self.base_url,
            "temperature": self.temperature,
        }
        config_manager.save_global_config(global_config)

    @classmethod
    def delete(cls, config_id: str):
        """Delete a configuration.

        Args:
            config_id: The ID of the configuration to delete.
                      Cannot delete "default" configuration.
                      Use "global" to delete global configuration.
        """
        config_manager = ConfigManager()
        config_manager.delete_config(config_id)


# Default configuration instance
default_config = LLMConfig.load()
