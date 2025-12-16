"""
Public Python API for gravi_cli.

This module provides the programmatic interface for using gravi_cli
as a library in Python scripts and applications.

Example usage:
    from gravi_cli.api import get_instance_config, get_instance_token

    # Get database credentials
    config = get_instance_config("prod")
    db_url = config["config"]["database_url"]

    # Get ServiceNow access token
    token_response = get_instance_token("dev")
    sn_token = token_response["access_token"]
"""

# Re-export the main API functions from auth module
from .auth import (
    get_mom_token,
    get_instance_config,
    get_instance_token,
)

# Re-export exceptions for library users
from .exceptions import (
    GraviError,
    NotAuthenticatedError,
    InvalidTokenError,
    APIError,
    RateLimitError,
    ConfigError,
)

# Public API
__all__ = [
    # Authentication functions
    "get_mom_token",
    "get_instance_config",
    "get_instance_token",
    # Exceptions
    "GraviError",
    "NotAuthenticatedError",
    "InvalidTokenError",
    "APIError",
    "RateLimitError",
    "ConfigError",
]
