from pydantic import BaseModel
from typing import List, Optional
from app.schemas.common import BaseResponse, VehicleInfo


class Cause(BaseModel):
    """Diagnostic cause schema"""
    description: str
    probability: float
    severity: str  # low, medium, high, critical


class DiagnosticStep(BaseModel):
    """Diagnostic step schema"""
    step_number: int
    description: str
    tools_required: List[str]
    expected_result: str


class Repair(BaseModel):
    """Repair procedure schema"""
    name: str
    description: str
    difficulty: str  # easy, moderate, difficult, expert
    estimated_time: str
    procedure_url: Optional[str] = None


class DiagnosticsRequest(BaseModel):
    """Diagnostics request schema"""
    vehicle: VehicleInfo
    system: str  # engine, transmission, brakes, etc.
    fault_codes: List[str]
    symptoms: str


class DiagnosticsResponse(BaseResponse):
    """Diagnostics response schema"""
    causes: List[Cause]
    diagnostic_steps: List[DiagnosticStep]
    repairs: List[Repair]
    parts_needed: List[str]
