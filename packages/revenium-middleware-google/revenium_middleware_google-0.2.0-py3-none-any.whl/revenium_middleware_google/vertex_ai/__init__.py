"""
Vertex AI SDK middleware for Revenium.

This module provides middleware for the native Vertex AI SDK (vertexai package),
offering enhanced features like comprehensive token counting and local tokenization.

Key advantages:
- Full token counting support including embeddings
- Local tokenization capabilities
- Enhanced metadata and usage tracking
- Better integration with Google Cloud services
"""

# Import middleware components to activate them
from . import middleware
from . import provider

# Export key functions for external use
from .middleware import (
    extract_vertex_ai_usage_data,
    extract_vertex_ai_generation_tokens,
    extract_vertex_ai_embedding_tokens,
    create_vertex_ai_metering_call,
    handle_vertex_ai_streaming_response,
)

from .provider import (
    detect_provider,
    get_provider_metadata,
    validate_vertex_ai_configuration,
    get_vertex_ai_config,
    is_vertex_ai_available,
)

__all__ = [
    # Middleware functions
    "extract_vertex_ai_usage_data",
    "extract_vertex_ai_generation_tokens",
    "extract_vertex_ai_embedding_tokens",
    "create_vertex_ai_metering_call",
    "handle_vertex_ai_streaming_response",
    # Provider functions
    "detect_provider",
    "get_provider_metadata",
    "validate_vertex_ai_configuration",
    "get_vertex_ai_config",
    "is_vertex_ai_available",
]
