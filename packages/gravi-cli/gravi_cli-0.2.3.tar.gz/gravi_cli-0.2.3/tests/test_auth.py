"""
Tests for auth module.
"""

import pytest
import os
from datetime import datetime, timedelta, UTC
from unittest.mock import patch, MagicMock

from gravi_cli.auth import get_mom_url, get_mom_token, get_instance_config, get_instance_token
from gravi_cli.config import Config
from gravi_cli.exceptions import NotAuthenticatedError, InvalidTokenError, APIError


class TestGetMomUrl:
    """Tests for get_mom_url()."""

    def test_returns_default_url_when_no_env_var(self):
        """Should return default URL when GRAVI_MOM_URL not set."""
        with patch.dict(os.environ, {}, clear=True):
            url = get_mom_url()
            assert url == "https://mom.gravitate.energy"

    def test_returns_custom_url_from_env_var(self):
        """Should return custom URL from GRAVI_MOM_URL env var."""
        custom_url = "https://mom.dev.gravitate.energy"
        with patch.dict(os.environ, {"GRAVI_MOM_URL": custom_url}):
            url = get_mom_url()
            assert url == custom_url


class TestGetMomToken:
    """Tests for get_mom_token()."""

    def test_raises_not_authenticated_when_no_config_and_no_env_var(self):
        """Should raise NotAuthenticatedError when no config exists and no env var."""
        with patch("gravi_cli.auth.config_exists", return_value=False):
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(NotAuthenticatedError) as exc_info:
                    get_mom_token()
                assert "Please run 'gravi login' first" in str(exc_info.value)

    def test_loads_refresh_token_from_config(self, mock_config, mocker):
        """Should load refresh token from config file when it exists."""
        # Mock config_exists to return True
        mocker.patch("gravi_cli.auth.config_exists", return_value=True)

        # Mock load_config to return our mock config
        mocker.patch("gravi_cli.auth.load_config", return_value=mock_config)

        # Mock MomClient and its refresh_token method
        mock_client = MagicMock()
        mock_client.refresh_token.return_value = {
            "access_token": "new_access_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        mocker.patch("gravi_cli.auth.MomClient", return_value=mock_client)

        # Call get_mom_token
        token = get_mom_token()

        # Verify it returned the access token
        assert token == "new_access_token"

        # Verify it called refresh_token with the config's refresh token
        mock_client.refresh_token.assert_called_once_with(mock_config.refresh_token)

    def test_uses_env_var_refresh_token_in_ci_cd_mode(self, mocker):
        """Should use GRAVI_REFRESH_TOKEN env var when set (CI/CD mode)."""
        env_refresh_token = "env_refresh_token_123"

        with patch.dict(os.environ, {"GRAVI_REFRESH_TOKEN": env_refresh_token}):
            # Mock MomClient
            mock_client = MagicMock()
            mock_client.refresh_token.return_value = {
                "access_token": "ci_access_token",
                "expires_in": 3600,
                "token_type": "Bearer"
            }
            mocker.patch("gravi_cli.auth.MomClient", return_value=mock_client)

            # Call get_mom_token
            token = get_mom_token()

            # Verify it used the env var token
            assert token == "ci_access_token"
            mock_client.refresh_token.assert_called_once_with(env_refresh_token)

    def test_successfully_refreshes_token_and_returns_access_token(self, mock_config, mocker):
        """Should successfully refresh token and return access token."""
        mocker.patch("gravi_cli.auth.config_exists", return_value=True)
        mocker.patch("gravi_cli.auth.load_config", return_value=mock_config)

        mock_client = MagicMock()
        mock_client.refresh_token.return_value = {
            "access_token": "fresh_access_token",
            "expires_in": 3600,
            "token_type": "Bearer"
        }
        mocker.patch("gravi_cli.auth.MomClient", return_value=mock_client)

        token = get_mom_token()

        assert token == "fresh_access_token"

    def test_raises_not_authenticated_when_refresh_token_invalid(self, mock_config, mocker):
        """Should raise NotAuthenticatedError when refresh token is invalid."""
        mocker.patch("gravi_cli.auth.config_exists", return_value=True)
        mocker.patch("gravi_cli.auth.load_config", return_value=mock_config)

        mock_client = MagicMock()
        mock_client.refresh_token.side_effect = InvalidTokenError("Token invalid")
        mocker.patch("gravi_cli.auth.MomClient", return_value=mock_client)

        with pytest.raises(NotAuthenticatedError) as exc_info:
            get_mom_token()
        assert "Refresh token expired or revoked" in str(exc_info.value)

    def test_auto_renews_refresh_token_when_response_includes_new_token(self, mock_config, mocker):
        """Should auto-renew refresh token when response includes new refresh_token."""
        mocker.patch("gravi_cli.auth.config_exists", return_value=True)
        mocker.patch("gravi_cli.auth.load_config", return_value=mock_config)

        # Mock save_config to verify it gets called
        mock_save_config = mocker.patch("gravi_cli.auth.save_config")

        mock_client = MagicMock()
        mock_client.refresh_token.return_value = {
            "access_token": "new_access_token",
            "expires_in": 3600,
            "token_type": "Bearer",
            "refresh_token": "new_refresh_token",
            "refresh_expires_in": 1209600  # 14 days
        }
        mocker.patch("gravi_cli.auth.MomClient", return_value=mock_client)

        token = get_mom_token()

        # Verify access token returned
        assert token == "new_access_token"

        # Verify config was saved with new refresh token
        mock_save_config.assert_called_once()
        saved_config = mock_save_config.call_args[0][0]
        assert saved_config.refresh_token == "new_refresh_token"

    def test_does_not_save_config_in_ci_cd_mode(self, mocker):
        """Should NOT save to config in CI/CD mode (env var only)."""
        env_refresh_token = "env_refresh_token_123"

        with patch.dict(os.environ, {"GRAVI_REFRESH_TOKEN": env_refresh_token}):
            # Mock config_exists to return False (no config file)
            mocker.patch("gravi_cli.auth.config_exists", return_value=False)

            # Mock save_config to verify it does NOT get called
            mock_save_config = mocker.patch("gravi_cli.auth.save_config")

            mock_client = MagicMock()
            mock_client.refresh_token.return_value = {
                "access_token": "ci_access_token",
                "expires_in": 3600,
                "token_type": "Bearer",
                "refresh_token": "new_refresh_token",
                "refresh_expires_in": 1209600
            }
            mocker.patch("gravi_cli.auth.MomClient", return_value=mock_client)

            token = get_mom_token()

            # Verify token returned
            assert token == "ci_access_token"

            # Verify save_config was NOT called
            mock_save_config.assert_not_called()


class TestGetInstanceConfig:
    """Tests for get_instance_config()."""

    def test_successfully_gets_instance_config(self, mocker):
        """Should successfully get instance config with valid token."""
        # Mock get_mom_token
        mocker.patch("gravi_cli.auth.get_mom_token", return_value="valid_access_token")

        # Mock MomClient
        mock_client = MagicMock()
        mock_client.get_instance_config.return_value = {
            "instance_key": "dev",
            "name": "Development",
            "api_url": "https://dev.example.com",
            "config": {
                "database_url": "postgresql://..."
            }
        }
        mocker.patch("gravi_cli.auth.MomClient", return_value=mock_client)

        result = get_instance_config("dev")

        assert result["instance_key"] == "dev"
        assert "config" in result
        mock_client.get_instance_config.assert_called_once_with("dev", "valid_access_token")

    def test_raises_not_authenticated_when_not_logged_in(self, mocker):
        """Should raise NotAuthenticatedError when not logged in."""
        mocker.patch("gravi_cli.auth.get_mom_token", side_effect=NotAuthenticatedError("Not logged in"))

        with pytest.raises(NotAuthenticatedError):
            get_instance_config("dev")

    def test_raises_api_error_when_instance_not_found(self, mocker):
        """Should raise APIError when instance not found."""
        mocker.patch("gravi_cli.auth.get_mom_token", return_value="valid_token")

        mock_client = MagicMock()
        mock_client.get_instance_config.side_effect = APIError("Instance not found", status_code=404)
        mocker.patch("gravi_cli.auth.MomClient", return_value=mock_client)

        with pytest.raises(APIError) as exc_info:
            get_instance_config("nonexistent")
        assert exc_info.value.status_code == 404


class TestGetInstanceToken:
    """Tests for get_instance_token()."""

    def test_successfully_gets_instance_token(self, mocker):
        """Should successfully get instance token with valid token."""
        mocker.patch("gravi_cli.auth.get_mom_token", return_value="valid_access_token")

        mock_client = MagicMock()
        mock_client.get_instance_token.return_value = {
            "access_token": "instance_token",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        mocker.patch("gravi_cli.auth.MomClient", return_value=mock_client)

        result = get_instance_token("dev")

        assert result["access_token"] == "instance_token"
        mock_client.get_instance_token.assert_called_once_with("dev", "valid_access_token")

    def test_raises_not_authenticated_when_not_logged_in(self, mocker):
        """Should raise NotAuthenticatedError when not logged in."""
        mocker.patch("gravi_cli.auth.get_mom_token", side_effect=NotAuthenticatedError("Not logged in"))

        with pytest.raises(NotAuthenticatedError):
            get_instance_token("dev")

    def test_raises_api_error_when_instance_not_found(self, mocker):
        """Should raise APIError when instance not found."""
        mocker.patch("gravi_cli.auth.get_mom_token", return_value="valid_token")

        mock_client = MagicMock()
        mock_client.get_instance_token.side_effect = APIError("Instance not found", status_code=404)
        mocker.patch("gravi_cli.auth.MomClient", return_value=mock_client)

        with pytest.raises(APIError) as exc_info:
            get_instance_token("nonexistent")
        assert exc_info.value.status_code == 404
