"""
Payment service for handling Credo transactions.

Handles payment initialization, verification, and status queries.
"""

import uuid
import requests
from typing import Optional, List, Dict, Any

from ..config import CredoConfig
from ..models import (
    PaymentRequest,
    PaymentResponse,
    VerifyResponse,
    Customer,
    PaymentMetadata,
    CustomField,
    FeeBearer,
)
from ..exceptions import CredoAPIError, CredoValidationError
from ..utils.validators import (
    validate_email,
    validate_amount,
    validate_reference,
    validate_url,
    validate_channels,
)


class PaymentService:
    """
    Service for handling payment operations.
    
    Provides methods for initializing payments, verifying transactions,
    and handling payment routing with service codes.
    
    Usage:
        config = CredoConfig.from_django_settings()
        service = PaymentService(config)
        
        # Initialize a simple payment
        response = service.initialize(
            amount=15000,
            email="customer@example.com",
            callback_url="https://yoursite.com/callback/"
        )
        
        # Verify a payment
        result = service.verify("transaction-reference")
    """
    
    def __init__(self, config: CredoConfig):
        """
        Initialize payment service.
        
        Args:
            config: CredoConfig instance with API credentials
        """
        self.config = config
        self._session = requests.Session()
    
    def _get_headers(self, use_secret_key: bool = False) -> Dict[str, str]:
        """Get request headers with authorization."""
        key = self.config.secret_key if use_secret_key else self.config.public_key
        return {
            "Authorization": key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        use_secret_key: bool = False
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the Credo API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            data: Request payload for POST requests
            use_secret_key: Whether to use secret key for auth
            
        Returns:
            Parsed JSON response
            
        Raises:
            CredoAPIError: If the API returns an error
        """
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers(use_secret_key)
        
        try:
            response = self._session.request(
                method=method.upper(),
                url=url,
                json=data,
                headers=headers,
                timeout=30,
            )
            
            response_data = response.json()
            
            if response.status_code >= 400:
                raise CredoAPIError(
                    message=response_data.get("message", "API request failed"),
                    status_code=response.status_code,
                    response_data=response_data,
                )
            
            return response_data
            
        except requests.exceptions.Timeout:
            raise CredoAPIError("Request timeout - please try again")
        except requests.exceptions.ConnectionError:
            raise CredoAPIError("Connection error - please check your internet connection")
        except requests.exceptions.JSONDecodeError:
            raise CredoAPIError("Invalid response from Credo API")
    
    def generate_reference(self) -> str:
        """Generate a unique transaction reference."""
        return uuid.uuid4().hex[:20]
    
    def initialize(
        self,
        amount: float,
        email: str,
        callback_url: Optional[str] = None,
        currency: str = "NGN",
        reference: Optional[str] = None,
        channels: Optional[List[str]] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        service_code: Optional[str] = None,
        bank_account: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        custom_fields: Optional[List[Dict[str, str]]] = None,
        bearer: int = 0,
    ) -> PaymentResponse:
        """
        Initialize a payment transaction.
        
        This creates a payment session and returns a URL to redirect
        the customer to complete the payment.
        
        Args:
            amount: Amount to charge (in main currency unit, e.g., Naira)
            email: Customer's email address
            callback_url: URL to redirect after payment (uses default if not provided)
            currency: Currency code (default: NGN)
            reference: Your unique transaction reference (auto-generated if not provided)
            channels: Payment channels to enable (default: ['card', 'bank'])
            first_name: Customer's first name
            last_name: Customer's last name
            phone_number: Customer's phone number
            service_code: Service code for dynamic settlement routing
            bank_account: Bank account for payment routing
            metadata: Additional metadata dictionary
            custom_fields: List of custom field dicts with variable_name, value, display_name
            bearer: Who bears the transaction fee:
                    0 = Customer bears the fee (default)
                    1 = Merchant bears the fee
                    Use FeeBearer.CUSTOMER or FeeBearer.MERCHANT for clarity
            
        Returns:
            PaymentResponse with authorization URL and transaction reference
            
        Raises:
            CredoValidationError: If input validation fails
            CredoAPIError: If the API returns an error
            
        Example:
            # Simple payment (customer pays fee)
            response = service.initialize(
                amount=15000,
                email="customer@example.com",
                callback_url="https://yoursite.com/callback/"
            )
            
            # Payment where merchant bears the fee
            response = service.initialize(
                amount=25000,
                email="customer@example.com",
                callback_url="https://yoursite.com/callback/",
                bearer=FeeBearer.MERCHANT  # or bearer=1
            )
            
            # Payment with routing to specific bank account
            response = service.initialize(
                amount=25000,
                email="tenant@example.com",
                callback_url="https://yoursite.com/callback/",
                service_code="PROPERTY_001",
                bank_account="0114877128",
                metadata={"property_id": "PROP-123"}
            )
        """
        # Validate inputs
        validate_email(email)
        validate_amount(amount, currency)
        
        # Use default callback URL if not provided
        final_callback_url = callback_url or self.config.default_callback_url
        validate_url(final_callback_url, "callback_url")
        
        if reference:
            validate_reference(reference)
        else:
            reference = self.generate_reference()
        
        # Use config default channels if not provided
        final_channels = channels or self.config.default_channels or ["card", "bank"]
        validate_channels(final_channels)
        
        # Build customer object
        customer = None
        if first_name or last_name or phone_number:
            customer = Customer(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
            )
        
        # Build metadata object
        payment_metadata = None
        if bank_account or metadata or custom_fields or self.config.logo_url:
            cf_objects = []
            if custom_fields:
                cf_objects = [
                    CustomField(
                        variable_name=cf["variable_name"],
                        value=cf["value"],
                        display_name=cf.get("display_name"),
                    )
                    for cf in custom_fields
                ]
            
            payment_metadata = PaymentMetadata(
                bank_account=bank_account,
                custom_fields=cf_objects,
                logo_url=self.config.logo_url or None,
                extra_data=metadata or {},
            )
        
        # Build payment request
        payment_request = PaymentRequest(
            amount=amount,
            email=email,
            callback_url=final_callback_url,
            currency=currency,
            reference=reference,
            channels=final_channels,
            customer=customer,
            metadata=payment_metadata,
            service_code=service_code,
            bearer=bearer,
        )
        
        # Make API request
        response_data = self._make_request(
            method="POST",
            endpoint="/transaction/initialize",
            data=payment_request.to_dict(),
            use_secret_key=False,  # Use public key for initialization
        )
        
        return PaymentResponse.from_api_response(response_data)
    
    def verify(self, reference: str) -> VerifyResponse:
        """
        Verify a payment transaction status.
        
        Use this to confirm the status of a payment, especially
        after receiving a callback or webhook.
        
        Args:
            reference: Transaction reference (transRef from Credo)
            
        Returns:
            VerifyResponse with full transaction details
            
        Raises:
            CredoAPIError: If the API returns an error
            
        Example:
            result = service.verify("JunW00GkHm01vo0N96pk")
            if result.is_successful:
                print(f"Payment of {result.trans_amount} was successful!")
        """
        if not reference:
            raise CredoValidationError("Transaction reference is required")
        
        response_data = self._make_request(
            method="GET",
            endpoint=f"/transaction/{reference}/verify",
            use_secret_key=True,  # Use secret key for verification
        )
        
        return VerifyResponse.from_api_response(response_data)
    
    def initialize_routed_payment(
        self,
        amount: float,
        email: str,
        service_code: str,
        bank_account: str,
        callback_url: Optional[str] = None,
        **kwargs
    ) -> PaymentResponse:
        """
        Initialize a payment with routing to a specific bank account.
        
        This is a convenience method for multi-destination payment scenarios
        where different payments need to be routed to different accounts
        (e.g., property management, marketplace payouts).
        
        Args:
            amount: Amount to charge
            email: Customer's email
            service_code: Service code for dynamic settlement
            bank_account: Destination bank account number
            callback_url: Redirect URL after payment
            **kwargs: Additional arguments passed to initialize()
            
        Returns:
            PaymentResponse with authorization URL
            
        Example:
            # Route payment for Property A to Account A
            response = service.initialize_routed_payment(
                amount=50000,
                email="tenant@example.com",
                service_code="PROPERTY_A_SERVICE",
                bank_account="1234567890",
                callback_url="https://yoursite.com/callback/",
                first_name="John",
                last_name="Doe"
            )
        """
        return self.initialize(
            amount=amount,
            email=email,
            service_code=service_code,
            bank_account=bank_account,
            callback_url=callback_url,
            **kwargs
        )
