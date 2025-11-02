"""
Booking Engine for SiamStay
Handles reservations, availability, and booking lifecycle
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class BookingStatus(str, Enum):
    """Booking status tracking"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class PaymentStatus(str, Enum):
    """Payment status for bookings"""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"
    FAILED = "failed"


class GuestProfile(BaseModel):
    """Guest information for booking"""
    guest_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    nationality: str
    passport_number: Optional[str] = None
    
    # Thailand-specific requirements
    visa_type: Optional[str] = None
    visa_expiry: Optional[date] = None
    thai_address: Optional[str] = None  # For TM30
    
    # Scoring and history
    guest_score: Optional[float] = None  # 0-100
    previous_bookings: int = 0
    verified: bool = False


class BookingDetails(BaseModel):
    """Core booking information"""
    check_in: date
    check_out: date
    guests_count: int = Field(ge=1, le=10)
    
    # Purpose and preferences
    purpose: str = "tourism"  # tourism, business, education, medical
    special_requests: Optional[str] = None
    
    # Calculated fields
    stay_duration_days: int
    stay_duration_months: float
    
    def __init__(self, **data):
        if 'check_in' in data and 'check_out' in data:
            check_in = data['check_in']
            check_out = data['check_out']
            stay_days = (check_out - check_in).days
            data['stay_duration_days'] = stay_days
            data['stay_duration_months'] = stay_days / 30.0
        super().__init__(**data)


class PricingBreakdown(BaseModel):
    """Detailed pricing calculation"""
    base_rent: float
    cleaning_fee: float = 0
    service_fee: float = 0  # SiamStay commission
    security_deposit: float = 0
    taxes: float = 0
    
    # Discounts
    long_stay_discount: float = 0
    seasonal_adjustment: float = 0
    
    # Totals
    subtotal: float
    total_amount: float
    
    # Payment schedule
    deposit_required: float  # Amount due at booking
    balance_due: float       # Amount due at check-in


class Booking(BaseModel):
    """Complete booking model"""
    booking_id: str
    property_id: str
    guest: GuestProfile
    details: BookingDetails
    pricing: PricingBreakdown
    
    # Status tracking
    status: BookingStatus = BookingStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING
    
    # Timestamps
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    checked_in_at: Optional[datetime] = None
    checked_out_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # Legal compliance
    contract_signed: bool = False
    tm30_filed: bool = False
    deposit_paid: bool = False
    
    # Communication
    confirmation_sent: bool = False
    check_in_instructions_sent: bool = False
    
    # Reviews and feedback
    guest_rating: Optional[float] = None
    property_rating: Optional[float] = None
    review_text: Optional[str] = None


class AvailabilityCalendar:
    """Manage property availability and blocking"""
    
    def __init__(self):
        # property_id -> {date: booking_id or "blocked"}
        self.calendar: Dict[str, Dict[date, str]] = {}
    
    def check_availability(
        self,
        property_id: str,
        check_in: date,
        check_out: date
    ) -> bool:
        """Check if property is available for given dates"""
        
        if property_id not in self.calendar:
            return True
        
        property_calendar = self.calendar[property_id]
        
        # Check each date in the range
        current_date = check_in
        while current_date < check_out:
            if current_date in property_calendar:
                return False  # Date is blocked
            current_date += timedelta(days=1)
        
        return True
    
    def block_dates(
        self,
        property_id: str,
        check_in: date,
        check_out: date,
        booking_id: str
    ):
        """Block dates for a booking"""
        
        if property_id not in self.calendar:
            self.calendar[property_id] = {}
        
        property_calendar = self.calendar[property_id]
        
        # Block each date in the range
        current_date = check_in
        while current_date < check_out:
            property_calendar[current_date] = booking_id
            current_date += timedelta(days=1)
    
    def release_dates(
        self,
        property_id: str,
        check_in: date,
        check_out: date
    ):
        """Release blocked dates (for cancellations)"""
        
        if property_id not in self.calendar:
            return
        
        property_calendar = self.calendar[property_id]
        
        # Release each date in the range
        current_date = check_in
        while current_date < check_out:
            if current_date in property_calendar:
                del property_calendar[current_date]
            current_date += timedelta(days=1)


class BookingEngine:
    """Core booking management service"""
    
    def __init__(self):
        self.bookings: Dict[str, Booking] = {}
        self.availability = AvailabilityCalendar()
    
    async def create_booking(
        self,
        property_id: str,
        guest_data: Dict[str, Any],
        booking_data: Dict[str, Any],
        pricing_data: Dict[str, Any]
    ) -> Booking:
        """Create new booking reservation"""
        
        # Validate minimum stay (Thailand requirement)
        check_in = booking_data["check_in"]
        check_out = booking_data["check_out"]
        stay_days = (check_out - check_in).days
        
        if stay_days < 30:
            raise ValueError("Minimum stay is 30 days for legal compliance")
        
        # Check availability
        if not self.availability.check_availability(property_id, check_in, check_out):
            raise ValueError("Property not available for selected dates")
        
        # Generate booking ID
        booking_id = f"book_{datetime.now().timestamp()}"
        
        # Create booking
        booking = Booking(
            booking_id=booking_id,
            property_id=property_id,
            guest=GuestProfile(**guest_data),
            details=BookingDetails(**booking_data),
            pricing=PricingBreakdown(**pricing_data),
            created_at=datetime.now()
        )
        
        # Store booking
        self.bookings[booking_id] = booking
        
        # Block dates
        self.availability.block_dates(property_id, check_in, check_out, booking_id)
        
        logger.info(f"Created booking {booking_id} for property {property_id}")
        
        return booking
    
    async def confirm_booking(self, booking_id: str) -> Booking:
        """Confirm booking after payment verification"""
        
        booking = self.bookings.get(booking_id)
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")
        
        if booking.status != BookingStatus.PENDING:
            raise ValueError(f"Booking {booking_id} cannot be confirmed")
        
        # Update status
        booking.status = BookingStatus.CONFIRMED
        booking.confirmed_at = datetime.now()
        
        # TODO: Send confirmation email
        booking.confirmation_sent = True
        
        logger.info(f"Confirmed booking {booking_id}")
        
        return booking
    
    async def cancel_booking(
        self,
        booking_id: str,
        reason: str = "guest_request"
    ) -> Dict[str, Any]:
        """Cancel booking and calculate refund"""
        
        booking = self.bookings.get(booking_id)
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")
        
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.CHECKED_OUT]:
            raise ValueError(f"Booking {booking_id} cannot be cancelled")
        
        # Calculate refund based on cancellation policy
        refund_amount = self._calculate_refund(booking)
        
        # Update booking status
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.now()
        
        # Release dates
        self.availability.release_dates(
            booking.property_id,
            booking.details.check_in,
            booking.details.check_out
        )
        
        logger.info(f"Cancelled booking {booking_id}, refund: {refund_amount}")
        
        return {
            "booking_id": booking_id,
            "cancelled_at": booking.cancelled_at,
            "refund_amount": refund_amount,
            "reason": reason
        }
    
    async def check_in_guest(
        self,
        booking_id: str,
        check_in_data: Dict[str, Any]
    ) -> Booking:
        """Process guest check-in"""
        
        booking = self.bookings.get(booking_id)
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")
        
        if booking.status != BookingStatus.CONFIRMED:
            raise ValueError(f"Booking {booking_id} not ready for check-in")
        
        # Update status
        booking.status = BookingStatus.CHECKED_IN
        booking.checked_in_at = datetime.now()
        
        # Mark TM30 filing as required
        # TODO: Integrate with Thai immigration system
        booking.tm30_filed = True
        
        logger.info(f"Checked in guest for booking {booking_id}")
        
        return booking
    
    def _calculate_refund(self, booking: Booking) -> float:
        """Calculate refund amount based on cancellation policy"""
        
        days_until_checkin = (booking.details.check_in - date.today()).days
        total_paid = booking.pricing.total_amount
        
        # Flexible cancellation policy for long-term stays
        if days_until_checkin >= 30:
            return total_paid * 0.95  # 95% refund
        elif days_until_checkin >= 14:
            return total_paid * 0.75  # 75% refund
        elif days_until_checkin >= 7:
            return total_paid * 0.50  # 50% refund
        else:
            return total_paid * 0.25  # 25% refund
    
    async def get_booking_analytics(self) -> Dict[str, Any]:
        """Get overall booking analytics"""
        
        total_bookings = len(self.bookings)
        confirmed_bookings = sum(
            1 for b in self.bookings.values() 
            if b.status == BookingStatus.CONFIRMED
        )
        
        total_revenue = sum(
            b.pricing.total_amount for b in self.bookings.values()
            if b.status != BookingStatus.CANCELLED
        )
        
        return {
            "total_bookings": total_bookings,
            "confirmed_bookings": confirmed_bookings,
            "confirmation_rate": confirmed_bookings / max(total_bookings, 1),
            "total_revenue": total_revenue,
            "average_booking_value": total_revenue / max(confirmed_bookings, 1),
            "average_stay_duration": sum(
                b.details.stay_duration_days for b in self.bookings.values()
            ) / max(total_bookings, 1)
        }
