"""
Credo Payment SDK for Django/Django REST Framework

A plug-and-play SDK for integrating Credo payment gateway into Django projects.
Supports both simple payments and multi-destination routing with service codes.

Usage:
    from credo_pay import CredoClient
    
    client = CredoClient()
    response = client.initialize_payment(
        amount=15000,
        email="customer@example.com",
        callback_url="https://yoursite.com/api/credo/webhook/"
    )
    
Webhook Handling:
    The SDK provides a unified CredoWebhookView that handles both:
    - GET requests: Customer redirect after payment (callback with query params)
    - POST requests: Server-to-server webhook notifications (JSON with signature)
    
    Subclass CredoWebhookView to implement custom logic:
    
    from credo_pay.views import CredoWebhookView
    
    class MyWebhookView(CredoWebhookView):
        def handle_callback(self, callback_data, verify_response):
            # Handle customer redirect
            if verify_response and verify_response.is_successful:
                return redirect('/success/')
            return redirect('/failed/')
        
        def handle_webhook(self, event):
            # Handle server-to-server notification
            if event.is_successful:
                Order.objects.filter(reference=event.business_ref).update(status='paid')
"""

from .client import CredoClient
from .config import CredoConfig
from .exceptions import (
    CredoError,
    CredoAPIError,
    CredoValidationError,
    CredoWebhookError,
    CredoConfigError,
)
from .models import (
    PaymentRequest,
    PaymentResponse,
    TransactionStatus,
    FeeBearer,
    VerifyResponse,
    WebhookEvent,
    Customer,
)
from .utils.callback import CallbackData, build_callback_url
from .views import CredoWebhookView

__version__ = "0.1.1"
__all__ = [
    # Client
    "CredoClient",
    "CredoConfig",
    # Exceptions
    "CredoError",
    "CredoAPIError",
    "CredoValidationError",
    "CredoWebhookError",
    "CredoConfigError",
    # Models
    "PaymentRequest",
    "PaymentResponse",
    "TransactionStatus",
    "FeeBearer",
    "VerifyResponse",
    "WebhookEvent",
    "Customer",
    # Utilities
    "CallbackData",
    "build_callback_url",
    # Views
    "CredoWebhookView",
]
