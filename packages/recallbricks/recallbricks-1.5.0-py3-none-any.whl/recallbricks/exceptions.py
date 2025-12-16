"""
RecallBricks SDK Exceptions
Production API Error Format:
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message",
        "hint": "Helpful hint for resolution",
        "requestId": "uuid",
        "timestamp": "ISO timestamp"
    }
}
"""

from typing import Optional


class RecallBricksError(Exception):
    """Base exception for RecallBricks SDK"""

    def __init__(self, message: str, code: Optional[str] = None,
                 hint: Optional[str] = None, request_id: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.hint = hint
        self.request_id = request_id

    def __str__(self):
        parts = [self.message]
        if self.hint:
            parts.append(f"Hint: {self.hint}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " | ".join(parts)


class AuthenticationError(RecallBricksError):
    """Raised when API key is invalid or missing"""

    def __init__(self, message: str, code: Optional[str] = None,
                 hint: Optional[str] = None, request_id: Optional[str] = None):
        super().__init__(message, code, hint, request_id)


class RateLimitError(RecallBricksError):
    """Raised when rate limit is exceeded"""

    def __init__(self, message: str, retry_after: Optional[str] = None,
                 code: Optional[str] = None, hint: Optional[str] = None,
                 request_id: Optional[str] = None):
        super().__init__(message, code, hint, request_id)
        self.retry_after = retry_after


class APIError(RecallBricksError):
    """Raised when API returns an error"""

    def __init__(self, message: str, status_code: Optional[int] = None,
                 code: Optional[str] = None, hint: Optional[str] = None,
                 request_id: Optional[str] = None):
        super().__init__(message, code, hint, request_id)
        self.status_code = status_code


class ValidationError(RecallBricksError):
    """Raised when input validation fails"""

    def __init__(self, message: str, field: Optional[str] = None,
                 code: Optional[str] = None):
        super().__init__(message, code)
        self.field = field


class NotFoundError(APIError):
    """Raised when a resource is not found"""

    def __init__(self, message: str, resource_type: Optional[str] = None,
                 resource_id: Optional[str] = None, request_id: Optional[str] = None):
        super().__init__(message, status_code=404, code="NOT_FOUND", request_id=request_id)
        self.resource_type = resource_type
        self.resource_id = resource_id
