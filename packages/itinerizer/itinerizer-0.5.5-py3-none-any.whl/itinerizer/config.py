"""
Configuration management for Itinerizer.

Handles local configuration and storage directory setup.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class ItinerarizerConfig:
    """Configuration settings for Itinerizer"""
    storage_path: str
    backup_path: str
    web_ui_port: int = 5001
    api_port: int = 8001
    log_level: str = "INFO"
    auto_backup: bool = True
    backup_retention_days: int = 30


class ConfigManager:
    """Manages Itinerizer configuration and local storage setup"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Optional custom config directory (defaults to ./.itinerizer)
        """
        self.config_dir = config_dir or Path.cwd() / ".itinerizer"
        self.config_file = self.config_dir / "config.json"
        self._config: Optional[ItinerarizerConfig] = None
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
    
    def get_config(self) -> ItinerarizerConfig:
        """Get current configuration, creating default if needed"""
        if self._config is None:
            self._config = self._load_or_create_config()
        return self._config
    
    def _load_or_create_config(self) -> ItinerarizerConfig:
        """Load existing config or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                return ItinerarizerConfig(**data)
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                print(f"Warning: Invalid config file, creating default: {e}")
        
        # Create default configuration
        config = ItinerarizerConfig(
            storage_path=str(self.config_dir / "itineraries"),
            backup_path=str(self.config_dir / "backups")
        )
        
        # Create storage directories
        Path(config.storage_path).mkdir(parents=True, exist_ok=True)
        Path(config.backup_path).mkdir(parents=True, exist_ok=True)
        
        # Save default config
        self.save_config(config)
        return config
    
    def save_config(self, config: ItinerarizerConfig) -> None:
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(asdict(config), f, indent=2)
        self._config = config
    
    def update_config(self, **kwargs) -> ItinerarizerConfig:
        """Update configuration with new values"""
        config = self.get_config()

        # Validate keys first
        invalid_keys = [key for key in kwargs.keys() if not hasattr(config, key)]
        if invalid_keys:
            raise ValueError(f"Invalid configuration keys: {', '.join(invalid_keys)}")

        # Update fields
        for key, value in kwargs.items():
            setattr(config, key, value)

        # Ensure storage directories exist
        Path(config.storage_path).mkdir(parents=True, exist_ok=True)
        Path(config.backup_path).mkdir(parents=True, exist_ok=True)

        self.save_config(config)
        return config
    
    def get_storage_path(self) -> str:
        """Get the configured storage path"""
        return self.get_config().storage_path
    
    def get_backup_path(self) -> str:
        """Get the configured backup path"""
        return self.get_config().backup_path
    
    def reset_config(self) -> ItinerarizerConfig:
        """Reset configuration to defaults"""
        if self.config_file.exists():
            self.config_file.unlink()
        self._config = None
        return self.get_config()


# Global config manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_dir: Optional[Path] = None) -> ConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    if _config_manager is None or config_dir is not None:
        _config_manager = ConfigManager(config_dir)
    return _config_manager


def get_default_storage_path() -> str:
    """Get the default storage path for itineraries"""
    return get_config_manager().get_storage_path()


def get_default_backup_path() -> str:
    """Get the default backup path for itineraries"""
    return get_config_manager().get_backup_path()


def setup_local_storage(base_dir: Optional[Path] = None) -> tuple[str, str]:
    """
    Setup local storage in .itinerizer directory.
    
    Args:
        base_dir: Base directory for .itinerizer (defaults to current working directory)
    
    Returns:
        Tuple of (storage_path, backup_path)
    """
    config_manager = get_config_manager(base_dir / ".itinerizer" if base_dir else None)
    config = config_manager.get_config()
    return config.storage_path, config.backup_path
