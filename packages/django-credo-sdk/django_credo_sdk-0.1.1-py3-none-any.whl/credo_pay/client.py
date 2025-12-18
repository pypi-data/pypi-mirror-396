"""
Main Credo client class.

Provides a unified interface for all Credo SDK operations.
"""

from typing import Optional, List, Dict, Any, Callable

from .config import CredoConfig
from .services.payment import PaymentService
from .services.webhook import WebhookService
from .models import (
    PaymentResponse,
    VerifyResponse,
    WebhookEvent,
)


class CredoClient:
    """
    Main client for interacting with Credo Payment Gateway.
    
    Provides a simple, unified interface for:
    - Initializing payments
    - Verifying transactions
    - Handling webhooks
    - Payment routing with service codes
    
    Usage:
        # Initialize with Django settings
        client = CredoClient()
        
        # Or with custom config
        config = CredoConfig(
            public_key="your-public-key",
            secret_key="your-secret-key",
            environment="sandbox"
        )
        client = CredoClient(config)
        
        # Initialize a payment
        response = client.initialize_payment(
            amount=15000,
            email="customer@example.com",
            callback_url="https://yoursite.com/callback/"
        )
        
        # Redirect customer to payment page
        redirect_url = response.authorization_url
        
        # Later, verify the payment
        result = client.verify_payment(response.trans_ref)
        if result.is_successful:
            print("Payment confirmed!")
    """
    
    def __init__(self, config: Optional[CredoConfig] = None):
        """
        Initialize Credo client.
        
        Args:
            config: Optional CredoConfig instance. If not provided,
                   configuration is loaded from Django settings.
        """
        if config is None:
            config = CredoConfig.from_django_settings()
        
        config.validate()
        
        self.config = config
        self._payment_service = PaymentService(config)
        self._webhook_service = WebhookService(config)
    
    # ==================== Payment Methods ====================
    
    def initialize_payment(
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
        
        Creates a payment session and returns a URL to redirect
        the customer to complete payment.
        
        Args:
            amount: Amount to charge (e.g., 15000 for ₦15,000)
            email: Customer's email address
            callback_url: URL to redirect after payment
            currency: Currency code (default: NGN)
            reference: Your unique reference (auto-generated if not provided)
            channels: Payment channels ['card', 'bank'] or subset
            first_name: Customer's first name
            last_name: Customer's last name
            phone_number: Customer's phone number
            service_code: Service code for payment routing
            bank_account: Bank account for payment routing
            metadata: Additional data to store with transaction
            custom_fields: Custom field list for metadata
            bearer: Who pays fees (0 = merchant, 1 = customer)
            
        Returns:
            PaymentResponse with authorization_url to redirect customer
            
        Example:
            response = client.initialize_payment(
                amount=15000,
                email="john@example.com",
                callback_url="https://yoursite.com/payment/callback/"
            )
            
            # Redirect to response.authorization_url
        """
        return self._payment_service.initialize(
            amount=amount,
            email=email,
            callback_url=callback_url,
            currency=currency,
            reference=reference,
            channels=channels,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            service_code=service_code,
            bank_account=bank_account,
            metadata=metadata,
            custom_fields=custom_fields,
            bearer=bearer,
        )
    
    def verify_payment(self, reference: str) -> VerifyResponse:
        """
        Verify a payment transaction status.
        
        Use this to confirm payment status after callback or webhook.
        
        Args:
            reference: Transaction reference (transRef from Credo)
            
        Returns:
            VerifyResponse with transaction details and status
            
        Example:
            result = client.verify_payment("JunW00GkHm01vo0N96pk")
            
            if result.is_successful:
                print(f"Paid: {result.trans_amount} {result.currency_code}")
            elif result.is_failed:
                print(f"Failed: {result.status_description}")
        """
        return self._payment_service.verify(reference)
    
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
        Initialize a payment routed to a specific destination.
        
        Use this for multi-destination payment scenarios like:
        - Property management (tenants paying to different property accounts)
        - Marketplace payouts
        - Split payments
        
        Args:
            amount: Amount to charge
            email: Customer's email
            service_code: Service code for routing (from Credo dashboard)
            bank_account: Destination bank account number
            callback_url: Redirect URL after payment
            **kwargs: Additional arguments (first_name, last_name, etc.)
            
        Returns:
            PaymentResponse with authorization_url
            
        Example:
            # Tenant paying rent for Property A
            response = client.initialize_routed_payment(
                amount=150000,
                email="tenant@example.com",
                service_code="PROPERTY_A_SERVICE_CODE",
                bank_account="0123456789",
                callback_url="https://yoursite.com/rent/callback/",
                first_name="John",
                last_name="Tenant"
            )
        """
        return self._payment_service.initialize_routed_payment(
            amount=amount,
            email=email,
            service_code=service_code,
            bank_account=bank_account,
            callback_url=callback_url,
            **kwargs
        )
    
    # ==================== Webhook Methods ====================
    
    def verify_webhook_signature(self, signature: str) -> bool:
        """
        Verify a webhook signature.
        
        Args:
            signature: X-Credo-Signature header value
            
        Returns:
            True if signature is valid
        """
        return self._webhook_service.verify_signature(signature)
    
    def parse_webhook(
        self,
        payload: bytes | str | Dict[str, Any]
    ) -> WebhookEvent:
        """
        Parse a webhook payload into WebhookEvent object.
        
        Args:
            payload: Raw webhook payload
            
        Returns:
            Parsed WebhookEvent
        """
        return self._webhook_service.parse_event(payload)
    
    def process_webhook(
        self,
        payload: bytes | str | Dict[str, Any],
        signature: str,
        verify: bool = True,
        use_payload_business_code: bool = False
    ) -> WebhookEvent:
        """
        Process a complete webhook request.
        
        Verifies signature, parses payload, and runs registered handlers.
        
        Args:
            payload: Raw webhook payload
            signature: X-Credo-Signature header value
            verify: Whether to verify signature (default: True)
            use_payload_business_code: If True, always extract business code from payload
                                       for signature verification instead of using config.
                                       Recommended per Credo docs since businessCode is
                                       included in every webhook payload.
            
        Returns:
            Parsed WebhookEvent
            
        Example:
            event = client.process_webhook(
                payload=request.body,
                signature=request.headers.get("X-Credo-Signature"),
                use_payload_business_code=True  # Extract business code from payload
            )
            
            if event.is_successful:
                order = Order.objects.get(reference=event.business_ref)
                order.mark_paid()
        """
        return self._webhook_service.process_webhook(
            payload, signature, verify, use_payload_business_code
        )
    
    def register_webhook_handler(
        self,
        event_type: str,
        handler: Callable[[WebhookEvent], None]
    ) -> None:
        """
        Register a handler for webhook events.
        
        Args:
            event_type: Event type to handle:
                - 'transaction.successful'
                - 'transaction.failed'
                - 'transaction.settlement.success'
            handler: Function that receives WebhookEvent
            
        Example:
            def on_payment_success(event):
                order = Order.objects.get(reference=event.business_ref)
                order.status = "paid"
                order.save()
            
            client.register_webhook_handler(
                "transaction.successful",
                on_payment_success
            )
        """
        self._webhook_service.register_handler(event_type, handler)
    
    # ==================== Utility Methods ====================
    
    def generate_reference(self) -> str:
        """Generate a unique transaction reference."""
        return self._payment_service.generate_reference()
    
    @property
    def is_production(self) -> bool:
        """Check if client is configured for production."""
        return self.config.is_production
    
    @property
    def inline_script_url(self) -> str:
        """Get the Credo inline payment script URL."""
        return self.config.inline_script_url
