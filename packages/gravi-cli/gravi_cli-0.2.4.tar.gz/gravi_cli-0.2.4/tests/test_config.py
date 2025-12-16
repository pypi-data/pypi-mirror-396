"""
Tests for config module.
"""

import pytest
import json
import os
from datetime import datetime, timedelta, UTC
from pathlib import Path

from gravi_cli.config import (
    Config,
    get_config_dir,
    get_config_path,
    load_config,
    save_config,
    delete_config,
    config_exists,
)
from gravi_cli.exceptions import ConfigError


class TestConfig:
    """Tests for Config model."""

    def test_config_model_creation(self):
        """Should create Config object with valid data."""
        config = Config(
            user_email="test@gravitate.com",
            refresh_token="test_token",
            refresh_token_expires_at=datetime.now(UTC),
            token_id="test_id",
            device_name="Test Device"
        )

        assert config.version == 1
        assert config.user_email == "test@gravitate.com"
        assert config.device_name == "Test Device"


class TestConfigFileOperations:
    """Tests for config file operations."""

    def test_save_and_load_config(self, temp_config_dir, mock_config):
        """Should save and load config successfully."""
        with patch('gravi_cli.config.get_config_dir', return_value=temp_config_dir):
            # Save config
            save_config(mock_config)

            # Verify file exists
            assert config_exists()

            # Load config
            loaded = load_config()

            assert loaded.user_email == mock_config.user_email
            assert loaded.refresh_token == mock_config.refresh_token
            assert loaded.token_id == mock_config.token_id
            assert loaded.device_name == mock_config.device_name

    def test_config_file_permissions(self, temp_config_dir, mock_config):
        """Should set proper file permissions (0600)."""
        with patch('gravi_cli.config.get_config_dir', return_value=temp_config_dir):
            save_config(mock_config)

            config_path = get_config_path()
            stat_info = os.stat(config_path)
            permissions = stat_info.st_mode & 0o777

            # Should be 0600 (read/write owner only)
            assert permissions == 0o600

    def test_datetime_serialization(self, temp_config_dir, mock_config):
        """Should correctly serialize and deserialize datetime."""
        with patch('gravi_cli.config.get_config_dir', return_value=temp_config_dir):
            original_dt = datetime.now(UTC) + timedelta(days=10)
            mock_config.refresh_token_expires_at = original_dt

            save_config(mock_config)
            loaded = load_config()

            # Compare timestamps (allow small difference for precision)
            assert isinstance(loaded.refresh_token_expires_at, datetime)
            diff = abs((loaded.refresh_token_expires_at - original_dt).total_seconds())
            assert diff < 1

    def test_load_nonexistent_config(self, temp_config_dir):
        """Should raise FileNotFoundError for nonexistent config."""
        with patch('gravi_cli.config.get_config_dir', return_value=temp_config_dir):
            with pytest.raises(FileNotFoundError):
                load_config()

    def test_delete_config(self, temp_config_dir, mock_config):
        """Should delete config file."""
        with patch('gravi_cli.config.get_config_dir', return_value=temp_config_dir):
            save_config(mock_config)
            assert config_exists()

            result = delete_config()
            assert result is True
            assert not config_exists()

    def test_delete_nonexistent_config(self, temp_config_dir):
        """Should return False when deleting nonexistent config."""
        with patch('gravi_cli.config.get_config_dir', return_value=temp_config_dir):
            result = delete_config()
            assert result is False


# Need to import patch
from unittest.mock import patch
