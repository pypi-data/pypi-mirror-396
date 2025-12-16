# CrewAI Integration Guide

Complete guide for integrating Revenium metering with CrewAI applications.

## Table of Contents

- [Version Compatibility](./CREWAI_VERSION_COMPATIBILITY.md) 📖
- [Quick Start](#quick-start)
- [Complete Working Example](#complete-working-example)
- [Advanced Patterns](#advanced-patterns)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

> **⚠️ Version Compatibility Note:**
> **All CrewAI versions supported** with automatic version detection.
> - **CrewAI < 0.203.0:** Full metadata tracking (crew + task level) via automatic monkey-patching
> - **CrewAI >= 0.203.0:** Crew-level metadata + task-level metadata using decorators)
> **📖 Full Details:** [CrewAI Version Compatibility Guide](./CREWAI_VERSION_COMPATIBILITY.md)

### Installation

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with CrewAI support
pip install "revenium-middleware-litellm[crewai]"

# Or install both packages separately
pip install revenium-middleware-litellm crewai
```

**Note:** CrewAI requires Python 3.12 or earlier (Python 3.13+ not yet supported by CrewAI dependencies).

### Environment Setup

Set your API credentials in a `.env` file or export them:

```bash
export REVENIUM_METERING_API_KEY=hak_your_revenium_api_key_here
export REVENIUM_METERING_BASE_URL=https://api.revenium.ai
export OPENAI_API_KEY=sk-your_openai_key_here
```

### Minimal Working Example

```python
import os
import revenium_middleware_litellm_client.middleware  # Import FIRST
from crewai import Agent, Task, Crew
from revenium_middleware_litellm_client.integrations.crewai import ReveniumCrewWrapper

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = "your-openai-key"

# Create a simple agent
agent = Agent(
    role="Research Assistant",
    goal="Provide helpful information",
    backstory="An AI assistant with expertise in research",
    verbose=True
)

# Create a task
task = Task(
    description="What are the top 3 benefits of AI?",
    agent=agent,
    expected_output="A list of 3 benefits"
)

# Wrap with Revenium tracking
crew = ReveniumCrewWrapper(
    agents=[agent],
    tasks=[task],
    organization_id="MyCompany",
    subscription_id="free-tier",
    product_id="research-assistant"
)

# Execute - all LiteLLM calls automatically tracked
result = crew.kickoff()
print(result)
```

**That's it** All LiteLLM calls made by your CrewAI agents are now automatically metered with:
- Your organization, subscription, and product IDs
- Auto-generated trace ID for this crew execution

> **⚠️ Important:** The method for tracking task-level metadata (i.e. agent role, task type) varies based on CrewAI middleware version.  Task-level metadata is tracked with CrewAI < 0.203.0 when using `ReveniumCrewWrapper`. For CrewAI >= 0.203.0, use decorators for full metadata tracking. See [Advanced Patterns](#advanced-patterns) below.

---

## Complete Working Example

This example demonstrates a multi-agent marketing strategy crew with comprehensive metadata tracking.

### Full Code

```python
#!/usr/bin/env python
"""
Complete CrewAI + Revenium Integration Example
Demonstrates multi-agent workflow with automatic metering
"""

import os
from datetime import datetime

# IMPORTANT: Import middleware BEFORE crewai
import revenium_middleware_litellm_client.middleware

from crewai import Agent, Task, Crew
from revenium_middleware_litellm_client.integrations.crewai import ReveniumCrewWrapper

# ============================================================================
# Configuration
# ============================================================================

# Set your API keys
os.environ["OPENAI_API_KEY"] = "your-openai-key"
os.environ["REVENIUM_METERING_API_KEY"] = "your-revenium-key"

# Optional: Set custom base URL (defaults to production)
# os.environ["REVENIUM_METERING_BASE_URL"] = "https://api.revenium.ai"

# ============================================================================
# Define Agents
# ============================================================================

# Agent 1: Market Researcher
market_researcher = Agent(
    role="Lead Market Analyst",
    goal="Conduct comprehensive market research and identify trends",
    backstory="""You are an expert market analyst with 10 years of experience
    in technology markets. You excel at identifying emerging trends and
    providing data-driven insights.""",
    verbose=True,
    allow_delegation=False
)

# Agent 2: Content Strategist
content_strategist = Agent(
    role="Content Strategy Expert",
    goal="Develop engaging content strategies based on market research",
    backstory="""You are a creative content strategist who transforms
    market insights into compelling content plans. You understand what
    resonates with different audiences.""",
    verbose=True,
    allow_delegation=False
)

# Agent 3: Content Writer
content_writer = Agent(
    role="Senior Content Writer",
    goal="Create high-quality, engaging content",
    backstory="""You are an experienced content writer who crafts
    compelling narratives. You excel at turning strategies into
    polished, publication-ready content.""",
    verbose=True,
    allow_delegation=False
)

# ============================================================================
# Define Tasks
# ============================================================================

# Task 1: Market Research
research_task = Task(
    description="""Research the latest trends in artificial intelligence
    and machine learning for 2024. Focus on:
    1. Emerging technologies
    2. Market size and growth projections
    3. Key players and innovations
    
    Provide a comprehensive summary with data points.""",
    agent=market_researcher,
    expected_output="A detailed market research report with key findings"
)

# Task 2: Content Strategy
strategy_task = Task(
    description="""Based on the market research, develop a content strategy
    for a blog post series. Include:
    1. Target audience definition
    2. Key themes and topics
    3. Content angles and hooks
    4. Recommended tone and style
    
    Create a strategic plan for 3 blog posts.""",
    agent=content_strategist,
    expected_output="A comprehensive content strategy document",
    context=[research_task]  # Depends on research task
)

# Task 3: Content Creation
writing_task = Task(
    description="""Write the first blog post based on the content strategy.
    The post should be:
    1. 800-1000 words
    2. Engaging and informative
    3. SEO-optimized
    4. Include a compelling introduction and conclusion
    
    Focus on the most important trend identified in the research.""",
    agent=content_writer,
    expected_output="A complete, publication-ready blog post",
    context=[research_task, strategy_task]  # Depends on both previous tasks
)

# ============================================================================
# Create Crew with Revenium Tracking
# ============================================================================

# Generate a unique trace ID for this workflow
trace_id = f"marketing-workflow-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

# Wrap the crew with Revenium tracking
crew = ReveniumCrewWrapper(
    agents=[market_researcher, content_strategist, content_writer],
    tasks=[research_task, strategy_task, writing_task],
    
    # Metadata for tracking
    organization_id="AcmeCorp",           # Your company/customer ID
    subscription_id="enterprise-plan",    # Subscription tier
    product_id="marketing-ai-assistant",  # Your product name
    trace_id=trace_id,                    # Unique workflow ID
    
    # Optional: Crew configuration
    verbose=True,  # Enable verbose output
    process="sequential"  # Tasks run in sequence
)

# ============================================================================
# Execute Workflow
# ============================================================================

print("=" * 80)
print("Starting Marketing Strategy Workflow")
print(f"Trace ID: {trace_id}")
print("=" * 80)

# Run the crew - all LiteLLM calls automatically tracked.
result = crew.kickoff()

print("\n" + "=" * 80)
print("Workflow Complete!")
print("=" * 80)
print("\nFinal Output:")
print(result)
```

### What Gets Tracked

For each LiteLLM call made by the agents, Revenium captures:

**1. Agent Metadata:**
- `agent`: "Lead Market Analyst" (from agent.role)
- `task_type`: "Research the latest trends..." (from task.description)

**2. Organization Metadata:**
- `organization_id`: "AcmeCorp"
- `subscription_id`: "enterprise-plan"
- `product_id`: "marketing-ai-assistant"
- `trace_id`: "marketing-workflow-20241013-143022"

**3. Usage Metrics:**
- Model used (e.g., "gpt-4")
- Input/output tokens
- Cost per call
- Response time
- Total cost for the workflow

All this data is available in your Revenium dashboard for:
- Cost tracking by agent
- Performance analysis by task type
- Usage trends by organization
- Workflow-level cost attribution

### Running the Example

1. Save the code to a file (e.g., `marketing_crew.py`)
2. Set your API keys:
   ```bash
   export OPENAI_API_KEY=sk-your_openai_key_here
   export REVENIUM_METERING_API_KEY=hak_your_revenium_api_key_here
   ```
3. Run the script:
   ```bash
   python marketing_crew.py
   ```

### Expected Output

The script will:
1. Execute all 3 tasks sequentially
2. Display agent thinking and outputs (if `verbose=True`)
3. Track all LiteLLM calls to Revenium
4. Print the final blog post

You can verify the tracking in your Revenium dashboard by searching for the trace ID.

---

## Advanced Patterns

### Pattern 1: Using Decorators with Custom Tools

Combine `ReveniumCrewWrapper` with decorators for custom tool functions:

```python
import revenium_middleware_litellm_client.middleware
from crewai import Agent, Task, Crew
from crewai.tools import tool
from revenium_middleware_litellm_client import track_task, track_quality
from revenium_middleware_litellm_client.integrations.crewai import ReveniumCrewWrapper

# Define a custom tool with decorator tracking
@tool("Data Analyzer")
@track_task("data_analysis")
@track_quality(0.95)
def analyze_data(data: str) -> str:
    """Analyzes data using AI."""
    import litellm
    response = litellm.completion(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Analyze this data: {data}"}]
    )
    return response.choices[0].message.content

# Create agent with custom tool
analyst = Agent(
    role="Data Analyst",
    goal="Analyze data and provide insights",
    backstory="Expert data analyst",
    tools=[analyze_data],
    verbose=True
)

task = Task(
    description="Analyze the sales data for Q4",
    agent=analyst,
    expected_output="Analysis report"
)

# Wrap with Revenium
crew = ReveniumCrewWrapper(
    agents=[analyst],
    tasks=[task],
    organization_id="DataCorp",
    subscription_id="data-plan",
    product_id="analytics-platform"
)

result = crew.kickoff()
```

**Result**: Tool calls get `task_type="data_analysis"` and `response_quality_score=0.95` in addition to the wrapper's metadata.

### Pattern 2: Multi-Tenant CrewAI Application

Track different customers/organizations:

```python
from datetime import datetime
import revenium_middleware_litellm_client.middleware
from crewai import Agent, Task
from revenium_middleware_litellm_client.integrations.crewai import ReveniumCrewWrapper

def create_crew_for_customer(customer_id, subscription_tier):
    """Factory function to create customer-specific crews."""

    # Create agents (same for all customers)
    agent = Agent(
        role="Customer Support Agent",
        goal="Provide excellent customer support",
        backstory="Experienced support specialist"
    )

    task = Task(
        description="Help the customer with their question",
        agent=agent,
        expected_output="Helpful response"
    )

    # Create crew with customer-specific metadata
    crew = ReveniumCrewWrapper(
        agents=[agent],
        tasks=[task],
        organization_id=customer_id,           # Different per customer
        subscription_id=subscription_tier,      # Different per tier
        product_id="support-ai",
        trace_id=f"support-{customer_id}-{datetime.now().timestamp()}"
    )

    return crew

# Usage
customer_a_crew = create_crew_for_customer("customer-a", "premium")
customer_b_crew = create_crew_for_customer("customer-b", "basic")

# Each crew's usage tracked separately by organization_id
result_a = customer_a_crew.kickoff()
result_b = customer_b_crew.kickoff()
```

**Result**: You can track costs and usage per customer in Revenium.

### Pattern 3: Quality Score Tracking

Track quality scores for agent outputs:

```python
import revenium_middleware_litellm_client.middleware
from crewai import Agent, Task
from revenium_middleware_litellm_client import metadata_context
from revenium_middleware_litellm_client.integrations.crewai import ReveniumCrewWrapper

# Create agent and task
agent = Agent(
    role="Quality Tester",
    goal="Test quality tracking",
    backstory="A test agent for quality score validation",
    verbose=True
)

task = Task(
    description="Provide a brief greeting",
    agent=agent,
    expected_output="A greeting"
)

# Create crew
crew = ReveniumCrewWrapper(
    agents=[agent],
    tasks=[task],
    organization_id="QualityCorp",
    subscription_id="quality-plan",
    product_id="quality-ai"
)

# Set quality threshold for this execution
with metadata_context.set(response_quality_score=0.90):
    result = crew.kickoff()

# All LiteLLM calls in this crew execution tracked with quality_score=0.90
```

### Pattern 4: Dynamic Metadata from Runtime Context

Extract metadata from runtime context:

```python
import revenium_middleware_litellm_client.middleware
from revenium_middleware_litellm_client import track_organization, track_subscriber

class MultiTenantCrewService:
    def __init__(self, org_id, user_email):
        self.org_id = org_id
        self.user_email = user_email

    @track_organization(id_from_attr="org_id")
    @track_subscriber(email_from_arg="user_email")
    def execute_crew(self, query, user_email=None):
        """Execute crew with automatic org and user tracking."""
        from crewai import Agent, Task
        from revenium_middleware_litellm_client.integrations.crewai import ReveniumCrewWrapper

        agent = Agent(
            role="Assistant",
            goal="Help the user",
            backstory="Helpful AI assistant"
        )

        task = Task(
            description=query,
            agent=agent,
            expected_output="Helpful response"
        )

        crew = ReveniumCrewWrapper(
            agents=[agent],
            tasks=[task],
            organization_id=self.org_id,
            subscription_id="default",
            product_id="multi-tenant-ai"
        )

        return crew.kickoff()

# Usage
service = MultiTenantCrewService("AcmeCorp", "user@acme.com")
result = service.execute_crew("What are the latest AI trends?")
# Tracked with organization_id="AcmeCorp", subscriber.email="user@acme.com"
```

---

## Troubleshooting

### Issue: Metadata Not Appearing in Revenium

**Symptoms**: Crew executes successfully but metadata is missing in Revenium dashboard.

**Solutions**:

1. **Verify middleware import order**:
   ```python
   # CORRECT: Import middleware BEFORE crewai
   import revenium_middleware_litellm_client.middleware
   from crewai import Agent, Task, Crew
   
   # WRONG: Don't import crewai first
   from crewai import Agent, Task, Crew
   import revenium_middleware_litellm_client.middleware  # Too late!
   ```

2. **Check environment variables**:
   ```python
   import os
   print("API Key set:", "REVENIUM_METERING_API_KEY" in os.environ)
   print("Base URL:", os.getenv("REVENIUM_METERING_BASE_URL", "default"))
   ```

3. **Enable debug logging**:
   ```bash
   export REVENIUM_LOG_LEVEL=DEBUG
   python your_script.py
   ```
   
   Look for log messages like:
   ```
   DEBUG - Sending metering data: {...}
   ```

### Issue: Some Agents Not Tracked

**Symptoms**: Some agents' calls appear in Revenium, others don't.

**Solutions**:

1. **Ensure all agents are in the wrapper**:
   ```python
   # Include ALL agents in the wrapper
   crew = ReveniumCrewWrapper(
       agents=[agent1, agent2, agent3],
       tasks=[task1, task2, task3],
       ...
   )
   ```

2. **Check for delegation**:
   If agents delegate to other agents not in the wrapper, those calls won't be tracked. Either:
   - Add all potential agents to the wrapper
   - Set `allow_delegation=False` on agents

### Issue: Trace IDs Not Unique

**Symptoms**: Multiple workflow executions have the same trace_id.

**Solution**: Generate unique trace IDs:

```python
import uuid
from datetime import datetime

# Option 1: UUID
trace_id = f"workflow-{uuid.uuid4()}"

# Option 2: Timestamp
trace_id = f"workflow-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}"

# Option 3: Combination
trace_id = f"workflow-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
```

### Debug Logging Tips

Enable comprehensive logging:

```python
import logging
import os

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable Revenium debug logs
os.environ["REVENIUM_LOG_LEVEL"] = "DEBUG"

# Enable LiteLLM debug logs
import litellm
litellm.set_verbose = True
```

---

## Additional Resources

- [Main README](../README.md) - Complete middleware documentation
- [Decorator Reference](../README.md#decorator-reference) - All available decorators
- [CrewAI Documentation](https://docs.crewai.com/) - Official CrewAI docs
- [Revenium Dashboard](https://app.revenium.ai) - View your usage data

---

## Support

If you encounter issues not covered in this guide:

1. Check the [main README](../README.md) for general middleware documentation
2. Enable debug logging to see detailed error messages
3. Verify your API keys and network connectivity
4. Contact Revenium support with your trace ID and error logs
