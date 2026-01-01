from fastapi import APIRouter, HTTPException
from app.schemas.paint_code import (
    PaintCodeRequest,
    PaintCodeResponse,
    PaintCodeLocation,
    PaintProduct
)
from app.services.paint_code_service import get_paint_code_service
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/paint-code/lookup", response_model=PaintCodeResponse)
async def lookup_paint_code(request: PaintCodeRequest):
    """
    🎨 Intelligent Paint Code Lookup

    This is NOT a simple code lookup. It provides:
    - Where to find the paint code sticker on YOUR specific vehicle
    - Step-by-step verification instructions
    - Recommended touch-up products available in Singapore
    - Professional advice on when DIY is appropriate
    - Color matching suggestions based on description

    Even without VIN decoding, we provide actionable guidance to help you
    find and verify your paint code, then get the right products.

    Example Input:
    ```json
    {
        "make": "Toyota",
        "model": "Camry",
        "year": 2018,
        "color_description": "white with pearl finish"
    }
    ```

    Returns comprehensive guidance with product recommendations.
    """
    try:
        logger.info(
            "paint_code_request",
            vin=request.vin,
            make=request.make,
            model=request.model,
            color=request.color_description
        )

        # Validate minimum requirements
        if not request.make and not request.vin:
            raise HTTPException(
                status_code=400,
                detail="Either vehicle make or VIN is required for paint code lookup"
            )

        # Get paint code service
        service = get_paint_code_service()

        # Perform intelligent lookup
        analysis = service.lookup_paint_code(
            vin=request.vin,
            make=request.make,
            model=request.model,
            year=request.year,
            color_description=request.color_description
        )

        # Check if analysis failed
        if not analysis.get("success", False):
            raise HTTPException(
                status_code=400,
                detail={
                    "message": analysis.get("message"),
                    "reason": analysis.get("reason"),
                    "helpful_tip": analysis.get("helpful_tip")
                }
            )

        # Transform service output to API schema
        locations_data = analysis["paint_code_locations"]
        products_data = analysis["recommended_products"]

        # Build Paint Code Locations
        paint_code_locations = [
            PaintCodeLocation(**loc)
            for loc in locations_data
        ]

        # Build Recommended Products
        recommended_products = [
            PaintProduct(**prod)
            for prod in products_data
        ]

        # Build response
        response = PaintCodeResponse(
            success=True,
            intent_understood=analysis["intent_understood"],
            paint_code=analysis.get("paint_code"),
            color_name=analysis.get("color_name"),
            alternative_names=analysis.get("alternative_names"),
            paint_code_locations=paint_code_locations,
            verification_steps=analysis["verification_steps"],
            recommended_products=recommended_products,
            professional_advice=analysis["professional_advice"],
            assumptions=analysis["assumptions"],
            confidence=analysis["confidence"],
            reasoning=analysis["reasoning"],
            metadata={
                **analysis["metadata"],
                "service_version": "1.0"
            }
        )

        logger.info(
            "paint_code_complete",
            make=request.make,
            suggested_code=analysis.get("paint_code"),
            confidence=analysis["confidence"]
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("paint_code_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Paint code lookup failed: {str(e)}")
