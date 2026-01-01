from fastapi import APIRouter, HTTPException
from app.schemas.diagnostics import (
    DiagnosticsRequest,
    DiagnosticsResponse,
    FaultCodeAnalysis,
    SafetyAssessment,
    Cause,
    CostEstimate,
    DiagnosticStep
)
from app.schemas.common import PriceRange
from app.services.diagnostics_service import get_diagnostics_service
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/diagnostics/troubleshoot", response_model=DiagnosticsResponse)
async def troubleshoot(request: DiagnosticsRequest):
    """
    🔧 Intelligent Diagnostic Troubleshooting

    This is NOT a simple fault code lookup. It provides:
    - Workshop-ready diagnostic analysis with reasoning
    - Ranked probable causes with explanations
    - Step-by-step diagnostic procedures
    - Cost estimates with assumptions
    - Safety assessments
    - Actionable next steps

    The system understands your intent, analyzes the fault code in context,
    and provides transparent reasoning for all recommendations.

    Example Input:
    ```json
    {
        "fault_codes": ["P0420"],
        "vehicle": {
            "make": "Toyota",
            "model": "Camry",
            "year": 2015
        },
        "symptoms": ["Check engine light on", "Poor fuel economy"],
        "mileage": 95000
    }
    ```

    Returns comprehensive analysis with explanations and assumptions.
    """
    try:
        logger.info(
            "diagnostics_request",
            codes=request.fault_codes,
            vehicle=request.vehicle.model_dump() if request.vehicle else None
        )

        # Currently handle single fault code (can extend to multiple codes)
        if not request.fault_codes:
            raise HTTPException(status_code=400, detail="At least one fault code is required")

        fault_code = request.fault_codes[0]

        # Prepare vehicle context
        vehicle_dict = None
        if request.vehicle:
            vehicle_dict = request.vehicle.model_dump()
            if request.mileage:
                vehicle_dict["mileage"] = request.mileage

        # Get diagnostics service
        service = get_diagnostics_service()

        # Perform intelligent analysis
        analysis = service.analyze_fault_code(
            fault_code=fault_code,
            vehicle=vehicle_dict,
            symptoms=request.symptoms,
            context=request.context
        )

        # Check if analysis failed (unknown code)
        if not analysis.get("success", False):
            raise HTTPException(
                status_code=404,
                detail={
                    "message": analysis.get("message"),
                    "explanation": analysis.get("explanation"),
                    "general_guidance": analysis.get("general_guidance"),
                    "next_steps": analysis.get("next_steps")
                }
            )

        # Transform service output to API schema
        fault_code_data = analysis["fault_code_analysis"]
        safety_data = analysis.get("safety_assessment", {})
        cost_data = analysis["cost_estimate"]
        causes_data = analysis["likely_causes"]
        steps_data = analysis["diagnostic_steps"]

        # Build Safety Assessment
        safety = SafetyAssessment(
            driveable=safety_data.get("driveable", True),
            explanation=safety_data.get("explanation", "Consult professional for safety assessment"),
            risks=safety_data.get("risks", []),
            urgency=analysis["recommendations"].get("urgency", "moderate")
        )

        # Build Fault Code Analysis
        fault_code_analysis = FaultCodeAnalysis(
            code=fault_code_data["code"],
            description=fault_code_data["description"],
            system=fault_code_data["system"],
            severity=fault_code_data["severity"],
            explanation=fault_code_data["explanation"],
            safety=safety
        )

        # Build Causes with cost estimates
        likely_causes = []
        for cause_data in causes_data:
            cause_cost = cause_data.get("cost_estimate")
            cost_estimate = None
            if cause_cost:
                cost_estimate = CostEstimate(
                    parts_cost=PriceRange(**cause_cost),
                    labor_cost=PriceRange(
                        min=cause_cost.get("min", 0) * 0.3,
                        max=cause_cost.get("max", 0) * 0.5,
                        currency="SGD"
                    ),
                    total_cost=PriceRange(
                        min=cause_cost.get("min", 0),
                        max=cause_cost.get("max", 0),
                        currency="SGD"
                    ),
                    explanation=f"Cost estimate for: {cause_data['cause']}",
                    assumptions=["Includes parts and typical labor rates in Singapore"]
                )

            likely_causes.append(Cause(
                cause=cause_data["cause"],
                probability=cause_data["probability"],
                explanation=cause_data["explanation"],
                severity=fault_code_data["severity"],
                cost_estimate=cost_estimate,
                parts_needed=None,  # Can be added from parts_needed field
                diy_feasible=analysis["recommendations"].get("diy_feasible")
            ))

        # Build Diagnostic Steps
        diagnostic_steps = []
        for step_data in steps_data:
            diagnostic_steps.append(DiagnosticStep(
                step=step_data["step"],
                action=step_data["action"],
                explanation=step_data["explanation"],
                tools_needed=step_data["tools_needed"],
                estimated_time=step_data["estimated_time"],
                what_to_look_for=step_data.get("what_to_look_for")
            ))

        # Build Overall Cost Estimate
        cost_estimate = CostEstimate(
            parts_cost=PriceRange(**cost_data["parts_cost"]),
            labor_cost=PriceRange(**cost_data["labor_cost"]),
            total_cost=PriceRange(**cost_data["total_estimate"]),
            explanation=cost_data["explanation"],
            assumptions=analysis["assumptions"]
        )

        # Generate reasoning summary
        reasoning = (
            f"Based on fault code {fault_code} analysis, the most likely cause is "
            f"{causes_data[0]['cause']} (probability: {causes_data[0]['probability']:.0%}). "
            f"{causes_data[0]['explanation']} "
            f"Recommended action: {analysis['recommendations']['immediate_action']}"
        )

        # Build response
        response = DiagnosticsResponse(
            success=True,
            intent_understood=analysis["intent_understood"],
            fault_code_analysis=fault_code_analysis,
            likely_causes=likely_causes,
            diagnostic_steps=diagnostic_steps,
            cost_estimate=cost_estimate,
            assumptions=analysis["assumptions"],
            next_steps=analysis["next_steps"],
            reasoning=reasoning,
            metadata={
                **analysis["metadata"],
                "service_version": "1.0",
                "fault_codes_analyzed": request.fault_codes
            }
        )

        logger.info(
            "diagnostics_complete",
            code=fault_code,
            top_cause=causes_data[0]["cause"],
            confidence=analysis["metadata"]["confidence"]
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("diagnostics_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Diagnostic analysis failed: {str(e)}")
