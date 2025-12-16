"""
Tests for mom API client.
"""

import pytest
import responses
from requests.exceptions import Timeout, ConnectionError

from gravi_cli.client import MomClient
from gravi_cli.exceptions import APIError, InvalidTokenError, RateLimitError


@pytest.fixture
def client():
    """Create test client."""
    return MomClient("https://mom.test.gravitate.energy")


class TestMomClient:
    """Tests for MomClient."""

    @responses.activate
    def test_initiate_device_auth_success(self, client):
        """Should successfully initiate device authorization."""
        responses.add(
            responses.POST,
            "https://mom.test.gravitate.energy/cli/device/initiate",
            json={
                "device_code": "test_device_code",
                "user_code": "ABCD-1234",
                "verification_uri": "https://mom.test.gravitate.energy/cli/authorize",
                "verification_uri_complete": "https://mom.test.gravitate.energy/cli/authorize?code=test_device_code",
                "expires_in": 600,
                "interval": 5
            },
            status=200
        )

        result = client.initiate_device_auth(device_name="Test Device")

        assert result["device_code"] == "test_device_code"
        assert result["user_code"] == "ABCD-1234"
        assert result["expires_in"] == 600

    @responses.activate
    def test_poll_device_auth_pending(self, client):
        """Should return pending status when not yet authorized."""
        responses.add(
            responses.POST,
            "https://mom.test.gravitate.energy/cli/device/poll",
            json={
                "authorized": False,
                "expires_in": 500
            },
            status=200
        )

        result = client.poll_device_auth("test_device_code")

        assert result["authorized"] is False
        assert "expires_in" in result

    @responses.activate
    def test_poll_device_auth_authorized(self, client):
        """Should return tokens when authorized."""
        responses.add(
            responses.POST,
            "https://mom.test.gravitate.energy/cli/device/poll",
            json={
                "authorized": True,
                "refresh_token": "test_refresh_token",
                "access_token": "test_access_token",
                "token_id": "test_token_id",
                "user_email": "test@gravitate.com",
                "device_name": "Test Device",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_expires_in": 1209600
            },
            status=200
        )

        result = client.poll_device_auth("test_device_code")

        assert result["authorized"] is True
        assert result["refresh_token"] == "test_refresh_token"
        assert result["user_email"] == "test@gravitate.com"

    @responses.activate
    def test_refresh_token_success(self, client):
        """Should successfully refresh token."""
        responses.add(
            responses.POST,
            "https://mom.test.gravitate.energy/cli/token/refresh",
            json={
                "access_token": "new_access_token",
                "expires_in": 3600,
                "token_type": "Bearer"
            },
            status=200
        )

        result = client.refresh_token("test_refresh_token")

        assert result["access_token"] == "new_access_token"
        assert result["expires_in"] == 3600

    @responses.activate
    def test_refresh_token_with_renewal(self, client):
        """Should return new refresh token when auto-renewed."""
        responses.add(
            responses.POST,
            "https://mom.test.gravitate.energy/cli/token/refresh",
            json={
                "access_token": "new_access_token",
                "expires_in": 3600,
                "token_type": "Bearer",
                "refresh_token": "new_refresh_token",
                "refresh_expires_in": 1209600
            },
            status=200
        )

        result = client.refresh_token("test_refresh_token")

        assert "refresh_token" in result
        assert result["refresh_token"] == "new_refresh_token"

    @responses.activate
    def test_refresh_token_invalid(self, client):
        """Should raise InvalidTokenError for invalid token."""
        responses.add(
            responses.POST,
            "https://mom.test.gravitate.energy/cli/token/refresh",
            json={
                "error": "invalid_token",
                "error_description": "Token is invalid or revoked"
            },
            status=200
        )

        with pytest.raises(InvalidTokenError):
            client.refresh_token("invalid_token")

    @responses.activate
    def test_rate_limit_error(self, client):
        """Should raise RateLimitError for 429 responses."""
        responses.add(
            responses.POST,
            "https://mom.test.gravitate.energy/cli/device/initiate",
            status=429,
            headers={"Retry-After": "60"}
        )

        with pytest.raises(RateLimitError) as exc_info:
            client.initiate_device_auth()

        assert "Rate limit exceeded" in str(exc_info.value)

    @responses.activate
    def test_authentication_error(self, client):
        """Should raise InvalidTokenError for 401 responses."""
        responses.add(
            responses.GET,
            "https://mom.test.gravitate.energy/cli/tokens/list",
            status=401
        )

        with pytest.raises(InvalidTokenError):
            client.list_cli_tokens("invalid_token")

    @responses.activate
    def test_list_cli_tokens(self, client):
        """Should list CLI tokens."""
        responses.add(
            responses.GET,
            "https://mom.test.gravitate.energy/cli/tokens/list",
            json={
                "tokens": [
                    {
                        "id": "token1",
                        "device_name": "Device 1",
                        "token_type": "user",
                        "created_at": "2025-01-01T00:00:00Z",
                        "days_until_expiry": 10
                    }
                ]
            },
            status=200
        )

        result = client.list_cli_tokens("test_access_token")

        assert len(result["tokens"]) == 1
        assert result["tokens"][0]["device_name"] == "Device 1"

    @responses.activate
    def test_delete_cli_token(self, client):
        """Should delete CLI token."""
        responses.add(
            responses.DELETE,
            "https://mom.test.gravitate.energy/cli/tokens/token123",
            json={
                "success": True,
                "message": "CLI token deleted successfully"
            },
            status=200
        )

        result = client.delete_cli_token("token123", "test_access_token")

        assert result["success"] is True

    @responses.activate
    def test_get_instance_config(self, client):
        """Should get instance configuration."""
        responses.add(
            responses.POST,
            "https://mom.test.gravitate.energy/instance/get_config",
            json={
                "instance_key": "dev",
                "name": "Development",
                "api_url": "https://dev.example.com",
                "config": {
                    "database_url": "postgresql://..."
                }
            },
            status=200
        )

        result = client.get_instance_config("dev", "test_access_token")

        assert result["instance_key"] == "dev"
        assert "config" in result

    @responses.activate
    def test_get_instance_token(self, client):
        """Should get instance token."""
        responses.add(
            responses.POST,
            "https://mom.test.gravitate.energy/instance/get_token",
            json={
                "access_token": "instance_token",
                "token_type": "Bearer"
            },
            status=200
        )

        result = client.get_instance_token("dev", "test_access_token")

        assert result["access_token"] == "instance_token"
