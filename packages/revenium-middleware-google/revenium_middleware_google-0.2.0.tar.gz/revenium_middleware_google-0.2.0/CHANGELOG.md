# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-12-05

### Added
- Trace visualization support with 8 new fields for enhanced observability:
  - `environment` - Deployment environment tracking (production, staging, etc.)
  - `region` - Cloud region identifier with auto-detection from AWS/Azure/GCP env vars
  - `credential_alias` - Human-readable API key identification
  - `trace_type` - Workflow category identifier for grouping (max 128 chars)
  - `trace_name` - Human-readable trace labels (max 256 chars)
  - `parent_transaction_id` - Distributed tracing support for linking operations
  - `transaction_name` - Operation-level naming with fallback to task_type
  - `retry_number` - Retry attempt counter for tracking failed operations
- New `trace_fields.py` module in common package for trace field capture and validation
- Comprehensive trace visualization example (`examples/trace_visualization_example.py`)
- Support for both environment variables and `usage_metadata` parameters for trace fields
- Auto-detection of environment and region from common cloud provider environment variables
- `.env.example` file with detailed trace field documentation

### Changed
- Updated `revenium_middleware` dependency to >=0.3.5 for trace visualization support
- Enhanced `common/utils.py` to capture and validate trace visualization fields
- Updated README with "Trace Visualization Fields (v0.2.0+)" section
- Improved metadata handling with dual support for env vars and parameters

### Documentation
- Added comprehensive trace visualization example with 5 scenarios
- Updated `.env.example` with trace field examples and detailed comments
- Added trace visualization fields table to README
- Linked to API reference and example files in documentation

## [0.1.2] - 2025-11-17

### Changed
- Added virtual environment setup instructions to examples/README.md for better user experience

## [0.1.1] - 2025-01-13

### Added
- Nested metadata structure support for enhanced subscriber tracking
- Comprehensive documentation for implementation patterns and validation

### Changed
- Improved metadata handling with backward compatibility for existing integrations

## [0.1.0] - 2025-09-08

### Added
- Support for Google AI SDK (Gemini Developer API)
- Support for Vertex AI SDK
- Token counting and usage tracking for both text generation and embeddings
- Streaming response support
- Optional dependencies for flexible installation (`[genai]`, `[vertex]`, `[all]`)
- Comprehensive example scripts
- Python 3.8+ support

[0.1.2]: https://github.com/revenium/revenium-middleware-google-python/releases/tag/v0.1.2
[0.1.1]: https://github.com/revenium/revenium-middleware-google-python/releases/tag/v0.1.1
[0.1.0]: https://github.com/revenium/revenium-middleware-google-python/releases/tag/v0.1.0
