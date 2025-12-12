import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Dict, Optional, Type, TypeVar

T = TypeVar("T")


class ConfigManager:
    """Manages configuration persistence for both global and individual configs."""

    @staticmethod
    def get_env_path() -> Path:
        """Get the path for the .env file."""
        # Ensure the base directory exists
        base_dir = Path.home() / ".baicai"
        base_dir.mkdir(exist_ok=True)
        env_dir = base_dir / "env"
        env_dir.mkdir(exist_ok=True)
        env_file = env_dir / ".env"
        env_file.touch(exist_ok=True)
        return env_file

    def __init__(self, config_dir: str = ".baicai/configs"):
        # Use user's home directory
        self.config_dir = Path.home() / config_dir  # e.g., ~/.baicai/configs
        self.config_dir.mkdir(parents=True, exist_ok=True)  # Ensure nested config dir exists

        # Define env_file using the static method
        self.env_file = self.get_env_path()  # Should return ~/.baicai/.env

        self.global_config_path = self.config_dir / "global_config.json"
        self.default_config_path = self.config_dir / "default_config.json"
        self._ensure_default_config()

    def _ensure_default_config(self):
        """Ensure default config file exists with default values."""
        default_config = {
            "provider": "groq",
            "model": "qwen/qwen3-32b",
            "temperature": 0.0,
        }

        # If default config doesn't exist or is invalid, create/update it
        try:
            if not self.default_config_path.exists():
                print("Default configuration not found. Creating default_config.json.")
                self.save_default_config(default_config)
            else:
                # Verify the existing default config has all required fields
                with open(self.default_config_path, "r") as f:
                    existing_config = json.load(f)
                    if not all(key in existing_config for key in default_config):
                        print("Default configuration is incomplete. Updating default_config.json.")
                        # Update with missing fields
                        existing_config.update({k: v for k, v in default_config.items() if k not in existing_config})
                        self.save_default_config(existing_config)
        except Exception as e:
            print(f"Error reading/updating default config: {e}. Creating new default config.")
            self.save_default_config(default_config)

    def save_default_config(self, config: Dict):
        """Save default configuration to disk. This should only be called during initialization."""
        try:
            with open(self.default_config_path, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving default config: {e}")
            raise

    def load_default_config(self) -> Dict:
        """Load default configuration from disk."""
        try:
            if not self.default_config_path.exists():
                self._ensure_default_config()
            with open(self.default_config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading default config: {e}")
            # Return hardcoded defaults if file can't be read
            return {
                "provider": "groq",
                "model": "qwen/qwen3-32b",
                "temperature": 0.0,
            }

    def save_global_config(self, config: Dict):
        """Save global configuration to disk."""
        try:
            with open(self.global_config_path, "w") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving global config: {e}")
            raise

    def load_global_config(self) -> Dict:
        """Load global configuration from disk. If not found, return default config."""
        try:
            if not self.global_config_path.exists():
                return self.load_default_config()
            with open(self.global_config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading global config: {e}")
            return self.load_default_config()

    def save_config(self, config_id: str, config: T):
        """Save individual configuration to disk."""
        if not is_dataclass(config):
            raise ValueError("Config must be a dataclass")
        if config_id == "default":
            raise ValueError("Cannot modify default configuration")

        try:
            config_path = self.config_dir / f"{config_id}_config.json"
            with open(config_path, "w") as f:
                json.dump(asdict(config), f, indent=4)
        except Exception as e:
            print(f"Error saving config {config_id}: {e}")
            raise

    def load_config(self, config_id: str, config_class: Type[T]) -> Optional[T]:
        """Load individual configuration from disk."""
        if config_id == "default":
            return config_class(**self.load_default_config())

        try:
            config_path = self.config_dir / f"{config_id}_config.json"
            if not config_path.exists():
                return None

            with open(config_path, "r") as f:
                data = json.load(f)
                return config_class(**data)
        except Exception as e:
            print(f"Error loading config {config_id}: {e}")
            return None

    def delete_config(self, config_id: str):
        """Delete a configuration file.

        Args:
            config_id: The ID of the configuration to delete.
                      Cannot delete "default" configuration.
                      Use "global" to delete global configuration.
        """
        if config_id == "default":
            raise ValueError("Cannot delete default configuration")

        try:
            if config_id == "global":
                if self.global_config_path.exists():
                    self.global_config_path.unlink()
                return

            config_path = self.config_dir / f"{config_id}_config.json"
            if config_path.exists():
                config_path.unlink()
        except Exception as e:
            print(f"Error deleting config {config_id}: {e}")
            raise

    def get_config_path(self, config_id: str) -> Path:
        """Get the path for a specific configuration file."""
        return self.config_dir / f"{config_id}_config.json"

    def list_configs(self) -> list[str]:
        """List all available individual configurations, excluding default and global."""
        try:
            return [
                f.stem.replace("_config", "")
                for f in self.config_dir.glob("*_config.json")
                if f.name not in ["default_config.json", "global_config.json"]
            ]
        except Exception as e:
            print(f"Error listing configs: {e}")
            return []

    @property
    def config_location(self) -> str:
        """Get the location of the config directory."""
        return str(self.config_dir)

    def save_key(self, key_name: str, key_value: str):
        """Save a key-value pair to the .env file."""
        try:
            lines = []
            if self.env_file.exists():  # Check existence before reading
                with open(self.env_file, "r") as f:
                    lines = f.readlines()

            with open(self.env_file, "w") as f:
                key_found = False
                for line in lines:
                    stripped_line = line.strip()
                    if stripped_line.startswith(f"{key_name}="):
                        f.write(f'{key_name}="{key_value}"\n')  # Update existing key
                        key_found = True
                    elif stripped_line:  # Avoid writing empty lines unless intended
                        f.write(line)
                if not key_found:
                    f.write(f'{key_name}="{key_value}"\n')  # Add new key
            print(f"{key_name} saved to {self.env_file}")
        except Exception as e:
            print(f"Error saving key {key_name}: {e}")
            raise
