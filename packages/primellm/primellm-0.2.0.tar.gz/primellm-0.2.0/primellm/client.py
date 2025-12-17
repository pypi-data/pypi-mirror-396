"""
PrimeLLM Python SDK v0.2.0

Production-grade SDK with streaming, retries, and full API parity.

Example:
    from primellm import PrimeLLM
    
    client = PrimeLLM(api_key="primellm_XXX")
    response = client.chat.create(
        model="gpt-5.1",
        messages=[{"role": "user", "content": "Hello!"}],
    )
    print(response["choices"][0]["message"]["content"])
"""

from __future__ import annotations

import os
import time
import random
from typing import Any, Dict, List, Optional, Iterator, Union

import httpx

from .errors import (
    PrimeLLMError,
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
    create_error_from_status,
)
from .tokenizer import count_tokens, set_tokenizer_adapter
from .streaming import stream_reader


# Retryable status codes
RETRYABLE_STATUSES = [429, 502, 503, 504]

# Default retry config
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 0.3  # 300ms
DEFAULT_MAX_DELAY = 10.0  # 10s


class PrimeLLM:
    """
    PrimeLLM API Client
    
    Production-grade client with streaming, retries, and full API access.
    
    Args:
        api_key: Your PrimeLLM API key. If not provided, reads from
                 PRIMELLM_API_KEY environment variable.
        base_url: API base URL. Default: https://api.primellm.in
        timeout: Request timeout in seconds. Default: 60
        max_retries: Max retry attempts for failed requests. Default: 3
    
    Example:
        client = PrimeLLM(api_key="primellm_XXX")
        response = client.chat.create(model="gpt-5.1", messages=[...])
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.primellm.in",
        timeout: float = 60.0,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        self.api_key = api_key or os.getenv("PRIMELLM_API_KEY")
        if not self.api_key:
            raise PrimeLLMError(
                "PrimeLLM API key is required. "
                "Pass api_key=... or set PRIMELLM_API_KEY env var."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize sub-clients
        self.chat = ChatClient(self)
        self.embeddings = EmbeddingsClient(self)
        self.models = ModelsClient(self)
        self.keys = KeysClient(self)
        self.credits = CreditsClient(self)
        self.tokens = TokensClient()
    
    def _headers(self) -> Dict[str, str]:
        """Build request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def _sleep_with_backoff(self, attempt: int) -> None:
        """Sleep with exponential backoff and jitter."""
        delay = min(
            DEFAULT_MAX_DELAY,
            DEFAULT_BASE_DELAY * (2 ** attempt) + random.uniform(0.1, 0.3)
        )
        time.sleep(delay)
    
    def request(
        self,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        method: str = "POST",
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retries and error handling.
        
        Args:
            path: API endpoint path
            body: Request body (for POST)
            method: HTTP method (GET, POST)
            
        Returns:
            Parsed JSON response
            
        Raises:
            PrimeLLMError: On request failure
        """
        url = f"{self.base_url}{path}"
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    if method == "GET":
                        res = client.get(url, headers=self._headers())
                    else:
                        res = client.post(url, json=body or {}, headers=self._headers())
                
                if res.status_code // 100 == 2:
                    return res.json()
                
                # Parse error
                detail = res.text
                try:
                    err_json = res.json()
                    detail = err_json.get("detail", detail)
                except:
                    pass
                
                # Check if retryable
                if res.status_code in RETRYABLE_STATUSES and attempt < self.max_retries - 1:
                    last_error = create_error_from_status(res.status_code, f"Request failed: {res.status_code}", detail)
                    self._sleep_with_backoff(attempt)
                    continue
                
                raise create_error_from_status(res.status_code, f"PrimeLLM API error: {res.status_code}", detail)
                
            except httpx.RequestError as exc:
                if attempt < self.max_retries - 1:
                    last_error = PrimeLLMError(f"Request failed: {exc}")
                    self._sleep_with_backoff(attempt)
                    continue
                raise PrimeLLMError(f"Request failed after {self.max_retries} attempts: {exc}") from exc
        
        raise last_error or PrimeLLMError("Request failed after retries")
    
    def stream_request(
        self,
        path: str,
        body: Dict[str, Any],
    ) -> Iterator[Dict[str, Any]]:
        """
        Make streaming HTTP request.
        
        Args:
            path: API endpoint path
            body: Request body with stream=true
            
        Yields:
            Chunk dictionaries from SSE events
        """
        url = f"{self.base_url}{path}"
        body = {**body, "stream": True}
        
        with httpx.Client(timeout=self.timeout) as client:
            with client.stream("POST", url, json=body, headers=self._headers()) as res:
                if res.status_code // 100 != 2:
                    res.read()
                    detail = res.text
                    try:
                        err_json = res.json()
                        detail = err_json.get("detail", detail)
                    except:
                        pass
                    raise create_error_from_status(res.status_code, f"Streaming failed: {res.status_code}", detail)
                
                yield from stream_reader(res)


class ChatClient:
    """Chat sub-client"""
    
    def __init__(self, client: PrimeLLM):
        self._client = client
    
    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create a chat completion.
        
        Args:
            model: Model name (e.g., "gpt-5.1")
            messages: List of message dicts with "role" and "content"
            **kwargs: Extra parameters (temperature, max_tokens, etc.)
            
        Returns:
            Chat completion response dict
        """
        payload = {"model": model, "messages": messages, **kwargs}
        return self._client.request("/v1/chat", payload)
    
    def stream(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs: Any,
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream chat completion.
        
        Args:
            model: Model name
            messages: List of message dicts
            **kwargs: Extra parameters
            
        Yields:
            Chunk dicts with delta content
        """
        payload = {"model": model, "messages": messages, **kwargs}
        yield from self._client.stream_request("/v1/chat", payload)


class EmbeddingsClient:
    """Embeddings sub-client"""
    
    def __init__(self, client: PrimeLLM):
        self._client = client
    
    def create(
        self,
        input: Union[str, List[str]],
        model: str = "embed-1",
    ) -> Dict[str, Any]:
        """
        Create embeddings for input text.
        
        Args:
            input: Text or list of texts to embed
            model: Embedding model name
            
        Returns:
            Embeddings response with data array
        """
        payload = {"model": model, "input": input}
        return self._client.request("/v1/embeddings", payload)


class ModelsClient:
    """Models sub-client"""
    
    def __init__(self, client: PrimeLLM):
        self._client = client
    
    def list(self) -> Dict[str, Any]:
        """List available models."""
        return self._client.request("/v1/models", method="GET")


class KeysClient:
    """API Keys sub-client"""
    
    def __init__(self, client: PrimeLLM):
        self._client = client
    
    def list(self) -> Dict[str, Any]:
        """List API keys."""
        return self._client.request("/v1/keys", method="GET")
    
    def create(self, label: Optional[str] = None) -> Dict[str, Any]:
        """Create a new API key."""
        return self._client.request("/v1/keys", {"label": label})
    
    def revoke(self, key_id: int) -> Dict[str, Any]:
        """Revoke an API key."""
        return self._client.request("/v1/keys/revoke", {"key_id": key_id})


class CreditsClient:
    """Credits sub-client"""
    
    def __init__(self, client: PrimeLLM):
        self._client = client
    
    def get(self) -> Dict[str, Any]:
        """Get current credit balance."""
        return self._client.request("/v1/credits", method="GET")


class TokensClient:
    """Token counting utility"""
    
    def count(self, input: Union[str, List[Dict[str, str]]]) -> int:
        """
        Count tokens in text or messages.
        
        Args:
            input: Text string or list of message dicts
            
        Returns:
            Estimated token count
        """
        return count_tokens(input)
    
    def set_adapter(self, adapter) -> None:
        """Set custom tokenizer adapter."""
        set_tokenizer_adapter(adapter)
