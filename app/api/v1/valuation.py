from fastapi import APIRouter, HTTPException
from app.schemas.valuation import (
    ValuationRequest,
    ValuationResponse,
    ValuationEstimate,
    DepreciationFactor,
    ComparableListing,
    MarketAnalysis
)
from app.schemas.common import PriceRange
from app.services.valuation_service import get_valuation_service
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/valuation/estimate", response_model=ValuationResponse)
async def estimate_value(request: ValuationRequest):
    """
    💰 Intelligent Vehicle Market Valuation

    This is NOT a simple price lookup. It provides:
    - Retail, private party, and trade-in value estimates
    - Detailed depreciation factor analysis with explanations
    - Comparable market listings
    - Current market trend analysis
    - Selling tips to maximize value
    - All assumptions listed transparently

    The system analyzes your vehicle in the context of the Singapore market,
    considering COE depreciation, mileage, condition, and current demand.

    Example Input:
    ```json
    {
        "vehicle": {
            "make": "Toyota",
            "model": "Corolla",
            "year": 2018
        },
        "mileage": 75000,
        "condition": "good",
        "location": "Singapore",
        "service_history": "full"
    }
    ```

    Returns comprehensive market analysis with reasoning and assumptions.
    """
    try:
        logger.info(
            "valuation_request",
            vehicle=request.vehicle.model_dump(),
            mileage=request.mileage,
            condition=request.condition
        )

        # Validate required fields
        if not request.vehicle.make or not request.vehicle.model or not request.vehicle.year:
            raise HTTPException(
                status_code=400,
                detail="Vehicle make, model, and year are required for valuation"
            )

        # Prepare vehicle context
        vehicle_dict = request.vehicle.model_dump()

        # Get valuation service
        service = get_valuation_service()

        # Perform intelligent valuation
        analysis = service.estimate_value(
            vehicle=vehicle_dict,
            mileage=request.mileage,
            condition=request.condition,
            location=request.location or "Singapore",
            modifications=request.modifications,
            accident_history=request.accident_history,
            service_history=request.service_history
        )

        # Check if analysis failed
        if not analysis.get("success", False):
            raise HTTPException(
                status_code=400,
                detail={
                    "message": analysis.get("message"),
                    "reason": analysis.get("reason"),
                    "required_fields": analysis.get("required_fields")
                }
            )

        # Transform service output to API schema
        valuation_data = analysis["valuation_estimate"]
        factors_data = analysis["depreciation_factors"]
        comparables_data = analysis["comparable_listings"]
        market_data = analysis["market_analysis"]

        # Build Valuation Estimate
        valuation_estimate = ValuationEstimate(
            retail_value=PriceRange(**valuation_data["retail_value"]),
            private_party=PriceRange(**valuation_data["private_party"]),
            trade_in_value=PriceRange(**valuation_data["trade_in_value"]),
            explanation=valuation_data["explanation"],
            confidence=valuation_data["confidence"]
        )

        # Build Depreciation Factors
        depreciation_factors = [
            DepreciationFactor(
                factor=factor["factor"],
                impact=factor["impact"],
                explanation=factor["explanation"]
            )
            for factor in factors_data
        ]

        # Build Comparable Listings
        comparable_listings = [
            ComparableListing(**comp)
            for comp in comparables_data
        ]

        # Build Market Analysis
        market_analysis = MarketAnalysis(**market_data)

        # Build response
        response = ValuationResponse(
            success=True,
            intent_understood=analysis["intent_understood"],
            valuation_estimate=valuation_estimate,
            depreciation_factors=depreciation_factors,
            comparable_listings=comparable_listings,
            market_analysis=market_analysis,
            selling_tips=analysis["selling_tips"],
            assumptions=analysis["assumptions"],
            reasoning=analysis["reasoning"],
            metadata={
                **analysis["metadata"],
                "service_version": "1.0",
                "location": request.location or "Singapore"
            }
        )

        logger.info(
            "valuation_complete",
            vehicle=f"{request.vehicle.year} {request.vehicle.make} {request.vehicle.model}",
            estimated_value=analysis["metadata"]["adjusted_value"],
            confidence=valuation_data["confidence"]
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("valuation_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Valuation analysis failed: {str(e)}")
