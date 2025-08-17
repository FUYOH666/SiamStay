"""
Payment Processing Service for SiamStay
Handles multi-currency payments, Thai banking, and international cards
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class Currency(str, Enum):
    """Supported currencies"""
    THB = "THB"  # Thai Baht
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    AUD = "AUD"  # Australian Dollar
    SGD = "SGD"  # Singapore Dollar
    USDT = "USDT"  # Tether (stablecoin)


class PaymentMethod(str, Enum):
    """Supported payment methods"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    PROMPTPAY = "promptpay"  # Thai QR payment
    CRYPTOCURRENCY = "cryptocurrency"
    WISE = "wise"  # International transfers


class PaymentStatus(str, Enum):
    """Payment transaction status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentProvider(str, Enum):
    """Payment service providers"""
    STRIPE = "stripe"
    OMISE = "omise"  # Thai payment processor
    SCB_EASY = "scb_easy"  # Siam Commercial Bank
    KASIKORN = "kasikorn"  # Kasikorn Bank
    PROMPTPAY = "promptpay"
    WISE_API = "wise"
    BINANCE_PAY = "binance_pay"


class PaymentDetails(BaseModel):
    """Payment transaction details"""
    amount: float = Field(gt=0)
    currency: Currency
    payment_method: PaymentMethod
    provider: PaymentProvider
    
    # Card details (encrypted/tokenized)
    card_last4: Optional[str] = None
    card_brand: Optional[str] = None
    
    # Bank transfer details
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    
    # Thai specific
    promptpay_phone: Optional[str] = None
    promptpay_id: Optional[str] = None
    
    # Crypto details
    wallet_address: Optional[str] = None
    transaction_hash: Optional[str] = None


class PaymentTransaction(BaseModel):
    """Complete payment transaction record"""
    transaction_id: str
    booking_id: str
    payer_id: str
    recipient_id: str  # Property owner
    
    payment_details: PaymentDetails
    status: PaymentStatus = PaymentStatus.PENDING
    
    # Amounts
    gross_amount: float
    fee_amount: float
    net_amount: float
    
    # Provider transaction IDs
    provider_transaction_id: Optional[str] = None
    provider_fee: Optional[float] = None
    
    # Timestamps
    created_at: datetime
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Compliance
    tax_withheld: Optional[float] = None
    receipt_url: Optional[str] = None
    
    # Error handling
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class BasePaymentProcessor(ABC):
    """Abstract base class for payment processors"""
    
    @abstractmethod
    async def process_payment(
        self,
        payment_details: PaymentDetails,
        metadata: Dict[str, Any]
    ) -> PaymentTransaction:
        """Process a payment transaction"""
        pass
    
    @abstractmethod
    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Refund a payment transaction"""
        pass
    
    @abstractmethod
    async def get_transaction_status(
        self,
        transaction_id: str
    ) -> PaymentStatus:
        """Get current transaction status"""
        pass


class StripeProcessor(BasePaymentProcessor):
    """Stripe payment processor for international cards"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # TODO: Initialize Stripe client
    
    async def process_payment(
        self,
        payment_details: PaymentDetails,
        metadata: Dict[str, Any]
    ) -> PaymentTransaction:
        """Process payment via Stripe"""
        
        # TODO: Implement Stripe payment processing
        logger.info(f"Processing Stripe payment: {payment_details.amount} {payment_details.currency}")
        
        transaction = PaymentTransaction(
            transaction_id=f"stripe_{datetime.now().timestamp()}",
            booking_id=metadata["booking_id"],
            payer_id=metadata["payer_id"],
            recipient_id=metadata["recipient_id"],
            payment_details=payment_details,
            gross_amount=payment_details.amount,
            fee_amount=payment_details.amount * 0.029,  # Stripe fee
            net_amount=payment_details.amount * 0.971,
            created_at=datetime.now()
        )
        
        return transaction
    
    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Refund Stripe payment"""
        
        # TODO: Implement Stripe refund
        return {
            "refund_id": f"refund_{datetime.now().timestamp()}",
            "amount": amount,
            "status": "pending"
        }
    
    async def get_transaction_status(self, transaction_id: str) -> PaymentStatus:
        """Get Stripe transaction status"""
        # TODO: Implement status check
        return PaymentStatus.COMPLETED


class ThaiPromptPayProcessor(BasePaymentProcessor):
    """PromptPay processor for Thai domestic payments"""
    
    def __init__(self, merchant_id: str):
        self.merchant_id = merchant_id
    
    async def process_payment(
        self,
        payment_details: PaymentDetails,
        metadata: Dict[str, Any]
    ) -> PaymentTransaction:
        """Process PromptPay payment"""
        
        logger.info(f"Processing PromptPay payment: {payment_details.amount} THB")
        
        transaction = PaymentTransaction(
            transaction_id=f"promptpay_{datetime.now().timestamp()}",
            booking_id=metadata["booking_id"],
            payer_id=metadata["payer_id"],
            recipient_id=metadata["recipient_id"],
            payment_details=payment_details,
            gross_amount=payment_details.amount,
            fee_amount=0,  # No fee for PromptPay
            net_amount=payment_details.amount,
            created_at=datetime.now()
        )
        
        return transaction
    
    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Refund PromptPay payment"""
        
        return {
            "refund_id": f"promptpay_refund_{datetime.now().timestamp()}",
            "amount": amount,
            "status": "manual_process_required"
        }
    
    async def get_transaction_status(self, transaction_id: str) -> PaymentStatus:
        """Get PromptPay transaction status"""
        return PaymentStatus.COMPLETED


class CryptoProcessor(BasePaymentProcessor):
    """Cryptocurrency payment processor"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # TODO: Initialize crypto payment provider (Binance Pay, etc.)
    
    async def process_payment(
        self,
        payment_details: PaymentDetails,
        metadata: Dict[str, Any]
    ) -> PaymentTransaction:
        """Process cryptocurrency payment"""
        
        logger.info(f"Processing crypto payment: {payment_details.amount} {payment_details.currency}")
        
        transaction = PaymentTransaction(
            transaction_id=f"crypto_{datetime.now().timestamp()}",
            booking_id=metadata["booking_id"],
            payer_id=metadata["payer_id"],
            recipient_id=metadata["recipient_id"],
            payment_details=payment_details,
            gross_amount=payment_details.amount,
            fee_amount=payment_details.amount * 0.01,  # 1% crypto fee
            net_amount=payment_details.amount * 0.99,
            created_at=datetime.now()
        )
        
        return transaction
    
    async def refund_payment(
        self,
        transaction_id: str,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Refund crypto payment"""
        
        return {
            "refund_id": f"crypto_refund_{datetime.now().timestamp()}",
            "amount": amount,
            "status": "blockchain_processing"
        }
    
    async def get_transaction_status(self, transaction_id: str) -> PaymentStatus:
        """Get crypto transaction status"""
        return PaymentStatus.COMPLETED


class PaymentProcessorFactory:
    """Factory for creating payment processors"""
    
    @staticmethod
    def create_processor(
        provider: PaymentProvider,
        **kwargs
    ) -> BasePaymentProcessor:
        """Create appropriate payment processor"""
        
        if provider == PaymentProvider.STRIPE:
            return StripeProcessor(kwargs["api_key"])
        elif provider == PaymentProvider.PROMPTPAY:
            return ThaiPromptPayProcessor(kwargs["merchant_id"])
        elif provider == PaymentProvider.BINANCE_PAY:
            return CryptoProcessor(kwargs["api_key"])
        else:
            raise ValueError(f"Unsupported payment provider: {provider}")


class PaymentService:
    """Main payment service orchestrator"""
    
    def __init__(self):
        self.transactions: Dict[str, PaymentTransaction] = {}
        self.processors: Dict[PaymentProvider, BasePaymentProcessor] = {}
    
    def register_processor(
        self,
        provider: PaymentProvider,
        processor: BasePaymentProcessor
    ):
        """Register a payment processor"""
        self.processors[provider] = processor
    
    async def process_booking_payment(
        self,
        booking_id: str,
        payer_id: str,
        recipient_id: str,
        payment_details: PaymentDetails
    ) -> PaymentTransaction:
        """Process payment for a booking"""
        
        processor = self.processors.get(payment_details.provider)
        if not processor:
            raise ValueError(f"Payment provider {payment_details.provider} not configured")
        
        metadata = {
            "booking_id": booking_id,
            "payer_id": payer_id,
            "recipient_id": recipient_id
        }
        
        # Process payment
        transaction = await processor.process_payment(payment_details, metadata)
        
        # Store transaction
        self.transactions[transaction.transaction_id] = transaction
        
        logger.info(f"Processed payment {transaction.transaction_id} for booking {booking_id}")
        
        return transaction
    
    async def calculate_optimal_payment_method(
        self,
        amount: float,
        currency: Currency,
        payer_country: str
    ) -> List[Dict[str, Any]]:
        """Suggest optimal payment methods based on amount and location"""
        
        suggestions = []
        
        # For Thai users
        if payer_country == "TH":
            if currency == Currency.THB:
                suggestions.append({
                    "method": PaymentMethod.PROMPTPAY,
                    "provider": PaymentProvider.PROMPTPAY,
                    "fee_percentage": 0,
                    "processing_time": "instant"
                })
        
        # For international users
        suggestions.append({
            "method": PaymentMethod.CREDIT_CARD,
            "provider": PaymentProvider.STRIPE,
            "fee_percentage": 2.9,
            "processing_time": "instant"
        })
        
        # For crypto enthusiasts
        if amount > 1000:  # USD equivalent
            suggestions.append({
                "method": PaymentMethod.CRYPTOCURRENCY,
                "provider": PaymentProvider.BINANCE_PAY,
                "fee_percentage": 1.0,
                "processing_time": "5-30 minutes"
            })
        
        return suggestions
    
    async def get_payment_analytics(self) -> Dict[str, Any]:
        """Get payment processing analytics"""
        
        total_transactions = len(self.transactions)
        completed_transactions = sum(
            1 for t in self.transactions.values()
            if t.status == PaymentStatus.COMPLETED
        )
        
        total_volume = sum(
            t.gross_amount for t in self.transactions.values()
            if t.status == PaymentStatus.COMPLETED
        )
        
        total_fees = sum(
            t.fee_amount for t in self.transactions.values()
            if t.status == PaymentStatus.COMPLETED
        )
        
        return {
            "total_transactions": total_transactions,
            "completed_transactions": completed_transactions,
            "success_rate": completed_transactions / max(total_transactions, 1),
            "total_volume": total_volume,
            "total_fees_collected": total_fees,
            "average_transaction_size": total_volume / max(completed_transactions, 1),
            "revenue_from_fees": total_fees  # SiamStay's revenue from processing
        }
