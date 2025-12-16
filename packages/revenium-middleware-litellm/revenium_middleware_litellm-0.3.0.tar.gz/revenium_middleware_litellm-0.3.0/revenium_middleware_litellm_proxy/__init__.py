"""
When you install and import this library, it will automatically hook
LiteLLM proxy requests using a custom logger, and log token usage after
each request. You can customize or extend this logging logic later
to add user or organization metadata for metering purposes.
"""
from .middleware import MiddlewareHandler