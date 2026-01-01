from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.parts import PartsIdentifyRequest, PartsIdentifyResponse, PartMatch
from app.schemas.common import PriceRange
from app.db.session import get_db
from app.db.models import PartPrice
from app.services.parts_search import get_search_engine
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/parts/identify", response_model=PartsIdentifyResponse)
async def identify_part(
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    vehicle_make: Optional[str] = Form(None),
    vehicle_model: Optional[str] = Form(None),
    vehicle_year: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Identify automotive parts from description or image

    HYBRID SYSTEM: Searches synthetic database + Google CSE + eBay
    Data sources used are indicated in the metadata

    Returns:
    - Matching parts with part numbers
    - Compatibility information
    - Price ranges (SGD)
    - Supplier information
    """
    logger.info("parts_identify_request",
               description=description,
               vehicle_make=vehicle_make,
               vehicle_model=vehicle_model,
               vehicle_year=vehicle_year,
               has_image=image is not None)

    # Validate input
    if not description and not image:
        raise HTTPException(status_code=400, detail="Either description or image is required")

    # Build vehicle context
    vehicle = None
    if vehicle_make or vehicle_model or vehicle_year:
        vehicle = {
            "make": vehicle_make,
            "model": vehicle_model,
            "year": vehicle_year
        }

    # Get search engine
    search_engine = get_search_engine()

    try:
        # Search for parts (image search not yet implemented, use description)
        if description:
            search_results = search_engine.search(
                db=db,
                query=description,
                vehicle=vehicle,
                limit=20,
                singapore_only=True
            )
        else:
            # TODO: Implement image-based part recognition
            raise HTTPException(status_code=501, detail="Image-based search not yet implemented")

        # Convert results to PartMatch schema
        matches = []
        for result in search_results.get("results", []):
            # Get price information
            price_data = db.query(PartPrice).filter(
                PartPrice.part_id == result["id"]
            ).all()

            # Calculate price range
            if price_data:
                prices_sgd = [float(p.price_sgd) for p in price_data if p.price_sgd]
                if prices_sgd:
                    price_range = PriceRange(
                        min=min(prices_sgd),
                        max=max(prices_sgd),
                        currency="SGD"
                    )
                else:
                    price_range = PriceRange(min=0, max=0, currency="SGD")

                # Get unique suppliers
                suppliers = list(set([p.seller_name for p in price_data if p.seller_name]))
            else:
                price_range = PriceRange(min=0, max=0, currency="SGD")
                suppliers = []

            # Build compatibility string
            compatibility = "Unknown"
            if result.get("compatible"):
                confidence = result.get("compatibility_confidence", 1.0)
                if confidence >= 0.9:
                    compatibility = "Guaranteed fit"
                elif confidence >= 0.7:
                    compatibility = "Likely compatible"
                else:
                    compatibility = "May be compatible"
            elif vehicle:
                compatibility = "Not confirmed for this vehicle"

            # Create match
            match = PartMatch(
                part_number=result.get("part_number", ""),
                name=result.get("name", ""),
                description=result.get("description", ""),
                compatibility=compatibility,
                price_range=price_range,
                suppliers=suppliers,
                confidence=result.get("final_score", result.get("relevance_score", 0.0)),
                oem=result.get("oem_or_aftermarket", "").lower() == "oem",
                image_url=None  # TODO: Get from database when available
            )
            matches.append(match)

        logger.info("parts_identify_success",
                   query=description,
                   matches_count=len(matches),
                   sources=search_results.get("sources_queried", []))

        return PartsIdentifyResponse(
            success=True,
            matches=matches,
            metadata={
                "query": description,
                "vehicle": vehicle,
                "total_results": len(matches),
                "processing_time_ms": search_results.get("processing_time_ms", 0),
                "sources_queried": search_results.get("sources_queried", []),  # HYBRID SYSTEM
                "singapore_only": True
            }
        )

    except Exception as e:
        logger.error("parts_identify_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Parts identification failed: {str(e)}")
