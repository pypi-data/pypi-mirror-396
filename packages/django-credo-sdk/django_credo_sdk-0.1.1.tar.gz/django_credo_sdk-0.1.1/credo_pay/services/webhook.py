"""
Webhook service for handling Credo webhook events.

Provides signature verification and event parsing.

Webhook Events (per Credo docs):
- transaction.successful: Payment was successful (status=0)
- transaction.failed: Payment declined (status=7)
- transaction.settlement.success: Settlement completed (status=5)

Signature Verification:
X-Credo-Signature = SHA512(WEBHOOK_TOKEN + BUSINESS_CODE)
"""

import json
from typing import Callable, Dict, Any, Optional

from ..config import CredoConfig
from ..models import WebhookEvent
from ..exceptions import CredoWebhookError
from ..utils.signature import verify_webhook_signature


class WebhookService:
    """
    Service for handling Credo webhooks.
    
    Provides methods for verifying webhook signatures and
    parsing webhook payloads into typed objects.
    
    Webhook Structure (per Credo docs):
    {
        "event": "transaction.successful",
        "data": {
            "businessCode": "700607002190001",
            "transRef": "cI9H00N2AB02Qb0s69Mj",
            "businessRef": "PL1683423455304ATm",
            "debitedAmount": 1000.0,
            "transAmount": 1000.0,
            "transFeeAmount": 15.0,
            "settlementAmount": 985.0,
            "customerId": "email@example.com",
            "transactionDate": "May 7, 2023, 1:37:53 AM",
            "channelId": 1,
            "currencyCode": "NGN",
            "status": 0,
            "paymentMethodType": "MasterCard",
            "paymentMethod": "Card",
            "customer": {
                "customerEmail": "john.wick@yahoo.com",
                "firstName": "John",
                "lastName": "Wick",
                "phoneNo": "23470122199999"
            }
        }
    }
    
    Usage:
        config = CredoConfig.from_django_settings()
        webhook_service = WebhookService(config)
        
        # In your webhook view
        def webhook_view(request):
            signature = request.headers.get("X-Credo-Signature")
            
            if not webhook_service.verify_signature(signature):
                return HttpResponse(status=401)
            
            event = webhook_service.parse_event(request.body)
            
            if event.is_successful:
                # Handle successful payment
                pass
    """
    
    def __init__(self, config: CredoConfig):
        """
        Initialize webhook service.
        
        Args:
            config: CredoConfig instance with webhook credentials
        """
        self.config = config
        self._handlers: Dict[str, Callable[[WebhookEvent], None]] = {}
    
    def verify_signature(self, received_signature: str, business_code: Optional[str] = None) -> bool:
        """
        Verify webhook signature.
        
        Per Credo docs: X-Credo-Signature = SHA512(Token + Business_code)
        
        Args:
            received_signature: The X-Credo-Signature header value
            business_code: Optional business code (uses config if not provided)
            
        Returns:
            True if signature is valid
            
        Raises:
            CredoWebhookError: If verification credentials are missing
        """
        if not self.config.webhook_token:
            raise CredoWebhookError(
                "Webhook token not configured. "
                "Set CREDO_WEBHOOK_SECRET_TOKEN in settings. "
                "This is a token you create and register in Credo Dashboard > Settings > Webhooks."
            )
        
        # Use provided business_code or fall back to config
        biz_code = business_code or self.config.business_code
        
        # Business code can now be extracted from payload in process_webhook
        if not biz_code:
            # Return False instead of raising error - let caller try payload extraction
            return False
        
        return verify_webhook_signature(
            received_signature=received_signature,
            token=self.config.webhook_token,
            business_code=biz_code,
        )
    
    def verify_signature_from_payload(self, received_signature: str, payload: Dict[str, Any]) -> bool:
        """
        Verify webhook signature using business code from the payload.
        
        This is useful when you haven't configured CREDO_BUSINESS_CODE
        in settings, as the business code is included in every webhook payload.
        
        Args:
            received_signature: The X-Credo-Signature header value
            payload: The parsed webhook payload (must contain data.businessCode)
            
        Returns:
            True if signature is valid
        """
        if not self.config.webhook_token:
            raise CredoWebhookError(
                "Webhook token not configured. Set CREDO_WEBHOOK_SECRET_TOKEN in settings."
            )
        
        # Extract business code from payload
        data = payload.get("data", {})
        business_code = data.get("businessCode", "")
        
        if not business_code:
            raise CredoWebhookError(
                "Business code not found in webhook payload. Cannot verify signature."
            )
        
        return verify_webhook_signature(
            received_signature=received_signature,
            token=self.config.webhook_token,
            business_code=business_code,
        )
    
    def parse_event(self, payload: bytes | str | Dict[str, Any]) -> WebhookEvent:
        """
        Parse webhook payload into WebhookEvent object.
        
        Args:
            payload: Raw webhook payload (bytes, string, or dict)
            
        Returns:
            Parsed WebhookEvent object
            
        Raises:
            CredoWebhookError: If payload is invalid
        """
        try:
            if isinstance(payload, bytes):
                data = json.loads(payload.decode("utf-8"))
            elif isinstance(payload, str):
                data = json.loads(payload)
            else:
                data = payload
            
            return WebhookEvent.from_payload(data)
            
        except json.JSONDecodeError as e:
            raise CredoWebhookError(f"Invalid JSON payload: {str(e)}")
        except Exception as e:
            raise CredoWebhookError(f"Failed to parse webhook: {str(e)}")
    
    def register_handler(
        self,
        event_type: str,
        handler: Callable[[WebhookEvent], None]
    ) -> None:
        """
        Register a handler for a specific event type.
        
        Available event types (per Credo docs):
        - transaction.successful: Payment was successful
        - transaction.failed: Payment was declined
        - transaction.settlement.success: Settlement completed
        
        Args:
            event_type: Event type to handle
            handler: Callable that takes a WebhookEvent
            
        Example:
            def handle_success(event):
                print(f"Payment successful: {event.trans_ref}")
                # Update order status, send confirmation email, etc.
            
            webhook_service.register_handler(
                "transaction.successful",
                handle_success
            )
        """
        self._handlers[event_type] = handler
    
    def handle_event(self, event: WebhookEvent) -> bool:
        """
        Handle a webhook event using registered handlers.
        
        Args:
            event: Parsed WebhookEvent object
            
        Returns:
            True if handler was found and executed
        """
        handler = self._handlers.get(event.event)
        
        if handler:
            handler(event)
            return True
        
        return False
    
    def process_webhook(
        self,
        payload: bytes | str | Dict[str, Any],
        signature: str,
        verify: bool = True,
        use_payload_business_code: bool = False
    ) -> WebhookEvent:
        """
        Process a complete webhook request.
        
        Combines signature verification, parsing, and handler execution.
        
        Per Credo docs, the businessCode is included in every webhook payload,
        so this method will automatically extract it from the payload for
        signature verification if CREDO_BUSINESS_CODE is not configured.
        
        Args:
            payload: Raw webhook payload
            signature: X-Credo-Signature header value
            verify: Whether to verify signature (default: True)
            use_payload_business_code: If True, always extract business code from payload.
                                       If False, tries config first, then falls back to payload.
            
        Returns:
            Parsed WebhookEvent object
            
        Raises:
            CredoWebhookError: If signature is invalid or parsing fails
        """
        # Parse payload first - we need it for business code extraction
        if isinstance(payload, bytes):
            parsed_payload = json.loads(payload.decode("utf-8"))
        elif isinstance(payload, str):
            parsed_payload = json.loads(payload)
        else:
            parsed_payload = payload
        
        if verify:
            # This is the recommended approach per Credo docs, as businessCode
            # is included in every webhook payload
            if use_payload_business_code or not self.config.business_code:
                # Use business code from payload (recommended approach)
                if not self.verify_signature_from_payload(signature, parsed_payload):
                    raise CredoWebhookError("Invalid webhook signature")
            else:
                # Try config business code first
                if not self.verify_signature(signature):
                    # Fall back to payload business code
                    if not self.verify_signature_from_payload(signature, parsed_payload):
                        raise CredoWebhookError("Invalid webhook signature")
        
        event = self.parse_event(parsed_payload)
        self.handle_event(event)
        
        return event
