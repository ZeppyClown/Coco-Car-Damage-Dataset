from pydantic import BaseModel
from typing import Optional
from app.schemas.common import BaseResponse


class PaintCodeRequest(BaseModel):
    """Paint code lookup request schema"""
    vin: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None


class PaintCodeResponse(BaseResponse):
    """Paint code lookup response schema"""
    paint_code: str
    color_name: str
    formula: Optional[str] = None
    confidence: float
