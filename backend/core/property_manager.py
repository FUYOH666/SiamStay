"""
Property Management System for SiamStay
Handles property onboarding, validation, and lifecycle management
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, date
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class PropertyType(str, Enum):
    """Types of properties available for rental"""
    CONDO = "condo"
    APARTMENT = "apartment"
    HOUSE = "house"
    VILLA = "villa"
    TOWNHOUSE = "townhouse"
    STUDIO = "studio"


class PropertyStatus(str, Enum):
    """Property listing status"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    SUSPENDED = "suspended"


class PropertyAmenities(BaseModel):
    """Property amenities and features"""
    wifi: bool = True
    air_conditioning: bool = True
    kitchen: bool = True
    washing_machine: bool = False
    parking: bool = False
    swimming_pool: bool = False
    gym: bool = False
    security: bool = False
    balcony: bool = False
    workspace: bool = False
    
    # Thailand-specific amenities
    motorbike_parking: bool = False
    thai_toilet: bool = False
    western_toilet: bool = True
    water_heater: bool = True
    cable_tv: bool = False


class Location(BaseModel):
    """Property location information"""
    address: str
    district: str  # Amphoe
    province: str  # Changwat
    postal_code: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Location scores (calculated)
    walkability_score: Optional[int] = None  # 0-100
    transit_score: Optional[int] = None      # 0-100
    convenience_score: Optional[int] = None  # 0-100


class PropertyDetails(BaseModel):
    """Core property information"""
    title: str
    description: str
    property_type: PropertyType
    bedrooms: int = Field(ge=0, le=10)
    bathrooms: int = Field(ge=0, le=10)
    area_sqm: Optional[float] = Field(ge=0)
    floor_number: Optional[int] = None
    total_floors: Optional[int] = None
    
    amenities: PropertyAmenities
    location: Location
    
    # Legal compliance
    building_permit: Optional[str] = None
    chanote_title: Optional[str] = None  # Thai land title
    juristic_person_approval: bool = False  # For condos


class PricingStrategy(BaseModel):
    """Property pricing configuration"""
    base_monthly_rate: float = Field(gt=0)
    cleaning_fee: Optional[float] = 0
    security_deposit: float = Field(gt=0)
    utility_included: bool = False
    
    # Dynamic pricing parameters
    seasonal_multiplier: bool = True
    event_pricing: bool = True
    minimum_stay_days: int = Field(ge=30)  # Thailand legal requirement
    maximum_stay_days: Optional[int] = None
    
    # Discounts
    weekly_discount: float = Field(ge=0, le=1, default=0)
    monthly_discount: float = Field(ge=0, le=1, default=0)
    long_term_discount: float = Field(ge=0, le=1, default=0)  # 3+ months


class Property(BaseModel):
    """Complete property model"""
    property_id: str
    owner_id: str
    
    details: PropertyDetails
    pricing: PricingStrategy
    
    status: PropertyStatus = PropertyStatus.DRAFT
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    # Media
    photos: List[str] = []  # URLs to property photos
    virtual_tour_url: Optional[str] = None
    video_url: Optional[str] = None
    
    # Performance metrics
    views_count: int = 0
    inquiries_count: int = 0
    bookings_count: int = 0
    average_rating: Optional[float] = None
    
    # SiamStay specific
    verification_status: str = "pending"  # pending, verified, rejected
    compliance_check: bool = False
    tm30_ready: bool = False


class PropertyManager:
    """Service for managing property lifecycle"""
    
    def __init__(self):
        self.properties: Dict[str, Property] = {}
    
    async def create_property(
        self,
        owner_id: str,
        property_data: Dict[str, Any]
    ) -> Property:
        """Create new property listing"""
        
        # Generate property ID
        property_id = f"prop_{datetime.now().timestamp()}"
        
        # Validate and create property
        property_obj = Property(
            property_id=property_id,
            owner_id=owner_id,
            details=PropertyDetails(**property_data["details"]),
            pricing=PricingStrategy(**property_data["pricing"]),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Store property
        self.properties[property_id] = property_obj
        
        logger.info(f"Created property {property_id} for owner {owner_id}")
        
        return property_obj
    
    async def validate_compliance(self, property_id: str) -> Dict[str, Any]:
        """Validate Thai legal compliance for property"""
        
        property_obj = self.properties.get(property_id)
        if not property_obj:
            raise ValueError(f"Property {property_id} not found")
        
        compliance_issues = []
        
        # Check minimum stay requirement
        if property_obj.pricing.minimum_stay_days < 30:
            compliance_issues.append(
                "Minimum stay must be 30+ days for legal compliance"
            )
        
        # Check property documentation
        if not property_obj.details.chanote_title:
            compliance_issues.append("Chanote title required for verification")
        
        # For condos, check juristic person approval
        if (property_obj.details.property_type == PropertyType.CONDO and 
            not property_obj.details.juristic_person_approval):
            compliance_issues.append(
                "Juristic person approval required for condo rentals"
            )
        
        compliance_status = len(compliance_issues) == 0
        
        # Update property compliance
        property_obj.compliance_check = compliance_status
        property_obj.updated_at = datetime.now()
        
        return {
            "compliant": compliance_status,
            "issues": compliance_issues,
            "checked_at": datetime.now()
        }
    
    async def calculate_dynamic_price(
        self,
        property_id: str,
        check_in: date,
        check_out: date
    ) -> Dict[str, Any]:
        """Calculate dynamic pricing for given dates"""
        
        property_obj = self.properties.get(property_id)
        if not property_obj:
            raise ValueError(f"Property {property_id} not found")
        
        base_rate = property_obj.pricing.base_monthly_rate
        stay_days = (check_out - check_in).days
        
        # Apply seasonal multiplier (placeholder logic)
        seasonal_factor = 1.0
        if check_in.month in [12, 1, 2]:  # High season
            seasonal_factor = 1.3
        elif check_in.month in [6, 7, 8, 9]:  # Low season
            seasonal_factor = 0.8
        
        # Apply length of stay discounts
        discount_factor = 1.0
        if stay_days >= 90:  # 3+ months
            discount_factor = 1 - property_obj.pricing.long_term_discount
        elif stay_days >= 60:  # 2+ months
            discount_factor = 1 - property_obj.pricing.monthly_discount
        
        # Calculate final price
        daily_rate = base_rate / 30  # Convert monthly to daily
        total_price = daily_rate * stay_days * seasonal_factor * discount_factor
        
        return {
            "base_monthly_rate": base_rate,
            "daily_rate": daily_rate,
            "stay_days": stay_days,
            "seasonal_factor": seasonal_factor,
            "discount_factor": discount_factor,
            "total_price": round(total_price, 2),
            "cleaning_fee": property_obj.pricing.cleaning_fee,
            "security_deposit": property_obj.pricing.security_deposit
        }
    
    async def get_property_analytics(self, property_id: str) -> Dict[str, Any]:
        """Get property performance analytics"""
        
        property_obj = self.properties.get(property_id)
        if not property_obj:
            raise ValueError(f"Property {property_id} not found")
        
        # TODO: Implement real analytics from database
        return {
            "property_id": property_id,
            "performance": {
                "views": property_obj.views_count,
                "inquiries": property_obj.inquiries_count,
                "bookings": property_obj.bookings_count,
                "conversion_rate": (
                    property_obj.bookings_count / max(property_obj.views_count, 1)
                ),
                "average_rating": property_obj.average_rating
            },
            "occupancy": {
                "current_month": 0.0,  # Placeholder
                "last_month": 0.0,
                "year_to_date": 0.0
            },
            "revenue": {
                "current_month": 0.0,  # Placeholder
                "last_month": 0.0,
                "year_to_date": 0.0
            }
        }


class PropertySearchEngine:
    """Advanced property search and filtering"""
    
    def __init__(self, property_manager: PropertyManager):
        self.property_manager = property_manager
    
    async def search_properties(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """Search properties with filters"""
        
        # Get all active properties
        all_properties = [
            prop for prop in self.property_manager.properties.values()
            if prop.status == PropertyStatus.ACTIVE
        ]
        
        # Apply filters
        filtered_properties = all_properties
        
        if "location" in filters:
            filtered_properties = [
                prop for prop in filtered_properties
                if filters["location"].lower() in prop.details.location.province.lower()
            ]
        
        if "property_type" in filters:
            filtered_properties = [
                prop for prop in filtered_properties
                if prop.details.property_type == filters["property_type"]
            ]
        
        if "min_price" in filters:
            filtered_properties = [
                prop for prop in filtered_properties
                if prop.pricing.base_monthly_rate >= filters["min_price"]
            ]
        
        if "max_price" in filters:
            filtered_properties = [
                prop for prop in filtered_properties
                if prop.pricing.base_monthly_rate <= filters["max_price"]
            ]
        
        if "bedrooms" in filters:
            filtered_properties = [
                prop for prop in filtered_properties
                if prop.details.bedrooms >= filters["bedrooms"]
            ]
        
        # Apply pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_properties = filtered_properties[start:end]
        
        return {
            "properties": paginated_properties,
            "total_count": len(filtered_properties),
            "page": page,
            "page_size": page_size,
            "total_pages": (len(filtered_properties) + page_size - 1) // page_size
        }
