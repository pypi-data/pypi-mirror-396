"""
PrimeLLM Token Counter

Simple token estimation using chars/4 approximation.
Provides adapter point for future tiktoken integration.
"""

from typing import List, Dict, Callable, Optional, Union

# Token counter adapter type
TokenizerAdapter = Callable[[str], int]

# Current tokenizer adapter
_tokenizer_adapter: Optional[TokenizerAdapter] = None


def count_tokens(input: Union[str, List[Dict[str, str]]]) -> int:
    """
    Count tokens in text or messages array.
    
    Args:
        input: Text string or list of message dicts with 'content' key
        
    Returns:
        Estimated token count
        
    Example:
        count_tokens("Hello world")  # ~3
        count_tokens([{"role": "user", "content": "Hello"}])  # ~2
    """
    if isinstance(input, list):
        text = " ".join(m.get("content", "") for m in input if isinstance(m, dict))
    else:
        text = input
    
    # Use custom adapter if set
    if _tokenizer_adapter:
        return _tokenizer_adapter(text)
    
    # Default: chars / 4 (simple approximation)
    chars = len(text)
    return max(1, (chars + 3) // 4)


def set_tokenizer_adapter(adapter: Optional[TokenizerAdapter]) -> None:
    """
    Set custom tokenizer adapter (for tiktoken or other).
    
    Args:
        adapter: Function that takes text and returns token count, or None to reset
        
    Example:
        import tiktoken
        enc = tiktoken.encoding_for_model("gpt-4")
        set_tokenizer_adapter(lambda text: len(enc.encode(text)))
    """
    global _tokenizer_adapter
    _tokenizer_adapter = adapter


def get_tokenizer_adapter() -> Optional[TokenizerAdapter]:
    """Get current tokenizer adapter"""
    return _tokenizer_adapter


def reset_tokenizer() -> None:
    """Reset tokenizer to default (chars/4)"""
    global _tokenizer_adapter
    _tokenizer_adapter = None
