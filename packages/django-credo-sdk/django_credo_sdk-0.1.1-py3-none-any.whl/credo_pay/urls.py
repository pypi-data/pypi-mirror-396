"""
URL patterns for Credo SDK views.

Include these in your project's urls.py:

    from django.urls import path, include
    
    urlpatterns = [
        path('api/credo/', include('credo_pay.urls')),
    ]
"""

from django.urls import path

from .views import (
    PaymentInitializeView,
    RoutedPaymentInitializeView,
    PaymentVerifyView,
    CredoWebhookView,
    DebugInterfaceView,
    DebugInitializePaymentView,
    DebugVerifyPaymentView,
    DebugWebhookSimulatorView,
    DebugConfigCheckView,
)

app_name = "credo_pay"

urlpatterns = [
    # ==========================================================================
    # Production API Endpoints
    # ==========================================================================
    
    # Initialize a payment
    path(
        "initialize/",
        PaymentInitializeView.as_view(),
        name="payment-initialize"
    ),
    
    # Initialize a routed payment (multi-destination)
    path(
        "routed/initialize/",
        RoutedPaymentInitializeView.as_view(),
        name="routed-payment-initialize"
    ),
    
    # Verify a payment by reference
    path(
        "verify/<str:reference>/",
        PaymentVerifyView.as_view(),
        name="payment-verify"
    ),
    
    # Unified webhook endpoint - handles BOTH:
    # - GET: Customer redirect after payment (callback with query params)
    # - POST: Server-to-server webhook notifications (JSON with signature)
    path(
        "webhook/",
        CredoWebhookView.as_view(),
        name="webhook"
    ),
    
    # ==========================================================================
    # Debug/Test Interface Endpoints
    # ==========================================================================
    
    path(
        "debug/",
        DebugInterfaceView.as_view(),
        name="debug-interface"
    ),
    path(
        "debug/initialize/",
        DebugInitializePaymentView.as_view(),
        name="debug-initialize"
    ),
    path(
        "debug/verify/",
        DebugVerifyPaymentView.as_view(),
        name="debug-verify"
    ),
    path(
        "debug/webhook/",
        DebugWebhookSimulatorView.as_view(),
        name="debug-webhook"
    ),
    path(
        "debug/config-check/",
        DebugConfigCheckView.as_view(),
        name="debug-config-check"
    ),
]
