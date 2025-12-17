"""
AIPT LLM Module - Universal LLM interface via litellm
"""

# Core config that doesn't require litellm
from aipt_v2.llm.config import LLMConfig

__all__ = [
    "LLM",
    "LLMConfig",
    "LLMResponse",
    "LLMRequestFailedError",
    "RequestStats",
    "MemoryCompressor",
    "get_global_queue",
]


def __getattr__(name):
    """Lazy import for components requiring litellm"""
    if name == "LLM":
        from llm.llm import LLM
        return LLM
    elif name == "LLMResponse":
        from llm.llm import LLMResponse
        return LLMResponse
    elif name == "LLMRequestFailedError":
        from llm.llm import LLMRequestFailedError
        return LLMRequestFailedError
    elif name == "RequestStats":
        from llm.llm import RequestStats
        return RequestStats
    elif name == "MemoryCompressor":
        from llm.memory import MemoryCompressor
        return MemoryCompressor
    elif name == "get_global_queue":
        from llm.request_queue import get_global_queue
        return get_global_queue
    raise AttributeError(f"module 'aipt_v2.llm' has no attribute '{name}'")
