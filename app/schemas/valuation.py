from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from app.schemas.common import BaseResponse, VehicleInfo, PriceRange


class ValuationEstimate(BaseModel):
    """Valuation estimate with market context"""
    retail_value: PriceRange  # Expected price at dealership
    private_party: PriceRange  # Expected price private sale
    trade_in_value: PriceRange  # Expected dealer trade-in value
    explanation: str  # Why this valuation range
    confidence: float  # 0.0 to 1.0


class DepreciationFactor(BaseModel):
    """Depreciation factor with explanation"""
    factor: str
    impact: float  # -10.5 = -10.5% impact on value
    explanation: str  # Why this factor affects value


class ComparableListing(BaseModel):
    """Comparable listing with similarity analysis"""
    source: str
    price: float
    currency: str = "SGD"
    mileage: int
    year: Optional[int] = None
    condition: Optional[str] = None
    location: str
    listing_url: Optional[str] = None
    date_listed: Optional[str] = None
    similarity_score: Optional[float] = None  # How similar to user's vehicle
    notes: Optional[str] = None


class MarketAnalysis(BaseModel):
    """Market condition analysis"""
    demand_level: str  # low, moderate, high, very_high
    supply_level: str  # scarce, limited, adequate, abundant
    market_trend: str  # declining, stable, rising
    explanation: str  # Market conditions explanation
    typical_days_to_sell: str


class ValuationRequest(BaseModel):
    """
    Vehicle valuation request

    Provides intelligent market value analysis with:
    - Retail, private party, and trade-in value estimates
    - Depreciation factor breakdown with explanations
    - Comparable market listings
    - Market trend analysis
    """
    vehicle: VehicleInfo
    mileage: int
    condition: str  # excellent, good, fair, poor
    location: Optional[str] = "Singapore"  # Location for market analysis
    modifications: Optional[List[str]] = None  # Any modifications
    accident_history: Optional[bool] = None
    service_history: Optional[str] = None  # full, partial, unknown


class ValuationResponse(BaseResponse):
    """
    Comprehensive valuation response with reasoning

    NOT a simple price lookup - provides intelligent market analysis
    with explanations, assumptions, and reasoning for all estimates.
    """
    intent_understood: str  # What the user wants to know
    valuation_estimate: ValuationEstimate  # Price ranges with confidence
    depreciation_factors: List[DepreciationFactor]  # What affects the value
    comparable_listings: List[ComparableListing]  # Similar vehicles for sale
    market_analysis: MarketAnalysis  # Current market conditions
    selling_tips: List[str]  # How to maximize sale price
    assumptions: List[str]  # What was assumed in analysis
    reasoning: str  # Overall reasoning for valuation
