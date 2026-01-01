from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.schemas.common import BaseResponse, VehicleInfo, PriceRange


class CostEstimate(BaseModel):
    """Cost estimate with explanation"""
    parts_cost: PriceRange
    labor_cost: PriceRange
    total_cost: PriceRange
    explanation: str  # Why this cost range
    assumptions: List[str]  # What was assumed in the estimate


class Cause(BaseModel):
    """Diagnostic cause with explanation and reasoning"""
    cause: str
    probability: float  # 0.0 to 1.0
    explanation: str  # Why this is a likely cause
    severity: str  # low, moderate, high, critical
    cost_estimate: Optional[CostEstimate] = None
    parts_needed: Optional[List[str]] = None
    diy_feasible: Optional[bool] = None


class DiagnosticStep(BaseModel):
    """Diagnostic step with tools and timing"""
    step: int
    action: str
    explanation: str  # Why this step is important
    tools_needed: List[str]
    estimated_time: str
    what_to_look_for: Optional[str] = None


class SafetyAssessment(BaseModel):
    """Safety information about the issue"""
    driveable: bool
    explanation: str  # Why it is/isn't safe to drive
    risks: List[str]  # Specific risks if driven
    urgency: str  # immediate, urgent, moderate, low


class FaultCodeAnalysis(BaseModel):
    """Detailed fault code analysis"""
    code: str
    description: str
    system: str  # engine, transmission, brakes, etc.
    severity: str
    explanation: str  # What this code means in plain language
    safety: SafetyAssessment


class DiagnosticsRequest(BaseModel):
    """
    Diagnostics request schema

    This endpoint analyzes fault codes and provides workshop-ready guidance
    with explanations, reasoning, and cost estimates.
    """
    fault_codes: List[str]  # OBD-II codes like ["P0420", "P0300"]
    vehicle: Optional[VehicleInfo] = None
    symptoms: Optional[List[str]] = None  # User-reported symptoms
    mileage: Optional[int] = None
    context: Optional[Dict[str, Any]] = None  # Additional context


class DiagnosticsResponse(BaseResponse):
    """
    Comprehensive diagnostics response with reasoning

    This is NOT a simple lookup - it provides intelligent analysis
    with explanations, assumptions, and workshop-ready guidance.
    """
    intent_understood: str  # What the user is trying to do
    fault_code_analysis: FaultCodeAnalysis  # Detailed code analysis
    likely_causes: List[Cause]  # Ranked by probability with explanations
    diagnostic_steps: List[DiagnosticStep]  # Step-by-step testing procedure
    cost_estimate: CostEstimate  # Overall cost estimate
    assumptions: List[str]  # What was assumed in this analysis
    next_steps: List[str]  # Recommended actions
    reasoning: str  # Overall reasoning for the recommendations
