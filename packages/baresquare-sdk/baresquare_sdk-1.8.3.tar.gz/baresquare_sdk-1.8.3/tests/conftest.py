"""Test settings and fixtures for baresquare_sdk tests."""

from unittest.mock import patch

import pytest

from baresquare_sdk.settings import Settings, reset_settings


@pytest.fixture(autouse=True)
def mock_settings():
    """Mock settings globally for all tests."""

    def get_test_settings():
        # Try to create settings from environment first (for tests that set specific env vars)
        # Settings() will succeed if PL_ENV, PL_SERVICE, PL_REGION are set via @patch.dict(os.environ, ...)
        try:
            return Settings()
        except Exception:
            # Fall back to default test settings if required env vars not set
            # Settings requires these 3 fields - they're mandatory in the Pydantic model
            return Settings(pl_env="test", pl_service="test-service", pl_region="us-east-1")

    # Patch everywhere get_settings is imported
    with (
        patch("baresquare_sdk.settings.get_settings", side_effect=get_test_settings),
        patch("baresquare_sdk.core.logger.get_settings", side_effect=get_test_settings),
    ):
        yield


@pytest.fixture(autouse=True)
def reset_sdk_settings():
    """Reset SDK settings before and after each test."""
    reset_settings()
    yield
    reset_settings()
