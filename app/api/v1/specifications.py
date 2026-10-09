import re
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas.specifications import SpecificationsResponse, Recall
from app.schemas.common import VehicleInfo
from app.db.session import get_db
from app.db.models import Vehicle, Specification
from app.core.logging import get_logger
from app.services.external.nhtsa import NHTSAService

router = APIRouter()
logger = get_logger(__name__)


@router.get("/specifications/{vin}", response_model=SpecificationsResponse)
async def get_specifications(vin: str, db: Session = Depends(get_db), use_cache: bool = True):
    """
    Get vehicle specifications by VIN

    This endpoint:
    1. Checks database cache first
    2. If not found, queries NHTSA API for real data
    3. Caches the result for future requests
    4. Returns complete vehicle specifications and recalls

    Args:
        vin: 17-character Vehicle Identification Number
        use_cache: Whether to use cached data (default: True)

    Returns:
        Complete vehicle specifications including:
        - Vehicle information (make, model, year, trim)
        - Engine specifications
        - Transmission details
        - Safety features
        - Recall information
    """
    logger.info("get_specifications", vin=vin, use_cache=use_cache)

    if len(vin) != 17:
        raise HTTPException(status_code=400, detail="VIN must be 17 characters")

    vin = vin.upper()
    if not re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", vin):
        raise HTTPException(status_code=400, detail="VIN contains invalid characters")

    # Initialize NHTSA service
    nhtsa = NHTSAService()

    # Try to get from database cache first
    vehicle = db.query(Vehicle).filter(Vehicle.vin == vin).first()

    if vehicle and use_cache:
        logger.info("using_cached_data", vin=vin)
        # Get cached specifications
        specs = db.query(Specification).filter(Specification.vehicle_id == vehicle.id).all()

        # Organize specifications by type
        specifications_dict = {}
        for spec in specs:
            if spec.spec_type not in specifications_dict:
                specifications_dict[spec.spec_type] = {}
            specifications_dict[spec.spec_type][spec.spec_key] = spec.spec_value

        # Get recalls
        recalls_data = await _get_model_recalls(nhtsa, vehicle.make, vehicle.model, vehicle.year)
        recalls = _format_recalls(recalls_data)

        return SpecificationsResponse(
            success=True,
            vin=vin,
            vehicle=VehicleInfo(
                make=vehicle.make,
                model=vehicle.model,
                year=vehicle.year,
                trim=vehicle.trim,
                vin=vehicle.vin
            ),
            specifications=specifications_dict,
            recalls=recalls,
            metadata={
                "source": "cache",
                "recalls_scope": "make_model_year",
                "vin_recall_completion_status": "not_checked",
                "specs_count": len(specs),
                "recalls_count": len(recalls)
            }
        )

    # Not in cache - query NHTSA API
    logger.info("querying_nhtsa_api", vin=vin)
    nhtsa_data = await nhtsa.decode_vin(vin)

    if not nhtsa_data:
        raise HTTPException(
            status_code=404,
            detail=f"Vehicle with VIN {vin} not found in NHTSA database"
        )

    # Get recalls
    recalls_data = await _get_model_recalls(nhtsa, nhtsa_data["make"], nhtsa_data["model"], int(nhtsa_data["year"]))
    recalls = _format_recalls(recalls_data)

    # Replace the NHTSA cache as one transaction when a fresh decode is requested.
    if not vehicle:
        vehicle = Vehicle(vin=vin)
        db.add(vehicle)
    for key in ("make", "model", "year", "trim"):
        value = nhtsa_data.get(key)
        setattr(vehicle, key, int(value) if key == "year" else value)
    db.flush()
    _cache_specifications(db, vehicle.id, nhtsa_data)

    # Format specifications for response
    specifications_dict = _format_nhtsa_specs(nhtsa_data)

    logger.info("nhtsa_data_retrieved", vin=vin, specs_count=len(specifications_dict))

    return SpecificationsResponse(
        success=True,
        vin=vin,
        vehicle=VehicleInfo(
            make=vehicle.make,
            model=vehicle.model,
            year=vehicle.year,
            trim=vehicle.trim,
            vin=vehicle.vin
        ),
        specifications=specifications_dict,
        recalls=recalls,
        metadata={
            "source": "nhtsa_api",
            "recalls_scope": "make_model_year",
            "vin_recall_completion_status": "not_checked",
            "cached": True,
            "recalls_count": len(recalls)
        }
    )


async def _get_model_recalls(service, make, model, year):
    try:
        return await service.get_recalls_by_make_model_year(make, model, year)
    except Exception:
        raise HTTPException(status_code=502, detail="Recall provider unavailable; recall status is unknown") from None


def _format_nhtsa_specs(nhtsa_data: dict) -> dict:
    """Format NHTSA data into organized specifications"""
    specs = {}

    # Engine specs
    if nhtsa_data.get("engine"):
        engine = nhtsa_data["engine"]
        if engine:
            specs["engine"] = {k: v for k, v in engine.items() if v}

    # Transmission
    if nhtsa_data.get("transmission"):
        trans = nhtsa_data["transmission"]
        if trans:
            specs["transmission"] = {k: v for k, v in trans.items() if v}

    # Safety features
    if nhtsa_data.get("safety"):
        safety = nhtsa_data["safety"]
        if safety:
            specs["safety"] = {k: v for k, v in safety.items() if v}

    # Basic vehicle info
    basic_info = {}
    for key in ["body_class", "vehicle_type", "drive_type", "doors", "manufacturer"]:
        if nhtsa_data.get(key):
            basic_info[key] = nhtsa_data[key]
    if basic_info:
        specs["vehicle_info"] = basic_info

    return specs


def _cache_specifications(db: Session, vehicle_id: int, nhtsa_data: dict):
    """Cache NHTSA specifications in database"""
    types = ("engine", "transmission", "safety", "vehicle_info")
    db.query(Specification).filter(Specification.vehicle_id == vehicle_id,
        Specification.spec_type.in_(types)).delete(synchronize_session=False)
    for spec_type, fields in _format_nhtsa_specs(nhtsa_data).items():
        for key, value in fields.items():
            db.add(Specification(vehicle_id=vehicle_id, spec_type=spec_type, spec_key=key, spec_value=str(value)))
    db.commit()


def _format_recalls(recalls_data: list) -> list:
    """Format NHTSA recalls data"""
    formatted_recalls = []

    for recall in recalls_data:
        formatted_recalls.append(
            Recall(
                recall_id=recall.get("NHTSACampaignNumber", ""),
                campaign_number=recall.get("Manufacturer", ""),
                description=recall.get("Component", ""),
                consequence=recall.get("Consequence", ""),
                remedy=recall.get("Remedy", ""),
                date_issued=recall.get("ReportReceivedDate", "")
            )
        )

    return formatted_recalls
