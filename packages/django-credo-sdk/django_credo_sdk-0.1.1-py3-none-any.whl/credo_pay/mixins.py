"""
Mixins for integrating Credo payments into Django models and views.
"""

from typing import Optional, Dict, Any, List
from django.db import models

from .client import CredoClient
from .models import PaymentResponse, VerifyResponse


class CredoPaymentMixin:
    """
    Mixin for models that need payment functionality.
    
    Add this mixin to your Django model to easily create and
    track payments.
    
    Example:
        class Order(CredoPaymentMixin, models.Model):
            customer_email = models.EmailField()
            amount = models.DecimalField(max_digits=10, decimal_places=2)
            payment_reference = models.CharField(max_length=50, blank=True)
            payment_status = models.CharField(max_length=20, default='pending')
            
            def get_payment_email(self):
                return self.customer_email
            
            def get_payment_amount(self):
                return float(self.amount)
        
        # Usage
        order = Order.objects.get(id=1)
        response = order.create_payment(
            callback_url="https://yoursite.com/callback/"
        )
        # Redirect to response.authorization_url
    """
    
    _credo_client: Optional[CredoClient] = None
    
    @property
    def credo_client(self) -> CredoClient:
        """Get or create Credo client."""
        if self._credo_client is None:
            self._credo_client = CredoClient()
        return self._credo_client
    
    def get_payment_email(self) -> str:
        """
        Get email for payment. Override in your model.
        
        Returns:
            Customer email address
        """
        raise NotImplementedError(
            "Implement get_payment_email() in your model"
        )
    
    def get_payment_amount(self) -> float:
        """
        Get amount for payment. Override in your model.
        
        Returns:
            Payment amount in main currency unit
        """
        raise NotImplementedError(
            "Implement get_payment_amount() in your model"
        )
    
    def get_payment_reference(self) -> Optional[str]:
        """
        Get custom reference for payment. Override to customize.
        
        Returns:
            Custom reference or None for auto-generated
        """
        return None
    
    def get_payment_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Get metadata for payment. Override to customize.
        
        Returns:
            Metadata dictionary or None
        """
        return None
    
    def create_payment(
        self,
        callback_url: str,
        currency: str = "NGN",
        channels: Optional[List[str]] = None,
        service_code: Optional[str] = None,
        bank_account: Optional[str] = None,
        **kwargs
    ) -> PaymentResponse:
        """
        Create a payment for this model instance.
        
        Args:
            callback_url: URL to redirect after payment
            currency: Currency code
            channels: Payment channels to enable
            service_code: Service code for routing
            bank_account: Destination bank account
            **kwargs: Additional arguments for initialize_payment()
            
        Returns:
            PaymentResponse with authorization_url
        """
        return self.credo_client.initialize_payment(
            amount=self.get_payment_amount(),
            email=self.get_payment_email(),
            callback_url=callback_url,
            currency=currency,
            reference=self.get_payment_reference(),
            channels=channels,
            service_code=service_code,
            bank_account=bank_account,
            metadata=self.get_payment_metadata(),
            **kwargs
        )
    
    def verify_payment(self, reference: str) -> VerifyResponse:
        """
        Verify a payment for this model instance.
        
        Args:
            reference: Transaction reference from Credo
            
        Returns:
            VerifyResponse with transaction status
        """
        return self.credo_client.verify_payment(reference)


class ServiceCodeRoutingMixin:
    """
    Mixin for models that need payment routing functionality.
    
    Use this for scenarios where different instances route
    payments to different bank accounts (e.g., properties,
    vendors, etc.)
    
    Example:
        class Property(ServiceCodeRoutingMixin, models.Model):
            name = models.CharField(max_length=100)
            bank_account = models.CharField(max_length=20)
            service_code = models.CharField(max_length=50)
            
            def get_service_code(self):
                return self.service_code
            
            def get_bank_account(self):
                return self.bank_account
        
        # Usage
        property = Property.objects.get(id=1)
        response = property.create_routed_payment(
            amount=50000,
            email="tenant@example.com",
            callback_url="https://yoursite.com/callback/"
        )
    """
    
    _credo_client: Optional[CredoClient] = None
    
    @property
    def credo_client(self) -> CredoClient:
        """Get or create Credo client."""
        if self._credo_client is None:
            self._credo_client = CredoClient()
        return self._credo_client
    
    def get_service_code(self) -> str:
        """
        Get service code for routing. Override in your model.
        
        Returns:
            Service code string
        """
        raise NotImplementedError(
            "Implement get_service_code() in your model"
        )
    
    def get_bank_account(self) -> str:
        """
        Get bank account for routing. Override in your model.
        
        Returns:
            Bank account number
        """
        raise NotImplementedError(
            "Implement get_bank_account() in your model"
        )
    
    def create_routed_payment(
        self,
        amount: float,
        email: str,
        callback_url: str,
        **kwargs
    ) -> PaymentResponse:
        """
        Create a routed payment for this model instance.
        
        Args:
            amount: Payment amount
            email: Customer email
            callback_url: Redirect URL after payment
            **kwargs: Additional arguments
            
        Returns:
            PaymentResponse with authorization_url
        """
        return self.credo_client.initialize_routed_payment(
            amount=amount,
            email=email,
            service_code=self.get_service_code(),
            bank_account=self.get_bank_account(),
            callback_url=callback_url,
            **kwargs
        )
