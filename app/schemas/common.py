from pydantic import BaseModel
from typing import Dict, List, Any, Optional


class BaseResponse(BaseModel):
    """Base response schema"""
    success: bool
    metadata: Dict[str, Any]


class VehicleInfo(BaseModel):
    """Vehicle information schema"""
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    trim: Optional[str] = None
    vin: Optional[str] = None


class PriceRange(BaseModel):
    """Price range schema"""
    min: float
    max: float
    currency: str = "USD"
