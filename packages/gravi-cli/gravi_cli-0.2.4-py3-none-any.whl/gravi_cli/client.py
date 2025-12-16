"""
Mom API client for gravi CLI.

Handles all HTTP communication with the mom backend API.
"""

import requests
from typing import Any

from .exceptions import APIError, InvalidTokenError, PermissionDeniedError, RateLimitError


class MomClient:
    """Client for interacting with mom backend API."""

    def __init__(self, mom_url: str, timeout: int = 30):
        """
        Initialize mom API client.

        Args:
            mom_url: Base URL for mom API (e.g., "https://mom.gravitate.energy")
            timeout: Request timeout in seconds
        """
        self.mom_url = mom_url.rstrip("/")
        self.timeout = timeout

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: dict | None = None,
        headers: dict | None = None,
        auth_token: str | None = None,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to mom API.

        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint (without leading slash)
            json_data: JSON payload for request body
            headers: Additional headers
            auth_token: Bearer token for authentication

        Returns:
            Response JSON as dictionary

        Raises:
            APIError: For non-2xx responses
            RateLimitError: For 429 rate limit responses
            InvalidTokenError: For 401 authentication failures
            PermissionDeniedError: For 403 permission denied responses
        """
        url = f"{self.mom_url}/{endpoint}"

        # Build headers
        request_headers = {
            "Content-Type": "application/json",
            "User-Agent": "gravi-cli/0.1.0",
        }
        if auth_token:
            request_headers["Authorization"] = f"Bearer {auth_token}"
        if headers:
            request_headers.update(headers)

        try:
            response = requests.request(
                method=method,
                url=url,
                json=json_data,
                headers=request_headers,
                timeout=self.timeout,
            )

            # Handle rate limiting
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "60")
                raise RateLimitError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds.",
                    status_code=429,
                    response_data=response.json() if response.content else None
                )

            # Handle authentication errors
            if response.status_code == 401:
                raise InvalidTokenError(
                    "Authentication failed. Token may be invalid or expired.",
                    status_code=401,
                    response_data=response.json() if response.content else None
                )

            # Handle permission errors
            if response.status_code == 403:
                error_data = response.json() if response.content else {}
                detail = error_data.get("detail", "")
                raise PermissionDeniedError(
                    f"You don't have permission to access this resource. {detail}".strip(),
                    status_code=403,
                    response_data=error_data
                )

            # Handle other errors
            if not response.ok:
                error_data = response.json() if response.content else {}
                error_message = error_data.get("detail", f"HTTP {response.status_code}: {response.reason}")
                raise APIError(
                    error_message,
                    status_code=response.status_code,
                    response_data=error_data
                )

            # Return response JSON
            return response.json()

        except requests.exceptions.Timeout:
            raise APIError(f"Request timed out after {self.timeout} seconds")
        except requests.exceptions.ConnectionError:
            raise APIError(f"Failed to connect to {self.mom_url}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}")

    # Device Authorization Flow

    def initiate_device_auth(self, device_name: str | None = None) -> dict:
        """
        Initiate device authorization flow.

        Args:
            device_name: Optional device name (hostname)

        Returns:
            {
                "device_code": "...",
                "user_code": "ABCD-1234",
                "verification_uri": "https://mom.../cli/authorize",
                "verification_uri_complete": "https://mom.../cli/authorize?code=...",
                "expires_in": 600,
                "interval": 5
            }
        """
        json_data = {}
        if device_name:
            json_data["device_name"] = device_name

        return self._make_request("POST", "cli/device/initiate", json_data=json_data)

    def poll_device_auth(self, device_code: str) -> dict:
        """
        Poll for device authorization status.

        Args:
            device_code: Device code from initiate response

        Returns:
            If pending:
            {
                "authorized": false,
                "expires_in": 500
            }

            If authorized:
            {
                "authorized": true,
                "refresh_token": "...",
                "access_token": "...",
                "token_id": "...",
                "user_email": "...",
                "device_name": "...",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_expires_in": 1209600
            }
        """
        return self._make_request("POST", "cli/device/poll", json_data={"device_code": device_code})

    # Token Management

    def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: CLI refresh token

        Returns:
            {
                "access_token": "...",
                "expires_in": 3600,
                "token_type": "Bearer",
                "refresh_token": "..." (optional, if auto-renewed),
                "refresh_expires_in": 1209600 (optional, if auto-renewed)
            }

        Raises:
            InvalidTokenError: If refresh token is invalid or revoked
        """
        response = self._make_request("POST", "cli/token/refresh", json_data={"refresh_token": refresh_token})

        # Check for error in response (some endpoints return 200 with error field)
        if "error" in response:
            if response["error"] == "invalid_token":
                raise InvalidTokenError(response.get("error_description", "Token is invalid or revoked"))
            raise APIError(f"Token refresh failed: {response.get('error_description', response['error'])}")

        return response

    def list_cli_tokens(self, access_token: str) -> dict:
        """
        List all CLI tokens for the authenticated user.

        Args:
            access_token: Mom access token

        Returns:
            {
                "tokens": [
                    {
                        "id": "...",
                        "device_name": "...",
                        "token_type": "user",
                        "created_at": "...",
                        "last_used_at": "...",
                        "expires_at": "...",
                        "days_until_expiry": 10
                    },
                    ...
                ]
            }
        """
        return self._make_request("GET", "cli/token/list", auth_token=access_token)

    def delete_cli_token(self, token_id: str, access_token: str) -> dict:
        """
        Revoke/delete a CLI token.

        Args:
            token_id: Token ID to revoke
            access_token: Mom access token

        Returns:
            {
                "success": true,
                "message": "CLI token deleted successfully"
            }
        """
        return self._make_request("DELETE", f"cli/token/{token_id}", auth_token=access_token)

    # Instance Operations

    def get_instance_config(self, instance_key: str, access_token: str) -> dict:
        """
        Get instance business configuration (model settings, fees, etc.).

        Args:
            instance_key: Instance identifier (e.g., "dev", "prod")
            access_token: Mom access token

        Returns:
            Business configuration including min_fee, full_fee, model settings, etc.
        """
        return self._make_request(
            "POST",
            "instance/get_config",
            json_data={"instance_key": instance_key},
            auth_token=access_token
        )

    def get_instance_credentials(self, instance_key: str, access_token: str) -> dict:
        """
        Get instance credentials and connection information.

        Args:
            instance_key: Instance identifier (e.g., "dev", "prod")
            access_token: Mom access token

        Returns:
            {
                "type": "dev",
                "short_name": "dev",
                "dbs": {
                    "backend": "dev_backend",
                    "price": "dev_price",
                    ...
                },
                "conn_str": "mongodb+srv://...",
                "url": "https://dev.bb.gravitate.energy",
                "auth_server": "https://dev.bb.gravitate.energy/service/auth",
                "system_psk": "...",
                "ignored_collections": [...],
                "runs_model": true,
                ...
            }
        """
        return self._make_request(
            "POST",
            "instance/get_credentials",
            json_data={"instance_key": instance_key},
            auth_token=access_token
        )

    def get_instance_token(self, instance_key: str, access_token: str) -> dict:
        """
        Get instance access token/credentials.

        Args:
            instance_key: Instance identifier (e.g., "dev", "prod")
            access_token: Mom access token

        Returns:
            Instance-specific response (format varies by instance type)
            Examples:
            - ServiceNow OAuth: {"access_token": "...", "token_type": "Bearer", "expires_in": 3600}
            - API Key based: {"api_key": "...", "environment": "production"}
            - Custom format: Any JSON structure the instance provides
        """
        return self._make_request(
            "POST",
            "instance/get_token",
            json_data={"instance_key": instance_key},
            auth_token=access_token
        )

    # Burner Operations

    def list_burners(self, access_token: str, status: str | None = None) -> dict:
        """
        List burners accessible to the authenticated user.

        Args:
            access_token: Mom access token
            status: Optional status filter (e.g., "ready", "creating")

        Returns:
            {
                "burners": [
                    {
                        "burner_id": "burner01",
                        "namespace": "burner01",
                        "status": "ready",
                        "url": "https://burner01.burner.gravitate.energy",
                        "created_by": "user@example.com",
                        "created_at": "2024-01-01T00:00:00Z",
                        "expires_at": "2024-01-02T00:00:00Z",
                        ...
                    },
                    ...
                ],
                "total": 5,
                "limit": 50,
                "offset": 0
            }
        """
        json_data = {"limit": 50, "offset": 0}
        if status:
            json_data["status"] = status
        return self._make_request(
            "POST",
            "burners/list",
            json_data=json_data,
            auth_token=access_token
        )

    def create_burner(
        self,
        access_token: str,
        ttl_hours: int = 2,
        sheet_id: str | None = None,
        source_env: str | None = None,
        seed_level: str = "barebone",
        custom_name: str | None = None,
        build: str = "dev",
        simple_demand: bool = False,
    ) -> dict:
        """
        Create a new burner instance.

        Args:
            access_token: Mom access token
            ttl_hours: Time-to-live in hours (1-168)
            sheet_id: Google Sheet ID for full seeding
            source_env: Source environment to copy from
            seed_level: Seeding level (none, barebone, full, copy)
            custom_name: Custom name for the burner
            build: Build to deploy (dev, test, rc, or SHA)
            simple_demand: Use even demand distribution

        Returns:
            {
                "operation_id": "...",
                "burner_id": "tank",
                "stream_url": "/burners/operations/stream?operation_id=...",
                "message": "Burner creation initiated"
            }
        """
        json_data = {
            "ttl_hours": ttl_hours,
            "seed_level": seed_level,
            "build": build,
            "simple_demand": simple_demand,
        }
        if sheet_id:
            json_data["sheet_id"] = sheet_id
        if source_env:
            json_data["source_env"] = source_env
        if custom_name:
            json_data["custom_name"] = custom_name

        return self._make_request(
            "POST",
            "burners/create",
            json_data=json_data,
            auth_token=access_token,
        )

    def delete_burner(self, burner_id: str, access_token: str) -> dict:
        """
        Delete a burner instance.

        Args:
            burner_id: Burner ID to delete (e.g., "tank")
            access_token: Mom access token

        Returns:
            {
                "operation_id": "...",
                "burner_id": "tank",
                "stream_url": "/burners/operations/stream?operation_id=...",
                "message": "Burner deletion initiated"
            }
        """
        return self._make_request(
            "POST",
            "burners/delete",
            json_data={"burner_id": burner_id},
            auth_token=access_token,
        )

    def get_burner(self, burner_id: str, access_token: str) -> dict:
        """
        Get details of a specific burner.

        Args:
            burner_id: Burner ID (e.g., "tank")
            access_token: Mom access token

        Returns:
            Burner details including status, url, created_by, expires_at, etc.
        """
        return self._make_request(
            "POST",
            "burners/get",
            json_data={"burner_id": burner_id},
            auth_token=access_token,
        )

    def get_operation_status(self, operation_id: str, access_token: str) -> dict:
        """
        Get status of a burner operation.

        Args:
            operation_id: Operation ID
            access_token: Mom access token

        Returns:
            {
                "operation_id": "...",
                "status": "pending|running|completed|failed",
                "progress_percent": 0-100,
                "current_step": "...",
                "initiated_at": "...",
                "completed_at": "...",
                "error_message": "..."
            }
        """
        return self._make_request(
            "POST",
            "burners/operations/get",
            json_data={"operation_id": operation_id},
            auth_token=access_token,
        )

    def list_burner_pods(self, burner_id: str, access_token: str) -> dict:
        """
        List all pods in a burner namespace, grouped by deployment.

        Args:
            burner_id: Burner ID (e.g., "tank")
            access_token: Mom access token

        Returns:
            {
                "pods": [...],
                "deployments": [
                    {"name": "backend", "desired_replicas": 1, "ready_replicas": 1, "pods": [...]},
                    ...
                ],
                "namespace": "burner-tank"
            }
        """
        return self._make_request(
            "GET",
            f"burners/{burner_id}/pods",
            auth_token=access_token,
        )

    def get_pod_logs(
        self,
        burner_id: str,
        pod_name: str,
        access_token: str,
        container: str | None = None,
        tail_lines: int = 100,
        since_seconds: int | None = None,
    ) -> dict:
        """
        Fetch logs from a pod.

        Args:
            burner_id: Burner ID (e.g., "tank")
            pod_name: Name of the pod
            access_token: Mom access token
            container: Container name (optional)
            tail_lines: Number of lines from end (default 100)
            since_seconds: Only fetch logs newer than this many seconds

        Returns:
            {
                "pod_name": "...",
                "container": "...",
                "logs": "...",
                "truncated": false
            }
        """
        # Build query params
        params = [f"tail_lines={tail_lines}"]
        if container:
            params.append(f"container={container}")
        if since_seconds:
            params.append(f"since_seconds={since_seconds}")

        query_string = "&".join(params)
        return self._make_request(
            "GET",
            f"burners/{burner_id}/pods/{pod_name}/logs?{query_string}",
            auth_token=access_token,
        )

    def restart_deployment(self, burner_id: str, deployment_name: str, access_token: str) -> dict:
        """
        Restart all pods in a deployment.

        Args:
            burner_id: Burner ID (e.g., "tank")
            deployment_name: Name of the deployment to restart
            access_token: Mom access token

        Returns:
            {"message": "Deployment backend restart initiated"}
        """
        return self._make_request(
            "POST",
            f"burners/{burner_id}/deployments/{deployment_name}/restart",
            auth_token=access_token,
        )
