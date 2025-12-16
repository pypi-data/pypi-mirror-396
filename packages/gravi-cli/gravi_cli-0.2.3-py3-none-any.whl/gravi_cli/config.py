"""
Configuration file management for gravi CLI.

Config file location: ~/.config/gravi/config.json
File permissions: 0600 (read/write owner only)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from .exceptions import ConfigError


class Config(BaseModel):
    """Configuration model for gravi CLI."""
    version: int = 1
    user_email: str
    refresh_token: str
    refresh_token_expires_at: datetime | str  # Stored as ISO string in file, parsed to datetime
    token_id: str
    device_name: str


def get_config_dir() -> Path:
    """Get the config directory path."""
    config_dir = Path.home() / ".config" / "gravi"
    return config_dir


def get_config_path() -> Path:
    """Get the config file path."""
    return get_config_dir() / "config.json"


def ensure_config_dir() -> None:
    """Ensure config directory exists with proper permissions."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    # Set directory permissions to 0700 (owner read/write/execute only)
    os.chmod(config_dir, 0o700)


def load_config() -> Config:
    """
    Load configuration from file.

    Returns:
        Config object with parsed datetime

    Raises:
        FileNotFoundError: If config file doesn't exist (user not logged in)
        ConfigError: If config file is invalid or corrupted
    """
    config_path = get_config_path()

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    try:
        with open(config_path, 'r') as f:
            data = json.load(f)

        # Parse ISO string to datetime if needed
        if isinstance(data.get('refresh_token_expires_at'), str):
            data['refresh_token_expires_at'] = datetime.fromisoformat(
                data['refresh_token_expires_at'].replace('Z', '+00:00')
            )

        return Config(**data)

    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config file: {e}")
    except Exception as e:
        raise ConfigError(f"Failed to load config: {e}")


def save_config(config: Config) -> None:
    """
    Save configuration to file.

    Args:
        config: Config object to save

    Raises:
        ConfigError: If unable to save config file
    """
    ensure_config_dir()
    config_path = get_config_path()

    try:
        # Convert config to dict
        data = config.model_dump()

        # Convert datetime to ISO string for JSON serialization
        if isinstance(data.get('refresh_token_expires_at'), datetime):
            data['refresh_token_expires_at'] = data['refresh_token_expires_at'].isoformat()

        # Write to temp file first, then rename (atomic operation)
        temp_path = config_path.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2)

        # Set file permissions to 0600 (owner read/write only)
        os.chmod(temp_path, 0o600)

        # Atomic rename
        temp_path.replace(config_path)

    except Exception as e:
        raise ConfigError(f"Failed to save config: {e}")


def delete_config() -> bool:
    """
    Delete configuration file.

    Returns:
        True if config was deleted, False if it didn't exist
    """
    config_path = get_config_path()
    if config_path.exists():
        config_path.unlink()
        return True
    return False


def config_exists() -> bool:
    """Check if config file exists."""
    return get_config_path().exists()
