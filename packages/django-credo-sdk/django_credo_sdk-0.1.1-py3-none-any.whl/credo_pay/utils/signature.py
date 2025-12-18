"""
Signature utilities for webhook verification.

Implements SHA512 signature verification as specified by Credo.
"""

import hashlib
import hmac
from typing import Optional


def generate_webhook_signature(token: str, business_code: str) -> str:
    """
    Generate webhook signature for verification.
    
    The signature is SHA512(token + business_code) as per Credo documentation.
    
    Args:
        token: Your webhook token configured on Credo dashboard
        business_code: Your Credo business code
        
    Returns:
        SHA512 hash string
    """
    content = f"{token}{business_code}"
    return hashlib.sha512(content.encode()).hexdigest()


def verify_webhook_signature(
    received_signature: str,
    token: str,
    business_code: str
) -> bool:
    """
    Verify that a webhook signature is valid.
    
    Args:
        received_signature: The X-Credo-Signature header value
        token: Your webhook token configured on Credo dashboard
        business_code: Your Credo business code
        
    Returns:
        True if signature is valid, False otherwise
    """
    if not received_signature or not token or not business_code:
        return False
    
    expected_signature = generate_webhook_signature(token, business_code)
    
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(
        received_signature.lower(),
        expected_signature.lower()
    )
