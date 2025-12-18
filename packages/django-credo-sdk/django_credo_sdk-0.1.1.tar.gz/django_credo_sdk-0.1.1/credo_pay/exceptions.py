"""
Custom exceptions for the Credo SDK.

All exceptions inherit from CredoError for easy catching.
"""

from typing import Optional, Dict, Any


class CredoError(Exception):
    """Base exception for all Credo SDK errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class CredoConfigError(CredoError):
    """Raised when there's a configuration error."""
    pass


class CredoAPIError(CredoError):
    """
    Raised when the Credo API returns an error.
    
    Attributes:
        status_code: HTTP status code from the API
        response_data: Full response data from the API
    """
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(message, {"status_code": status_code, "response": response_data})


class CredoValidationError(CredoError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        details = {"field": field} if field else {}
        super().__init__(message, details)


class CredoWebhookError(CredoError):
    """Raised when webhook verification or processing fails."""
    pass


class CredoPaymentError(CredoError):
    """Raised when a payment operation fails."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        trans_ref: Optional[str] = None
    ):
        self.status_code = status_code
        self.trans_ref = trans_ref
        super().__init__(message, {"status_code": status_code, "trans_ref": trans_ref})
