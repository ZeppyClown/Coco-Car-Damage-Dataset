from pydantic import BaseModel
from typing import Dict, List, Optional
from app.schemas.common import BaseResponse, VehicleInfo


class ValuationEstimate(BaseModel):
    """Valuation estimate schema"""
    low: float
    average: float
    high: float
    currency: str = "USD"


class ComparableListing(BaseModel):
    """Comparable listing schema"""
    source: str
    price: float
    mileage: int
    location: str
    listing_url: Optional[str] = None
    date_listed: Optional[str] = None


class ValuationRequest(BaseModel):
    """Valuation request schema"""
    vehicle: VehicleInfo
    mileage: int
    condition: str
    location: str  # ZIP code or city


class ValuationResponse(BaseResponse):
    """Valuation response schema"""
    estimate: ValuationEstimate
    comparables: List[ComparableListing]
    factors: Dict[str, float]
