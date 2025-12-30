from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from app.schemas.common import BaseResponse, VehicleInfo


class Recall(BaseModel):
    """Recall information schema"""
    recall_id: str
    campaign_number: str
    description: str
    consequence: str
    remedy: str
    date_issued: str


class SpecificationsResponse(BaseResponse):
    """Specifications response schema"""
    vin: str
    vehicle: VehicleInfo
    specifications: Dict[str, Any]
    recalls: List[Recall]
