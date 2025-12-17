"""
PrimeLLM Streaming Utilities

Generator for streaming chat completions via SSE.
"""

import json
from typing import Iterator, Dict, Any, Optional


def parse_sse_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse SSE data line to chunk dict"""
    if not line.startswith("data:"):
        return None
    
    data = line[5:].strip()
    if not data or data == "[DONE]":
        return None
    
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def stream_reader(response) -> Iterator[Dict[str, Any]]:
    """
    Create generator from SSE response stream.
    
    Args:
        response: httpx Response object with streaming content
        
    Yields:
        Chunk dictionaries from SSE events
    """
    buffer = ""
    
    for chunk in response.iter_bytes():
        buffer += chunk.decode("utf-8", errors="ignore")
        
        # Process complete lines
        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)
            line = line.strip()
            
            if not line:
                continue
            
            parsed = parse_sse_line(line)
            if parsed:
                yield parsed
                
                # Check for done
                if parsed.get("object") == "chat.completion.done" or parsed.get("done"):
                    return
    
    # Process remaining buffer
    if buffer.strip():
        parsed = parse_sse_line(buffer.strip())
        if parsed:
            yield parsed
