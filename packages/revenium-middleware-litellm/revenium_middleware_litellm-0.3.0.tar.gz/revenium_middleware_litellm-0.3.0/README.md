# Revenium Middleware for LiteLLM

[![PyPI version](https://img.shields.io/pypi/v/revenium-middleware-litellm.svg)](https://pypi.org/project/revenium-middleware-litellm/)
[![Python Versions](https://img.shields.io/pypi/pyversions/revenium-middleware-litellm.svg)](https://pypi.org/project/revenium-middleware-litellm/)
[![Documentation](https://img.shields.io/badge/docs-revenium.io-blue)](https://docs.revenium.io)
[![Website](https://img.shields.io/badge/website-revenium.ai-blue)](https://www.revenium.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Transparent Python middleware for automatic Revenium usage tracking with LiteLLM**

A professional-grade Python middleware that seamlessly integrates with LiteLLM to provide automatic usage tracking, billing analytics, and comprehensive metadata collection. Features drop-in integration with zero code changes required and supports both client-side middleware and server-side proxy callbacks.

## Features

- **Seamless Integration** - Drop-in middleware, just import and go
- **Optional Metadata** - Track users, organizations, and business context (all fields optional)
- **Two Integration Patterns** - Client-side middleware or server-side proxy callbacks
- **Decorator-Based Tracking** - Simple `@track_agent` and `@track_task` decorators for automatic metadata injection
- **CrewAI Integration** - Pre-built wrapper for AI agent frameworks
- **All Providers** - Works with any LLM provider supported by LiteLLM
- **Fire-and-Forget** - Never blocks your application flow
- **Accurate Pricing** - Automatic cost calculation based on model and tokens

## Getting Started

### 1. Install Package

```bash
# Create project directory and navigate to it
mkdir my-litellm-project
cd my-litellm-project

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install packages (run after activation)
pip install revenium-middleware-litellm python-dotenv

# For CrewAI support
pip install "revenium-middleware-litellm[crewai]"
```

### 2. Configure Environment Variables

Create a `.env` file in your project root. See [`.env.example`](.env.example) for all available configuration options.

**Minimum required configuration:**

```env
REVENIUM_METERING_API_KEY=hak_your_revenium_api_key_here
REVENIUM_METERING_BASE_URL=https://api.revenium.ai
LITELLM_PROXY_URL=https://your-litellm-proxy.com
LITELLM_API_KEY=sk-your_proxy_key_here
```

**NOTE: Replace the placeholder values with your actual API keys.**

### 3. Run Your First Example

**For complete examples and usage patterns, see [`examples/README.md`](examples/README.md).**

**Quick start:**

```bash
# Run the getting started example
python examples/getting_started.py
```

Or use this simple inline code:

```python
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import revenium_middleware_litellm_client.middleware  # Auto-initializes on import
import litellm
import os

# Configure LiteLLM to use the proxy
litellm.api_base = os.getenv("LITELLM_PROXY_URL")
litellm.api_key = os.getenv("LITELLM_API_KEY")

response = litellm.completion(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
# Your LiteLLM API calls here - automatically metered
```

**That's it!** The middleware automatically meters all LiteLLM API calls.

---

## Requirements

- Python 3.8+
- LiteLLM 1.0.0+
- Works with all LLM providers supported by LiteLLM

---

## What Gets Tracked

The middleware automatically captures comprehensive usage data:

### **Usage Metrics**

- **Token Counts** - Input tokens, output tokens, total tokens
- **Model Information** - Model name, provider, API version
- **Request Timing** - Request duration, response time
- **Cost Calculation** - Estimated costs based on current pricing

### **Business Context (Optional)**

- **User Tracking** - Subscriber ID, email, credentials
- **Organization Data** - Organization ID, subscription ID, product ID
- **Task Classification** - Task type, agent identifier, trace ID
- **Quality Metrics** - Response quality scores

### **Technical Details**

- **API Endpoints** - Chat completions via LiteLLM
- **Request Types** - Streaming vs non-streaming
- **Error Tracking** - Failed requests, error types
- **Provider Info** - LLM provider detection via LiteLLM

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

**Resources:**
- [API Reference](https://revenium.readme.io/reference/meter_ai_completion) - Complete metadata field documentation

### Trace Visualization Fields (v0.3.0+)

Enhanced observability fields for distributed tracing and analytics. These can be set via environment variables or passed in `usage_metadata`:

| Field | Environment Variable | Description | Use Case |
|-------|---------------------|-------------|----------|
| `environment` | `REVENIUM_ENVIRONMENT` | Deployment environment (e.g., "production", "staging") | Track usage across different deployment environments; auto-detects from `ENVIRONMENT`, `DEPLOYMENT_ENV` |
| `region` | `REVENIUM_REGION` | Cloud region identifier (e.g., "us-east-1", "eastus") | Multi-region deployment tracking; auto-detects from `AWS_REGION`, `AZURE_REGION`, `GCP_REGION`, `GOOGLE_CLOUD_REGION` |
| `credential_alias` | `REVENIUM_CREDENTIAL_ALIAS` | Human-readable API key name (e.g., "prod-openai-key") | Track which credential was used for credential rotation and security auditing |
| `trace_type` | `REVENIUM_TRACE_TYPE` | Workflow category identifier (max 128 chars) | Group similar workflows (e.g., "customer-support", "data-analysis") for analytics |
| `trace_name` | `REVENIUM_TRACE_NAME` | Human-readable trace label (max 256 chars) | Label trace instances (e.g., "Customer Support Chat", "Document Analysis") |
| `parent_transaction_id` | `REVENIUM_PARENT_TRANSACTION_ID` | Parent transaction ID for distributed tracing | Link child operations to parent transactions across services |
| `transaction_name` | `REVENIUM_TRANSACTION_NAME` | Human-friendly operation name | Label individual operations (e.g., "Generate Response", "Analyze Sentiment") |
| `retry_number` | `REVENIUM_RETRY_NUMBER` | Retry attempt counter (0 for first attempt, 1+ for retries) | Track retry attempts for failed operations and analyze retry patterns |

**Field Precedence:** `usage_metadata` parameter > environment variable

**Example using environment variables:**
```python
import os
os.environ['REVENIUM_ENVIRONMENT'] = 'production'
os.environ['REVENIUM_REGION'] = 'us-east-1'
os.environ['REVENIUM_TRACE_TYPE'] = 'customer-support'

response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**Example using usage_metadata:**
```python
response = litellm.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}],
    usage_metadata={
        "environment": "production",
        "region": "us-east-1",
        "trace_type": "customer-support",
        "trace_name": "Customer Support Chat"
    }
)
```

**Resources:**
- [Trace Visualization Example](examples/trace_visualization_example.py) - Comprehensive examples of all trace fields
- [.env.example](.env.example) - Environment variable configuration examples

## Configuration Options

### Environment Variables

For a complete list of all available environment variables with examples, see [`.env.example`](.env.example).

**Key variables:**
- `REVENIUM_METERING_API_KEY` - Your Revenium API key (required)
- `REVENIUM_METERING_BASE_URL` - Revenium API endpoint (default: https://api.revenium.ai)
- `LITELLM_PROXY_URL` - Your LiteLLM proxy URL
- `LITELLM_API_KEY` - Your LiteLLM proxy API key
- `REVENIUM_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

## Examples

The package includes comprehensive examples in the [`examples/`](examples/) directory.

### Getting Started

```bash
python examples/getting_started.py
```

### Available Examples

| Example | File | Description |
|---------|------|-------------|
| Getting Started | `getting_started.py` | Basic client middleware with metadata |
| Trace Visualization | `trace_visualization_example.py` | Comprehensive trace fields demonstration |
| Proxy Headers | `litellm_proxy_example.py` | Server-side via HTTP headers |
| CrewAI Integration | `crewai_decorator_example.py` | Multi-agent workflow tracking |

**See [`examples/README.md`](examples/README.md) for detailed documentation of all examples.**

---

## Decorator-Based Tracking

Use decorators for automatic metadata injection:

| Decorator | Purpose |
|-----------|---------|
| `@track_agent()` | Identify the AI agent |
| `@track_task()` | Classify the type of work |
| `@track_trace()` | Set trace ID for distributed tracing |
| `@track_organization()` | Track multi-tenant organizations |
| `@track_subscription()` | Track subscription-based billing |
| `@track_product()` | Track product-specific usage |
| `@track_subscriber()` | Identify end users |
| `@track_quality()` | Track response quality scores |

All decorators support static values, extraction from function arguments (`name_from_arg`), or extraction from object attributes (`name_from_attr`).

**See [examples/README.md](examples/README.md) for detailed decorator documentation and usage patterns.**

---

## Proxy Middleware

For server-side integration, add the callback to your LiteLLM `config.yaml`:

```yaml
litellm_settings:
  callbacks: ["revenium_middleware_litellm_proxy.middleware.proxy_handler_instance"]
```

When using the LiteLLM proxy, pass metadata via HTTP headers (`x-revenium-*`).

**See [examples/README.md](examples/README.md) for proxy header reference and examples.**

---

## CrewAI Integration

Pre-built wrapper for tracking CrewAI agent executions.

**Note:** CrewAI requires Python 3.12 or earlier (Python 3.13+ not yet supported by CrewAI dependencies).

**See [CrewAI Integration Guide](docs/CREWAI_INTEGRATION.md) for detailed documentation.**

---

## Logging

Control log level via environment variable:

```bash
export REVENIUM_LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

---

## Documentation

- [Full Documentation](https://docs.revenium.io)
- [Examples README](examples/README.md) - Detailed code examples and decorator reference
- [CrewAI Integration Guide](docs/CREWAI_INTEGRATION.md)

## Contributing

See [CONTRIBUTING.md](https://github.com/revenium/revenium-middleware-litellm-proxy-python/blob/main/CONTRIBUTING.md)

## Code of Conduct

See [CODE_OF_CONDUCT.md](https://github.com/revenium/revenium-middleware-litellm-proxy-python/blob/main/CODE_OF_CONDUCT.md)

## Security

See [SECURITY.md](https://github.com/revenium/revenium-middleware-litellm-proxy-python/blob/main/SECURITY.md)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/revenium/revenium-middleware-litellm-proxy-python/blob/main/LICENSE) file for details.

## Support

For issues, feature requests, or contributions:

- **Website**: [www.revenium.ai](https://www.revenium.ai)
- **GitHub Repository**: [revenium/revenium-middleware-litellm-proxy-python](https://github.com/revenium/revenium-middleware-litellm-proxy-python)
- **Issues**: [Report bugs or request features](https://github.com/revenium/revenium-middleware-litellm-proxy-python/issues)
- **Documentation**: [docs.revenium.io](https://docs.revenium.io)
- **Email**: support@revenium.io

---

**Built by Revenium**
