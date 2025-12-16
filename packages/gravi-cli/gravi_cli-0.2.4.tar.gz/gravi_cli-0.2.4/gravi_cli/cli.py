"""
Main CLI interface for gravi.

Implements all CLI commands using Click framework.
"""

import os
import sys
import json
import time
import socket
import shlex
import webbrowser
from datetime import datetime, UTC

import click

from . import __version__
from .auth import get_mom_url, get_mom_token, get_instance_config, get_instance_token
from .client import MomClient
from .config import (
    Config,
    load_config,
    save_config,
    delete_config,
    config_exists,
    get_config_path,
)
from .exceptions import (
    NotAuthenticatedError,
    InvalidTokenError,
    APIError,
    RateLimitError,
    ConfigError,
    PermissionDeniedError,
)


@click.group()
@click.version_option(version=__version__, prog_name="gravi")
def main():
    """Gravi CLI - Gravitate infrastructure management tool."""
    pass


@main.command()
@click.option(
    "--mom-url",
    envvar="GRAVI_MOM_URL",
    default="https://mom.gravitate.energy/api",
    help="Mom API URL (default: https://mom.gravitate.energy/api)",
)
def login(mom_url):
    """Authenticate with mom via browser."""
    client = MomClient(mom_url)

    # Check if already logged in
    if config_exists():
        try:
            config = load_config()
            click.echo(f"Already logged in as {config.user_email}")
            if click.confirm("Do you want to log in again?", default=False):
                delete_config()
            else:
                return
        except Exception:
            # Config corrupted, proceed with login
            pass

    # Step 1: Initiate device authorization
    click.echo("Initiating authentication...")

    # Get device name from hostname with fallback
    try:
        device_name = socket.gethostname()
        if not device_name or device_name == "localhost":
            device_name = "unknown-device"
    except Exception:
        device_name = "unknown-device"

    try:
        device_auth = client.initiate_device_auth(device_name=device_name)
    except APIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    # Step 2: Display instructions
    click.echo("\n" + "=" * 60)
    click.echo("Please authorize this CLI tool:")
    click.echo(f"  1. Opening browser to: {device_auth['verification_uri_complete']}")
    click.echo(f"  2. Or manually visit: {device_auth['verification_uri']}")
    click.echo(f"     and enter code: {device_auth['user_code']}")
    click.echo("=" * 60 + "\n")

    # Step 3: Open browser automatically
    try:
        webbrowser.open(device_auth["verification_uri_complete"])
    except Exception:
        click.echo("Could not open browser automatically. Please visit the URL manually.")

    # Step 4: Poll for authorization
    device_code = device_auth["device_code"]
    interval = device_auth["interval"]
    expires_in = device_auth["expires_in"]

    click.echo("Waiting for authorization...", nl=False)

    start_time = time.time()
    while time.time() - start_time < expires_in:
        time.sleep(interval)

        try:
            result = client.poll_device_auth(device_code)
        except APIError as e:
            if "expired" in str(e).lower():
                click.echo(" ✗")
                click.echo("\nError: Authorization timed out. Please try again.", err=True)
                sys.exit(1)
            # Continue polling on other errors
            click.echo(".", nl=False)
            continue

        if result.get("error"):
            if result["error"] == "expired_token":
                click.echo(" ✗")
                click.echo("\nError: Authorization timed out. Please try again.", err=True)
                sys.exit(1)
            # Continue polling for other errors
            click.echo(".", nl=False)
            continue

        if result.get("authorized"):
            click.echo(" ✓")

            # Step 5: Extract credentials from response
            user_email = result["user_email"]
            token_id = result["token_id"]
            refresh_token = result["refresh_token"]
            refresh_expires_in = result["refresh_expires_in"]
            device_name = result["device_name"]  # Final device name (may have been edited by user)

            # Save config (without mom_url - it's runtime only)
            config = Config(
                user_email=user_email,
                refresh_token=refresh_token,
                refresh_token_expires_at=datetime.now(UTC) + timedelta(seconds=refresh_expires_in),
                token_id=token_id,
                device_name=device_name,
            )

            try:
                save_config(config)
            except ConfigError as e:
                click.echo(f"\nError saving config: {e}", err=True)
                sys.exit(1)

            click.echo(f"\n✓ Successfully logged in as {user_email}")
            click.echo(f"  Credentials saved to: {get_config_path()}")
            return

        click.echo(".", nl=False)

    # Timeout
    click.echo(" ✗")
    click.echo("\nError: Authorization timed out or cancelled. Please try again.", err=True)
    sys.exit(1)


@main.command()
def logout():
    """Clear local credentials and revoke token on backend."""
    try:
        config = load_config()

        # Try to revoke token on backend
        try:
            mom_token = get_mom_token()
            mom_url = get_mom_url()
            client = MomClient(mom_url)
            # Delete this specific token by token_id
            client.delete_cli_token(config.token_id, mom_token)
            click.echo("✓ Token revoked on server")
        except Exception as e:
            click.echo(f"⚠  Could not revoke token on server: {e}")
            click.echo("  (Will still clear local credentials)")

        # Delete local config file
        config_path = get_config_path()
        if delete_config():
            click.echo(f"✓ Local credentials cleared from {config_path}")
        else:
            click.echo("No local credentials found")

    except FileNotFoundError:
        click.echo("✓ Logged out (no existing session)")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
def status():
    """Show login status and token expiry."""
    try:
        config = load_config()

        mom_url = get_mom_url()

        click.echo("Gravi CLI Status")
        click.echo("=" * 40)
        click.echo(f"User:         {config.user_email}")
        click.echo(f"Mom URL:      {mom_url}")
        click.echo(f"Device:       {config.device_name}")
        click.echo(f"Token ID:     {config.token_id}")

        # Calculate expiry
        # Handle both string (from config file) and datetime object
        if isinstance(config.refresh_token_expires_at, str):
            expires_at = datetime.fromisoformat(config.refresh_token_expires_at.replace("Z", "+00:00"))
        else:
            expires_at = config.refresh_token_expires_at

        time_remaining = expires_at - datetime.now(UTC)
        days_remaining = time_remaining.days

        if days_remaining < 0:
            click.echo("Token:        ✗ EXPIRED")
            click.echo("Action:       Run 'gravi login' to re-authenticate")
        elif days_remaining < 2:
            click.echo(f"Token:        ⚠  Expires in {days_remaining} day(s)")
            click.echo("Action:       Will auto-renew on next use")
        else:
            click.echo(f"Token:        ✓ Valid for {days_remaining} more days")

    except FileNotFoundError:
        click.echo("Not logged in. Run 'gravi login' to authenticate.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
def whoami():
    """Show current user info and mom URL."""
    try:
        config = load_config()

        # Get fresh access token to verify we're still authenticated
        mom_token = get_mom_token()
        mom_url = get_mom_url()

        click.echo(f"Logged in as: {config.user_email}")
        click.echo(f"Mom URL:      {mom_url}")
        click.echo(f"Device:       {config.device_name}")

    except FileNotFoundError:
        click.echo("Not logged in. Run 'gravi login' to authenticate.")
    except NotAuthenticatedError:
        click.echo("Session expired. Run 'gravi login' to re-authenticate.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.group()
def tokens():
    """Manage CLI authorization tokens."""
    pass


@tokens.command("list")
def tokens_list():
    """List all authorized CLI tokens."""
    try:
        config = load_config()
        mom_token = get_mom_token()
        mom_url = get_mom_url()
        client = MomClient(mom_url)

        response = client.list_cli_tokens(mom_token)

        if not response["tokens"]:
            click.echo("No active tokens found.")
            return

        click.echo("Active CLI Tokens:")
        click.echo("=" * 80)

        for token in response["tokens"]:
            is_current = token["id"] == config.token_id
            marker = "→" if is_current else " "

            click.echo(f"{marker} ID: {token['id']}")
            click.echo(f"  Device:      {token['device_name']}")
            click.echo(f"  Type:        {token['token_type']}")
            click.echo(f"  Created:     {token['created_at']}")
            click.echo(f"  Last used:   {token.get('last_used_at', 'Never')}")
            click.echo(f"  Expires in:  {token['days_until_expiry']} days")
            if is_current:
                click.echo("  (Current session)")
            click.echo()

    except NotAuthenticatedError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@tokens.command("revoke")
@click.argument("token_id", required=False)
@click.option("--all", is_flag=True, help="Revoke all tokens")
def tokens_revoke(token_id, all):
    """Revoke a CLI token by ID, or all tokens."""
    try:
        config = load_config()
        mom_token = get_mom_token()
        mom_url = get_mom_url()
        client = MomClient(mom_url)

        if all:
            if not click.confirm(
                "Are you sure you want to revoke ALL tokens? This will log you out everywhere.",
                default=False,
            ):
                click.echo("Cancelled.")
                return

            # Get all tokens and revoke them
            response = client.list_cli_tokens(mom_token)
            for token in response["tokens"]:
                client.delete_cli_token(token["id"], mom_token)
                click.echo(f"✓ Revoked token: {token['device_name']}")

            # Clear local config
            delete_config()
            click.echo("\n✓ All tokens revoked. You are now logged out.")

        elif token_id:
            client.delete_cli_token(token_id, mom_token)
            click.echo(f"✓ Token {token_id} revoked")

            # If revoking current token, clear local config
            # Compare as strings to handle both string and ObjectId types
            if str(token_id) == str(config.token_id):
                delete_config()
                click.echo("✓ Current session ended. Run 'gravi login' to re-authenticate.")

        else:
            click.echo("Error: Specify a token ID or use --all flag", err=True)
            click.echo("Usage: gravi tokens revoke <token_id>")
            click.echo("       gravi tokens revoke --all")
            sys.exit(1)

    except NotAuthenticatedError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("instance_key")
@click.option(
    "--format",
    type=click.Choice(["json", "env"]),
    default="json",
    help="Output format (default: json)",
)
def config(instance_key, format):
    """Get instance configuration (credentials, URLs, etc.)."""
    try:
        config_data = get_instance_config(instance_key)

        if format == "json":
            click.echo(json.dumps(config_data, indent=2))
        elif format == "env":
            # Flatten config for environment variables
            click.echo(f"# Environment variables for {instance_key}")
            click.echo(f"export INSTANCE_KEY={shlex.quote(config_data['instance_key'])}")
            click.echo(f"export INSTANCE_NAME={shlex.quote(config_data['name'])}")
            click.echo(f"export API_URL={shlex.quote(config_data['api_url'])}")

            for key, value in config_data.get("config", {}).items():
                env_key = key.upper()
                # Quote values to handle special characters and spaces
                click.echo(f"export {env_key}={shlex.quote(str(value))}")

    except NotAuthenticatedError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("instance_key")
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output as JSON for scripting",
)
def token(instance_key, output_json):
    """Get access and refresh tokens for an instance."""
    try:
        token_data = get_instance_token(instance_key)

        if output_json:
            click.echo(json.dumps({
                "access_token": token_data.get("access_token", ""),
                "refresh_token": token_data.get("refresh_token", ""),
            }))
        else:
            click.echo(f"AccessToken: {token_data.get('access_token', 'N/A')}")
            click.echo(f"RefreshToken: {token_data.get('refresh_token', 'N/A')}")

    except NotAuthenticatedError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except PermissionDeniedError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# Add missing import for timedelta
from datetime import timedelta

import asyncio


@main.command()
@click.argument("burner_id", required=False)
def dbtun(burner_id):
    """Tunnel to database services in a burner instance.

    Opens local ports that tunnel to MongoDB and Redis in the burner.
    Use MongoDB Compass or redis-cli to connect via the displayed connection strings.

    If BURNER_ID is not provided, uses the most recently created burner.

    Examples:

        gravi dbtun              # Auto-select newest burner

        gravi dbtun burner01     # Connect to specific burner
    """
    from .tunnel import run_tunnel

    try:
        mom_token = get_mom_token()
        mom_url = get_mom_url()
        client = MomClient(mom_url)

        # If no burner_id provided, find the newest one
        if not burner_id:
            response = client.list_burners(mom_token, status="ready")
            burners = response.get("burners", [])

            if not burners:
                click.echo("Error: No active burners found. Create one first.", err=True)
                sys.exit(1)

            # Burners are sorted by created_at desc, so first is newest
            burner_id = burners[0]["burner_id"]
            click.echo(f"Auto-selected: {burner_id}")

        # Run the tunnel
        asyncio.run(run_tunnel(mom_url, mom_token, burner_id))

    except NotAuthenticatedError:
        click.echo("Error: Please run 'gravi login' first", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nDisconnected.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ============================================================================
# Burner Commands
# ============================================================================

@main.group()
def burner():
    """Manage ephemeral burner instances."""
    pass


def poll_operation_until_complete(
    client: MomClient,
    token: str,
    operation_id: str,
    show_progress: bool = True,
    poll_interval: float = 2.0,
    timeout: float = 600.0,
) -> dict:
    """
    Poll an operation until it completes or fails.

    Args:
        client: MomClient instance
        token: Access token
        operation_id: Operation ID to poll
        show_progress: Whether to print progress
        poll_interval: Seconds between polls
        timeout: Maximum time to wait

    Returns:
        Final operation status dict
    """
    start_time = time.time()
    last_step = None

    while True:
        if time.time() - start_time > timeout:
            return {"status": "failed", "error_message": "Timeout waiting for operation"}

        status = client.get_operation_status(operation_id, token)

        if show_progress:
            current_step = status.get("current_step")
            progress = status.get("progress_percent", 0)
            if current_step and current_step != last_step:
                click.echo(f"\n  {current_step}...", nl=False)
                last_step = current_step
            else:
                click.echo(".", nl=False)

        if status["status"] in ("completed", "failed"):
            if show_progress:
                click.echo()
            return status

        time.sleep(poll_interval)


@burner.command("start")
@click.option("--ttl", "ttl_hours", default=2, type=int, help="Time-to-live in hours (1-168)")
@click.option("--sheet-id", default=None, help="Google Sheet ID for full seeding")
@click.option("--source-env", default=None, help="Source environment to copy from")
@click.option("--simple-demand", is_flag=True, help="Use even demand distribution")
@click.option("--sync", is_flag=True, help="Wait for burner to be ready")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def burner_start(ttl_hours, sheet_id, source_env, simple_demand, sync, output_json):
    """Create a new burner instance.

    Examples:

        gravi burner start                      # Quick barebone burner

        gravi burner start --ttl 8              # 8 hour TTL

        gravi burner start --sync               # Wait until ready

        gravi burner start --sheet-id ABC123    # Full seed from sheet
    """
    try:
        mom_token = get_mom_token()
        mom_url = get_mom_url()
        client = MomClient(mom_url)

        # Determine seed level based on options
        seed_level = "barebone"
        if sheet_id:
            seed_level = "full"
        elif source_env:
            seed_level = "copy"

        # Initiate creation
        response = client.create_burner(
            access_token=mom_token,
            ttl_hours=ttl_hours,
            sheet_id=sheet_id,
            source_env=source_env,
            seed_level=seed_level,
            simple_demand=simple_demand,
        )

        burner_id = response["burner_id"]
        operation_id = response["operation_id"]

        if not sync:
            # Async mode: just output the operation info and exit
            if output_json:
                click.echo(json.dumps(response))
            else:
                click.echo(f"Burner '{burner_id}' creation started")
                click.echo(f"  Operation ID: {operation_id}")
                click.echo(f"\nUse 'gravi burner status {burner_id}' to check status")
            return

        # Sync mode: poll until complete
        if not output_json:
            click.echo(f"Creating burner '{burner_id}'", nl=False)

        final_result = poll_operation_until_complete(
            client, mom_token, operation_id,
            show_progress=(not output_json)
        )

        if final_result["status"] == "completed":
            # Fetch the burner details
            burner_info = client.get_burner(burner_id, mom_token)

            if output_json:
                click.echo(json.dumps(burner_info))
            else:
                click.echo(f"\nBurner ready:")
                click.echo(f"  ID:      {burner_info['burner_id']}")
                click.echo(f"  URL:     https://{burner_info['url']}")
                click.echo(f"  Expires: {burner_info['expires_at']}")
        else:
            error_msg = final_result.get("error_message", "Unknown error")
            if output_json:
                click.echo(json.dumps({"error": error_msg, "burner_id": burner_id}))
            else:
                click.echo(f"\nError: {error_msg}", err=True)
            sys.exit(1)

    except NotAuthenticatedError:
        click.echo("Error: Please run 'gravi login' first", err=True)
        sys.exit(1)
    except RateLimitError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except APIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@burner.command("delete")
@click.argument("burner_id")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def burner_delete(burner_id, output_json):
    """Delete a burner instance.

    Examples:

        gravi burner delete tank

        gravi burner delete pump --json
    """
    try:
        mom_token = get_mom_token()
        mom_url = get_mom_url()
        client = MomClient(mom_url)

        response = client.delete_burner(burner_id, mom_token)

        if output_json:
            click.echo(json.dumps(response))
        else:
            click.echo(f"Burner '{burner_id}' deletion initiated")
            click.echo(f"  Operation ID: {response['operation_id']}")

    except NotAuthenticatedError:
        click.echo("Error: Please run 'gravi login' first", err=True)
        sys.exit(1)
    except APIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@burner.command("status")
@click.argument("burner_id")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def burner_status(burner_id, output_json):
    """Get detailed status of a burner.

    Examples:

        gravi burner status tank

        gravi burner status pump --json
    """
    try:
        mom_token = get_mom_token()
        mom_url = get_mom_url()
        client = MomClient(mom_url)

        burner_info = client.get_burner(burner_id, mom_token)

        if output_json:
            click.echo(json.dumps(burner_info))
        else:
            click.echo(f"Burner: {burner_info['burner_id']}")
            click.echo("=" * 40)
            click.echo(f"Status:     {burner_info['status']}")
            click.echo(f"URL:        https://{burner_info['url']}")
            click.echo(f"Created by: {burner_info['created_by']}")
            click.echo(f"Created:    {burner_info['created_at']}")
            click.echo(f"Expires:    {burner_info['expires_at']}")
            click.echo(f"TTL:        {burner_info['ttl_hours']} hours")
            click.echo(f"Build:      {burner_info['build']}")
            click.echo(f"Seed level: {burner_info['seed_level']}")
            if burner_info.get('custom_name'):
                click.echo(f"Name:       {burner_info['custom_name']}")
            if burner_info.get('sheet_id'):
                click.echo(f"Sheet ID:   {burner_info['sheet_id']}")

    except NotAuthenticatedError:
        click.echo("Error: Please run 'gravi login' first", err=True)
        sys.exit(1)
    except APIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@burner.command("pods")
@click.argument("burner_id")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def burner_pods(burner_id, output_json):
    """List pods in a burner instance.

    Shows all pods grouped by deployment with their status.

    Examples:

        gravi burner pods tank

        gravi burner pods pump --json
    """
    try:
        mom_token = get_mom_token()
        mom_url = get_mom_url()
        client = MomClient(mom_url)

        data = client.list_burner_pods(burner_id, mom_token)

        if output_json:
            click.echo(json.dumps(data))
        else:
            click.echo(f"Pods in burner '{burner_id}' ({data['namespace']})")
            click.echo("=" * 60)

            for deployment in data.get("deployments", []):
                ready = deployment["ready_replicas"]
                desired = deployment["desired_replicas"]
                status_icon = "✓" if ready == desired else "○"
                click.echo(f"\n{status_icon} {deployment['name']} ({ready}/{desired} ready)")

                for pod in deployment.get("pods", []):
                    pod_status = pod.get("status", "Unknown")
                    restarts = pod.get("restart_count", 0)
                    restart_str = f" (restarts: {restarts})" if restarts > 0 else ""
                    status_color = "green" if pod_status == "Running" else "yellow"
                    click.echo(f"    {pod['name']}: {pod_status}{restart_str}")

    except NotAuthenticatedError:
        click.echo("Error: Please run 'gravi login' first", err=True)
        sys.exit(1)
    except APIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@burner.command("logs")
@click.argument("burner_id")
@click.argument("pod_name")
@click.option("--tail", "-n", "tail_lines", default=100, type=int, help="Number of lines (default: 100)")
@click.option("--container", "-c", default=None, help="Container name (optional)")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def burner_logs(burner_id, pod_name, tail_lines, container, output_json):
    """Fetch logs from a pod in a burner.

    Examples:

        gravi burner logs tank backend-xyz

        gravi burner logs tank backend-xyz --tail 500

        gravi burner logs tank backend-xyz -c backend
    """
    try:
        mom_token = get_mom_token()
        mom_url = get_mom_url()
        client = MomClient(mom_url)

        data = client.get_pod_logs(
            burner_id=burner_id,
            pod_name=pod_name,
            access_token=mom_token,
            container=container,
            tail_lines=tail_lines,
        )

        if output_json:
            click.echo(json.dumps(data))
        else:
            if data.get("truncated"):
                click.echo(f"[Showing last {tail_lines} lines, logs truncated]", err=True)
            # API returns 'lines' as array or 'logs' as string
            logs = data.get("logs") or "\n".join(data.get("lines", []))
            click.echo(logs)

    except NotAuthenticatedError:
        click.echo("Error: Please run 'gravi login' first", err=True)
        sys.exit(1)
    except APIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@burner.command("restart")
@click.argument("burner_id")
@click.argument("deployment_name")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def burner_restart(burner_id, deployment_name, output_json):
    """Restart a deployment in a burner.

    Triggers a rolling restart of all pods in the deployment.

    Examples:

        gravi burner restart tank backend

        gravi burner restart pump forecast
    """
    try:
        mom_token = get_mom_token()
        mom_url = get_mom_url()
        client = MomClient(mom_url)

        response = client.restart_deployment(burner_id, deployment_name, mom_token)

        if output_json:
            click.echo(json.dumps(response))
        else:
            click.echo(f"Restart initiated for '{deployment_name}' in burner '{burner_id}'")

    except NotAuthenticatedError:
        click.echo("Error: Please run 'gravi login' first", err=True)
        sys.exit(1)
    except APIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
