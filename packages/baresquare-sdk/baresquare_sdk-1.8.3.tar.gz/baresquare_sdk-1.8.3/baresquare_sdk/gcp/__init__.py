"""Baresquare GCP Python utilities.

This package provides GCP-specific utilities for Baresquare services.
"""

try:
    # Check if GCP dependencies are available

    from baresquare_sdk.gcp import authentication, bigquery, clients, drive, pagers, secret_manager, sheets

    from baresquare_sdk.core.logger import logger

    __all__ = ["authentication", "bigquery", "clients", "drive", "pagers", "secret_manager", "sheets", "logger"]

except ImportError as e:
    raise ImportError("GCP dependencies not found. Install with: pip install baresquare-sdk[gcp]") from e
