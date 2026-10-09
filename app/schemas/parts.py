from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.common import BaseResponse, VehicleInfo, PriceRange


class PartMatch(BaseModel):
    """Part match schema"""
    part_number: str
    name: str
    description: str
    compatibility: str
    price_range: Optional[PriceRange] = None
    suppliers: List[str]
    confidence: float
    oem: bool = False
    image_url: Optional[str] = None
    source_url: Optional[str] = None


class PartsIdentifyRequest(BaseModel):
    """Parts identification request schema"""
    description: Optional[str] = None
    vehicle: Optional[VehicleInfo] = None


class PartsIdentifyResponse(BaseResponse):
    """Parts identification response schema"""
    matches: List[PartMatch]


class CompatibilityRequest(BaseModel):
    part_id: int = Field(gt=0)
    make: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1900, le=2100)
    trim: Optional[str] = None
    engine: Optional[str] = None
