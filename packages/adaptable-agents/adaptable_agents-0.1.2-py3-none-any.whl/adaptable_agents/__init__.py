"""Adaptable Agents Python Client - Wrap your LLM clients with automatic context generation."""

from .client import AdaptableAgent, ContextConfig
from .openai_wrapper import AdaptableOpenAIClient
from .anthropic_wrapper import AdaptableAnthropicClient

__version__ = "0.1.1"
__all__ = [
    "AdaptableAgent",
    "AdaptableOpenAIClient",
    "AdaptableAnthropicClient",
    "ContextConfig",
]
