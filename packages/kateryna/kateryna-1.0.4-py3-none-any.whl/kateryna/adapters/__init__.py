"""
LLM Adapters for Kateryna Epistemic Analysis
============================================

Pre-built adapters for popular LLM providers.
"""

from .base import BaseEpistemicAdapter

__all__ = [
    'BaseEpistemicAdapter',
    'OpenAIEpistemicAdapter',
    'OpenAISyncEpistemicAdapter',
    'AnthropicEpistemicAdapter',
    'AnthropicSyncEpistemicAdapter',
    'OllamaEpistemicAdapter',
    'OllamaSyncEpistemicAdapter',
]


def __getattr__(name):
    """Lazy load adapters to avoid import errors for missing dependencies."""
    if name in ('OpenAIEpistemicAdapter', 'OpenAISyncEpistemicAdapter'):
        from .openai import OpenAIEpistemicAdapter, OpenAISyncEpistemicAdapter
        return OpenAIEpistemicAdapter if name == 'OpenAIEpistemicAdapter' else OpenAISyncEpistemicAdapter

    if name in ('AnthropicEpistemicAdapter', 'AnthropicSyncEpistemicAdapter'):
        from .anthropic import AnthropicEpistemicAdapter, AnthropicSyncEpistemicAdapter
        return AnthropicEpistemicAdapter if name == 'AnthropicEpistemicAdapter' else AnthropicSyncEpistemicAdapter

    if name in ('OllamaEpistemicAdapter', 'OllamaSyncEpistemicAdapter'):
        from .ollama import OllamaEpistemicAdapter, OllamaSyncEpistemicAdapter
        return OllamaEpistemicAdapter if name == 'OllamaEpistemicAdapter' else OllamaSyncEpistemicAdapter

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
