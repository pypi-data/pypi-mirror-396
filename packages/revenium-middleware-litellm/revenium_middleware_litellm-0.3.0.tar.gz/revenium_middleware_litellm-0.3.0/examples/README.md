# Revenium LiteLLM Middleware - Examples

This guide provides complete examples for integrating Revenium usage tracking with LiteLLM.

## Two Integration Patterns

This middleware supports two integration patterns depending on your architecture:

### Pattern 1: Client-Side Middleware (Python Applications)

Use this when you're building a Python application that calls a LiteLLM proxy.

```
┌─────────────────────┐      ┌──────────────────┐      ┌─────────────┐
│  Your Python App    │      │  LiteLLM Proxy   │      │  LLM APIs   │
│  + Revenium Client  │ ──── │  (your server)   │ ──── │  (OpenAI,   │
│    Middleware       │      │                  │      │   etc.)     │
└─────────────────────┘      └──────────────────┘      └─────────────┘
         │
         └── Sends metering data to Revenium
```

**Examples:** `getting_started.py`, `crewai_decorator_example.py`

### Pattern 2: Server-Side Proxy Headers (Any Language/Client)

Use this when you want to pass metadata via HTTP headers from any client (curl, JavaScript, etc.) to a LiteLLM proxy that has the Revenium callback installed.

```
┌─────────────────────┐      ┌──────────────────────────┐      ┌─────────────┐
│  Any HTTP Client    │      │  LiteLLM Proxy           │      │  LLM APIs   │
│  (curl, JS, etc.)   │ ──── │  + Revenium Proxy        │ ──── │  (OpenAI,   │
│  with x-revenium-*  │      │    Callback              │      │   etc.)     │
│  headers            │      │                          │      │             │
└─────────────────────┘      └──────────────────────────┘      └─────────────┘
                                       │
                                       └── Sends metering data to Revenium
```

**Example:** `litellm_proxy_example.py`

---

## Quick Start

### 1. Create Your Project

```bash
mkdir my-litellm-project
cd my-litellm-project
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install revenium-middleware-litellm python-dotenv

# Optional: For CrewAI support
pip install "revenium-middleware-litellm[crewai]"
```

### 3. Environment Setup

Create a `.env` file:

```bash
# Revenium Configuration (Required)
REVENIUM_METERING_API_KEY=hak_your_revenium_key_here
REVENIUM_METERING_BASE_URL=https://api.revenium.ai

# LiteLLM Proxy Configuration (Required)
LITELLM_PROXY_URL=https://your-litellm-proxy.com
LITELLM_API_KEY=sk-your-proxy-key

# Optional: Enable debug logging
REVENIUM_LOG_LEVEL=DEBUG
```

Get your Revenium API key: https://app.revenium.ai

### 4. Run an Example

```bash
curl -O https://raw.githubusercontent.com/revenium/revenium-middleware-litellm-proxy-python/main/examples/getting_started.py
python getting_started.py
```

---

## Available Examples

### `getting_started.py` - Client-Side Middleware

**Use case:** Python applications calling a LiteLLM proxy

The simplest way to get started. Uses the client middleware to automatically meter all `litellm.completion()` calls.

**What it demonstrates:**
- Automatic metering via middleware import
- Passing metadata via `usage_metadata` parameter
- Basic and enhanced tracking examples

**Run it:**
```bash
python examples/getting_started.py
```

---

### `litellm_proxy_example.py` - Server-Side Headers

**Use case:** Any HTTP client calling a LiteLLM proxy with Revenium callback installed

Shows how to pass Revenium metadata via HTTP headers. This is useful when:
- Your client isn't Python (JavaScript, curl, etc.)
- You want metadata to flow through the proxy layer
- The proxy has the `revenium_middleware_litellm_proxy` callback configured

**What it demonstrates:**
- Raw HTTP requests to LiteLLM proxy
- `x-revenium-*` header format for all metadata fields
- No client-side middleware needed

**Run it:**
```bash
python examples/litellm_proxy_example.py
```

---

### `crewai_decorator_example.py` - CrewAI Integration

**Use case:** Multi-agent workflows with CrewAI

Demonstrates the `ReveniumCrewWrapper` for tracking CrewAI agent executions.

**What it demonstrates:**
- `ReveniumCrewWrapper` usage
- Decorator-based tracking (`@track_agent`, `@track_task`)
- Multi-agent workflow attribution

**Run it:**
```bash
pip install "revenium-middleware-litellm[crewai]"
python examples/crewai_decorator_example.py
```

---

## Requirements

- Python 3.8+
- LiteLLM 1.0.0+
- Valid Revenium API key
- A LiteLLM proxy (your own or hosted)

---

## Decorator Reference

The middleware provides 8 decorators for automatic metadata injection. All decorators:
- Work with both sync and async functions
- Support static values, dynamic extraction from arguments, or dynamic extraction from object attributes
- Can be stacked together for comprehensive tracking
- Are framework-agnostic (work with any Python code using LiteLLM)

### Available Decorators

| Decorator | Purpose | Example |
|-----------|---------|---------|
| `@track_agent()` | Identify the AI agent making the call | `@track_agent("Lead Analyst")` |
| `@track_task()` | Classify the type of work being performed | `@track_task("market_research")` |
| `@track_trace()` | Set trace ID for distributed tracing | `@track_trace("workflow-123")` |
| `@track_organization()` | Track multi-tenant organizations | `@track_organization("AcmeCorp")` |
| `@track_subscription()` | Track subscription-based billing | `@track_subscription("premium-tier")` |
| `@track_product()` | Track product-specific usage | `@track_product("ai-assistant")` |
| `@track_subscriber()` | Identify end users | `@track_subscriber(subscriber_id="user-123")` |
| `@track_quality()` | Track response quality scores | `@track_quality(0.95)` |

---

## Usage Patterns

**Note:** All examples below assume the middleware has been activated with:
```python
import revenium_middleware_litellm_client.middleware
import litellm
```

### 1. Static Values

The simplest usage - provide a fixed value:

```python
from revenium_middleware_litellm_client import track_agent, track_task
import revenium_middleware_litellm_client.middleware  # Activate middleware
import litellm

@track_agent("Customer Support Agent")
@track_task("customer_inquiry")
def handle_customer_question(question):
    return litellm.completion(
        model="gpt-4",
        messages=[{"role": "user", "content": question}]
    )
```

### 2. Dynamic Values from Arguments

Extract metadata from function arguments:

```python
from revenium_middleware_litellm_client import track_agent, track_organization

@track_agent(name_from_arg="agent_name")
@track_organization(id_from_arg="org_id")
def process_request(agent_name, org_id, request_data):
    # agent_name and org_id are automatically extracted and tracked
    return litellm.completion(
        model="gpt-4",
        messages=[{"role": "user", "content": request_data}]
    )

# Usage
result = process_request("Sales Agent", "AcmeCorp", "Analyze Q4 sales")
# Tracked with agent="Sales Agent", organization_id="AcmeCorp"
```

### 3. Dynamic Values from Object Attributes

Extract metadata from object attributes (useful for class methods):

```python
from revenium_middleware_litellm_client import track_agent, track_organization

class AIAssistant:
    def __init__(self, name, organization):
        self.name = name
        self.organization = organization

    @track_agent(name_from_attr="name")
    @track_organization(id_from_attr="organization")
    def process(self, query):
        # self.name and self.organization are automatically extracted
        return litellm.completion(
            model="gpt-4",
            messages=[{"role": "user", "content": query}]
        )

# Usage
assistant = AIAssistant("Research Agent", "TechCorp")
result = assistant.process("What are the latest AI trends?")
# Tracked with agent="Research Agent", organization_id="TechCorp"
```

### 4. Stacking Multiple Decorators

Combine decorators for comprehensive tracking:

```python
from revenium_middleware_litellm_client import (
    track_agent,
    track_task,
    track_trace,
    track_organization,
    track_subscription,
    track_product,
    track_quality
)

@track_organization("AcmeCorp")
@track_subscription("enterprise-plan")
@track_product("ai-analytics")
@track_trace("batch-job-2024-001")
@track_agent("Data Analyst")
@track_task("data_analysis")
@track_quality(0.95)
def analyze_data(data):
    return litellm.completion(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Analyze: {data}"}]
    )
```

### 5. Async Function Support

All decorators work seamlessly with async functions:

```python
from revenium_middleware_litellm_client import track_agent, track_task

@track_agent("Async Agent")
@track_task("async_processing")
async def process_async(query):
    return await litellm.acompletion(
        model="gpt-4",
        messages=[{"role": "user", "content": query}]
    )

# Usage
import asyncio
result = asyncio.run(process_async("What is AI?"))
```

---

## Decorator Details

### `@track_agent()`

Track which AI agent is making the call.

**Parameters:**
- `agent` (str, optional): Static agent name
- `name_from_arg` (str, optional): Extract from function argument
- `name_from_attr` (str, optional): Extract from object attribute

**Examples:**
```python
# Static
@track_agent("Lead Analyst")
def analyze(): ...

# From argument
@track_agent(name_from_arg="agent_name")
def process(agent_name, data): ...

# From attribute
@track_agent(name_from_attr="name")
def process(self): ...  # Uses self.name
```

### `@track_task()`

Classify the type of work being performed.

**Parameters:**
- `task_type` (str, optional): Static task type
- `type_from_arg` (str, optional): Extract from function argument
- `type_from_attr` (str, optional): Extract from object attribute

**Examples:**
```python
# Static
@track_task("market_research")
def research(): ...

# From argument
@track_task(type_from_arg="task_name")
def execute(task_name, data): ...
```

### `@track_trace()`

Set trace ID for distributed tracing and request correlation.

**Parameters:**
- `trace_id` (str, optional): Static trace ID
- `id_from_arg` (str, optional): Extract from function argument
- `id_from_attr` (str, optional): Extract from object attribute

**Examples:**
```python
# Static
@track_trace("workflow-123")
def process(): ...

# From argument
@track_trace(id_from_arg="request_id")
def handle(request_id, data): ...
```

### `@track_organization()`

Track multi-tenant organizations or customers.

**Parameters:**
- `organization_id` (str, optional): Static organization ID
- `id_from_arg` (str, optional): Extract from function argument
- `id_from_attr` (str, optional): Extract from object attribute

**Examples:**
```python
# Static
@track_organization("AcmeCorp")
def process(): ...

# From argument
@track_organization(id_from_arg="org_id")
def handle(org_id, data): ...
```

### `@track_subscription()`

Track subscription-based billing and usage.

**Parameters:**
- `subscription_id` (str, optional): Static subscription ID
- `id_from_arg` (str, optional): Extract from function argument
- `id_from_attr` (str, optional): Extract from object attribute

**Examples:**
```python
# Static
@track_subscription("premium-tier")
def process(): ...

# From argument
@track_subscription(id_from_arg="sub_id")
def handle(sub_id, data): ...
```

### `@track_product()`

Track product-specific usage across different products or features.

**Parameters:**
- `product_id` (str, optional): Static product ID
- `id_from_arg` (str, optional): Extract from function argument
- `id_from_attr` (str, optional): Extract from object attribute

**Examples:**
```python
# Static
@track_product("ai-assistant")
def process(): ...

# From argument
@track_product(id_from_arg="product_name")
def handle(product_name, data): ...
```

### `@track_subscriber()`

Identify end users with detailed subscriber information.

**Parameters:**
- `subscriber_id` (str, optional): Static subscriber ID
- `subscriber_email` (str, optional): Static subscriber email
- `credential_name` (str, optional): Static credential name
- `id_from_arg` (str, optional): Extract ID from function argument
- `email_from_arg` (str, optional): Extract email from function argument
- `credential_from_arg` (str, optional): Extract credential from function argument

**Examples:**
```python
# Static
@track_subscriber(
    subscriber_id="user-123",
    subscriber_email="user@example.com",
    credential_name="api-key-1"
)
def process(): ...

# From arguments
@track_subscriber(
    id_from_arg="user_id",
    email_from_arg="user_email"
)
def handle(user_id, user_email, data): ...
```

### `@track_quality()`

Track response quality scores for monitoring AI output quality.

**Parameters:**
- `quality_score` (float, optional): Static quality score (0.0-1.0)
- `score_from_arg` (str, optional): Extract from function argument
- `score_from_attr` (str, optional): Extract from object attribute

**Examples:**
```python
# Static
@track_quality(0.95)
def process(): ...

# From argument
@track_quality(score_from_arg="min_quality")
def handle(min_quality, data): ...
```

---

## Metadata Precedence

When multiple methods are used to set metadata, the following precedence order applies:

```
Explicit usage_metadata kwargs > Decorator metadata > Context API metadata
```

**Example:**

```python
from revenium_middleware_litellm_client import track_organization, metadata_context

# Context sets organization_id="ContextOrg"
with metadata_context.set(organization_id="ContextOrg"):

    # Decorator sets organization_id="DecoratorOrg"
    @track_organization("DecoratorOrg")
    def process():
        # Explicit kwarg sets organization_id="ExplicitOrg"
        return litellm.completion(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}],
            usage_metadata={"organization_id": "ExplicitOrg"}
        )

    result = process()
    # Result: organization_id="ExplicitOrg" (explicit wins)
```

**When to use each method:**

- **Explicit kwargs**: When you need to override metadata for a specific call
- **Decorators**: When metadata is consistent for a function but varies between functions
- **Context API**: When metadata is consistent across multiple calls in a scope

---

## Framework Examples

### FastAPI Integration

```python
from fastapi import FastAPI, Header
from pydantic import BaseModel
from revenium_middleware_litellm_client import track_organization, track_subscriber
import revenium_middleware_litellm_client.middleware
import litellm

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
@track_organization(id_from_arg="org_id")
@track_subscriber(email_from_arg="user_email")
async def chat_endpoint(
    request: ChatRequest,
    org_id: str = Header(..., alias="X-Organization-ID"),
    user_email: str = Header(..., alias="X-User-Email"),
):
    response = await litellm.acompletion(
        model="gpt-4",
        messages=[{"role": "user", "content": request.message}]
    )
    return {"response": response.choices[0].message.content}
```

### Batch Processing

```python
from revenium_middleware_litellm_client import track_trace, track_task
import revenium_middleware_litellm_client.middleware
import litellm

@track_trace(id_from_arg="batch_id")
@track_task("batch_processing")
def process_batch(batch_id, items):
    results = []
    for item in items:
        response = litellm.completion(
            model="gpt-4",
            messages=[{"role": "user", "content": f"Process: {item}"}]
        )
        results.append(response.choices[0].message.content)
    return results

# All items in the batch tracked with the same trace_id
results = process_batch("batch-2024-001", ["item1", "item2", "item3"])
```

### CLI Tool

```python
import click
from revenium_middleware_litellm_client import track_agent, track_task
import revenium_middleware_litellm_client.middleware
import litellm

@click.command()
@click.argument('query')
@click.option('--agent', default='CLI Agent')
@track_agent(name_from_arg="agent")
@track_task("cli_query")
def ask(query, agent):
    """Ask a question to the AI."""
    response = litellm.completion(
        model="gpt-4",
        messages=[{"role": "user", "content": query}]
    )
    click.echo(response.choices[0].message.content)

if __name__ == '__main__':
    ask()
```

---

## LiteLLM Proxy Integration

This middleware integrates with the LiteLLM proxy using its custom callback mechanism.

### Proxy Server Setup

To integrate the Revenium middleware with your LiteLLM proxy server:

1. **Install the middleware** on the proxy server:
   ```bash
   pip install revenium-middleware-litellm
   ```

2. **Set environment variables** where the proxy runs:
   ```bash
   export REVENIUM_METERING_API_KEY=hak_your_revenium_api_key_here
   export REVENIUM_METERING_BASE_URL=https://api.revenium.ai
   ```

3. **Configure your LiteLLM proxy** to use the Revenium middleware callback.

### Proxy Server Configuration

Add the Revenium middleware callback to your LiteLLM `config.yaml`:

```yaml
model_list:
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: openai/gpt-3.5-turbo
      api_key: "os.environ/OPENAI_API_KEY"

general_settings:
  master_key: "sk-1234"

litellm_settings:
  callbacks: ["revenium_middleware_litellm_proxy.middleware.proxy_handler_instance"]
```

**Important:** LiteLLM proxy expects the callbacks list to contain importable Python paths to the callback handler instances. Ensure the `revenium-middleware-litellm` package is installed in the Python environment where the LiteLLM proxy runs.

### Custom HTTP Headers

Pass metadata to the proxy via HTTP headers:

```python
import os
import requests
import json

proxy_base = os.getenv("LITELLM_PROXY_URL")  # e.g., https://your-litellm-proxy.com
proxy_url = f"{proxy_base}/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-1234",
    "x-revenium-trace-id": "conv-28a7e9d4",
    "x-revenium-task-type": "summarize-customer-issue",
    "x-revenium-organization-id": "acme-corp",
    "x-revenium-product-id": "saas-app-gold-tier",
    "x-revenium-agent": "support-agent",
    "x-revenium-subscriber-id": "user-123",
    "x-revenium-subscription-id": "premium-plan",
    "x-revenium-response-quality-score": "0.95",
}

data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the meaning of life?"}
    ]
}

response = requests.post(proxy_url, headers=headers, data=json.dumps(data))
print(response.json())
```

### Proxy Header Reference

| Header | Description |
|--------|-------------|
| `x-revenium-trace-id` | Unique identifier for a conversation or session |
| `x-revenium-task-type` | Classification of the AI operation |
| `x-revenium-organization-id` | Customer or department ID (falls back to LiteLLM's `user_api_key_team_alias`) |
| `x-revenium-subscription-id` | Reference to a billing plan |
| `x-revenium-product-id` | Your product or feature making the call |
| `x-revenium-agent` | Identifier for the AI agent |
| `x-revenium-subscriber-id` | Subscriber ID from your system |
| `x-revenium-response-quality-score` | Quality score (0-1) |

**Note:** Subscriber email and credential information are automatically extracted from LiteLLM's virtual key metadata (`user_api_key_user_email`, `user_api_key_alias`) when using LiteLLM's built-in user management.

---

## Type-Safe Metadata with Pydantic

For enhanced IDE autocomplete and runtime type validation:

```bash
pip install "revenium-middleware-litellm[validation]"
```

```python
from revenium_middleware_litellm_client import UsageMetadata, Subscriber
from pydantic import ValidationError

# IDE autocomplete and type checking
metadata = UsageMetadata(
    organization_id="AcmeCorp",
    subscription_id="82764738",
    product_id="Platinum",
    trace_id="abc-123",
    agent="Lead Analyst",
    task_type="research",
    response_quality_score=0.95
)

# Type errors caught immediately
try:
    bad_metadata = UsageMetadata(organization_id=12345)  # TypeError
except ValidationError as e:
    print(e)

# Convert to dict for use with litellm
metadata_dict = metadata.model_dump(exclude_none=True)
```

Pydantic is completely optional - the middleware works without it.
