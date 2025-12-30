from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from app.schemas.common import BaseResponse


class QueryRequest(BaseModel):
    """Main query request schema"""
    text: str
    context: Optional[Dict[str, Any]] = None


class QueryResponse(BaseResponse):
    """Main query response schema"""
    intent: str
    confidence: float
    result: Dict[str, Any]
    follow_up_questions: List[str]
    next_steps: List[str]
