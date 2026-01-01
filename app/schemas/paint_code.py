from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.schemas.common import BaseResponse


class PaintCodeLocation(BaseModel):
    """Where to find the paint code on the vehicle"""
    location: str
    description: str
    image_url: Optional[str] = None


class PaintProduct(BaseModel):
    """Recommended paint product"""
    product_type: str  # touch-up pen, spray can, professional paint
    brand: str
    product_name: str
    estimated_price: Optional[str] = None
    where_to_buy: str
    notes: str


class PaintCodeRequest(BaseModel):
    """
    Paint code lookup request

    Provides:
    - Paint code identification from VIN or vehicle info
    - Where to find the paint code on your vehicle
    - Official color name and variations
    - Recommended touch-up products
    - Instructions for color verification
    """
    vin: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color_description: Optional[str] = None  # User's description of the color


class PaintCodeResponse(BaseResponse):
    """
    Comprehensive paint code response with guidance

    NOT a simple lookup - provides actionable information about:
    - Where to find the code on your specific vehicle
    - How to verify the color match
    - What products to use for touch-up
    - All assumptions and confidence levels
    """
    intent_understood: str  # What the user wants to know
    paint_code: Optional[str]  # The paint code (if found)
    color_name: Optional[str]  # Official color name
    alternative_names: Optional[List[str]]  # Other names for this color
    paint_code_locations: List[PaintCodeLocation]  # Where to find code on vehicle
    verification_steps: List[str]  # How to verify the paint code
    recommended_products: List[PaintProduct]  # Touch-up products
    professional_advice: str  # When to consult professional
    assumptions: List[str]  # What was assumed
    confidence: float  # Confidence in the paint code match
    reasoning: str  # Why this is the likely paint code
