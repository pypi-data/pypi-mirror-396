"""
Common utilities for Google AI middleware.

This module contains shared functionality used by both Google AI SDK
and Vertex AI SDK middleware implementations.
"""

import datetime
import logging
import os
import uuid
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from revenium_middleware import client, run_async_in_thread, shutdown_event

from .types import UsageData, OperationType, ProviderMetadata, TokenCounts
from .exceptions import MeteringError, APIResponseError, safe_extract
from .protocols import has_token_counts, safe_getattr, get_token_count
from . import trace_fields

logger = logging.getLogger("revenium_middleware.extension")


def ensure_meter_in_url(base_url: Optional[str] = None) -> str:
    """
    Ensure the URL contains /meter path segment.

    Intelligently handles various URL formats that users might provide:
    - Plain base URL: https://api.revenium.ai → https://api.revenium.ai/meter
    - With /meter: https://api.revenium.ai/meter → https://api.revenium.ai/meter
    - With /meter/v2: https://api.revenium.ai/meter/v2 → https://api.revenium.ai/meter
    - With trailing slash: https://api.revenium.ai/ → https://api.revenium.ai/meter

    The /meter path is then followed by /v2/ai/completions when making API calls.

    Args:
        base_url: The base URL provided by user or environment variable.
                 If None, uses REVENIUM_METERING_BASE_URL env var.

    Returns:
        str: URL with /meter path segment (no trailing slash)
    """
    if base_url is None:
        base_url = os.environ.get("REVENIUM_METERING_BASE_URL")
    if not base_url or not base_url.strip():
        return "https://api.revenium.ai/meter"

    # Remove trailing slashes
    base_url = base_url.rstrip("/")

    # Parse the URL
    parsed = urlparse(base_url)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc
    path = parsed.path.rstrip("/")

    # If netloc is empty, return default
    if not netloc:
        return "https://api.revenium.ai/meter"

    # Remove version suffixes (/v1, /v2, /v3, /v4, /v5) from path
    if path.endswith(("/v1", "/v2", "/v3", "/v4", "/v5")):
        path = path.rsplit("/", 1)[0]

    # If path already ends with /meter, keep it
    if path.endswith("/meter"):
        return f"{scheme}://{netloc}{path}"

    # Otherwise append /meter
    return f"{scheme}://{netloc}/meter"


def is_debug_logging_enabled() -> bool:
    """
    Check if debug logging is currently enabled for Revenium middleware.

    Returns:
        bool: True if debug logging is enabled, False otherwise
    """
    # Check environment variable first
    log_level_str = os.getenv("REVENIUM_LOG_LEVEL", "INFO").upper()
    if log_level_str == "DEBUG":
        return True

    # Check actual logger level as fallback
    revenium_logger = logging.getLogger("revenium_middleware")
    return revenium_logger.getEffectiveLevel() <= logging.DEBUG


def generate_transaction_id() -> str:
    """Generate a unique transaction ID."""
    return str(uuid.uuid4())


def format_timestamp(dt: datetime.datetime) -> str:
    """Format datetime as ISO string for API calls."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def calculate_duration_ms(
    start_time: datetime.datetime, end_time: datetime.datetime
) -> int:
    """Calculate duration in milliseconds between two timestamps."""
    return int((end_time - start_time).total_seconds() * 1000)


async def log_token_usage(
    transaction_id: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: int,
    cached_tokens: int,
    stop_reason: str,
    request_time: str,
    response_time: str,
    request_duration: int,
    usage_metadata: Dict[str, Any],
    provider: str = "Google",
    model_source: str = "GOOGLE",
    is_streamed: bool = False,
    time_to_first_token: int = 0,
    operation_type: OperationType = OperationType.CHAT,
) -> None:
    """
    Log token usage to Revenium.

    Args:
        transaction_id: Unique identifier for this API call
        model: Model name used for the request
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens
        total_tokens: Total token count
        cached_tokens: Number of cached tokens used
        stop_reason: Reason the generation stopped
        request_time: ISO timestamp of request start
        response_time: ISO timestamp of response completion
        request_duration: Duration in milliseconds
        usage_metadata: Additional metadata for the request
        provider: Provider name (always "Google")
        model_source: Model source (always "GOOGLE")
        is_streamed: Whether this was a streaming response
        time_to_first_token: Time to first token in milliseconds
        operation_type: Type of operation (CHAT or EMBED)
    """
    if shutdown_event.is_set():
        logger.warning("Skipping metering call during shutdown")
        return

    logger.debug(
        "Metering call to Revenium for %s operation %s",
        operation_type.lower(),
        transaction_id,
    )

    # Prepare arguments for create_completion (using snake_case for Python client library)
    completion_args = {
        "cache_creation_token_count": cached_tokens,
        "cache_read_token_count": 0,
        "input_token_cost": None,  # Let backend calculate from model pricing
        "output_token_cost": None,  # Let backend calculate from model pricing
        "total_cost": None,  # Let backend calculate from model pricing
        "output_token_count": completion_tokens,
        "cost_type": "AI",
        "model": model,
        "input_token_count": prompt_tokens,
        "provider": provider,
        "model_source": model_source,
        "reasoning_token_count": 0,
        "request_time": request_time,
        "response_time": response_time,
        "completion_start_time": response_time,
        "request_duration": int(request_duration),
        "stop_reason": stop_reason,
        "total_token_count": total_tokens,
        "transaction_id": transaction_id,
        "is_streamed": is_streamed,
        "operation_type": operation_type.value,  # Convert enum to string
        "time_to_first_token": time_to_first_token,
        "middleware_source": "python",  # Required parameter for Google Python middleware
    }

    # Add optional metadata fields if they exist (using snake_case for Python client)
    if usage_metadata.get("trace_id"):
        completion_args["trace_id"] = usage_metadata.get("trace_id")
    if usage_metadata.get("task_type"):
        completion_args["task_type"] = usage_metadata.get("task_type")
    if usage_metadata.get("organization_id") or usage_metadata.get("organizationId"):
        completion_args["organization_id"] = usage_metadata.get(
            "organization_id"
        ) or usage_metadata.get("organizationId")
    if usage_metadata.get("subscription_id"):
        completion_args["subscription_id"] = usage_metadata.get("subscription_id")
    if usage_metadata.get("product_id"):
        completion_args["product_id"] = usage_metadata.get("product_id")
    if usage_metadata.get("agent"):
        completion_args["agent"] = usage_metadata.get("agent")
    if usage_metadata.get("response_quality_score"):
        completion_args["response_quality_score"] = usage_metadata.get(
            "response_quality_score"
        )

    # Add trace visualization fields (v0.2.0+)
    # These fields support both environment variables and usage_metadata parameters
    # Priority: usage_metadata > environment variable

    # Environment field
    environment = (
        usage_metadata.get("environment") or
        trace_fields.get_environment()
    )
    if environment:
        completion_args["environment"] = environment

    # Region field
    region = (
        usage_metadata.get("region") or
        trace_fields.get_region()
    )
    if region:
        completion_args["region"] = region

    # Credential alias field
    credential_alias = (
        usage_metadata.get("credential_alias") or
        usage_metadata.get("credentialAlias") or
        trace_fields.get_credential_alias()
    )
    if credential_alias:
        completion_args["credential_alias"] = credential_alias

    # Trace type field
    trace_type = (
        usage_metadata.get("trace_type") or
        usage_metadata.get("traceType") or
        trace_fields.get_trace_type()
    )
    if trace_type:
        # Validate if coming from usage_metadata
        if usage_metadata.get("trace_type") or usage_metadata.get("traceType"):
            trace_type = trace_fields.validate_trace_type(trace_type)
        if trace_type:
            completion_args["trace_type"] = trace_type

    # Trace name field
    trace_name = (
        usage_metadata.get("trace_name") or
        usage_metadata.get("traceName") or
        trace_fields.get_trace_name()
    )
    if trace_name:
        # Validate if coming from usage_metadata
        if usage_metadata.get("trace_name") or usage_metadata.get("traceName"):
            trace_name = trace_fields.validate_trace_name(trace_name)
        if trace_name:
            completion_args["trace_name"] = trace_name

    # Parent transaction ID field
    parent_transaction_id = (
        usage_metadata.get("parent_transaction_id") or
        usage_metadata.get("parentTransactionId") or
        trace_fields.get_parent_transaction_id()
    )
    if parent_transaction_id:
        completion_args["parent_transaction_id"] = parent_transaction_id

    # Transaction name field (with fallback to task_type)
    transaction_name = trace_fields.get_transaction_name(usage_metadata)
    if transaction_name:
        completion_args["transaction_name"] = transaction_name

    # Retry number field
    retry_number = trace_fields.get_retry_number()
    if retry_number > 0:
        completion_args["retry_number"] = retry_number

    # Build subscriber object - support both nested and flat formats
    subscriber_data = {}
    flat_keys_used = []

    # Prefer nested format if present (recommended structure)
    if "subscriber" in usage_metadata:
        nested_subscriber = usage_metadata["subscriber"]
        if isinstance(nested_subscriber, dict):
            # Use nested structure directly
            subscriber_data = nested_subscriber.copy()
            logger.debug("Using nested subscriber format (recommended)")
    else:
        # Fall back to flat keys for backward compatibility
        subscriber_id = usage_metadata.get("subscriber_id")
        subscriber_email = usage_metadata.get("subscriber_email")
        credential_name = usage_metadata.get("subscriber_credential_name")
        credential_value = usage_metadata.get("subscriber_credential")

        if subscriber_id:
            subscriber_data["id"] = subscriber_id
            flat_keys_used.append("subscriber_id")
        if subscriber_email:
            subscriber_data["email"] = subscriber_email
            flat_keys_used.append("subscriber_email")

        # Add credential sub-object if credential data is provided
        credential_data = {}
        if credential_name:
            credential_data["name"] = credential_name
            flat_keys_used.append("subscriber_credential_name")
        if credential_value:
            credential_data["value"] = credential_value
            flat_keys_used.append("subscriber_credential")

        if credential_data:
            subscriber_data["credential"] = credential_data

        # Log deprecation warning if flat keys were used
        if flat_keys_used:
            logger.warning(
                f"Flat subscriber keys are deprecated: {flat_keys_used}. "
                "Please use nested 'subscriber' object format: "
                "{'subscriber': {'id': '...', 'email': '...', 'credential': {'name': '...', 'value': '...'}}}"
            )

    # Only add subscriber to completion_args if we have subscriber data
    if subscriber_data:
        completion_args["subscriber"] = subscriber_data

    # Log the arguments at debug level
    logger.debug("Calling client.ai.create_completion with args: %s", completion_args)

    # Debug logging for metering call
    logger.debug(
        f"Metering call for {operation_type.value}: {transaction_id}, tokens: {prompt_tokens}+{completion_tokens}={total_tokens}"
    )

    try:
        # The client.ai.create_completion method is not async, so don't use await
        result = client.ai.create_completion(**completion_args)
        logger.debug("Metering call result: %s", result)
        logger.info(" REVENIUM SUCCESS: Metering call successful: %s", result.id)
    except Exception as e:
        if not shutdown_event.is_set():
            # Create a structured error for better handling
            error_details = {
                "transaction_id": transaction_id,
                "model": model,
                "error_type": type(e).__name__,
                "completion_args_keys": list(completion_args.keys()),
            }

            # Log error with structured information
            logger.error(" REVENIUM FAILURE: Error in metering call: %s", str(e))
            logger.error(" REVENIUM FAILURE: Error details: %s", error_details)

            # Log traceback at debug level to avoid spam
            logger.debug("Metering call traceback:", exc_info=True)

            # Raise a specific MeteringError for better error handling upstream
            raise MeteringError(
                f"Failed to send metering data: {str(e)}",
                transaction_id=transaction_id,
                api_response=None,
                error_details=error_details,
            ) from e
        else:
            logger.debug("Metering call failed during shutdown - this is expected")


def create_metering_call(
    usage_data: UsageData,
    usage_metadata: Dict[str, Any],
    time_to_first_token: int = 0,
    is_streamed: bool = False,
) -> None:
    """
    Create and execute a metering call using UsageData.

    This is a higher-level function that uses the standardized UsageData structure.
    """
    # Override streaming and timing info
    usage_data.is_streamed = is_streamed
    usage_data.time_to_first_token = time_to_first_token

    # Create async metering call
    async def metering_call():
        await log_token_usage(
            transaction_id=usage_data.transaction_id,
            model=usage_data.model,
            prompt_tokens=usage_data.input_token_count,  # These are positional parameters
            completion_tokens=usage_data.output_token_count,  # These are positional parameters
            total_tokens=usage_data.total_token_count,  # These are positional parameters
            cached_tokens=usage_data.cache_creation_token_count,
            stop_reason=usage_data.stop_reason,
            request_time=usage_data.request_time,
            response_time=usage_data.response_time,
            request_duration=usage_data.request_duration,
            usage_metadata=usage_metadata,
            provider=usage_data.provider,
            model_source=usage_data.model_source,
            is_streamed=usage_data.is_streamed,
            time_to_first_token=usage_data.time_to_first_token,
            operation_type=OperationType(usage_data.operation_type),
        )

    # Execute in background thread
    run_async_in_thread(metering_call())


@safe_extract
def extract_model_name(response: Any, fallback: Optional[str] = None) -> str:
    """
    Extract model name from API response with fallback.

    Args:
        response: API response object
        fallback: Fallback model name if extraction fails

    Returns:
        Model name string

    Raises:
        TokenExtractionError: If extraction fails and no fallback is provided
    """
    if response is None:
        if fallback:
            logger.debug("Response is None, using fallback model name: %s", fallback)
            return fallback
        raise APIResponseError("Response is None and no fallback model name provided")

    # Try common model name attributes using safe access
    model_attrs = ["model", "model_name", "_model_name", "model_version"]
    for attr in model_attrs:
        model_name = safe_getattr(response, attr)
        if model_name:
            return str(model_name)

    # Try nested model attributes
    usage = safe_getattr(response, "usage")
    if usage:
        model_name = safe_getattr(usage, "model")
        if model_name:
            return str(model_name)

    # Use fallback if provided
    if fallback:
        logger.debug(
            "Could not extract model name from response, using fallback: %s", fallback
        )
        return fallback

    # Log available attributes for debugging
    available_attrs = [attr for attr in dir(response) if not attr.startswith("_")]
    logger.warning(
        "Could not extract model name from response. Available attributes: %s",
        available_attrs[:10],
    )

    return "unknown-model"


@safe_extract
def extract_token_counts(response: Any, operation_type: OperationType) -> TokenCounts:
    """
    Extract token counts from API response.

    This function handles the differences between SDKs and operation types.

    Args:
        response: API response object
        operation_type: Type of operation (CHAT or EMBED)

    Returns:
        TokenCounts object with extracted counts

    Raises:
        TokenExtractionError: If response is invalid
    """
    if response is None:
        logger.warning("Response is None, returning zero token counts")
        return TokenCounts(
            input_tokens=0, output_tokens=0, total_tokens=0, cached_tokens=0
        )

    # Initialize with zeros
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0
    cached_tokens = 0

    # Try to extract from usage_metadata first (Google AI SDK pattern)
    usage = safe_getattr(response, "usage_metadata") or safe_getattr(response, "usage")

    if usage and has_token_counts(usage):
        # Use the utility function for safe token extraction
        input_tokens = get_token_count(
            usage, ["prompt_token_count", "prompt_tokens", "input_tokens"]
        )
        output_tokens = get_token_count(
            usage, ["candidates_token_count", "completion_tokens", "output_tokens"]
        )
        total_tokens = get_token_count(usage, ["total_token_count", "total_tokens"])
        cached_tokens = get_token_count(
            usage, ["cached_content_token_count", "cached_tokens"]
        )

        logger.debug(
            "Extracted token counts from usage: input=%d, output=%d, total=%d, cached=%d",
            input_tokens,
            output_tokens,
            total_tokens,
            cached_tokens,
        )
    else:
        logger.debug("No usage metadata found or no token counts available in response")

    # For embeddings, output tokens are always 0
    if operation_type == OperationType.EMBED:
        output_tokens = 0
        logger.debug("Operation type is EMBED, setting output_tokens to 0")

    # Calculate total if not provided but we have input/output
    if total_tokens == 0 and (input_tokens > 0 or output_tokens > 0):
        total_tokens = input_tokens + output_tokens
        logger.debug(
            "Calculated total_tokens as %d (input=%d + output=%d)",
            total_tokens,
            input_tokens,
            output_tokens,
        )

    return TokenCounts(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        cached_tokens=cached_tokens,
    )


def create_usage_data(
    response: Any,
    operation_type: OperationType,
    provider_metadata: ProviderMetadata,
    request_time: datetime.datetime,
    response_time: datetime.datetime,
    model_name_fallback: Optional[str] = None,
    stop_reason_fallback: str = "END",
) -> UsageData:
    """
    Create standardized UsageData from API response.

    This is the main function for converting SDK-specific responses
    to our common UsageData format.
    """
    # Extract token counts
    token_counts = extract_token_counts(response, operation_type)

    # Extract model name
    model_name = extract_model_name(response, model_name_fallback)

    # Extract stop reason (SDK-specific logic should be handled by caller)
    stop_reason = stop_reason_fallback
    if hasattr(response, "finish_reason"):
        stop_reason = response.finish_reason or stop_reason_fallback
    elif hasattr(response, "candidates") and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, "finish_reason"):
            stop_reason = candidate.finish_reason or stop_reason_fallback

    # Create UsageData
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
