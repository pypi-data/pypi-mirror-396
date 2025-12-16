"""
Pytest fixtures and configuration for gravi_cli tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta, UTC
from unittest.mock import patch

from gravi_cli.config import Config


@pytest.fixture
def temp_config_dir(monkeypatch):
    """
    Create a temporary config directory for testing.

    Monkeypatches get_config_dir() to return temp directory.
    Automatically cleaned up after test.
    """
    temp_dir = Path(tempfile.mkdtemp())

    # Mock get_config_dir to return temp directory
    with patch('gravi_cli.config.get_config_dir', return_value=temp_dir):
        yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config():
    """Create a mock Config object for testing."""
    return Config(
        version=1,
        user_email="test@gravitate.com",
        refresh_token="mock_refresh_token",
        refresh_token_expires_at=datetime.now(UTC) + timedelta(days=14),
        token_id="507f1f77bcf86cd799439011",
        device_name="Test Device"
    )


@pytest.fixture
def mock_mom_url():
    """Mock mom URL."""
    return "https://mom.test.gravitate.energy"
