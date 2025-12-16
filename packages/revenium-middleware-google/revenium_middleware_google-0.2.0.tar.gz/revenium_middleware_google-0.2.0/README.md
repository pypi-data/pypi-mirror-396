# Revenium Middleware for Google AI (Python)

[![PyPI version](https://img.shields.io/pypi/v/revenium-middleware-google.svg)](https://pypi.org/project/revenium-middleware-google/)
[![Python Versions](https://img.shields.io/pypi/pyversions/revenium-middleware-google.svg)](https://pypi.org/project/revenium-middleware-google/)
[![Documentation](https://img.shields.io/badge/docs-revenium.io-blue)](https://docs.revenium.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[//]: # ([![Build Status]&#40;https://github.com/revenium/revenium-middleware-google/actions/workflows/ci.yml/badge.svg&#41;]&#40;https://github.com/revenium/revenium-middleware-google/actions&#41;)

A middleware library for metering and monitoring Google AI services usage in Python applications. Supports both Google AI SDK (Gemini Developer API) and Vertex AI SDK with flexible optional dependencies.

**For complete examples and setup instructions, see [`examples/README.md`](https://github.com/revenium/revenium-middleware-google-python/blob/HEAD/examples/README.md)**

## Features

- **Precise Usage Tracking**: Monitor tokens, costs, and request counts for Google AI services
- **Seamless Integration**: Drop-in middleware that works with minimal code changes
- **Dual SDK Support**: Choose between Google AI SDK or Vertex AI SDK based on your needs
- **Optional Dependencies**: Install only the SDK components you need
- **Streaming Support**: Full support for streaming responses (both SDKs)
- **Enhanced Token Counting**: Complete token tracking including embeddings (Vertex AI)
- **Flexible Configuration**: Customize metering behavior to suit your application needs

## What's Supported

| Feature | Google AI SDK | Vertex AI SDK |
|---------|---------------|---------------|
| **Chat Completion** | Full support | Full support |
| **Streaming** | Full support | Full support |
| **Text Embeddings** | Basic support* | Full support |
| **Token Metering** | Chat/Streaming | All operations |
| **Metadata Tracking** | Full support | Full support |
| **Setup Complexity** | Simple (API key) | Moderate (GCP project) |

**Note**: *Google AI SDK embeddings don't return token counts due to API limitations, but requests are still tracked.

## Installation

Choose the SDK variant that best fits your needs:

```bash
# Google AI SDK only (Gemini Developer API)
pip install "revenium-middleware-google[genai]"

# Vertex AI SDK only (recommended for production)
pip install "revenium-middleware-google[vertex]"

# Both SDKs (maximum flexibility)
pip install "revenium-middleware-google[all]"
```

### Which SDK Should I Choose?

| Use Case | Recommended SDK | Why |
|----------|----------------|-----|
| **Quick prototyping** | Google AI SDK | Simple API key setup, but does NOT support token counts on embeddings |
| **Production applications** | Vertex AI SDK | Full token counting, enterprise features |
| **Embeddings-heavy workloads** | Vertex AI SDK | Complete token tracking for embeddings |
| **Enterprise/GCP environments** | Vertex AI SDK | Advanced Google Cloud integration |
| **Simple chat applications** | Either SDK | Both provide full chat support |

**Recommendation**: Use Vertex AI SDK for production applications that need comprehensive token counting and advanced features.

## Quick Start

### 1. Create Project Directory

```bash
mkdir my-google-ai-project
cd my-google-ai-project
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install the Package

```bash
# Install with both SDKs (recommended)
pip install "revenium-middleware-google[all]" python-dotenv
```

### 4. Configure Environment Variables

Create a `.env` file in your project directory:

```bash
# Required
REVENIUM_METERING_API_KEY=hak_your_revenium_api_key

# For Google AI SDK (Gemini Developer API)
GOOGLE_API_KEY=your_google_api_key

# For Vertex AI SDK (Google Cloud)
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
GOOGLE_CLOUD_LOCATION=us-central1

# Optional
# REVENIUM_LOG_LEVEL=DEBUG
```

**For Vertex AI:** Authenticate with Google Cloud:
```bash
gcloud auth application-default login
```

### 5. Run Your First Example

Download and run an example from the repository:

```bash
# For Google AI SDK
curl -O https://raw.githubusercontent.com/revenium/revenium-middleware-google-python/main/examples/getting_started_google_ai.py
python getting_started_google_ai.py

# For Vertex AI SDK
curl -O https://raw.githubusercontent.com/revenium/revenium-middleware-google-python/main/examples/getting_started_vertex_ai.py
python getting_started_vertex_ai.py
```

Or create a file `test.py` with this simple code:

```python
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import revenium_middleware_google
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="Hello! Introduce yourself in one sentence."
)
print(response.text)
```

Run it:

```bash
python test.py
```

The middleware automatically tracks your Google AI usage and sends data to Revenium.

**For complete examples and usage patterns, see [`examples/README.md`](https://github.com/revenium/revenium-middleware-google-python/blob/HEAD/examples/README.md).**

---

## Usage

Simply import the middleware and your Google AI calls will be metered automatically:

```python
import revenium_middleware_google
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="Hello! Introduce yourself in one sentence."
)
print(response.text)
```

The middleware automatically meters all Google AI and Vertex AI calls. For production use, add metadata tracking to associate usage with organizations, users, or features.

**For complete examples, see:**
- [`examples/getting_started_google_ai.py`](https://github.com/revenium/revenium-middleware-google-python/blob/HEAD/examples/getting_started_google_ai.py) - Minimal Google AI SDK example with metadata fields documented
- [`examples/getting_started_vertex_ai.py`](https://github.com/revenium/revenium-middleware-google-python/blob/HEAD/examples/getting_started_vertex_ai.py) - Minimal Vertex AI SDK example
- [`examples/simple_test.py`](https://github.com/revenium/revenium-middleware-google-python/blob/HEAD/examples/simple_test.py) - Comprehensive test suite with metadata tracking
- [`examples/simple_streaming_test.py`](https://github.com/revenium/revenium-middleware-google-python/blob/HEAD/examples/simple_streaming_test.py) - Complete streaming examples
- [`examples/simple_embeddings_test.py`](https://github.com/revenium/revenium-middleware-google-python/blob/HEAD/examples/simple_embeddings_test.py) - Text embeddings examples
- [`examples/README.md`](https://github.com/revenium/revenium-middleware-google-python/blob/HEAD/examples/README.md) - Complete examples documentation

## Configuration

For detailed configuration options, environment variables, and advanced setup, see the [Configuration section in examples/README.md](https://github.com/revenium/revenium-middleware-google-python/blob/HEAD/examples/README.md#configuration)

## Metadata Fields

Add business context to track usage by organization, user, task type, or custom fields. Pass a `usage_metadata` dictionary with any of these optional fields:

| Field | Description | Use Case |
|-------|-------------|----------|
| `trace_id` | Unique identifier for session or conversation tracking | Link multiple API calls together for debugging, user session analytics, or distributed tracing across services |
| `task_type` | Type of AI task being performed | Categorize usage by workload (e.g., "chat", "code-generation", "doc-summary") for cost analysis and optimization |
| `subscriber.id` | Unique user identifier | Track individual user consumption for billing, rate limiting, or user analytics |
| `subscriber.email` | User email address | Identify users for support, compliance, or usage reports |
| `subscriber.credential.name` | Authentication credential name | Track which API key or service account made the request |
| `subscriber.credential.value` | Authentication credential value | Associate usage with specific credentials for security auditing |
| `organization_id` | Organization or company identifier | Multi-tenant cost allocation, usage quotas per organization |
| `subscription_id` | Subscription plan identifier | Track usage against subscription limits, identify plan upgrade opportunities |
| `product_id` | Your product or feature identifier | Attribute AI costs to specific features in your application (e.g., "chatbot", "email-assistant") |
| `agent` | AI agent or bot identifier | Distinguish between multiple AI agents or automation workflows in your system |
| `response_quality_score` | Custom quality rating (0.0-1.0) | Track user satisfaction or automated quality metrics for model performance analysis |

**Example usage:** See [`examples/getting_started_google_ai.py`](https://github.com/revenium/revenium-middleware-google-python/blob/HEAD/examples/getting_started_google_ai.py) for complete metadata implementation.

**API Reference:** [Complete metadata field documentation](https://revenium.readme.io/reference/meter_ai_completion)

### Trace Visualization Fields (v0.2.0+)

Enhanced observability fields for distributed tracing and analytics. These can be set via environment variables or passed in `usage_metadata`:

| Field | Environment Variable | Description | Use Case |
|-------|---------------------|-------------|----------|
| `environment` | `REVENIUM_ENVIRONMENT` | Deployment environment (e.g., "production", "staging") | Track usage across different deployment environments; auto-detects from `ENVIRONMENT`, `DEPLOYMENT_ENV` |
| `region` | `REVENIUM_REGION` | Cloud region identifier (e.g., "us-east-1", "eastus") | Multi-region deployment tracking; auto-detects from `AWS_REGION`, `AZURE_REGION`, `GCP_REGION`, `GOOGLE_CLOUD_REGION` |
| `credential_alias` | `REVENIUM_CREDENTIAL_ALIAS` | Human-readable API key name (e.g., "prod-google-key") | Track which credential was used for credential rotation and security auditing |
| `trace_type` | `REVENIUM_TRACE_TYPE` | Workflow category identifier (max 128 chars) | Group similar workflows (e.g., "customer-support", "data-analysis") for analytics |
| `trace_name` | `REVENIUM_TRACE_NAME` | Human-readable trace label (max 256 chars) | Label trace instances (e.g., "Customer Support Chat", "Document Analysis") |
| `parent_transaction_id` | `REVENIUM_PARENT_TRANSACTION_ID` | Parent transaction ID for distributed tracing | Link child operations to parent transactions across services |
| `transaction_name` | `REVENIUM_TRANSACTION_NAME` | Human-friendly operation name | Label individual operations (e.g., "Generate Response", "Analyze Sentiment") |

**Note:** `operation_type` and `operation_subtype` are automatically detected by the middleware based on the API method and request parameters.

**Resources:**
- [API Reference](https://revenium.readme.io/reference/meter_ai_completion) - Complete metadata field documentation
- [`.env.example`](.env.example) - Environment variable configuration examples
- [`examples/trace_visualization_example.py`](examples/trace_visualization_example.py) - Comprehensive trace visualization examples

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **"No module named 'google.genai'"** | Install with Google AI support: `pip install "revenium-middleware-google[genai]"` |
| **"No module named 'vertexai'"** | Install with Vertex AI support: `pip install "revenium-middleware-google[vertex]"` |
| **Vertex AI authentication errors** | Verify Google Cloud credentials: `gcloud auth application-default login` |
| **"Project not found" errors** | Ensure `GOOGLE_CLOUD_PROJECT` is set correctly |
| **Embeddings showing 0 tokens** | Expected with Google AI SDK; use Vertex AI for full token counting |
| **Requests not being tracked** | Ensure middleware is imported before Google AI/Vertex AI SDKs |

### Debug Mode

Enable debug logging to see provider detection and routing decisions:

```bash
# export REVENIUM_LOG_LEVEL=DEBUG
python your_script.py
```

### Force Specific SDK

To ensure only one SDK is used:

```bash
# Use only Google AI SDK
pip install "revenium-middleware-google[genai]"

# Use only Vertex AI SDK
pip install "revenium-middleware-google[vertex]"
```

### Google AI SDK Troubleshooting

**Middleware not tracking requests:**
- Ensure middleware is imported before Google AI SDK
- Check that environment variables are loaded correctly
- Verify your `REVENIUM_METERING_API_KEY` is correct

**Embeddings showing 0 tokens:**
- This is expected due to Google AI SDK limitations
- Model name and metadata are still tracked correctly
- Chat and streaming operations provide full token data

### Vertex AI SDK Troubleshooting

**Authentication issues:**
- Verify Google Cloud credentials: `gcloud auth list`
- Check project access: `gcloud projects describe YOUR_PROJECT_ID`
- Ensure service account has required permissions

**Model not available errors:**
- Check if models are available in your region
- Verify Vertex AI API is enabled in your project
- Try a different model or region

## Logging

Control logging with the `REVENIUM_LOG_LEVEL` environment variable in your `.env` file:

```bash
# Add to your .env file
REVENIUM_LOG_LEVEL=DEBUG
```

Available log levels:
- `DEBUG`: Detailed debugging information (shows provider detection, routing decisions, token counts)
- `INFO`: General information messages (default)
- `WARNING`: Warning messages only
- `ERROR`: Error messages only
- `CRITICAL`: Critical error messages only

## Compatibility

- Python 3.8+
- Google AI SDK (`google-genai>=0.1.0`) or Vertex AI SDK (`google-cloud-aiplatform>=1.0.0`)
- Google Cloud Project (for Vertex AI SDK)

## Supported Models

The middleware automatically works with **all Google AI models** available through both SDKs, including:

- **Gemini models** (all versions and variants)
- **Text embedding models** (all versions)
- **Future model releases** (automatic support with no code changes required)

The middleware detects and meters any model supported by the Google AI SDK or Vertex AI SDK. When Google releases new models, they work immediately without updates to the middleware.

## Documentation

For detailed documentation, visit [docs.revenium.io](https://docs.revenium.io)

## Contributing

See [CONTRIBUTING.md](https://github.com/revenium/revenium-middleware-google-python/blob/HEAD/CONTRIBUTING.md)

## Code of Conduct

See [CODE_OF_CONDUCT.md](https://github.com/revenium/revenium-middleware-google-python/blob/HEAD/CODE_OF_CONDUCT.md)

## Security

See [SECURITY.md](https://github.com/revenium/revenium-middleware-google-python/blob/HEAD/SECURITY.md)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/revenium/revenium-middleware-google-python/blob/HEAD/LICENSE) file for details.

## Support

For issues, feature requests, or contributions:

- **Website**: [www.revenium.ai](https://www.revenium.ai)
- **GitHub Repository**: [revenium/revenium-middleware-google-python](https://github.com/revenium/revenium-middleware-google-python)
- **Issues**: [Report bugs or request features](https://github.com/revenium/revenium-middleware-google-python/issues)
- **Documentation**: [docs.revenium.io](https://docs.revenium.io)
- **Email**: support@revenium.io

---

**Built by Revenium**
