"""
Data models for Credo SDK.

Uses dataclasses for clean, type-safe data structures.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from enum import IntEnum
from datetime import datetime


class TransactionStatus(IntEnum):
    """
    Credo transaction status codes.
    
    Reference from Credo documentation:
    - 0: Successful transaction
    - 1: Refunded transaction
    - 2: Refund queued
    - 3: Failed transaction
    - 4: Settlement queued
    - 5: Settled transaction
    - 6: Review (flagged for human review)
    - 7: Declined (failed fraud check)
    - 8: Failed (aged - over 24 hours)
    - 9: Abandoned (15/14 status over 24 hours)
    - 13: Attempted (customer attempted payment)
    - 14: Initialised (payment URL loaded on browser)
    - 15: Initialising (payment request sent, URL returned)
    
    Note: Records with status 14 & 15 are not considered transactions
    yet and might not show in transaction history.
    """
    SUCCESSFUL = 0
    REFUNDED = 1
    REFUND_QUEUED = 2
    FAILED = 3
    SETTLE_QUEUED = 4
    SETTLED = 5
    REVIEW = 6
    DECLINED = 7
    FAILED_AGED = 8
    ABANDONED = 9
    ATTEMPTED = 13
    INITIALISED = 14
    INITIALISING = 15
    
    @classmethod
    def is_successful(cls, status: int) -> bool:
        """Check if status indicates a successful payment."""
        return status in [cls.SUCCESSFUL, cls.SETTLED, cls.SETTLE_QUEUED]
    
    @classmethod
    def is_failed(cls, status: int) -> bool:
        """Check if status indicates a failed payment."""
        return status in [cls.FAILED, cls.DECLINED, cls.FAILED_AGED, cls.ABANDONED]
    
    @classmethod
    def is_pending(cls, status: int) -> bool:
        """Check if status indicates a pending payment."""
        return status in [cls.INITIALISING, cls.INITIALISED, cls.ATTEMPTED, cls.REVIEW]
    
    @classmethod
    def is_refund(cls, status: int) -> bool:
        """Check if status indicates a refund state."""
        return status in [cls.REFUNDED, cls.REFUND_QUEUED]
    
    @classmethod
    def requires_action(cls, status: int) -> bool:
        """Check if status requires manual action/review."""
        return status == cls.REVIEW
    
    @classmethod
    def get_description(cls, status: int) -> str:
        """Get human-readable description for status code."""
        descriptions = {
            0: "Successful transaction",
            1: "Transaction refunded",
            2: "Refund queued",
            3: "Failed transaction",
            4: "Settlement queued",
            5: "Transaction settled",
            6: "Flagged for review",
            7: "Transaction declined (fraud check failed)",
            8: "Failed (aged - over 24 hours)",
            9: "Transaction abandoned",
            13: "Payment attempted",
            14: "Payment initialized",
            15: "Initializing payment",
        }
        return descriptions.get(status, f"Unknown status: {status}")


class FeeBearer(IntEnum):
    """
    Who bears the transaction fee.
    
    Per Credo documentation:
    - 0: Customer bears the fee
    - 1: Merchant bears the fee
    """
    CUSTOMER = 0  # Customer pays the transaction fee
    MERCHANT = 1  # Merchant pays the transaction fee


@dataclass
class Customer:
    """Customer information for payment."""
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        data = {"email": self.email}
        if self.first_name:
            data["customerFirstName"] = self.first_name
        if self.last_name:
            data["customerLastName"] = self.last_name
        if self.phone_number:
            data["customerPhoneNumber"] = self.phone_number
        return data


@dataclass
class CustomField:
    """Custom metadata field."""
    variable_name: str
    value: str
    display_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for API request."""
        data = {
            "variable_name": self.variable_name,
            "value": self.value
        }
        if self.display_name:
            data["display_name"] = self.display_name
        return data


@dataclass
class PaymentMetadata:
    """
    Metadata for payment transactions.
    
    Useful for routing payments to specific bank accounts
    and storing custom data.
    """
    bank_account: Optional[str] = None
    custom_fields: List[CustomField] = field(default_factory=list)
    logo_url: Optional[str] = None
    extra_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        data = {}
        if self.bank_account:
            data["bankAccount"] = self.bank_account
        if self.custom_fields:
            data["customFields"] = [cf.to_dict() for cf in self.custom_fields]
        if self.logo_url:
            data["logoUrl"] = self.logo_url
        data.update(self.extra_data)
        return data


@dataclass
class PaymentRequest:
    """
    Payment initialization request data.
    
    Attributes:
        amount: Amount to charge (in the currency's main unit, e.g., Naira)
        email: Customer's email address
        callback_url: URL to redirect after payment
        currency: Currency code (default: NGN)
        reference: Unique transaction reference (auto-generated if not provided)
        channels: Payment channels to enable (card, bank, or both)
        customer: Customer details
        metadata: Additional metadata for the transaction
        service_code: Service code for dynamic settlement routing
        bearer: Who bears the transaction fee (0 = customer, 1 = merchant)
    """
    amount: float
    email: str
    callback_url: str
    currency: str = "NGN"
    reference: Optional[str] = None
    channels: List[str] = field(default_factory=lambda: ["card", "bank"])
    customer: Optional[Customer] = None
    metadata: Optional[PaymentMetadata] = None
    service_code: Optional[str] = None
    bearer: int = 0  # Fixed: 0 = customer bears fee (default), 1 = merchant bears fee
    
    def __post_init__(self):
        """Validate payment request data."""
        if self.amount <= 0:
            raise ValueError("Amount must be greater than 0")
        if not self.email:
            raise ValueError("Email is required")
        if not self.callback_url:
            raise ValueError("Callback URL is required")
        
        # Validate channels
        valid_channels = {"card", "bank"}
        for channel in self.channels:
            if channel not in valid_channels:
                raise ValueError(f"Invalid channel: {channel}. Must be 'card' or 'bank'")
        
        # Validate bearer
        if self.bearer not in [0, 1]:
            raise ValueError("Bearer must be 0 (customer) or 1 (merchant)")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request."""
        data = {
            "amount": self.amount,
            "email": self.email,
            "callbackUrl": self.callback_url,
            "currency": self.currency,
            "channels": self.channels,
            "bearer": self.bearer,
        }
        
        if self.reference:
            data["reference"] = self.reference
        
        if self.service_code:
            data["serviceCode"] = self.service_code
        
        if self.customer:
            data.update(self.customer.to_dict())
        
        if self.metadata:
            data["metadata"] = self.metadata.to_dict()
        
        return data


@dataclass
class PaymentResponse:
    """
    Response from payment initialization.
    
    Attributes:
        status: HTTP status code
        message: Response message
        authorization_url: URL to redirect customer for payment
        trans_ref: Credo transaction reference
        reference: Your transaction reference
    """
    status: int
    message: str
    authorization_url: Optional[str] = None
    trans_ref: Optional[str] = None
    reference: Optional[str] = None
    raw_response: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_api_response(cls, response_data: Dict[str, Any]) -> "PaymentResponse":
        """Create from API response dictionary."""
        data = response_data.get("data", {})
        return cls(
            status=response_data.get("status", 0),
            message=response_data.get("message", ""),
            authorization_url=data.get("authorizationUrl") or data.get("credoReference"),
            trans_ref=data.get("transRef") or data.get("credoReference"),
            reference=data.get("reference") or data.get("businessRef"),
            raw_response=response_data,
        )
    
    @property
    def is_successful(self) -> bool:
        """Check if initialization was successful."""
        return self.status == 200 and self.authorization_url is not None


@dataclass
class VerifyResponse:
    """
    Response from transaction verification.
    
    Contains full transaction details including amounts,
    status, and customer information.
    """
    status: int
    message: str
    business_code: Optional[str] = None
    trans_ref: Optional[str] = None
    business_ref: Optional[str] = None
    debited_amount: float = 0.0
    trans_amount: float = 0.0
    trans_fee_amount: float = 0.0
    settlement_amount: float = 0.0
    customer_id: Optional[str] = None
    transaction_date: Optional[str] = None
    channel_id: int = 0
    currency_code: str = "NGN"
    transaction_status: int = 0
    metadata: List[Dict[str, Any]] = field(default_factory=list)
    raw_response: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_api_response(cls, response_data: Dict[str, Any]) -> "VerifyResponse":
        """Create from API response dictionary."""
        data = response_data.get("data", {})
        return cls(
            status=response_data.get("status", 0),
            message=response_data.get("message", ""),
            business_code=data.get("businessCode"),
            trans_ref=data.get("transRef"),
            business_ref=data.get("businessRef"),
            debited_amount=float(data.get("debitedAmount", 0)),
            trans_amount=float(data.get("transAmount", 0)),
            trans_fee_amount=float(data.get("transFeeAmount", 0)),
            settlement_amount=float(data.get("settlementAmount", 0)),
            customer_id=data.get("customerId"),
            transaction_date=data.get("transactionDate"),
            channel_id=data.get("channelId", 0),
            currency_code=data.get("currencyCode", "NGN"),
            transaction_status=data.get("status", 0),
            metadata=data.get("metadata", []),
            raw_response=response_data,
        )
    
    @property
    def is_successful(self) -> bool:
        """Check if transaction was successful."""
        return TransactionStatus.is_successful(self.transaction_status)
    
    @property
    def is_failed(self) -> bool:
        """Check if transaction failed."""
        return TransactionStatus.is_failed(self.transaction_status)
    
    @property
    def is_pending(self) -> bool:
        """Check if transaction is pending."""
        return TransactionStatus.is_pending(self.transaction_status)
    
    @property
    def status_description(self) -> str:
        """Get human-readable status description."""
        return TransactionStatus.get_description(self.transaction_status)


@dataclass
class WebhookCustomer:
    """Customer data from webhook payload."""
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebhookCustomer":
        """Create from webhook data dictionary."""
        return cls(
            email=data.get("customerEmail"),
            first_name=data.get("firstName"),
            last_name=data.get("lastName"),
            phone_number=data.get("phoneNo"),
        )


@dataclass
class WebhookEvent:
    """
    Parsed webhook event from Credo.
    
    Attributes:
        event: Event type (e.g., 'transaction.successful')
        trans_ref: Credo transaction reference
        business_ref: Your transaction reference
        amount: Transaction amount
        status: Transaction status code
        customer: Customer information
    """
    event: str
    trans_ref: Optional[str] = None
    business_ref: Optional[str] = None
    business_code: Optional[str] = None
    debited_amount: float = 0.0
    trans_amount: float = 0.0
    trans_fee_amount: float = 0.0
    settlement_amount: float = 0.0
    customer_id: Optional[str] = None
    transaction_date: Optional[str] = None
    channel_id: int = 0
    currency_code: str = "NGN"
    status: int = 0
    payment_method_type: Optional[str] = None
    payment_method: Optional[str] = None
    customer: Optional[WebhookCustomer] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "WebhookEvent":
        """Create from webhook payload dictionary."""
        data = payload.get("data", {})
        customer_data = data.get("customer", {})
        
        return cls(
            event=payload.get("event", ""),
            trans_ref=data.get("transRef"),
            business_ref=data.get("businessRef"),
            business_code=data.get("businessCode"),
            debited_amount=float(data.get("debitedAmount", 0)),
            trans_amount=float(data.get("transAmount", 0)),
            trans_fee_amount=float(data.get("transFeeAmount", 0)),
            settlement_amount=float(data.get("settlementAmount", 0)),
            customer_id=data.get("customerId"),
            transaction_date=data.get("transactionDate"),
            channel_id=data.get("channelId", 0),
            currency_code=data.get("currencyCode", "NGN"),
            status=data.get("status", 0),
            payment_method_type=data.get("paymentMethodType"),
            payment_method=data.get("paymentMethod"),
            customer=WebhookCustomer.from_dict(customer_data) if customer_data else None,
            raw_data=payload,
        )
    
    @property
    def is_successful(self) -> bool:
        """Check if event indicates successful transaction."""
        return self.event == "transaction.successful" and TransactionStatus.is_successful(self.status)
    
    @property
    def is_failed(self) -> bool:
        """Check if event indicates failed transaction."""
        return self.event == "transaction.failed"
    
    @property
    def is_settlement(self) -> bool:
        """Check if event is a settlement notification."""
        return self.event == "transaction.settlement.success"
