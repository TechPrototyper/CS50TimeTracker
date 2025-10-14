#!/usr/bin/env python3
"""
SITR Config Manager

Handles configuration file management for SITR (Simple Time Tracker).
Stores settings in ~/.sitrconfig as JSON.
"""
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class ConfigManager:
    """Manages SITR configuration file."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize config manager.

        Args:
            config_path: Optional custom config file path.
                        Defaults to ~/.sitrconfig
        """
        if config_path is None:
            self.config_path = Path.home() / ".sitrconfig"
        else:
            self.config_path = config_path

        self.sitr_dir = Path.home() / ".sitr"
        self.old_user_file = self.sitr_dir / "current_user"

        # Ensure .sitr directory exists
        self.sitr_dir.mkdir(exist_ok=True)

        # Migrate old config if exists
        self._migrate_old_config()

        # Load or create config
        self.config = self._load_config()

    def _migrate_old_config(self):
        """Migrate from old current_user file to new config format."""
        if self.old_user_file.exists() and not self.config_path.exists():
            try:
                old_user_id = int(self.old_user_file.read_text().strip())
                # Create new config with migrated user ID
                default_config = self._get_default_config()
                default_config["current_user_id"] = old_user_id
                self._save_config(default_config)
                print(f"✓ Migrated user config from {self.old_user_file}")
                # Keep old file for backward compatibility
            except (ValueError, IOError) as e:
                print(f"Warning: Could not migrate old config: {e}")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "api_url": "http://127.0.0.1:8000",
            "auto_start_server": True,
            "current_user_id": None,
            "current_user_email": None,
            "server_port": 8000,
            "server_host": "127.0.0.1",
            "last_updated": datetime.utcnow().isoformat()
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_path.exists():
            return self._get_default_config()

        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            # Merge with defaults to ensure all keys exist
            default_config = self._get_default_config()
            default_config.update(config)
            return default_config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config, using defaults: {e}")
            return self._get_default_config()

    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file."""
        config["last_updated"] = datetime.utcnow().isoformat()
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error: Could not save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self._save_config(self.config)

    def get_api_url(self) -> str:
        """Get API URL."""
        return self.config.get(
            "api_url",
            "http://127.0.0.1:8000"
        )

    def set_api_url(self, url: str):
        """Set API URL."""
        self.set("api_url", url)

    def get_auto_start_server(self) -> bool:
        """Get auto-start server setting."""
        return self.config.get("auto_start_server", True)

    def set_auto_start_server(self, enabled: bool):
        """Set auto-start server setting."""
        self.set("auto_start_server", enabled)

    def get_current_user_id(self) -> Optional[int]:
        """Get current user ID."""
        return self.config.get("current_user_id")

    def set_current_user_id(self, user_id: int):
        """Set current user ID."""
        self.set("current_user_id", user_id)
        # Also update old file for backward compatibility
        try:
            self.old_user_file.write_text(str(user_id))
        except IOError:
            pass

    def get_current_user_email(self) -> Optional[str]:
        """Get current user email."""
        return self.config.get("current_user_email")

    def set_current_user_email(self, email: str):
        """Set current user email."""
        self.set("current_user_email", email)

    def get_server_host(self) -> str:
        """Get server host."""
        return self.config.get("server_host", "127.0.0.1")

    def get_server_port(self) -> int:
        """Get server port."""
        return self.config.get("server_port", 8000)

    def set_server_host(self, host: str):
        """Set server host."""
        self.set("server_host", host)

    def set_server_port(self, port: int):
        """Set server port."""
        self.set("server_port", port)

    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = self._get_default_config()
        self._save_config(self.config)

    def show_config(self) -> str:
        """Get formatted configuration string."""
        lines = ["SITR Configuration:", "=" * 50]
        for key, value in sorted(self.config.items()):
            lines.append(f"{key:25} : {value}")
        return "\n".join(lines)


# Singleton instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get singleton config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
