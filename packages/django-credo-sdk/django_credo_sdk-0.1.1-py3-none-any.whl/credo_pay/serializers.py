"""
Django REST Framework serializers for Credo SDK.

Provides serializers for payment requests, responses,
and webhook payloads.
"""

from rest_framework import serializers


class CustomerSerializer(serializers.Serializer):
    """Serializer for customer information."""
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)


class CustomFieldSerializer(serializers.Serializer):
    """Serializer for custom metadata fields."""
    variable_name = serializers.CharField(max_length=100)
    value = serializers.CharField(max_length=500)
    display_name = serializers.CharField(max_length=100, required=False, allow_blank=True)


class PaymentInitializeSerializer(serializers.Serializer):
    """
    Serializer for payment initialization requests.
    
    Use this to validate incoming payment requests in your API views.
    """
    amount = serializers.FloatField(min_value=100)
    email = serializers.EmailField()
    callback_url = serializers.URLField(required=False, allow_blank=True)
    currency = serializers.CharField(max_length=3, default="NGN")
    reference = serializers.CharField(max_length=50, required=False, allow_blank=True)
    channels = serializers.ListField(
        child=serializers.ChoiceField(choices=["card", "bank"]),
        default=["card", "bank"],
        required=False
    )
    first_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    service_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    bank_account = serializers.CharField(max_length=20, required=False, allow_blank=True)
    metadata = serializers.DictField(required=False, default=dict)
    custom_fields = CustomFieldSerializer(many=True, required=False, default=list)
    bearer = serializers.ChoiceField(
        choices=[0, 1],
        default=0,
        help_text="Who bears the transaction fee: 0 = Customer (default), 1 = Merchant"
    )


class PaymentResponseSerializer(serializers.Serializer):
    """Serializer for payment initialization response."""
    status = serializers.IntegerField()
    message = serializers.CharField()
    authorization_url = serializers.URLField(allow_null=True, allow_blank=True)
    trans_ref = serializers.CharField(allow_null=True, allow_blank=True)
    reference = serializers.CharField(allow_null=True, allow_blank=True)


class VerifyResponseSerializer(serializers.Serializer):
    """Serializer for payment verification response."""
    status = serializers.IntegerField()
    message = serializers.CharField()
    business_code = serializers.CharField(allow_null=True, allow_blank=True)
    trans_ref = serializers.CharField(allow_null=True, allow_blank=True)
    business_ref = serializers.CharField(allow_null=True, allow_blank=True)
    debited_amount = serializers.FloatField()
    trans_amount = serializers.FloatField()
    trans_fee_amount = serializers.FloatField()
    settlement_amount = serializers.FloatField()
    customer_id = serializers.CharField(allow_null=True, allow_blank=True)
    transaction_date = serializers.CharField(allow_null=True, allow_blank=True)
    channel_id = serializers.IntegerField()
    currency_code = serializers.CharField()
    transaction_status = serializers.IntegerField()
    is_successful = serializers.BooleanField()
    is_failed = serializers.BooleanField()
    status_description = serializers.CharField()


class WebhookCustomerSerializer(serializers.Serializer):
    """Serializer for webhook customer data."""
    customerEmail = serializers.EmailField(required=False, allow_null=True)
    firstName = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    lastName = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    phoneNo = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class WebhookDataSerializer(serializers.Serializer):
    """Serializer for webhook data payload."""
    businessCode = serializers.CharField()
    transRef = serializers.CharField()
    businessRef = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    debitedAmount = serializers.FloatField()
    transAmount = serializers.FloatField()
    transFeeAmount = serializers.FloatField()
    settlementAmount = serializers.FloatField()
    customerId = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    transactionDate = serializers.CharField()
    channelId = serializers.IntegerField()
    currencyCode = serializers.CharField()
    status = serializers.IntegerField()
    paymentMethodType = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    paymentMethod = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    customer = WebhookCustomerSerializer(required=False, allow_null=True)


class WebhookPayloadSerializer(serializers.Serializer):
    """
    Serializer for incoming webhook payload.
    
    Use this to validate webhook requests in your views.
    """
    event = serializers.ChoiceField(choices=[
        "transaction.successful",
        "transaction.failed",
        "transaction.settlement.success"
    ])
    data = WebhookDataSerializer()


class RoutedPaymentSerializer(PaymentInitializeSerializer):
    """
    Serializer for routed payments.
    
    Extends PaymentInitializeSerializer with required service_code
    and bank_account for payment routing scenarios.
    """
    service_code = serializers.CharField(max_length=50, required=True)
    bank_account = serializers.CharField(max_length=20, required=True)


class CallbackDataSerializer(serializers.Serializer):
    """
    Serializer for Credo callback data.
    
    Credo redirects to your callback URL with these query parameters
    after a payment attempt (success or failure).
    """
    status = serializers.IntegerField(help_text="Transaction status code (0 = success)")
    error_message = serializers.CharField(
        allow_blank=True,
        help_text="Description of the result (e.g., 'Approved')"
    )
    trans_ref = serializers.CharField(help_text="Credo transaction reference")
    trans_amount = serializers.FloatField(help_text="Transaction amount")
    currency = serializers.CharField(help_text="Currency code (e.g., 'NGN')")
    reference = serializers.CharField(
        allow_blank=True,
        help_text="Your business reference"
    )
    is_successful = serializers.BooleanField(read_only=True)
