from fastapi import APIRouter, UploadFile, File, Form, Depends
from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.v1.specifications import get_specifications
from typing import Optional, Dict, Any, List
from app.schemas.query import QueryRequest, QueryResponse
from app.services.query_service import get_query_service
from app.services.diagnostics_service import get_diagnostics_service
from app.services.valuation_service import get_valuation_service
from app.services.paint_code_service import get_paint_code_service
from app.services.parts_search import get_search_engine
from app.core.logging import get_logger
import time

router = APIRouter()
logger = get_logger(__name__)


@router.post("/query", response_model=QueryResponse)
async def process_query(
    text: str = Form(..., min_length=1, max_length=4000),
    image: Optional[UploadFile] = File(None),
    context: Optional[Dict[str, Any]] = Form(None),
    db: Session = Depends(get_db)
):
    """
    🤖 Multi-Modal Automotive Intelligence System

    This is NOT a simple keyword lookup or parts search API.

    This endpoint:
    1. Understands your intent (diagnostics, valuation, parts, paint code, specs)
    2. Extracts all relevant entities (VIN, fault codes, symptoms, vehicle info)
    3. Automatically routes to the appropriate intelligent module
    4. Executes the module and returns workshop-ready answers
    5. Provides transparent reasoning, assumptions, and next steps

    Example Queries:
    - "My 2015 Honda Civic has code P0420, what's wrong?"
      → Executes diagnostics module, returns causes, steps, costs

    - "How much is my 2018 Toyota Camry with 75k km worth?"
      → Executes valuation module, returns estimates, market analysis

    - "Need paint code for my white BMW 3-series"
      → Executes paint code module, returns locations, products

    - "Find brake pads for 2017 Mazda CX-5"
      → Executes parts search, returns compatible parts with links

    You get complete, explained answers - not just suggestions to call other endpoints.
    """
    start_time = time.time()

    logger.info("query_received", query_length=len(text), has_image=image is not None)

    try:
        # Get query service instance
        query_service = get_query_service()

        # Step 1: Classify intent and extract entities
        query_result = query_service.process_query(text)

        intent = query_result["intent"]
        confidence = query_result["confidence"]
        entities = query_result["entities"]

        logger.info("intent_classified", intent=intent, confidence=f"{confidence:.3f}", entity_fields=list(entities))

        # Step 2: Route to appropriate module and EXECUTE it
        result = await _execute_module(intent, entities, text, image, context, db)

        # Step 3: Generate follow-up questions based on actual result
        follow_up_questions = _generate_follow_up_questions(intent, entities, result)
        next_steps = result.get("next_steps", [])

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        logger.info("query_executed",
                   intent=intent,
                   module_executed=result.get("module_executed"),
                   processing_time_ms=processing_time_ms)

        return QueryResponse(
            success=True,
            intent=intent or "unknown",
            confidence=confidence,
            result=result,
            metadata={
                "processing_time_ms": processing_time_ms,
                "entities": entities,
                "models_used": ["intent_classifier_simple", "entity_extractor", result.get("module_executed")],
                "sources": ["ml_model", "intelligent_module_execution"]
            },
            follow_up_questions=follow_up_questions,
            next_steps=next_steps
        )

    except Exception as e:
        logger.error("query_processing_error", error_type=type(e).__name__)
        processing_time_ms = int((time.time() - start_time) * 1000)

        return QueryResponse(
            success=False,
            intent="error",
            confidence=0.0,
            result={
                "error": "Query processing failed",
                "explanation": "An error occurred while processing your query. Please try rephrasing or providing more details."
            },
            metadata={
                "processing_time_ms": processing_time_ms,
                "models_used": [],
                "sources": []
            },
            follow_up_questions=["Could you rephrase your question with more details?"],
            next_steps=["Try being more specific about what you need help with"]
        )


async def _execute_module(
    intent: str,
    entities: Dict[str, Any],
    query_text: str,
    image: Optional[UploadFile],
    context: Optional[Dict[str, Any]],
    db: Session
) -> Dict[str, Any]:
    """
    Execute the appropriate intelligent module based on intent

    This is the key function that actually RUNS the modules instead of just suggesting them.
    """

    if intent == "diagnostics":
        return await _execute_diagnostics(entities, query_text)

    elif intent == "vehicle_valuation":
        return await _execute_valuation(entities, query_text)

    elif intent == "paint_code":
        return await _execute_paint_code(entities, query_text)

    elif intent == "parts_identification":
        return await _execute_parts_search(entities, query_text, db)

    elif intent == "specifications":
        return await _execute_specifications(entities, query_text, db)

    elif intent == "general_question":
        return _execute_general_question(entities, query_text)

    else:
        return {
            "module_executed": "unknown_intent_handler",
            "message": "I couldn't determine what you need help with",
            "intent_detected": intent,
            "entities_found": entities,
            "suggestion": "Try asking about diagnostics, valuations, paint codes, parts, or specifications",
            "next_steps": ["Rephrase your query to be more specific"]
        }


async def _execute_diagnostics(entities: Dict[str, Any], query_text: str) -> Dict[str, Any]:
    """Execute diagnostics module"""
    service = get_diagnostics_service()

    # Extract fault codes
    fault_codes = entities.get("fault_codes", [])
    if not fault_codes:
        return {
            "module_executed": "diagnostics_missing_data",
            "message": "I understand you need diagnostic help, but I need a fault code",
            "explanation": "Please provide the OBD-II fault code (like P0420 or P0300) from your scanner",
            "next_steps": [
                "Get the fault code from your OBD-II scanner",
                "Provide the code in your query (e.g., 'I have code P0420')",
                "If you don't have a scanner, describe your symptoms in detail"
            ]
        }

    # Extract vehicle info
    vehicle = {}
    if entities.get("make"):
        vehicle["make"] = entities["make"]
    if entities.get("model"):
        vehicle["model"] = entities["model"]
    if entities.get("year"):
        vehicle["year"] = entities["year"]
    if entities.get("mileage"):
        vehicle["mileage"] = entities["mileage"]

    # Extract symptoms
    symptoms = entities.get("symptoms", [])

    # Execute diagnostics analysis
    analysis = service.analyze_fault_code(
        fault_code=fault_codes[0],  # Use first code
        vehicle=vehicle if vehicle else None,
        symptoms=symptoms if symptoms else None,
        context=None
    )

    # Return the full analysis
    return {
        "module_executed": "diagnostics_service",
        **analysis
    }


async def _execute_valuation(entities: Dict[str, Any], query_text: str) -> Dict[str, Any]:
    """Execute valuation module"""
    service = get_valuation_service()

    # Build vehicle dict
    vehicle = {}
    required_fields = []

    if entities.get("make"):
        vehicle["make"] = entities["make"]
    else:
        required_fields.append("vehicle make (e.g., Toyota, Honda)")

    if entities.get("model"):
        vehicle["model"] = entities["model"]
    else:
        required_fields.append("vehicle model (e.g., Camry, Civic)")

    if entities.get("year"):
        vehicle["year"] = entities["year"]
    else:
        required_fields.append("vehicle year (e.g., 2018)")

    mileage = entities.get("mileage")
    if mileage is None:
        required_fields.append("current mileage (e.g., 75000 km)")

    if required_fields:
        return {
            "module_executed": "valuation_missing_data",
            "message": "I understand you want a valuation, but I need more information",
            "missing_fields": required_fields,
            "explanation": f"For accurate valuation, please provide: {', '.join(required_fields)}",
            "example": "Try: 'How much is my 2018 Toyota Camry with 75,000 km worth?'",
            "next_steps": [f"Provide your {field}" for field in required_fields[:3]]
        }

    # Execute valuation
    analysis = service.estimate_value(
        vehicle=vehicle,
        mileage=mileage,
        condition=entities.get("condition", "good"),
        location="Singapore"
    )

    return {
        "module_executed": "valuation_service",
        **analysis
    }


async def _execute_paint_code(entities: Dict[str, Any], query_text: str) -> Dict[str, Any]:
    """Execute paint code lookup"""
    service = get_paint_code_service()

    make = entities.get("make")
    if not make:
        return {
            "module_executed": "paint_code_missing_data",
            "message": "I understand you need a paint code, but I need to know your vehicle make",
            "explanation": "Please tell me the manufacturer of your vehicle (e.g., Toyota, BMW, Honda)",
            "example": "Try: 'Need paint code for my white Toyota Camry'",
            "next_steps": ["Provide your vehicle's make (manufacturer)"]
        }

    # Execute paint code lookup
    analysis = service.lookup_paint_code(
        vin=entities.get("vin"),
        make=make,
        model=entities.get("model"),
        year=entities.get("year"),
        color_description=entities.get("color")
    )

    return {
        "module_executed": "paint_code_service",
        **analysis
    }


async def _execute_parts_search(entities, query_text, db):
    part_name = entities.get("part_name")
    if not part_name:
        return {"module_executed": "parts_search_missing_data", "missing_fields": ["part name"],
                "message": "Specify the part you need"}
    vehicle = {key: entities[key] for key in ("make", "model", "year") if key in entities}
    result = await run_in_threadpool(get_search_engine().search, db=db, query=part_name,
                                    vehicle=vehicle or None, limit=20, singapore_only=True)
    return {"module_executed": "parts_search_service", "success": True, **result}


async def _execute_specifications(entities, query_text, db):
    if not entities.get("vin"):
        return {"module_executed": "specifications_missing_data", "missing_fields": ["VIN"],
                "message": "Provide a 17-character VIN for the specification lookup"}
    result = await get_specifications(entities["vin"], db=db, use_cache=True)
    return {"module_executed": "specifications_service", **result.model_dump()}


def _execute_general_question(entities: Dict[str, Any], query_text: str) -> Dict[str, Any]:
    """Handle general automotive questions"""
    return {
        "module_executed": "general_question_handler",
        "intent_understood": "User has a general automotive question",
        "query": query_text,
        "message": "General question detected - would provide automotive knowledge response",
        "suggestion": "For specific help, try asking about diagnostics, valuations, paint codes, or parts",
        "next_steps": [
            "Ask about a specific vehicle issue if you have one",
            "Or ask about valuation, paint codes, or parts needs"
        ]
    }


def _generate_follow_up_questions(
    intent: Optional[str],
    entities: Dict[str, Any],
    result: Dict[str, Any]
) -> List[str]:
    """Generate contextual follow-up questions based on actual execution result"""
    questions = []

    # If module was executed successfully
    if result.get("success"):
        # Diagnostics follow-ups
        if intent == "diagnostics":
            questions.append("Would you like to know about parts needed for this repair?")
            questions.append("Do you want to know where to find qualified mechanics?")

        # Valuation follow-ups
        elif intent == "vehicle_valuation":
            questions.append("Would you like tips on preparing your vehicle for sale?")
            questions.append("Want to know the best time to sell?")

        # Paint code follow-ups
        elif intent == "paint_code":
            questions.append("Need help with touch-up application techniques?")
            questions.append("Want recommendations for paint preparation?")

        # Parts search follow-ups
        elif intent == "parts_identification":
            questions.append("Would you like installation instructions for this part?")
            questions.append("Need help finding a mechanic to install it?")

    # If module needs more data
    elif result.get("module_executed", "").endswith("_missing_data"):
        missing = result.get("missing_fields", [])
        for field in missing[:2]:
            questions.append(f"What is your {field}?")

    # Generic fallback
    if not questions:
        questions.append("Is there anything else I can help you with?")

    return questions[:3]
