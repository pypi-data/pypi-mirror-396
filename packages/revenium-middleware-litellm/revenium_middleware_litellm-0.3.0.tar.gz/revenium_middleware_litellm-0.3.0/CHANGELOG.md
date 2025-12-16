# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-12-08

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
- New `trace_fields.py` module for trace field capture and validation
- Comprehensive trace visualization example (`examples/trace_visualization_example.py`)
- Support for both environment variables and `usage_metadata` parameters for trace fields
- Auto-detection of environment and region from common cloud provider environment variables
- Updated `.env.example` with detailed trace field documentation

### Changed
- Updated `revenium_middleware` dependency to >=0.3.5 for trace visualization support
- Enhanced `middleware.py` to capture and validate trace visualization fields
- Updated README with "Trace Visualization Fields (v0.3.0+)" section
- Improved metadata handling with dual support for env vars and parameters

## [0.2.0] - 2024-11-22

### Added
- Context-based metadata injection via `metadata_context.set()` for setting metadata once across multiple calls
- 8 decorator functions for automatic metadata tracking:
  - `@track_agent()` - Identify AI agents making calls
  - `@track_task()` - Classify work type
  - `@track_trace()` - Distributed tracing support
  - `@track_organization()` - Multi-tenant tracking
  - `@track_subscription()` - Subscription-based billing
  - `@track_product()` - Product-specific usage
  - `@track_subscriber()` - End user identification
  - `@track_quality()` - Response quality scores
- CrewAI integration with `ReveniumCrewWrapper` for automatic agent/task tracking
- Optional Pydantic validation models for type-safe metadata (`UsageMetadata`, `Subscriber`)
- Hook system for metadata enrichment via `register_metadata_hook()`
- Comprehensive CrewAI integration guide in `docs/CREWAI_INTEGRATION.md`
- Repository prepared for public release with governance files

### Changed
- Enhanced documentation with comprehensive examples for all new features
- Restructured README to be more concise with detailed examples in `examples/README.md`
- Improved test coverage for async functions and decorator patterns

### Fixed
- Ensure `execute_metadata_hooks` always returns a copy to prevent mutation issues
- Address async test configuration with pytest-asyncio
- Documentation accuracy: removed unsupported proxy headers, added missing metadata fields

## [0.1.28] - 2025-08-06

### Changed
- Documentation cleanup and clarification
- Renamed API key variable to avoid confusion
- Added example scripts

### Fixed
- Return response correctly in `handle_response` middleware function

## [0.1.27] - 2025-08-06

### Added
- Initial public release preparation
- LiteLLM client middleware for direct `litellm.completion` calls
- LiteLLM proxy middleware for server integration
- Support for all standard Revenium metadata fields:
  - `trace_id` - Conversation/session grouping
  - `task_type` - AI operation classification
  - `subscriber` - User tracking with credentials
  - `organization_id` - Customer/department tracking
  - `subscription_id` - Billing plan reference
  - `product_id` - Product/feature identification
  - `agent` - AI agent identification
  - `response_quality_score` - Quality metrics
- Zero-config integration via environment variables
- Custom HTTP headers support for proxy mode
- Python 3.8+ compatibility

## [0.1.0] - 2025-08-01

### Added
- Initial implementation
- Basic LiteLLM client middleware
- Basic LiteLLM proxy callback handler
