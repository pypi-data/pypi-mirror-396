"""
URL Standardization for Revenium Client.

This module patches the Revenium client initialization to automatically
ensure /meter is in the URL, allowing users to provide URLs without /meter.
"""

import logging
import os

logger = logging.getLogger("revenium_middleware.extension")


def patch_revenium_client_url_standardization() -> None:
    """
    Patch the Revenium client to ensure /meter is in the URL.

    This function wraps the ReveniumMetering and AsyncReveniumMetering
    __init__ methods to ensure /meter is present in the base URL.

    Supported URL formats:
    - Plain base URL: https://api.revenium.ai → appends /meter
    - With /meter: https://api.revenium.ai/meter → keeps as is
    - With /meter/v2: https://api.revenium.ai/meter/v2 → removes /v2
    - With trailing slash: https://api.revenium.ai/ → appends /meter
    - Local development: http://localhost:8000 → appends /meter
    """
    try:
        from revenium_metering import ReveniumMetering, AsyncReveniumMetering
        from .utils import ensure_meter_in_url

        # Store original __init__ methods
        original_sync_init = ReveniumMetering.__init__
        original_async_init = AsyncReveniumMetering.__init__

        def patched_sync_init(self, *, api_key=None, base_url=None, **kwargs):
            """Patched sync __init__ with URL standardization."""
            if base_url is not None:
                base_url = ensure_meter_in_url(base_url)
                logger.debug(
                    "Ensured /meter in Revenium base_url: %s", base_url
                )
            else:
                env_url = os.environ.get("REVENIUM_METERING_BASE_URL")
                if env_url:
                    standardized = ensure_meter_in_url(env_url)
                    if standardized != env_url:
                        logger.debug(
                            "Ensured /meter in REVENIUM_METERING_BASE_URL "
                            "from %s to %s",
                            env_url,
                            standardized,
                        )
                    os.environ["REVENIUM_METERING_BASE_URL"] = standardized
                    base_url = standardized

            original_sync_init(
                self, api_key=api_key, base_url=base_url, **kwargs
            )

        def patched_async_init(self, *, api_key=None, base_url=None, **kwargs):
            """Patched async __init__ with URL standardization."""
            if base_url is not None:
                base_url = ensure_meter_in_url(base_url)
                logger.debug(
                    "Ensured /meter in Revenium base_url: %s", base_url
                )
            else:
                env_url = os.environ.get("REVENIUM_METERING_BASE_URL")
                if env_url:
                    standardized = ensure_meter_in_url(env_url)
                    if standardized != env_url:
                        logger.debug(
                            "Ensured /meter in REVENIUM_METERING_BASE_URL "
                            "from %s to %s",
                            env_url,
                            standardized,
                        )
                    os.environ["REVENIUM_METERING_BASE_URL"] = standardized
                    base_url = standardized

            original_async_init(
                self, api_key=api_key, base_url=base_url, **kwargs
            )

        # Apply patches
        ReveniumMetering.__init__ = patched_sync_init
        AsyncReveniumMetering.__init__ = patched_async_init

        # Also fix the already-created client instance
        try:
            from revenium_middleware import client

            env_url = os.environ.get("REVENIUM_METERING_BASE_URL")
            if env_url and hasattr(client, "base_url"):
                standardized = ensure_meter_in_url(env_url)
                if standardized != client.base_url:
                    logger.debug(
                        "Fixing already-created client base_url "
                        "from %s to %s",
                        client.base_url,
                        standardized,
                    )
                    client.base_url = standardized
                    # Also update the environment variable
                    os.environ["REVENIUM_METERING_BASE_URL"] = standardized
        except Exception as e:
            logger.debug("Could not fix already-created client: %s", e)

        logger.debug("URL /meter patching applied successfully")

    except ImportError:
        logger.debug(
            "Could not import ReveniumMetering classes for patching"
        )
    except Exception as e:
        logger.debug("Error applying URL /meter patching: %s", e)

