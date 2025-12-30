from pydantic import BaseModel
from typing import List, Optional
from app.schemas.common import BaseResponse, VehicleInfo, PriceRange


class PartMatch(BaseModel):
    """Part match schema"""
    part_number: str
    name: str
    description: str
    compatibility: str
    price_range: PriceRange
    suppliers: List[str]
    confidence: float
    oem: bool = False
    image_url: Optional[str] = None


class PartsIdentifyRequest(BaseModel):
    """Parts identification request schema"""
    description: Optional[str] = None
    vehicle: Optional[VehicleInfo] = None


class PartsIdentifyResponse(BaseResponse):
    """Parts identification response schema"""
    matches: List[PartMatch]
