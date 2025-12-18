"""
Input validation utilities for Credo SDK.
"""

import re
from typing import Optional
from ..exceptions import CredoValidationError


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid
        
    Raises:
        CredoValidationError: If email is invalid
    """
    if not email:
        raise CredoValidationError("Email is required", field="email")
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise CredoValidationError("Invalid email format", field="email")
    
    return True


def validate_amount(amount: float, currency: str = "NGN") -> bool:
    """
    Validate payment amount.
    
    Args:
        amount: Amount to validate
        currency: Currency code
        
    Returns:
        True if valid
        
    Raises:
        CredoValidationError: If amount is invalid
    """
    if amount <= 0:
        raise CredoValidationError("Amount must be greater than 0", field="amount")
    
    # NGN minimum is typically 100 Naira
    if currency == "NGN" and amount < 100:
        raise CredoValidationError(
            "Minimum amount for NGN is 100",
            field="amount"
        )
    
    return True


def validate_reference(reference: str) -> bool:
    """
    Validate transaction reference.
    
    References must be alphanumeric only.
    
    Args:
        reference: Transaction reference to validate
        
    Returns:
        True if valid
        
    Raises:
        CredoValidationError: If reference is invalid
    """
    if not reference:
        return True  # Reference is optional
    
    if not re.match(r'^[a-zA-Z0-9]+$', reference):
        raise CredoValidationError(
            "Reference must be alphanumeric only",
            field="reference"
        )
    
    return True


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid
        
    Raises:
        CredoValidationError: If phone is invalid
    """
    if not phone:
        return True  # Phone is optional
    
    # Remove spaces and dashes
    cleaned = re.sub(r'[\s-]', '', phone)
    
    # Should be digits, optionally starting with +
    if not re.match(r'^\+?\d{10,15}$', cleaned):
        raise CredoValidationError(
            "Invalid phone number format",
            field="phone_number"
        )
    
    return True


def validate_url(url: str, field_name: str = "url") -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        field_name: Name of the field for error messages
        
    Returns:
        True if valid
        
    Raises:
        CredoValidationError: If URL is invalid
    """
    if not url:
        raise CredoValidationError(f"{field_name} is required", field=field_name)
    
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url, re.IGNORECASE):
        raise CredoValidationError(
            f"Invalid URL format for {field_name}",
            field=field_name
        )
    
    return True


def validate_channels(channels: list) -> bool:
    """
    Validate payment channels.
    
    Args:
        channels: List of payment channels
        
    Returns:
        True if valid
        
    Raises:
        CredoValidationError: If channels are invalid
    """
    if not channels:
        raise CredoValidationError(
            "At least one payment channel is required",
            field="channels"
        )
    
    valid_channels = {"card", "bank"}
    for channel in channels:
        if channel not in valid_channels:
            raise CredoValidationError(
                f"Invalid channel: {channel}. Must be 'card' or 'bank'",
                field="channels"
            )
    
    return True
