"""
Authentication and token management for gravi CLI.

Handles token refresh, auto-renewal, and provides the main API
for accessing mom and instance credentials.
"""

import os
import socket
import time
import webbrowser
from datetime import datetime, timedelta, UTC

from .client import MomClient
from .config import Config, load_config, save_config, delete_config, config_exists
from .exceptions import NotAuthenticatedError, InvalidTokenError, APIError


def get_mom_url() -> str:
    """
    Get mom URL from environment or use default.

    Returns:
        Mom API base URL

    Priority:
        1. GRAVI_MOM_URL environment variable
        2. Default: https://mom.gravitate.energy/api
    """
    return os.getenv("GRAVI_MOM_URL", "https://mom.gravitate.energy/api")


def ensure_logged_in() -> None:
    """
    Ensure the user is logged in, triggering the login flow if not.

    This function checks if the user has valid authentication credentials.
    If not authenticated or if the refresh token is invalid/expired, it
    automatically initiates the device authorization flow and opens a browser
    for the user to authorize.

    Raises:
        Exception: If the login flow fails or is cancelled
    """
    # Check if already logged in with valid credentials
    if config_exists():
        try:
            config = load_config()
            # Try to get a token to verify it's still valid
            mom_url = get_mom_url()
            client = MomClient(mom_url)
            try:
                client.refresh_token(config.refresh_token)
                # Token is valid, user is logged in
                return
            except (InvalidTokenError, APIError):
                # Token expired or invalid, need to re-authenticate
                print(f"Your authentication has expired. Logging in again...")
                delete_config()
        except Exception:
            # Config corrupted, proceed with login
            pass

    # Not logged in or token expired - initiate login flow
    print("Gravi CLI requires authentication.")
    print("Opening browser for login...")

    mom_url = get_mom_url()
    client = MomClient(mom_url)

    # Get device name
    try:
        device_name = socket.gethostname()
        if not device_name or device_name == "localhost":
            device_name = "unknown-device"
    except Exception:
        device_name = "unknown-device"

    # Initiate device authorization
    try:
        device_auth = client.initiate_device_auth(device_name=device_name)
    except APIError as e:
        raise Exception(f"Failed to initiate login: {e}")

    # Display instructions
    print("\n" + "=" * 60)
    print("Please authorize this CLI tool:")
    print(f"  1. Opening browser to: {device_auth['verification_uri_complete']}")
    print(f"  2. Or manually visit: {device_auth['verification_uri']}")
    print(f"     and enter code: {device_auth['user_code']}")
    print("=" * 60 + "\n")

    # Open browser automatically
    try:
        webbrowser.open(device_auth["verification_uri_complete"])
    except Exception:
        print("Could not open browser automatically. Please visit the URL manually.")

    # Poll for authorization
    device_code = device_auth["device_code"]
    interval = device_auth["interval"]
    expires_in = device_auth["expires_in"]

    print("Waiting for authorization...", end="", flush=True)

    start_time = time.time()
    while time.time() - start_time < expires_in:
        time.sleep(interval)

        try:
            result = client.poll_device_auth(device_code)
        except APIError as e:
            if "expired" in str(e).lower():
                print(" ✗")
                raise Exception("Authorization timed out. Please try again.")
            # Continue polling on other errors
            print(".", end="", flush=True)
            continue

        if result.get("error"):
            if result["error"] == "expired_token":
                print(" ✗")
                raise Exception("Authorization timed out. Please try again.")
            # Continue polling for other errors
            print(".", end="", flush=True)
            continue

        if result.get("authorized"):
            print(" ✓")

            # Extract credentials from response
            user_email = result["user_email"]
            token_id = result["token_id"]
            refresh_token = result["refresh_token"]
            refresh_expires_in = result["refresh_expires_in"]
            device_name = result["device_name"]

            # Save config
            config = Config(
                user_email=user_email,
                refresh_token=refresh_token,
                refresh_token_expires_at=datetime.now(UTC) + timedelta(seconds=refresh_expires_in),
                token_id=token_id,
                device_name=device_name,
            )
            save_config(config)

            print(f"\n✓ Successfully logged in as {user_email}")
            print(f"  Device: {device_name}")
            return

        print(".", end="", flush=True)

    # Timed out
    print(" ✗")
    raise Exception("Authorization timed out. Please try again.")


def get_mom_token() -> str:
    """
    Get valid Mom access token, refreshing if necessary.

    This function:
    1. Checks for GRAVI_REFRESH_TOKEN environment variable (CI/CD usage)
    2. Falls back to config file refresh token
    3. Refreshes the access token using the refresh token
    4. Auto-renews refresh token if <7 days remaining (saves to config)
    5. Returns fresh access token (in-memory only, not persisted)

    Returns:
        Valid mom access token

    Raises:
        NotAuthenticatedError: If not logged in or token expired
        InvalidTokenError: If refresh token is invalid or revoked
    """
    # Check for CI/CD environment variable first
    refresh_token = os.getenv("GRAVI_REFRESH_TOKEN")

    # Fall back to config file if not in CI/CD
    if not refresh_token:
        if not config_exists():
            raise NotAuthenticatedError("Please run 'gravi login' first")

        config = load_config()
        refresh_token = config.refresh_token
    else:
        # CI/CD mode - load config if it exists (for potential auto-renewal)
        config = None
        if config_exists():
            config = load_config()

    if not refresh_token:
        raise NotAuthenticatedError("Please run 'gravi login' first")

    # Always get fresh access token from refresh token
    mom_url = get_mom_url()
    client = MomClient(mom_url)

    try:
        response = client.refresh_token(refresh_token)
    except InvalidTokenError:
        raise NotAuthenticatedError("Refresh token expired or revoked. Please run 'gravi login' again")

    # Check if refresh token was renewed (auto-renewal if <7 days remaining)
    if "refresh_token" in response and config:
        config.refresh_token = response["refresh_token"]
        config.refresh_token_expires_at = datetime.now(UTC) + timedelta(seconds=response["refresh_expires_in"])
        save_config(config)

    # Return access token (in-memory only, not persisted)
    return response["access_token"]


def get_instance_config(instance_key: str) -> dict:
    """
    Get instance credentials and connection information.

    Args:
        instance_key: Instance identifier (e.g., "dev", "prod")

    Returns:
        Instance credentials dictionary:
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
            ...
        }

    Raises:
        NotAuthenticatedError: If not logged in or token expired
        InvalidTokenError: If token is invalid or revoked
        APIError: If API request fails
    """
    mom_url = get_mom_url()
    mom_token = get_mom_token()
    client = MomClient(mom_url)
    return client.get_instance_credentials(instance_key, mom_token)


def get_instance_token(instance_key: str) -> dict:
    """
    Get instance access token/credentials.

    Args:
        instance_key: Instance identifier (e.g., "dev", "prod")

    Returns:
        Instance-specific credentials (format varies by instance type)
        Examples:
        - ServiceNow OAuth: {"access_token": "...", "token_type": "Bearer", "expires_in": 3600}
        - API Key based: {"api_key": "...", "environment": "production"}
        - Custom format: Any JSON structure the instance provides

    Raises:
        NotAuthenticatedError: If not logged in or token expired
        InvalidTokenError: If token is invalid or revoked
        APIError: If API request fails
    """
    mom_url = get_mom_url()
    mom_token = get_mom_token()
    client = MomClient(mom_url)
    return client.get_instance_token(instance_key, mom_token)
