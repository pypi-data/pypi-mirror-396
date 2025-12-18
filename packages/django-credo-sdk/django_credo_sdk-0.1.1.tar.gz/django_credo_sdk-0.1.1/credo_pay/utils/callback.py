"""
Callback URL utilities for handling Credo payment redirects.

When Credo completes a payment (success or failure), it redirects
the customer back to your callback URL with query parameters containing
the transaction result.
"""

from urllib.parse import urlencode, urlparse, parse_qs
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class CallbackData:
    """
    Parsed callback data from Credo redirect.
    
    When Credo redirects to your callback URL, it includes these query params:
    - status: Transaction status code (0 = success)
    - errorMessage: Description (e.g., "Approved")
    - transRef: Credo's transaction reference
    - transAmount: Transaction amount
    - currency: Currency code
    - reference: Your business reference
    """
    status: int
    error_message: str
    trans_ref: str
    trans_amount: float
    currency: str
    reference: str
    raw_params: Dict[str, Any]
    
    @property
    def is_successful(self) -> bool:
        """Check if transaction was successful."""
        return self.status == 0
    
    @property
    def is_approved(self) -> bool:
        """Check if transaction was approved."""
        return self.error_message.lower() == "approved"
    
    @classmethod
    def from_url(cls, url: str) -> "CallbackData":
        """
        Parse callback data from a full URL.
        
        Args:
            url: Full callback URL with query parameters
            
        Returns:
            CallbackData instance
            
        Example:
            data = CallbackData.from_url(
                "https://example.com/callback?status=0&errorMessage=Approved&transRef=abc123"
            )
        """
        parsed = urlparse(url)
        return cls.from_query_string(parsed.query)
    
    @classmethod
    def from_query_string(cls, query_string: str) -> "CallbackData":
        """
        Parse callback data from query string.
        
        Args:
            query_string: Query string without the leading '?'
            
        Returns:
            CallbackData instance
        """
        params = parse_qs(query_string)
        
        # Helper to get first value from list or default
        def get_param(key: str, default: str = "") -> str:
            values = params.get(key, [default])
            return values[0] if values else default
        
        return cls(
            status=int(get_param("status", "0")),
            error_message=get_param("errorMessage", ""),
            trans_ref=get_param("transRef", ""),
            trans_amount=float(get_param("transAmount", "0")),
            currency=get_param("currency", "NGN"),
            reference=get_param("reference", ""),
            raw_params={k: v[0] if len(v) == 1 else v for k, v in params.items()},
        )
    
    @classmethod
    def from_request(cls, request) -> "CallbackData":
        """
        Parse callback data from Django request.
        
        Args:
            request: Django HttpRequest or DRF Request
            
        Returns:
            CallbackData instance
            
        Example:
            def callback_view(request):
                data = CallbackData.from_request(request)
                if data.is_successful:
                    # Handle success
                    pass
        """
        # Support both Django and DRF requests
        params = getattr(request, 'query_params', None) or request.GET
        
        return cls(
            status=int(params.get("status", 0)),
            error_message=params.get("errorMessage", ""),
            trans_ref=params.get("transRef", ""),
            trans_amount=float(params.get("transAmount", 0)),
            currency=params.get("currency", "NGN"),
            reference=params.get("reference", ""),
            raw_params=dict(params),
        )


def build_callback_url(
    base_url: str,
    success_path: Optional[str] = None,
    failure_path: Optional[str] = None,
    extra_params: Optional[Dict[str, str]] = None
) -> str:
    """
    Build a callback URL with optional path and parameters.
    
    Note: Credo will append its own query parameters to this URL
    when redirecting the customer back.
    
    Args:
        base_url: Base URL of your site
        success_path: Path for the callback endpoint
        failure_path: Not used (Credo uses same URL for success/failure)
        extra_params: Additional query parameters to include
        
    Returns:
        Complete callback URL
        
    Example:
        url = build_callback_url(
            "https://example.com",
            success_path="/payment/complete/",
            extra_params={"order_id": "12345"}
        )
        # Returns: https://example.com/payment/complete/?order_id=12345
    """
    # Remove trailing slash from base
    base_url = base_url.rstrip("/")
    
    # Add path
    if success_path:
        path = success_path.strip("/")
        url = f"{base_url}/{path}/"
    else:
        url = f"{base_url}/"
    
    # Add extra params
    if extra_params:
        url = f"{url}?{urlencode(extra_params)}"
    
    return url
