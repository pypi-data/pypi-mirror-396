"""
PrimeLLM Python SDK v0.2.0

Official Python client for the PrimeLLM unified AI API.
"""

from .client import PrimeLLM
from .errors import (
    PrimeLLMError,
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError,
)
from .tokenizer import count_tokens, set_tokenizer_adapter

__version__ = "0.2.0"
__all__ = [
    "PrimeLLM",
    "PrimeLLMError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "ServerError",
    "count_tokens",
    "set_tokenizer_adapter",
]
