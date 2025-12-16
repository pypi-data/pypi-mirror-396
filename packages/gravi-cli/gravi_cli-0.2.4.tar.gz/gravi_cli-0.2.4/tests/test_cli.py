"""
Tests for CLI commands.
"""

import pytest
import os
import json
from datetime import datetime, timedelta, UTC
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from gravi_cli.cli import main, login, logout, status, whoami, tokens, config
from gravi_cli.config import Config
from gravi_cli.exceptions import NotAuthenticatedError, InvalidTokenError, APIError


@pytest.fixture
def runner():
    """Create Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_device_auth_response():
    """Mock device auth initiation response."""
    return {
        "device_code": "test_device_code_123",
        "user_code": "ABCD-1234",
        "verification_uri": "https://mom.test.gravitate.energy/cli/authorize",
        "verification_uri_complete": "https://mom.test.gravitate.energy/cli/authorize?code=test_device_code_123",
        "expires_in": 600,
        "interval": 5
    }


@pytest.fixture
def mock_device_poll_authorized_response():
    """Mock device auth poll response when authorized."""
    return {
        "authorized": True,
        "refresh_token": "test_refresh_token",
        "access_token": "test_access_token",
        "token_id": "507f1f77bcf86cd799439011",
        "user_email": "test@gravitate.com",
        "device_name": "Test Device",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_expires_in": 1209600  # 14 days
    }


class TestLoginCommand:
    """Tests for 'gravi login' command."""

    def test_successfully_completes_login_flow(self, runner, mock_device_auth_response,
                                                mock_device_poll_authorized_response, mocker, temp_config_dir):
        """Should successfully complete login flow."""
        # Mock config_exists to return False (not logged in)
        mocker.patch("gravi_cli.cli.config_exists", return_value=False)
        mocker.patch("gravi_cli.config.get_config_dir", return_value=temp_config_dir)

        # Mock MomClient
        mock_client = MagicMock()
        mock_client.initiate_device_auth.return_value = mock_device_auth_response
        mock_client.poll_device_auth.return_value = mock_device_poll_authorized_response
        mocker.patch("gravi_cli.cli.MomClient", return_value=mock_client)

        # Mock webbrowser.open
        mock_webbrowser = mocker.patch("gravi_cli.cli.webbrowser.open")

        # Mock socket.gethostname
        mocker.patch("gravi_cli.cli.socket.gethostname", return_value="test-laptop")

        result = runner.invoke(login, ["--mom-url", "https://mom.test.gravitate.energy"])

        assert result.exit_code == 0
        assert "Successfully logged in" in result.output
        assert "test@gravitate.com" in result.output
        mock_webbrowser.assert_called_once()

    def test_displays_user_code_and_verification_uri(self, runner, mock_device_auth_response,
                                                      mock_device_poll_authorized_response, mocker, temp_config_dir):
        """Should display user code and verification URI."""
        mocker.patch("gravi_cli.cli.config_exists", return_value=False)
        mocker.patch("gravi_cli.config.get_config_dir", return_value=temp_config_dir)

        mock_client = MagicMock()
        mock_client.initiate_device_auth.return_value = mock_device_auth_response
        mock_client.poll_device_auth.return_value = mock_device_poll_authorized_response
        mocker.patch("gravi_cli.cli.MomClient", return_value=mock_client)
        mocker.patch("gravi_cli.cli.webbrowser.open")
        mocker.patch("gravi_cli.cli.socket.gethostname", return_value="test-laptop")

        result = runner.invoke(login)

        assert "ABCD-1234" in result.output
        assert "https://mom.test.gravitate.energy/cli/authorize" in result.output

    def test_opens_browser_automatically(self, runner, mock_device_auth_response,
                                         mock_device_poll_authorized_response, mocker, temp_config_dir):
        """Should open browser automatically."""
        mocker.patch("gravi_cli.cli.config_exists", return_value=False)
        mocker.patch("gravi_cli.config.get_config_dir", return_value=temp_config_dir)

        mock_client = MagicMock()
        mock_client.initiate_device_auth.return_value = mock_device_auth_response
        mock_client.poll_device_auth.return_value = mock_device_poll_authorized_response
        mocker.patch("gravi_cli.cli.MomClient", return_value=mock_client)

        mock_webbrowser = mocker.patch("gravi_cli.cli.webbrowser.open")
        mocker.patch("gravi_cli.cli.socket.gethostname", return_value="test-laptop")

        result = runner.invoke(login)

        mock_webbrowser.assert_called_once_with(
            "https://mom.test.gravitate.energy/cli/authorize?code=test_device_code_123"
        )

    def test_asks_confirmation_if_already_logged_in(self, runner, mock_config, mocker, temp_config_dir):
        """Should ask user confirmation if already logged in."""
        mocker.patch("gravi_cli.cli.config_exists", return_value=True)
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)

        # User declines to log in again
        result = runner.invoke(login, input="n\n")

        assert result.exit_code == 0
        assert "Already logged in" in result.output
        assert mock_config.user_email in result.output

    def test_handles_api_error_during_initiation(self, runner, mocker, temp_config_dir):
        """Should handle API errors during initiation gracefully."""
        mocker.patch("gravi_cli.cli.config_exists", return_value=False)

        mock_client = MagicMock()
        mock_client.initiate_device_auth.side_effect = APIError("Rate limit exceeded", status_code=429)
        mocker.patch("gravi_cli.cli.MomClient", return_value=mock_client)

        result = runner.invoke(login)

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_uses_custom_mom_url_from_flag(self, runner, mock_device_auth_response,
                                           mock_device_poll_authorized_response, mocker, temp_config_dir):
        """Should use custom mom URL from --mom-url flag."""
        mocker.patch("gravi_cli.cli.config_exists", return_value=False)
        mocker.patch("gravi_cli.config.get_config_dir", return_value=temp_config_dir)

        mock_client_class = mocker.patch("gravi_cli.cli.MomClient")
        mock_client = MagicMock()
        mock_client.initiate_device_auth.return_value = mock_device_auth_response
        mock_client.poll_device_auth.return_value = mock_device_poll_authorized_response
        mock_client_class.return_value = mock_client

        mocker.patch("gravi_cli.cli.webbrowser.open")
        mocker.patch("gravi_cli.cli.socket.gethostname", return_value="test-laptop")

        result = runner.invoke(login, ["--mom-url", "https://mom.custom.com"])

        # Verify MomClient was instantiated with custom URL
        mock_client_class.assert_called_with("https://mom.custom.com")
        assert result.exit_code == 0

    def test_gets_device_name_from_hostname(self, runner, mock_device_auth_response,
                                            mock_device_poll_authorized_response, mocker, temp_config_dir):
        """Should get device name from hostname."""
        mocker.patch("gravi_cli.cli.config_exists", return_value=False)
        mocker.patch("gravi_cli.config.get_config_dir", return_value=temp_config_dir)

        mock_client = MagicMock()
        mock_client.initiate_device_auth.return_value = mock_device_auth_response
        mock_client.poll_device_auth.return_value = mock_device_poll_authorized_response
        mocker.patch("gravi_cli.cli.MomClient", return_value=mock_client)

        mocker.patch("gravi_cli.cli.webbrowser.open")
        mock_gethostname = mocker.patch("gravi_cli.cli.socket.gethostname", return_value="johns-macbook")

        result = runner.invoke(login)

        mock_gethostname.assert_called_once()
        mock_client.initiate_device_auth.assert_called_once_with(device_name="johns-macbook")


class TestLogoutCommand:
    """Tests for 'gravi logout' command."""

    def test_revokes_token_and_deletes_config(self, runner, mock_config, mocker, temp_config_dir):
        """Should revoke token on server and delete local config."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mocker.patch("gravi_cli.cli.get_mom_token", return_value="test_access_token")
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.test.gravitate.energy")
        mocker.patch("gravi_cli.cli.get_config_path", return_value=str(temp_config_dir / "config.json"))

        mock_client = MagicMock()
        mock_client.delete_cli_token.return_value = {"success": True}
        mocker.patch("gravi_cli.cli.MomClient", return_value=mock_client)

        mock_delete_config = mocker.patch("gravi_cli.cli.delete_config", return_value=True)

        result = runner.invoke(logout)

        assert result.exit_code == 0
        assert "Token revoked on server" in result.output
        assert "Local credentials cleared" in result.output
        mock_client.delete_cli_token.assert_called_once_with(mock_config.token_id, "test_access_token")
        mock_delete_config.assert_called_once()

    def test_handles_not_logged_in(self, runner, mocker):
        """Should handle case when not logged in gracefully."""
        mocker.patch("gravi_cli.cli.load_config", side_effect=FileNotFoundError())

        result = runner.invoke(logout)

        assert result.exit_code == 0
        assert "Logged out" in result.output

    def test_continues_logout_even_if_server_revocation_fails(self, runner, mock_config, mocker, temp_config_dir):
        """Should continue logout even if server revocation fails."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mocker.patch("gravi_cli.cli.get_mom_token", side_effect=Exception("Network error"))
        mocker.patch("gravi_cli.cli.get_config_path", return_value=str(temp_config_dir / "config.json"))

        mock_delete_config = mocker.patch("gravi_cli.cli.delete_config", return_value=True)

        result = runner.invoke(logout)

        assert result.exit_code == 0
        assert "Could not revoke token on server" in result.output
        assert "Local credentials cleared" in result.output
        mock_delete_config.assert_called_once()


class TestStatusCommand:
    """Tests for 'gravi status' command."""

    def test_shows_user_info_when_logged_in(self, runner, mock_config, mocker):
        """Should show user info when logged in."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        result = runner.invoke(status)

        assert result.exit_code == 0
        assert mock_config.user_email in result.output
        assert mock_config.device_name in result.output
        assert "https://mom.gravitate.energy" in result.output

    def test_shows_token_expiry_info(self, runner, mocker):
        """Should show token expiry info."""
        future_expiry = datetime.now(UTC) + timedelta(days=10)
        config = Config(
            user_email="test@gravitate.com",
            refresh_token="test_token",
            refresh_token_expires_at=future_expiry,
            token_id="test_id",
            device_name="Test Device"
        )
        mocker.patch("gravi_cli.cli.load_config", return_value=config)
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        result = runner.invoke(status)

        assert result.exit_code == 0
        assert "Valid for" in result.output or "10" in result.output

    def test_shows_expired_warning_when_token_expired(self, runner, mocker):
        """Should show 'expired' warning when token expired."""
        past_expiry = datetime.now(UTC) - timedelta(days=1)
        config = Config(
            user_email="test@gravitate.com",
            refresh_token="test_token",
            refresh_token_expires_at=past_expiry,
            token_id="test_id",
            device_name="Test Device"
        )
        mocker.patch("gravi_cli.cli.load_config", return_value=config)
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        result = runner.invoke(status)

        assert result.exit_code == 0
        assert "EXPIRED" in result.output

    def test_shows_auto_renew_warning_when_less_than_2_days(self, runner, mocker):
        """Should show 'auto-renew' warning when <2 days remaining."""
        soon_expiry = datetime.now(UTC) + timedelta(days=1)
        config = Config(
            user_email="test@gravitate.com",
            refresh_token="test_token",
            refresh_token_expires_at=soon_expiry,
            token_id="test_id",
            device_name="Test Device"
        )
        mocker.patch("gravi_cli.cli.load_config", return_value=config)
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        result = runner.invoke(status)

        assert result.exit_code == 0
        assert "auto-renew" in result.output

    def test_shows_not_logged_in_when_no_config(self, runner, mocker):
        """Should show 'not logged in' when no config exists."""
        mocker.patch("gravi_cli.cli.load_config", side_effect=FileNotFoundError())

        result = runner.invoke(status)

        assert result.exit_code == 0
        assert "Not logged in" in result.output


class TestWhoamiCommand:
    """Tests for 'gravi whoami' command."""

    def test_shows_user_email_and_device_info(self, runner, mock_config, mocker):
        """Should show user email and device info."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mocker.patch("gravi_cli.cli.get_mom_token", return_value="test_access_token")
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        result = runner.invoke(whoami)

        assert result.exit_code == 0
        assert mock_config.user_email in result.output
        assert mock_config.device_name in result.output

    def test_verifies_token_is_still_valid(self, runner, mock_config, mocker):
        """Should verify token is still valid by calling get_mom_token()."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mock_get_token = mocker.patch("gravi_cli.cli.get_mom_token", return_value="test_access_token")
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        result = runner.invoke(whoami)

        mock_get_token.assert_called_once()

    def test_shows_not_logged_in_when_no_config(self, runner, mocker):
        """Should show 'not logged in' when no config."""
        mocker.patch("gravi_cli.cli.load_config", side_effect=FileNotFoundError())

        result = runner.invoke(whoami)

        assert result.exit_code == 0
        assert "Not logged in" in result.output

    def test_shows_session_expired_when_token_invalid(self, runner, mock_config, mocker):
        """Should show 'session expired' when token invalid."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mocker.patch("gravi_cli.cli.get_mom_token", side_effect=NotAuthenticatedError("Token expired"))
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        result = runner.invoke(whoami)

        assert result.exit_code == 0
        assert "Session expired" in result.output


class TestTokensListCommand:
    """Tests for 'gravi tokens list' command."""

    def test_lists_all_cli_tokens(self, runner, mock_config, mocker):
        """Should list all CLI tokens."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mocker.patch("gravi_cli.cli.get_mom_token", return_value="test_access_token")
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        mock_client = MagicMock()
        mock_client.list_cli_tokens.return_value = {
            "tokens": [
                {
                    "id": "507f1f77bcf86cd799439011",
                    "device_name": "Test Device",
                    "token_type": "user",
                    "created_at": "2025-01-01T00:00:00Z",
                    "last_used_at": "2025-01-02T00:00:00Z",
                    "days_until_expiry": 10
                },
                {
                    "id": "other_token_id",
                    "device_name": "Other Device",
                    "token_type": "user",
                    "created_at": "2025-01-01T00:00:00Z",
                    "days_until_expiry": 5
                }
            ]
        }
        mocker.patch("gravi_cli.cli.MomClient", return_value=mock_client)

        result = runner.invoke(tokens, ["list"])

        assert result.exit_code == 0
        assert "Test Device" in result.output
        assert "Other Device" in result.output
        assert "10 days" in result.output

    def test_marks_current_token_with_arrow(self, runner, mock_config, mocker):
        """Should mark current token with arrow indicator."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mocker.patch("gravi_cli.cli.get_mom_token", return_value="test_access_token")
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        mock_client = MagicMock()
        mock_client.list_cli_tokens.return_value = {
            "tokens": [
                {
                    "id": mock_config.token_id,
                    "device_name": mock_config.device_name,
                    "token_type": "user",
                    "created_at": "2025-01-01T00:00:00Z",
                    "days_until_expiry": 10
                }
            ]
        }
        mocker.patch("gravi_cli.cli.MomClient", return_value=mock_client)

        result = runner.invoke(tokens, ["list"])

        assert result.exit_code == 0
        assert "Current session" in result.output

    def test_shows_no_tokens_when_none_exist(self, runner, mock_config, mocker):
        """Should show 'no tokens' when none exist."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mocker.patch("gravi_cli.cli.get_mom_token", return_value="test_access_token")
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        mock_client = MagicMock()
        mock_client.list_cli_tokens.return_value = {"tokens": []}
        mocker.patch("gravi_cli.cli.MomClient", return_value=mock_client)

        result = runner.invoke(tokens, ["list"])

        assert result.exit_code == 0
        assert "No active tokens" in result.output


class TestTokensRevokeCommand:
    """Tests for 'gravi tokens revoke' command."""

    def test_revokes_specific_token_by_id(self, runner, mock_config, mocker):
        """Should revoke specific token by ID."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mocker.patch("gravi_cli.cli.get_mom_token", return_value="test_access_token")
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        mock_client = MagicMock()
        mock_client.delete_cli_token.return_value = {"success": True}
        mocker.patch("gravi_cli.cli.MomClient", return_value=mock_client)

        result = runner.invoke(tokens, ["revoke", "other_token_id"])

        assert result.exit_code == 0
        assert "Token other_token_id revoked" in result.output
        mock_client.delete_cli_token.assert_called_once_with("other_token_id", "test_access_token")

    def test_clears_local_config_if_revoking_current_token(self, runner, mock_config, mocker):
        """Should clear local config if revoking current token."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mocker.patch("gravi_cli.cli.get_mom_token", return_value="test_access_token")
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        mock_client = MagicMock()
        mock_client.delete_cli_token.return_value = {"success": True}
        mocker.patch("gravi_cli.cli.MomClient", return_value=mock_client)

        mock_delete_config = mocker.patch("gravi_cli.cli.delete_config")

        result = runner.invoke(tokens, ["revoke", str(mock_config.token_id)])

        assert result.exit_code == 0
        assert "Current session ended" in result.output
        mock_delete_config.assert_called_once()

    def test_does_not_clear_config_if_revoking_other_token(self, runner, mock_config, mocker):
        """Should not clear config if revoking other token."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mocker.patch("gravi_cli.cli.get_mom_token", return_value="test_access_token")
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        mock_client = MagicMock()
        mock_client.delete_cli_token.return_value = {"success": True}
        mocker.patch("gravi_cli.cli.MomClient", return_value=mock_client)

        mock_delete_config = mocker.patch("gravi_cli.cli.delete_config")

        result = runner.invoke(tokens, ["revoke", "other_token_id"])

        assert result.exit_code == 0
        mock_delete_config.assert_not_called()

    def test_shows_error_when_no_token_id_provided(self, runner, mock_config, mocker):
        """Should show error when no token ID provided without --all."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mocker.patch("gravi_cli.cli.get_mom_token", return_value="test_access_token")
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        result = runner.invoke(tokens, ["revoke"])

        assert result.exit_code == 1
        assert "Specify a token ID or use --all flag" in result.output

    def test_revokes_all_tokens_when_confirmed(self, runner, mock_config, mocker):
        """Should revoke all tokens when user confirms."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mocker.patch("gravi_cli.cli.get_mom_token", return_value="test_access_token")
        mocker.patch("gravi_cli.cli.get_mom_url", return_value="https://mom.gravitate.energy")

        mock_client = MagicMock()
        mock_client.list_cli_tokens.return_value = {
            "tokens": [
                {"id": "token1", "device_name": "Device 1"},
                {"id": "token2", "device_name": "Device 2"}
            ]
        }
        mock_client.delete_cli_token.return_value = {"success": True}
        mocker.patch("gravi_cli.cli.MomClient", return_value=mock_client)

        mock_delete_config = mocker.patch("gravi_cli.cli.delete_config")

        # Confirm with 'y'
        result = runner.invoke(tokens, ["revoke", "--all"], input="y\n")

        assert result.exit_code == 0
        assert "All tokens revoked" in result.output
        assert mock_client.delete_cli_token.call_count == 2
        mock_delete_config.assert_called_once()

    def test_cancels_when_user_declines_confirmation(self, runner, mock_config, mocker):
        """Should cancel when user declines confirmation."""
        mocker.patch("gravi_cli.cli.load_config", return_value=mock_config)
        mocker.patch("gravi_cli.cli.get_mom_token", return_value="test_access_token")

        # Decline with 'n'
        result = runner.invoke(tokens, ["revoke", "--all"], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.output


class TestConfigCommand:
    """Tests for 'gravi config' command."""

    def test_gets_instance_config_and_outputs_json(self, runner, mocker):
        """Should get instance config and output JSON (default)."""
        mock_config_data = {
            "instance_key": "dev",
            "name": "Development",
            "api_url": "https://dev.example.com",
            "config": {
                "database_url": "postgresql://localhost/db",
                "redis_url": "redis://localhost:6379"
            }
        }
        mocker.patch("gravi_cli.cli.get_instance_config", return_value=mock_config_data)

        result = runner.invoke(config, ["dev"])

        assert result.exit_code == 0
        # Output should be valid JSON
        output_data = json.loads(result.output)
        assert output_data["instance_key"] == "dev"
        assert "database_url" in output_data["config"]

    def test_outputs_env_format_with_format_flag(self, runner, mocker):
        """Should output env format with --format=env."""
        mock_config_data = {
            "instance_key": "dev",
            "name": "Development",
            "api_url": "https://dev.example.com",
            "config": {
                "database_url": "postgresql://localhost/db",
                "redis_url": "redis://localhost:6379"
            }
        }
        mocker.patch("gravi_cli.cli.get_instance_config", return_value=mock_config_data)

        result = runner.invoke(config, ["dev", "--format=env"])

        assert result.exit_code == 0
        assert "export INSTANCE_KEY=" in result.output
        assert "export DATABASE_URL=" in result.output
        assert "export REDIS_URL=" in result.output

    def test_properly_shell_escapes_values_in_env_format(self, runner, mocker):
        """Should properly shell-escape values in env format."""
        mock_config_data = {
            "instance_key": "dev",
            "name": "Development Environment",
            "api_url": "https://dev.example.com",
            "config": {
                "secret": "pass with spaces",
                "other": "value'with'quotes"
            }
        }
        mocker.patch("gravi_cli.cli.get_instance_config", return_value=mock_config_data)

        result = runner.invoke(config, ["dev", "--format=env"])

        assert result.exit_code == 0
        # Should have quoted values with spaces
        assert "'pass with spaces'" in result.output or '"pass with spaces"' in result.output

    def test_handles_authentication_errors(self, runner, mocker):
        """Should handle authentication errors."""
        mocker.patch("gravi_cli.cli.get_instance_config",
                     side_effect=NotAuthenticatedError("Not logged in"))

        result = runner.invoke(config, ["dev"])

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_handles_instance_not_found_errors(self, runner, mocker):
        """Should handle instance not found errors."""
        mocker.patch("gravi_cli.cli.get_instance_config",
                     side_effect=APIError("Instance not found", status_code=404))

        result = runner.invoke(config, ["nonexistent"])

        assert result.exit_code == 1
        assert "Error" in result.output
