"""
Google AI SDK middleware for Revenium.

This module provides middleware for the Google AI SDK (google-genai package),
supporting both Gemini Developer API and Vertex AI endpoints through the
unified google-genai interface.

The middleware automatically wraps Google AI SDK methods to provide transparent
usage tracking and metering to Revenium.
"""

# Import middleware components to activate them
from . import middleware
from . import provider

# Export key functions for external use
from .middleware import (
    extract_google_ai_usage_data,
    create_google_ai_metering_call,
    handle_streaming_response,
)

from .provider import (
    detect_provider,
    get_provider_metadata,
    is_vertex_ai_endpoint,
    get_or_detect_provider,
    reset_provider_cache,
    GoogleAIEndpoint,
)

__all__ = [
    # Middleware functions
    "extract_google_ai_usage_data",
    "create_google_ai_metering_call",
    "handle_streaming_response",
    # Provider functions
    "detect_provider",
    "get_provider_metadata",
    "is_vertex_ai_endpoint",
    "get_or_detect_provider",
    "reset_provider_cache",
    "GoogleAIEndpoint",
]
