"""
Vertex AI SDK middleware for Revenium.

This module provides middleware for the native Vertex AI SDK (vertexai package),
offering enhanced features like comprehensive token counting and local tokenization.

Key advantages over Google AI SDK:
- Full token counting support including embeddings
- Local tokenization capabilities
- Enhanced metadata and usage tracking
- Better integration with Google Cloud services
"""

import datetime
import logging
from typing import Dict, Any, Optional, List

import wrapt
from revenium_middleware import run_async_in_thread

# Import common utilities and types
from ..common import (
    OperationType,
    ProviderMetadata,
    UsageData,
    TokenCounts,
    normalize_stop_reason,
    Provider,
    create_metering_call,
    create_usage_data,
    extract_model_name,
    extract_token_counts,
    StreamingError,
    handle_metering_error,
    safe_getattr,
)

# Vertex AI specific imports
from .provider import detect_provider, get_provider_metadata

logger = logging.getLogger("revenium_middleware.extension")


def extract_vertex_ai_usage_data(
    response: Any,
    operation_type: OperationType,
    request_time: datetime.datetime,
    response_time: datetime.datetime,
    model_name_fallback: Optional[str] = None,
) -> UsageData:
    """
    Extract usage data from Vertex AI API responses.

    This function handles the enhanced features of the Vertex AI SDK,
    particularly the comprehensive token counting for all operations.
    """
    # Get provider metadata for Vertex AI
    provider_metadata = ProviderMetadata.for_vertex_ai_sdk()

    # Extract model name - Vertex AI specific logic
    model_name = None

    # First try Vertex AI specific fields
    if hasattr(response, "_raw_response") and response._raw_response:
        raw_response = response._raw_response
        if hasattr(raw_response, "model_version") and raw_response.model_version:
            model_name = raw_response.model_version
            logger.debug(
                f"Extracted model name from Vertex AI _raw_response.model_version: {model_name}"
            )

    # Fallback to common extraction if not found
    if not model_name:
        model_name = extract_model_name(response, model_name_fallback)

    # Use fallback if still not found
    if not model_name:
        model_name = model_name_fallback or "unknown-model"

    # Clean up model name - remove Google's path prefixes
    if model_name and isinstance(model_name, str):
        # Remove common Google path prefixes
        prefixes_to_remove = [
            "publishers/google/models/",
            "models/",
            "google/models/",
            "projects/",
        ]
        for prefix in prefixes_to_remove:
            if model_name.startswith(prefix):
                model_name = model_name[len(prefix) :]
                logger.debug(
                    f"Cleaned model name, removed prefix '{prefix}': {model_name}"
                )
                break

    # Extract token counts with Vertex AI specific handling
    if operation_type == OperationType.EMBED:
        # Vertex AI SDK provides token counts for embeddings!
        token_counts = extract_vertex_ai_embedding_tokens(response)
        stop_reason = "END"  # Embeddings always complete successfully
        logger.debug(
            f"Vertex AI embeddings token usage: {token_counts.total_tokens} tokens"
        )
    else:  # CHAT
        # Extract usage metadata from Vertex AI response
        token_counts = extract_vertex_ai_generation_tokens(response)

        # Determine finish reason from candidates
        vertex_finish_reason = None
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "finish_reason"):
                vertex_finish_reason = candidate.finish_reason
                logger.debug(
                    f" Raw vertex_finish_reason: {vertex_finish_reason} (type: {type(vertex_finish_reason)})"
                )

                # Convert enum to string if needed
                if hasattr(vertex_finish_reason, "name"):
                    vertex_finish_reason = vertex_finish_reason.name
                    logger.debug(f" Converted enum to string: {vertex_finish_reason}")
                elif not isinstance(vertex_finish_reason, str):
                    vertex_finish_reason = str(vertex_finish_reason)
                    logger.debug(f" Converted to string: {vertex_finish_reason}")

        stop_reason = normalize_stop_reason(
            vertex_finish_reason, Provider.VERTEX_AI_SDK
        )
        logger.debug(f" Final stop_reason after normalization: {stop_reason}")
        logger.debug(
            f"Vertex AI chat token usage: prompt={token_counts.input_tokens}, "
            f"candidates={token_counts.output_tokens}, total={token_counts.total_tokens}"
        )

    # Create standardized UsageData
    return UsageData.create(
        operation_type=operation_type,
        input_tokens=token_counts.input_tokens,
        output_tokens=token_counts.output_tokens,
        total_tokens=token_counts.total_tokens,
        model=model_name,
        provider_metadata=provider_metadata,
        stop_reason=stop_reason,
        request_time=request_time,
        response_time=response_time,
        cache_creation_token_count=token_counts.cached_tokens,
    )


def extract_vertex_ai_generation_tokens(response: Any) -> TokenCounts:
    """
    Extract token counts from Vertex AI generation responses.

    Vertex AI provides comprehensive token counting in the usage_metadata.
    """
    token_counts = TokenCounts(
        input_tokens=0, output_tokens=0, total_tokens=0, cached_tokens=0
    )

    if hasattr(response, "usage_metadata") and response.usage_metadata:
        usage_metadata = response.usage_metadata

        # Vertex AI uses different attribute names than Google AI SDK
        token_counts.input_tokens = getattr(usage_metadata, "prompt_token_count", 0)
        token_counts.output_tokens = getattr(
            usage_metadata, "candidates_token_count", 0
        )
        token_counts.total_tokens = getattr(
            usage_metadata,
            "total_token_count",
            token_counts.input_tokens + token_counts.output_tokens,
        )

        # Vertex AI may provide cached token counts
        token_counts.cached_tokens = getattr(
            usage_metadata, "cached_content_token_count", 0
        )
    else:
        logger.warning("No usage metadata found in Vertex AI generation response")

    return token_counts


def extract_vertex_ai_embedding_tokens(response: Any) -> TokenCounts:
    """
    Extract token counts from Vertex AI embedding responses.

    This is a key advantage of Vertex AI SDK - embeddings include token counts!
    """
    token_counts = TokenCounts(
        input_tokens=0, output_tokens=0, total_tokens=0, cached_tokens=0
    )

    # Vertex AI embeddings response is a list of TextEmbedding objects
    if isinstance(response, list) and len(response) > 0:
        # Get the first embedding object
        first_embedding = response[0]

        # Check if it has statistics with token_count
        if hasattr(first_embedding, "statistics") and first_embedding.statistics:
            stats = first_embedding.statistics
            if hasattr(stats, "token_count"):
                # Convert to int if it's a float
                token_count = (
                    int(stats.token_count)
                    if hasattr(stats.token_count, "__int__")
                    else stats.token_count
                )
                token_counts.input_tokens = token_count
                token_counts.total_tokens = token_count
                # Embeddings don't generate output tokens
                token_counts.output_tokens = 0
                logger.debug(
                    f"Extracted token count from Vertex AI embedding statistics: {token_count}"
                )
                return token_counts

        # Check if the embedding has _prediction_response with metadata
        if (
            hasattr(first_embedding, "_prediction_response")
            and first_embedding._prediction_response
        ):
            pred_response = first_embedding._prediction_response
            if hasattr(pred_response, "metadata") and pred_response.metadata:
                # Check for billableCharacterCount or other token-related fields
                metadata = pred_response.metadata
                if hasattr(metadata, "billableCharacterCount"):
                    # Use billable character count as a proxy for tokens
                    char_count = metadata.billableCharacterCount
                    # Rough approximation: 4 characters per token (common for many tokenizers)
                    estimated_tokens = max(1, int(char_count / 4))
                    token_counts.input_tokens = estimated_tokens
                    token_counts.total_tokens = estimated_tokens
                    token_counts.output_tokens = 0
                    logger.debug(
                        f"Estimated token count from billable characters: {char_count} chars -> {estimated_tokens} tokens"
                    )
                    return token_counts

    # Fallback: check if response itself has statistics or usage_metadata
    elif hasattr(response, "statistics") and response.statistics:
        # Some Vertex AI embedding responses have statistics
        stats = response.statistics
        if hasattr(stats, "token_count"):
            token_counts.input_tokens = stats.token_count
            token_counts.total_tokens = stats.token_count
            # Embeddings don't generate output tokens
            token_counts.output_tokens = 0
    elif hasattr(response, "usage_metadata") and response.usage_metadata:
        # Alternative location for token counts
        usage_metadata = response.usage_metadata
        token_counts.input_tokens = getattr(usage_metadata, "prompt_token_count", 0)
        token_counts.total_tokens = getattr(
            usage_metadata, "total_token_count", token_counts.input_tokens
        )
        token_counts.output_tokens = 0  # Embeddings don't generate output
    else:
        # If no token counts available, log warning
        logger.debug("No token counts found in Vertex AI embedding response")

    return token_counts


def create_vertex_ai_metering_call(
    response: Any,
    operation_type: OperationType,
    request_time_dt: datetime.datetime,
    usage_metadata: Dict[str, Any],
    time_to_first_token: int = 0,
    is_streamed: bool = False,
    model_name_fallback: Optional[str] = None,
) -> None:
    """
    Create and execute a metering call for Vertex AI SDK responses.

    This is the main function used by the wrapper functions.
    """
    # Record response timing
    response_time_dt = datetime.datetime.now(datetime.timezone.utc)

    # Extract usage data using Vertex AI specific logic
    usage_data = extract_vertex_ai_usage_data(
        response=response,
        operation_type=operation_type,
        request_time=request_time_dt,
        response_time=response_time_dt,
        model_name_fallback=model_name_fallback,
    )

    # Create metering call using common utilities
    create_metering_call(
        usage_data=usage_data,
        usage_metadata=usage_metadata,
        time_to_first_token=time_to_first_token,
        is_streamed=is_streamed,
    )


# Dynamic wrapper discovery and application for Vertex AI GenerativeModel.generate_content
def _apply_generate_content_wrappers():
    """
    Dynamically discover and wrap all Vertex AI GenerativeModel.generate_content methods.
    This handles current and future module path variations like:
    - vertexai.generative_models.GenerativeModel
    - vertexai.preview.generative_models.GenerativeModel
    - vertexai.v1.generative_models.GenerativeModel
    - etc.
    """
    import sys
    import importlib

    # Known module patterns to try
    module_patterns = [
        "vertexai.generative_models",
        "vertexai.preview.generative_models",
        "vertexai.v1.generative_models",
        "vertexai.v1beta1.generative_models",
        "vertexai.v2.generative_models",
        "vertexai.beta.generative_models",
        "vertexai.alpha.generative_models",
    ]

    wrapped_modules = []

    for module_path in module_patterns:
        try:
            # Try to import the module
            module = importlib.import_module(module_path)

            # Check if GenerativeModel class exists
            if hasattr(module, "GenerativeModel"):
                generative_model_class = getattr(module, "GenerativeModel")

                # Check if generate_content method exists
                if hasattr(generative_model_class, "generate_content"):
                    logger.debug(
                        f"Found GenerativeModel.generate_content in {module_path}"
                    )

                    # Apply wrapper using wrapt
                    @wrapt.patch_function_wrapper(
                        module_path, "GenerativeModel.generate_content"
                    )
                    def generate_content_wrapper_dynamic(
                        wrapped, instance, args, kwargs
                    ):
                        return generate_content_wrapper_impl(
                            wrapped, instance, args, kwargs
                        )

                    wrapped_modules.append(module_path)
                    logger.debug(
                        f" Applied wrapper to {module_path}.GenerativeModel.generate_content"
                    )
                else:
                    logger.debug(
                        f"  {module_path}.GenerativeModel exists but no generate_content method"
                    )
            else:
                logger.debug(f"  {module_path} exists but no GenerativeModel class")

        except ImportError:
            logger.debug(f"  Module {module_path} not available")
        except Exception as e:
            logger.debug(f"  Error checking {module_path}: {e}")

    if wrapped_modules:
        logger.info(
            f" Vertex AI GenerativeModel wrappers applied to: {', '.join(wrapped_modules)}"
        )
    else:
        logger.warning("  No Vertex AI GenerativeModel modules found to wrap")

    return wrapped_modules


def generate_content_wrapper_impl(wrapped, instance, args, kwargs):
    """Enhanced wrapper that handles both streaming and non-streaming Vertex AI calls."""
    logger.debug("Enhanced Vertex AI generate_content wrapper called!")
    logger.debug(f"Wrapper args: {args}")
    logger.debug(f"Wrapper kwargs: {kwargs}")
    logger.debug(f"Instance type: {type(instance)}")

    # Extract usage metadata from instance or kwargs
    usage_metadata = getattr(instance, "_revenium_usage_metadata", {}) or kwargs.pop(
        "usage_metadata", {}
    )
    logger.debug(f"Captured usage metadata for generate_content: {usage_metadata}")
    logger.debug(
        f"Instance has _revenium_usage_metadata: {hasattr(instance, '_revenium_usage_metadata')}"
    )
    if hasattr(instance, "_revenium_usage_metadata"):
        logger.debug(
            f"Instance._revenium_usage_metadata value: {getattr(instance, '_revenium_usage_metadata')}"
        )

    # Try to extract model name from the instance
    model_name_from_instance = None
    for attr in [
        "_model_name",
        "model_name",
        "_model_id",
        "model_id",
        "_model",
        "model",
    ]:
        if hasattr(instance, attr):
            model_name_from_instance = getattr(instance, attr)
            logger.debug(
                f"Found model name in instance.{attr}: {model_name_from_instance}"
            )
            break

    # Clean up the instance model name too
    if model_name_from_instance and isinstance(model_name_from_instance, str):
        # Remove common Google path prefixes
        prefixes_to_remove = [
            "publishers/google/models/",
            "models/",
            "google/models/",
            "projects/",
        ]
        for prefix in prefixes_to_remove:
            if model_name_from_instance.startswith(prefix):
                model_name_from_instance = model_name_from_instance[len(prefix) :]
                logger.debug(
                    f"Cleaned instance model name, removed prefix '{prefix}': {model_name_from_instance}"
                )
                break

    if not model_name_from_instance:
        logger.debug(
            f"Could not find model name in instance. Available attributes: {dir(instance)}"
        )
        # Try to get it from the instance string representation
        instance_str = str(instance)
        if "model_name=" in instance_str:
            # Extract from string like "GenerativeModel(model_name='gemini-2.0-flash-lite-001')"
            import re

            match = re.search(r"model_name='([^']+)'", instance_str)
            if match:
                model_name_from_instance = match.group(1)
                logger.debug(
                    f"Extracted model name from instance string: {model_name_from_instance}"
                )
        elif "models/" in instance_str:
            # Extract from string like "models/gemini-2.0-flash-lite-001"
            import re

            match = re.search(r"models/([^'\s)]+)", instance_str)
            if match:
                model_name_from_instance = match.group(1)
                logger.debug(
                    f"Extracted model name from instance string (models/): {model_name_from_instance}"
                )

    # Check if this is a streaming call
    is_streaming = kwargs.get("stream", False)

    # Record request time
    request_time_dt = datetime.datetime.now(datetime.timezone.utc)
    logger.debug(
        f"Calling wrapped Vertex AI generate_content function (streaming={is_streaming}) with args: {args}, kwargs: {kwargs}"
    )

    # Call the original Vertex AI function
    response = wrapped(*args, **kwargs)

    if is_streaming:
        logger.debug("Handling Vertex AI streaming response")
        # Return wrapped stream that will meter usage when complete
        return handle_vertex_ai_streaming_response(
            stream=response,
            request_time_dt=request_time_dt,
            usage_metadata=usage_metadata,
            model_name_fallback=model_name_from_instance,
        )
    else:
        logger.debug("Handling Vertex AI non-streaming response: %s", response)
        # Handle non-streaming response immediately
        create_vertex_ai_metering_call(
            response=response,
            operation_type=OperationType.CHAT,
            request_time_dt=request_time_dt,
            usage_metadata=usage_metadata,
            model_name_fallback=model_name_from_instance,
        )
        return response


# Wrapper for Vertex AI TextEmbeddingModel.get_embeddings method
@wrapt.patch_function_wrapper(
    "vertexai.language_models", "TextEmbeddingModel.get_embeddings"
)
def get_embeddings_wrapper(wrapped, instance, args, kwargs):
    """Wraps the vertexai.language_models.TextEmbeddingModel.get_embeddings method to log token usage."""
    logger.debug("Vertex AI get_embeddings wrapper called")

    # Extract usage metadata from instance or kwargs
    usage_metadata = getattr(instance, "_revenium_usage_metadata", {}) or kwargs.pop(
        "usage_metadata", {}
    )

    # Try to extract model name from the instance using the same logic as generate_content
    model_name_from_instance = None
    for attr in [
        "_model_name",
        "model_name",
        "_model_id",
        "model_id",
        "_model",
        "model",
    ]:
        if hasattr(instance, attr):
            model_name_from_instance = getattr(instance, attr)
            logger.debug(
                f"Found model name in embeddings instance.{attr}: {model_name_from_instance}"
            )
            break

    if not model_name_from_instance:
        logger.debug(
            f"Could not find model name in embeddings instance. Available attributes: {dir(instance)}"
        )
        # Try to get it from the instance string representation
        instance_str = str(instance)
        if "model_name=" in instance_str:
            # Extract from string like "TextEmbeddingModel(model_name='text-embedding-004')"
            import re

            match = re.search(r"model_name='([^']+)'", instance_str)
            if match:
                model_name_from_instance = match.group(1)
                logger.debug(
                    f"Extracted model name from embeddings instance string: {model_name_from_instance}"
                )
        elif "models/" in instance_str:
            # Extract from string like "models/text-embedding-004"
            import re

            match = re.search(r"models/([^'\s)]+)", instance_str)
            if match:
                model_name_from_instance = match.group(1)
                logger.debug(
                    f"Extracted model name from embeddings instance string (models/): {model_name_from_instance}"
                )

    logger.debug(
        f"Final captured model name from Vertex AI embeddings instance: {model_name_from_instance}"
    )

    # Record request time
    request_time_dt = datetime.datetime.now(datetime.timezone.utc)
    logger.debug(
        f"Calling wrapped Vertex AI get_embeddings function with args: {args}, kwargs: {kwargs}"
    )

    # Call the original Vertex AI function
    response = wrapped(*args, **kwargs)

    logger.debug("Handling Vertex AI get_embeddings response: %s", response)

    # Create metering call for embeddings
    create_vertex_ai_metering_call(
        response=response,
        operation_type=OperationType.EMBED,
        request_time_dt=request_time_dt,
        usage_metadata=usage_metadata,
        model_name_fallback=model_name_from_instance,
    )

    return response


def handle_vertex_ai_streaming_response(
    stream, request_time_dt, usage_metadata, model_name_fallback=None
):
    """
    Handle streaming responses from Vertex AI.
    Wraps the stream to collect metrics and log them after completion.
    """

    class VertexAIStreamWrapper:
        def __init__(self, stream):
            self.stream = stream
            self.chunks = []
            self.model = model_name_fallback
            self.finish_reason = None
            self.usage_metadata = None
            self.first_chunk_time = None
            self._closed = False
            self._usage_logged = False

            # Limit chunk storage to prevent memory issues
            self._max_chunks = 1000

        def __iter__(self):
            return self

        def __next__(self):
            if self._closed:
                raise StopIteration("Stream has been closed")

            try:
                chunk = next(self.stream)
                self._process_chunk(chunk)
                return chunk
            except StopIteration:
                self._finalize()
                raise
            except Exception as e:
                self._handle_error(e)
                raise

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()
            return False  # Don't suppress exceptions

        def close(self):
            """Properly close the stream and clean up resources."""
            if not self._closed:
                self._closed = True
                if not self._usage_logged:
                    try:
                        self._log_usage()
                    except Exception as e:
                        logger.error(
                            "Error logging usage during Vertex AI stream cleanup: %s", e
                        )

                # Clear chunks to free memory
                self.chunks.clear()

                # Close underlying stream if it has a close method
                if hasattr(self.stream, "close"):
                    try:
                        self.stream.close()
                    except Exception as e:
                        logger.debug("Error closing underlying Vertex AI stream: %s", e)

        def _finalize(self):
            """Finalize the stream and log usage."""
            if not self._usage_logged:
                self._log_usage()
                self._usage_logged = True

        def _handle_error(self, error: Exception):
            """Handle errors during streaming."""
            logger.error("Error in Vertex AI streaming response: %s", error)
            if not self._usage_logged:
                # Try to log partial usage data
                try:
                    self._log_usage()
                    self._usage_logged = True
                except Exception as log_error:
                    logger.error(
                        "Failed to log Vertex AI usage after stream error: %s",
                        log_error,
                    )

        def _process_chunk(self, chunk):
            """Process each chunk to extract metadata"""
            # Limit chunk storage to prevent memory issues
            if len(self.chunks) < self._max_chunks:
                self.chunks.append(chunk)
            elif len(self.chunks) == self._max_chunks:
                logger.warning(
                    "Reached maximum chunk limit (%d) for Vertex AI stream, not storing additional chunks",
                    self._max_chunks,
                )

            # Record time of first chunk
            if self.first_chunk_time is None:
                self.first_chunk_time = datetime.datetime.now(datetime.timezone.utc)

            # Extract model name from chunk if available using safe access
            if self.model is None:
                self.model = extract_model_name(chunk, self.model)

            # Check for finish reason and usage metadata in the chunk using safe access
            candidates = safe_getattr(chunk, "candidates")
            if candidates and len(candidates) > 0:
                candidate = candidates[0]
                finish_reason = safe_getattr(candidate, "finish_reason")
                if finish_reason:
                    self.finish_reason = finish_reason

            # Check for usage metadata in the chunk (final chunk typically has this)
            usage_metadata = safe_getattr(chunk, "usage_metadata")
            if usage_metadata:
                self.usage_metadata = usage_metadata

        def _log_usage(self):
            """Log usage after stream completion"""
            try:
                if not self.chunks:
                    logger.warning("No chunks received in Vertex AI streaming response")
                    return

                # Calculate time to first token
                time_to_first_token = 0
                if self.first_chunk_time:
                    time_to_first_token = int(
                        (self.first_chunk_time - request_time_dt).total_seconds() * 1000
                    )

                # Create a synthetic response object for usage extraction
                class SyntheticResponse:
                    def __init__(self, model_name, usage_metadata, candidates):
                        self.model_name = model_name
                        self.usage_metadata = usage_metadata
                        self.candidates = candidates

                # Create synthetic response from collected data
                synthetic_response = SyntheticResponse(
                    model_name=self.model,
                    usage_metadata=self.usage_metadata,
                    candidates=(
                        [
                            type(
                                "obj", (object,), {"finish_reason": self.finish_reason}
                            )()
                        ]
                        if self.finish_reason
                        else []
                    ),
                )

                # Create metering call for streaming response
                create_vertex_ai_metering_call(
                    response=synthetic_response,
                    operation_type=OperationType.CHAT,
                    request_time_dt=request_time_dt,
                    usage_metadata=usage_metadata,
                    time_to_first_token=time_to_first_token,
                    is_streamed=True,
                    model_name_fallback=self.model,
                )

                logger.debug(
                    "Vertex AI streaming usage logged: model=%s, chunks=%d, time_to_first_token=%dms",
                    self.model,
                    len(self.chunks),
                    time_to_first_token,
                )

            except Exception as e:
                # Don't let logging errors break the stream
                logger.error("Error logging Vertex AI streaming usage: %s", e)
                raise StreamingError(
                    f"Failed to log Vertex AI streaming usage: {str(e)}",
                    chunk_count=len(self.chunks) if self.chunks else 0,
                    stream_state="completed",
                ) from e

    return VertexAIStreamWrapper(stream)


# Apply the dynamic wrappers when this module is imported
try:
    _apply_generate_content_wrappers()
except Exception as e:
    logger.error(f"Failed to apply dynamic Vertex AI wrappers: {e}")
