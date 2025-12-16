"""
Tests for public API module.
"""

import pytest


class TestPublicAPIImports:
    """Tests for public API imports and exports."""

    def test_can_import_all_public_functions(self):
        """Should be able to import all public API functions."""
        from gravi_cli.api import (
            get_mom_token,
            get_instance_config,
            get_instance_token,
        )

        # Just verify they're callable
        assert callable(get_mom_token)
        assert callable(get_instance_config)
        assert callable(get_instance_token)

    def test_can_import_all_exception_classes(self):
        """Should be able to import all exception classes."""
        from gravi_cli.api import (
            GraviError,
            NotAuthenticatedError,
            InvalidTokenError,
            APIError,
            RateLimitError,
            ConfigError,
        )

        # Verify they're all exception classes
        assert issubclass(GraviError, Exception)
        assert issubclass(NotAuthenticatedError, GraviError)
        assert issubclass(InvalidTokenError, APIError)
        assert issubclass(APIError, GraviError)
        assert issubclass(RateLimitError, APIError)
        assert issubclass(ConfigError, GraviError)

    def test_all_exports_match_dunder_all(self):
        """Should verify __all__ exports match actual exports."""
        import gravi_cli.api as api

        # Get __all__ list
        expected_exports = set(api.__all__)

        # Get actual exports (exclude private members)
        actual_exports = {name for name in dir(api) if not name.startswith("_")}

        # __all__ should be a subset of actual exports
        assert expected_exports.issubset(actual_exports)

        # Verify specific expected items are in __all__
        assert "get_mom_token" in expected_exports
        assert "get_instance_config" in expected_exports
        assert "get_instance_token" in expected_exports
        assert "GraviError" in expected_exports
        assert "NotAuthenticatedError" in expected_exports
        assert "InvalidTokenError" in expected_exports
        assert "APIError" in expected_exports
        assert "RateLimitError" in expected_exports
        assert "ConfigError" in expected_exports

    def test_functions_are_properly_exported_from_auth(self):
        """Should verify functions are properly re-exported from auth module."""
        from gravi_cli.api import get_mom_token, get_instance_config, get_instance_token
        from gravi_cli.auth import (
            get_mom_token as auth_get_mom_token,
            get_instance_config as auth_get_instance_config,
            get_instance_token as auth_get_instance_token,
        )

        # Verify they're the same functions
        assert get_mom_token is auth_get_mom_token
        assert get_instance_config is auth_get_instance_config
        assert get_instance_token is auth_get_instance_token

    def test_exceptions_are_properly_exported_from_exceptions(self):
        """Should verify exceptions are properly re-exported from exceptions module."""
        from gravi_cli.api import (
            GraviError,
            NotAuthenticatedError,
            InvalidTokenError,
            APIError,
            RateLimitError,
            ConfigError,
        )
        from gravi_cli.exceptions import (
            GraviError as exc_GraviError,
            NotAuthenticatedError as exc_NotAuthenticatedError,
            InvalidTokenError as exc_InvalidTokenError,
            APIError as exc_APIError,
            RateLimitError as exc_RateLimitError,
            ConfigError as exc_ConfigError,
        )

        # Verify they're the same classes
        assert GraviError is exc_GraviError
        assert NotAuthenticatedError is exc_NotAuthenticatedError
        assert InvalidTokenError is exc_InvalidTokenError
        assert APIError is exc_APIError
        assert RateLimitError is exc_RateLimitError
        assert ConfigError is exc_ConfigError
