"""
Django REST Framework views for Credo SDK.

Provides ready-to-use views for payment initialization,
verification, and unified webhook/callback handling.
"""

import logging
from typing import Any, Optional

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .client import CredoClient
from .serializers import (
    PaymentInitializeSerializer,
    PaymentResponseSerializer,
    VerifyResponseSerializer,
    RoutedPaymentSerializer,
)
from .exceptions import CredoError, CredoWebhookError
from .models import WebhookEvent, VerifyResponse
from .utils.callback import CallbackData
from .config import CredoConfig

logger = logging.getLogger(__name__)


class BaseCredoView(APIView):
    """Base view with Credo client initialization."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = None
    
    @property
    def credo_client(self) -> CredoClient:
        """Get or create Credo client instance."""
        if self._client is None:
            self._client = CredoClient()
        return self._client


# =============================================================================
# Debug Interface Views
# =============================================================================

class DebugInterfaceView(APIView):
    """
    Debug/Test interface for developers.
    
    GET /api/credo/debug/
    
    Provides a web-based interface to test payment flows,
    verify transactions, and simulate webhook events.
    """
    permission_classes = [AllowAny]
    
    def get(self, request: Request) -> Response:
        from django.shortcuts import render
        
        config = CredoConfig()
        
        context = {
            'environment': config.environment,
            'is_sandbox': config.environment == 'sandbox',
            'base_url': config.base_url,
            'public_key_set': bool(config.public_key),
            'secret_key_set': bool(config.secret_key),
            'business_code_set': bool(config.business_code),
            'terminal_id': config.terminal_id,
            'default_currency': config.default_currency,
            'default_channels': config.default_channels,
            'callback_url': config.default_callback_url,
            'public_key_preview': f"{config.public_key[:12]}..." if config.public_key else 'Not set',
        }
        
        return render(request, 'credo_pay/debug.html', context)


class DebugInitializePaymentView(BaseCredoView):
    """HTMX endpoint for initializing test payments."""
    permission_classes = [AllowAny]
    
    def post(self, request: Request) -> Response:
        from django.shortcuts import render
        
        try:
            amount = int(request.data.get('amount', 1000))
            email = request.data.get('email', 'test@example.com')
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            phone_number = request.data.get('phone_number', '')
            callback_url = request.data.get('callback_url', '')
            currency = request.data.get('currency', 'NGN')
            channels = request.data.getlist('channels') or ['card', 'bank']
            service_code = request.data.get('service_code', '').strip() or None
            bank_account = request.data.get('bank_account', '').strip() or None
            
            response = self.credo_client.initialize_payment(
                amount=amount,
                email=email,
                callback_url=callback_url or None,
                currency=currency,
                channels=channels,
                first_name=first_name or None,
                last_name=last_name or None,
                phone_number=phone_number or None,
                service_code=service_code,
                bank_account=bank_account,
            )
            
            context = {
                'success': True,
                'authorization_url': response.authorization_url,
                'trans_ref': response.trans_ref,
                'reference': response.reference,
                'message': response.message,
                'service_code': service_code,
                'bank_account': bank_account,
            }
            
        except CredoError as e:
            context = {
                'success': False,
                'error': str(e),
                'details': e.details,
            }
        except Exception as e:
            context = {
                'success': False,
                'error': str(e),
            }
        
        return render(request, 'credo_pay/partials/payment_result.html', context)


class DebugVerifyPaymentView(BaseCredoView):
    """HTMX endpoint for verifying payments."""
    permission_classes = [AllowAny]
    
    def post(self, request: Request) -> Response:
        from django.shortcuts import render
        
        reference = request.data.get('reference', '').strip()
        
        if not reference:
            return render(request, 'credo_pay/partials/verify_result.html', {
                'success': False,
                'error': 'Reference is required',
            })
        
        try:
            response = self.credo_client.verify_payment(reference)
            
            context = {
                'success': True,
                'trans_ref': response.trans_ref,
                'business_ref': response.business_ref,
                'debited_amount': response.debited_amount,
                'trans_amount': response.trans_amount,
                'fee_amount': response.fee_amount,
                'settlement_amount': response.settlement_amount,
                'customer_id': response.customer_id,
                'transaction_date': response.transaction_date,
                'currency': response.currency_code,
                'status_code': response.status,
                'status_description': response.status_description,
                'is_successful': response.is_successful,
                'is_pending': response.is_pending,
                'is_failed': response.is_failed,
            }
            
        except CredoError as e:
            context = {
                'success': False,
                'error': str(e),
                'details': e.details,
            }
        except Exception as e:
            context = {
                'success': False,
                'error': str(e),
            }
        
        return render(request, 'credo_pay/partials/verify_result.html', context)


class DebugWebhookSimulatorView(BaseCredoView):
    """HTMX endpoint for simulating webhooks."""
    permission_classes = [AllowAny]
    
    def post(self, request: Request) -> Response:
        from django.shortcuts import render
        import json
        
        event_type = request.data.get('event_type', 'transaction.successful')
        trans_ref = request.data.get('trans_ref', 'TEST123456')
        amount = int(request.data.get('amount', 1000))
        
        # Generate sample webhook payload
        payload = {
            "event": event_type,
            "data": {
                "businessCode": "700607001390003",
                "transRef": trans_ref,
                "businessRef": f"REF_{trans_ref}",
                "debitedAmount": float(amount),
                "transAmount": float(amount),
                "transFeeAmount": round(amount * 0.015, 2),
                "settlementAmount": round(amount * 0.985, 2),
                "customerId": "test@example.com",
                "transactionDate": "2024-01-15 12:30:00",
                "channelId": 1,
                "currencyCode": "NGN",
                "status": 0 if event_type == "transaction.successful" else 7,
                "paymentMethodType": "MasterCard",
                "paymentMethod": "Card",
                "customer": {
                    "customerEmail": "test@example.com",
                    "firstName": "Test",
                    "lastName": "User",
                    "phoneNo": "2348012345678"
                }
            }
        }
        
        context = {
            'event_type': event_type,
            'payload': json.dumps(payload, indent=2),
            'payload_raw': payload,
        }
        
        return render(request, 'credo_pay/partials/webhook_payload.html', context)


class DebugConfigCheckView(BaseCredoView):
    """HTMX endpoint for checking configuration."""
    permission_classes = [AllowAny]
    
    def get(self, request: Request) -> Response:
        from django.shortcuts import render
        
        config = CredoConfig.from_django_settings()
        
        checks = []
        all_passed = True
        
        # Check environment
        checks.append({
            'name': 'Environment',
            'value': config.environment,
            'passed': config.environment in ['sandbox', 'production'],
            'message': f'Using {config.environment} environment',
        })
        
        # Check public key
        public_key_valid = bool(config.public_key)
        checks.append({
            'name': 'Public Key',
            'value': f"{config.public_key[:16]}..." if config.public_key else 'Not set',
            'passed': public_key_valid,
            'message': 'Public key configured' if public_key_valid else 'Missing public key',
        })
        if not public_key_valid:
            all_passed = False
        
        secret_key_valid = bool(config.secret_key)
        checks.append({
            'name': 'Secret Key',
            'value': f"{config.secret_key[:16]}..." if config.secret_key else 'Not set',
            'passed': secret_key_valid,
            'message': 'Secret key configured' if secret_key_valid else 'Missing secret key',
        })
        if not secret_key_valid:
            all_passed = False
        
        business_code_valid = bool(config.business_code) and config.business_code != 'your_business_code_here'
        checks.append({
            'name': 'Business Code',
            'value': config.business_code if business_code_valid else 'Not set',
            'passed': True,
            'message': 'Business code configured' if business_code_valid else 'Optional: Set for webhook verification (get from Credo dashboard)',
        })
        
        # Check terminal ID
        terminal_valid = bool(config.terminal_id)
        is_sandbox_terminal = config.terminal_id == "0000000001"
        checks.append({
            'name': 'Terminal ID',
            'value': config.terminal_id or 'Not set',
            'passed': terminal_valid,
            'message': 'Using sandbox terminal ID' if is_sandbox_terminal else ('Terminal ID configured' if terminal_valid else 'Missing terminal ID'),
        })
        
        # Check callback URL
        callback_valid = bool(config.default_callback_url)
        checks.append({
            'name': 'Callback URL',
            'value': config.default_callback_url or 'Not set',
            'passed': callback_valid,
            'message': 'Callback URL configured' if callback_valid else 'Warning: Missing callback URL - Credo will output response as plain text',
        })
        
        # Check webhook token (optional)
        webhook_valid = bool(config.webhook_token)
        checks.append({
            'name': 'Webhook Token',
            'value': f"{config.webhook_token[:8]}..." if config.webhook_token else 'Not set',
            'passed': True,
            'message': 'Webhook token configured' if webhook_valid else 'Optional: Set to verify webhook signatures',
        })
        
        checks.append({
            'name': 'API Base URL',
            'value': config.base_url,
            'passed': True,
            'message': f'API calls will use {config.environment} environment',
        })
        
        context = {
            'checks': checks,
            'all_passed': all_passed,
            'environment': config.environment,
        }
        
        return render(request, 'credo_pay/partials/config_check.html', context)


# =============================================================================
# Production API Views
# =============================================================================

class PaymentInitializeView(BaseCredoView):
    """
    API view for initializing payments.
    
    POST /api/payments/initialize/
    
    Request Body:
        {
            "amount": 15000,
            "email": "customer@example.com",
            "callback_url": "https://yoursite.com/webhook/",
            "first_name": "John",
            "last_name": "Doe"
        }
    
    Response:
        {
            "status": 200,
            "message": "Successfully processed",
            "authorization_url": "https://pay.credocentral.com/...",
            "trans_ref": "abc123",
            "reference": "your-reference"
        }
    """
    
    def post(self, request: Request) -> Response:
        serializer = PaymentInitializeSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"error": "Validation failed", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            data = serializer.validated_data
            
            response = self.credo_client.initialize_payment(
                amount=data["amount"],
                email=data["email"],
                callback_url=data.get("callback_url"),
                currency=data.get("currency", "NGN"),
                reference=data.get("reference"),
                channels=data.get("channels"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                phone_number=data.get("phone_number"),
                service_code=data.get("service_code"),
                bank_account=data.get("bank_account"),
                metadata=data.get("metadata"),
                custom_fields=data.get("custom_fields"),
                bearer=data.get("bearer", 0),
            )
            
            return Response(
                PaymentResponseSerializer(response).data,
                status=status.HTTP_200_OK
            )
            
        except CredoError as e:
            logger.error(f"Credo payment initialization failed: {e}")
            return Response(
                {"error": str(e), "details": e.details},
                status=status.HTTP_400_BAD_REQUEST
            )


class RoutedPaymentInitializeView(BaseCredoView):
    """
    API view for initializing routed payments.
    
    Use this for multi-destination payment scenarios where
    payments need to be routed to different bank accounts.
    
    POST /api/payments/routed/initialize/
    
    Request Body:
        {
            "amount": 50000,
            "email": "tenant@example.com",
            "service_code": "PROPERTY_A_CODE",
            "bank_account": "0123456789",
            "callback_url": "https://yoursite.com/webhook/"
        }
    """
    
    def post(self, request: Request) -> Response:
        serializer = RoutedPaymentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {"error": "Validation failed", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            data = serializer.validated_data
            
            response = self.credo_client.initialize_routed_payment(
                amount=data["amount"],
                email=data["email"],
                service_code=data["service_code"],
                bank_account=data["bank_account"],
                callback_url=data.get("callback_url"),
                currency=data.get("currency", "NGN"),
                reference=data.get("reference"),
                channels=data.get("channels"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                phone_number=data.get("phone_number"),
                metadata=data.get("metadata"),
                custom_fields=data.get("custom_fields"),
                bearer=data.get("bearer", 0),
            )
            
            return Response(
                PaymentResponseSerializer(response).data,
                status=status.HTTP_200_OK
            )
            
        except CredoError as e:
            logger.error(f"Credo routed payment initialization failed: {e}")
            return Response(
                {"error": str(e), "details": e.details},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentVerifyView(BaseCredoView):
    """
    API view for verifying payment status.
    
    GET /api/payments/verify/<reference>/
    
    Response:
        {
            "status": 200,
            "message": "Successfully processed",
            "trans_ref": "abc123",
            "trans_amount": 15000,
            "transaction_status": 0,
            "is_successful": true,
            "status_description": "Successful transaction"
        }
    """
    
    def get(self, request: Request, reference: str) -> Response:
        try:
            response = self.credo_client.verify_payment(reference)
            
            return Response(
                VerifyResponseSerializer(response).data,
                status=status.HTTP_200_OK
            )
            
        except CredoError as e:
            logger.error(f"Credo payment verification failed: {e}")
            return Response(
                {"error": str(e), "details": e.details},
                status=status.HTTP_400_BAD_REQUEST
            )


# =============================================================================
# Unified Webhook View (Handles both GET callback and POST webhook)
# =============================================================================

class CredoWebhookView(BaseCredoView):
    """
    Unified webhook endpoint for Credo payment notifications.
    
    This single endpoint handles BOTH:
    
    1. GET requests - Customer redirect after payment (callback)
       - Credo redirects customer's browser here with query params
       - Example: /webhook/?status=0&errorMessage=Approved&transRef=abc123&transAmount=15000
       - Always verify the transaction status via API (recommended)
    
    2. POST requests - Server-to-server webhook notifications
       - Credo sends JSON payload with X-Credo-Signature header
       - Events: transaction.successful, transaction.failed, transaction.settlement.success
    
    URL: /api/credo/webhook/
    
    Usage:
        # In your urls.py, use this view OR create a subclass:
        
        class MyWebhookView(CredoWebhookView):
            def handle_callback(self, callback_data, verify_response):
                # Handle customer redirect after payment
                if verify_response and verify_response.is_successful:
                    Order.objects.filter(reference=callback_data.reference).update(status='paid')
                    return redirect('/payment/success/')
                return redirect('/payment/failed/')
            
            def handle_webhook(self, event):
                # Handle server-to-server webhook
                if event.is_successful:
                    Order.objects.filter(reference=event.business_ref).update(status='paid')
                elif event.is_failed:
                    Order.objects.filter(reference=event.business_ref).update(status='failed')
    """
    permission_classes = [AllowAny]
    
    # Configuration options
    verify_callback_transaction: bool = True  # Verify transaction via API on GET callback
    verify_webhook_signature: bool = True  # Verify X-Credo-Signature on POST webhook
    
    def get(self, request: Request) -> Response:
        """
        Handle GET request - Customer redirect after payment.
        
        Credo redirects the customer here with query parameters:
        ?status=0&errorMessage=Approved&transRef=abc123&transAmount=15000&currency=NGN&reference=your-ref
        
        Per Credo docs: "We redirect to you even if the payment failed, so it's 
        advised you verify that the transaction was indeed successful when unsure 
        before completing the order."
        """
        try:
            # Parse callback data from query parameters
            callback_data = CallbackData.from_request(request)
            
            logger.info(
                f"Payment callback received: status={callback_data.status}, "
                f"trans_ref={callback_data.trans_ref}, "
                f"reference={callback_data.reference}"
            )
            
            # Verify transaction with Credo API (recommended per docs)
            verify_response: Optional[VerifyResponse] = None
            if self.verify_callback_transaction and callback_data.trans_ref:
                try:
                    verify_response = self.credo_client.verify_payment(
                        callback_data.trans_ref
                    )
                    logger.info(
                        f"Transaction verified: status={verify_response.transaction_status}, "
                        f"is_successful={verify_response.is_successful}"
                    )
                except CredoError as e:
                    logger.warning(f"Failed to verify transaction: {e}")
            
            # Call developer's custom handler
            custom_response = self.handle_callback(callback_data, verify_response)
            if custom_response is not None:
                return custom_response
            
            # Default response (SDK provides basic response)
            return self._default_callback_response(callback_data, verify_response)
                
        except Exception as e:
            logger.error(f"Callback processing error: {e}")
            return Response(
                {"error": "Failed to process callback", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request: Request) -> Response:
        """
        Handle POST request - Server-to-server webhook notification.
        
        Credo sends a JSON payload with X-Credo-Signature header.
        The signature is SHA512(WEBHOOK_TOKEN + BUSINESS_CODE).
        
        Per Credo docs, the businessCode is included in every webhook payload's
        data object, so this handler extracts it from the payload for verification.
        
        Events:
        - transaction.successful (status=0)
        - transaction.failed (status=7)
        - transaction.settlement.success (status=5)
        """
        signature = request.headers.get("X-Credo-Signature", "")
        
        try:
            # The SDK now extracts businessCode from the webhook payload for signature verification,
            # eliminating the need to configure CREDO_BUSINESS_CODE in settings
            event = self.credo_client.process_webhook(
                payload=request.body,
                signature=signature,
                verify=self.verify_webhook_signature,
                use_payload_business_code=True  # Always use payload's business code
            )
            
            logger.info(
                f"Webhook received: event={event.event}, "
                f"trans_ref={event.trans_ref}, "
                f"amount={event.trans_amount}"
            )
            
            # Call developer's custom handler
            self.handle_webhook(event)
            
            # Return success to Credo
            return Response(
                {"status": "success", "event": event.event},
                status=status.HTTP_200_OK
            )
            
        except CredoWebhookError as e:
            logger.warning(f"Webhook verification failed: {e}")
            return Response(
                {"error": "Invalid webhook signature"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except CredoError as e:
            logger.error(f"Webhook processing failed: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def handle_callback(
        self,
        callback_data: CallbackData,
        verify_response: Optional[VerifyResponse]
    ) -> Optional[Response]:
        """
        Hook method for custom callback processing.
        
        Override this in your subclass to handle payment callbacks.
        This is called when Credo redirects the customer back to your site.
        
        Args:
            callback_data: Parsed CallbackData from query parameters
            verify_response: VerifyResponse from Credo API (if verify_callback_transaction=True)
            
        Returns:
            Response object to return, or None to use default response
            
        Example:
            def handle_callback(self, callback_data, verify_response):
                # Use verify_response for authoritative status (recommended)
                if verify_response and verify_response.is_successful:
                    Order.objects.filter(
                        reference=callback_data.reference
                    ).update(status="paid")
                    return redirect('/orders/success/')
                    
                elif verify_response and verify_response.is_failed:
                    return redirect('/orders/failed/')
                
                # Fallback to callback_data if verification failed
                if callback_data.is_successful:
                    return redirect('/orders/success/')
                return redirect('/orders/failed/')
        """
        pass
    
    def handle_webhook(self, event: WebhookEvent) -> None:
        """
        Hook method for custom webhook processing.
        
        Override this in your subclass to handle webhook events.
        This is called for server-to-server notifications from Credo.
        
        Args:
            event: Parsed WebhookEvent object
            
        Example:
            def handle_webhook(self, event):
                if event.is_successful:
                    # Payment confirmed - fulfill order
                    Order.objects.filter(
                        reference=event.business_ref
                    ).update(status="paid")
                    send_confirmation_email(event.customer.email)
                    
                elif event.is_failed:
                    # Payment failed
                    Order.objects.filter(
                        reference=event.business_ref
                    ).update(status="payment_failed")
                    
                elif event.is_settlement:
                    # Funds settled to your account
                    Transaction.objects.filter(
                        trans_ref=event.trans_ref
                    ).update(settled=True, settled_amount=event.settlement_amount)
        """
        logger.info(
            f"Webhook processed: {event.event} - "
            f"Ref: {event.trans_ref} - "
            f"Amount: {event.trans_amount}"
        )
    
    def _default_callback_response(
        self,
        callback_data: CallbackData,
        verify_response: Optional[VerifyResponse]
    ) -> Response:
        """Generate default response for callback (used if handle_callback returns None)."""
        # Prefer verify_response status if available
        if verify_response:
            is_successful = verify_response.is_successful
            status_desc = verify_response.status_description
        else:
            is_successful = callback_data.is_successful
            status_desc = callback_data.error_message
        
        if is_successful:
            return Response({
                "status": "success",
                "message": "Payment completed successfully",
                "trans_ref": callback_data.trans_ref,
                "reference": callback_data.reference,
                "amount": callback_data.trans_amount,
                "currency": callback_data.currency,
                "verified": verify_response is not None,
            })
        else:
            return Response({
                "status": "failed",
                "message": status_desc or "Payment failed",
                "trans_ref": callback_data.trans_ref,
                "reference": callback_data.reference,
                "verified": verify_response is not None,
            }, status=status.HTTP_400_BAD_REQUEST)
