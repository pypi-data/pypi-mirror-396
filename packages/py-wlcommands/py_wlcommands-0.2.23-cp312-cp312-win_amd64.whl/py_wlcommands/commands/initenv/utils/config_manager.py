"""Configuration manager utility."""

import json
import os
from pathlib import Path
from typing import Any

import toml  # type: ignore[import-untyped]


class ConfigManager:
    """Manager for loading and managing configuration."""

    def __init__(self, config_file: str = "config.json") -> None:
        self.config_file = config_file
        self.config: dict[str, Any] = {}
        self.load_config()
        self._vendor_path = self._get_vendor_path()

    def _get_vendor_path(self) -> Path:
        """Get the path to the vendors directory."""
        current_file = Path(__file__)
        vendor_path = current_file.parent.parent.parent.parent / "vendors"
        return vendor_path.resolve()

    def load_config(self) -> None:
        """Load configuration from file or environment variables."""
        # Load from config file if exists
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, OSError):
                # If file loading fails, continue with empty config
                self.config = {}

        # Override with environment variables
        self._load_from_env()

    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Example environment variable loading
        python_version = os.environ.get("PYTHON_VERSION")
        if python_version:
            self.config["python_version"] = python_version

        venv_path = os.environ.get("VENV_PATH")
        if venv_path:
            self.config["venv_path"] = venv_path

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key."""
        self.config[key] = value

    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except (OSError, TypeError) as e:
            raise Exception(f"Failed to save configuration: {e}")

    def get_vendor_config_path(self, config_file: str) -> Path:
        """Get the path to a configuration file in the vendors directory.

        For hooks, automatically selects the appropriate directory based on the platform,
        unless an explicit platform directory (win/unix) is already specified.
        """
        import os

        # Check if we're dealing with hooks and no explicit platform is specified
        if config_file.startswith("hooks") and not any(
            platform in config_file for platform in ["/win", "/unix", "win/", "unix/"]
        ):
            # Determine the appropriate hook directory based on platform
            if os.name == "nt":  # Windows
                # Replace hooks/ with hooks/win/
                if config_file == "hooks":
                    config_file = "hooks/win"
                elif config_file.startswith("hooks/"):
                    config_file = config_file.replace("hooks/", "hooks/win/")
            else:  # Unix-like (Linux, macOS)
                # Replace hooks/ with hooks/unix/
                if config_file == "hooks":
                    config_file = "hooks/unix"
                elif config_file.startswith("hooks/"):
                    config_file = config_file.replace("hooks/", "hooks/unix/")

        return self._vendor_path / config_file

    def load_vendor_config(self, config_file: str) -> dict[str, Any]:
        """Load configuration from a file in the vendors directory."""
        config_path = self._vendor_path / config_file
        if not config_path.exists():
            return {}

        try:
            if config_path.suffix == ".toml":
                with open(config_path, encoding="utf-8") as f:
                    return toml.load(f)
            elif config_path.suffix == ".json":
                with open(config_path, encoding="utf-8") as f:
                    return json.load(f)
            else:
                # For other file types, return the raw content
                with open(config_path, encoding="utf-8") as f:
                    return {"content": f.read()}
        except (OSError, json.JSONDecodeError, toml.TomlDecodeError):
            return {}

    def load_template(self, template_file: str) -> str:
        """Load a template file from the vendors directory."""
        template_path = self._vendor_path / template_file
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        with open(template_path, encoding="utf-8") as f:
            return f.read()
