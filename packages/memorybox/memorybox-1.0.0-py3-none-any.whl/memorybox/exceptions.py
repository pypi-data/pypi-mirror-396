"""
Memory Box SDK - Exceptions
Custom exception classes for the Memory Box SDK
"""


class MemoryBoxError(Exception):
    """Base exception for Memory Box SDK errors."""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)
    
    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(MemoryBoxError):
    """
    Raised when authentication fails.
    This usually means the API key is invalid, expired, or revoked.
    """
    pass


class NotFoundError(MemoryBoxError):
    """
    Raised when a requested resource is not found.
    """
    pass


class RateLimitError(MemoryBoxError):
    """
    Raised when the API rate limit is exceeded.
    """
    
    def __init__(self, message: str, retry_after: int = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ValidationError(MemoryBoxError):
    """
    Raised when request validation fails.
    This includes missing required fields or invalid field values.
    """
    
    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(message, **kwargs)
        self.field = field


class ServerError(MemoryBoxError):
    """
    Raised when the server returns an unexpected error.
    """
    pass


class PermissionError(MemoryBoxError):
    """
    Raised when the API key doesn't have sufficient permissions.
    For example, using a read-only key for write operations.
    """
    pass

