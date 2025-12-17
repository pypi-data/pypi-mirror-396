"""
PrimeLLM SDK Error Classes

Typed errors for better error handling in applications.
"""


class PrimeLLMError(Exception):
    """Base error class for all PrimeLLM SDK errors"""
    
    def __init__(self, message: str, status: int = None, detail: str = None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.detail = detail


class AuthenticationError(PrimeLLMError):
    """Authentication failed (401)"""
    
    def __init__(self, message: str = "Invalid or missing API key", **kwargs):
        super().__init__(message, status=401, **kwargs)


class InsufficientCreditsError(PrimeLLMError):
    """Insufficient credits (402)"""
    
    def __init__(self, message: str = "Insufficient credits", **kwargs):
        super().__init__(message, status=402, **kwargs)


class RateLimitError(PrimeLLMError):
    """Rate limit exceeded (429)"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None, **kwargs):
        super().__init__(message, status=429, **kwargs)
        self.retry_after = retry_after


class NotFoundError(PrimeLLMError):
    """Resource not found (404)"""
    
    def __init__(self, message: str = "Resource not found", **kwargs):
        super().__init__(message, status=404, **kwargs)


class ValidationError(PrimeLLMError):
    """Validation error (400)"""
    
    def __init__(self, message: str = "Invalid request", **kwargs):
        super().__init__(message, status=400, **kwargs)


class ServerError(PrimeLLMError):
    """Server error (5xx)"""
    
    def __init__(self, message: str = "Server error", **kwargs):
        super().__init__(message, status=500, **kwargs)


def create_error_from_status(status: int, message: str, detail: str = None) -> PrimeLLMError:
    """Map HTTP status code to appropriate error class"""
    if status == 400:
        return ValidationError(message, detail=detail)
    elif status == 401:
        return AuthenticationError(message, detail=detail)
    elif status == 402:
        return InsufficientCreditsError(message, detail=detail)
    elif status == 404:
        return NotFoundError(message, detail=detail)
    elif status == 429:
        return RateLimitError(message, detail=detail)
    elif status >= 500:
        return ServerError(message, detail=detail)
    else:
        return PrimeLLMError(message, status=status, detail=detail)
