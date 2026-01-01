"""
Intelligent Diagnostics Service
Analyzes fault codes and provides workshop-ready diagnostic guidance
"""
from typing import List, Dict, Optional, Any
from datetime import datetime
from app.data.fault_codes_database import get_fault_code_info, FAULT_CODE_DATABASE
from app.core.logging import get_logger

logger = get_logger(__name__)


class DiagnosticsService:
    """
    Intelligent automotive diagnostics service

    Provides:
    - Fault code analysis with explanations
    - Probable causes with reasoning
    - Diagnostic procedures
    - Cost estimates
    - Workshop-ready guidance
    """

    def analyze_fault_code(
        self,
        fault_code: str,
        vehicle: Optional[Dict[str, Any]] = None,
        symptoms: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a fault code and provide comprehensive diagnostic guidance

        Args:
            fault_code: DTC code (e.g., "P0420")
            vehicle: Vehicle information {make, model, year, mileage}
            symptoms: List of reported symptoms
            context: Additional context (recent repairs, modifications, etc.)

        Returns:
            Structured diagnostic analysis with explanations and reasoning
        """
        logger.info("diagnostic_analysis_start", code=fault_code, vehicle=vehicle)

        # Get fault code information
        code_info = get_fault_code_info(fault_code)

        if not code_info:
            return self._handle_unknown_code(fault_code, vehicle, symptoms)

        # Build comprehensive analysis
        analysis = {
            "success": True,
            "intent_understood": self._generate_intent_summary(fault_code, vehicle, symptoms),
            "fault_code_analysis": self._analyze_code(fault_code, code_info, vehicle),
            "likely_causes": self._rank_causes(code_info, vehicle, symptoms, context),
            "diagnostic_steps": self._customize_diagnostic_steps(code_info, vehicle),
            "parts_potentially_needed": self._estimate_parts(code_info, vehicle),
            "safety_assessment": code_info.get("immediate_safety", {}),
            "repair_guidance": self._generate_repair_guidance(code_info, vehicle),
            "cost_estimate": self._estimate_total_cost(code_info, vehicle),
            "recommendations": self._generate_recommendations(code_info, vehicle, symptoms),
            "assumptions": self._list_assumptions(vehicle, context),
            "next_steps": self._generate_next_steps(code_info, vehicle),
            "metadata": {
                "confidence": self._calculate_confidence(code_info, vehicle),
                "sources": ["OBD-II standard database", "Manufacturer service bulletins"],
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        }

        logger.info("diagnostic_analysis_complete", code=fault_code, confidence=analysis["metadata"]["confidence"])

        return analysis

    def _generate_intent_summary(
        self,
        fault_code: str,
        vehicle: Optional[Dict],
        symptoms: Optional[List[str]]
    ) -> str:
        """Generate human-readable summary of what user is asking"""
        parts = []

        if symptoms:
            symptom_str = ", ".join(symptoms)
            parts.append(f"experiencing {symptom_str}")

        parts.append(f"with fault code {fault_code}")

        if vehicle:
            vehicle_str = f"{vehicle.get('year', '')} {vehicle.get('make', '')} {vehicle.get('model', '')}".strip()
            if vehicle_str:
                parts.append(f"on {vehicle_str}")

        return f"User is troubleshooting " + " ".join(parts)

    def _analyze_code(
        self,
        code: str,
        code_info: Dict,
        vehicle: Optional[Dict]
    ) -> Dict[str, Any]:
        """Analyze the fault code with context"""
        return {
            "code": code,
            "description": code_info.get("description"),
            "system": code_info.get("system"),
            "severity": code_info.get("severity"),
            "explanation": code_info.get("explanation"),
            "vehicle_specific_notes": self._get_vehicle_specific_notes(code, vehicle)
        }

    def _rank_causes(
        self,
        code_info: Dict,
        vehicle: Optional[Dict],
        symptoms: Optional[List[str]],
        context: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Rank probable causes based on vehicle and symptom context
        Adjusts probabilities based on mileage, symptoms, etc.
        """
        causes = code_info.get("common_causes", [])
        ranked_causes = []

        for cause_data in causes:
            adjusted_prob = cause_data["probability"]
            adjustments = []

            # Adjust based on mileage
            if vehicle and vehicle.get("mileage"):
                mileage = vehicle["mileage"]
                typical_mileage = cause_data.get("typical_mileage", "")

                if "80,000+" in typical_mileage and mileage > 80000:
                    adjusted_prob *= 1.3
                    adjustments.append(f"High mileage ({mileage:,} miles) increases likelihood")
                elif mileage < 30000:
                    adjusted_prob *= 0.7
                    adjustments.append(f"Low mileage ({mileage:,} miles) decreases likelihood")

            # Adjust based on symptoms
            if symptoms:
                symptom_keywords = {
                    "catalyst": ["smell", "rotten egg", "sulfur"],
                    "o2 sensor": ["rough idle", "poor fuel economy"],
                    "spark plug": ["misfire", "rough", "shaking"],
                    "vacuum leak": ["hissing", "rough idle", "stalling"]
                }

                cause_lower = cause_data["cause"].lower()
                for key, keywords in symptom_keywords.items():
                    if key in cause_lower:
                        if any(kw in " ".join(symptoms).lower() for kw in keywords):
                            adjusted_prob *= 1.2
                            adjustments.append(f"Symptoms consistent with {key} issue")

            # Normalize probability
            adjusted_prob = min(adjusted_prob, 0.95)

            ranked_causes.append({
                "cause": cause_data["cause"],
                "probability": round(adjusted_prob, 2),
                "explanation": cause_data["explanation"],
                "cost_estimate": cause_data.get("cost_estimate", {}),
                "probability_adjustments": adjustments if adjustments else ["No adjustments - base probability"]
            })

        # Sort by probability
        ranked_causes.sort(key=lambda x: x["probability"], reverse=True)

        return ranked_causes

    def _customize_diagnostic_steps(
        self,
        code_info: Dict,
        vehicle: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """Customize diagnostic steps based on vehicle"""
        steps = code_info.get("diagnostic_steps", [])

        # Add vehicle-specific notes
        for step in steps:
            if vehicle:
                make = vehicle.get("make", "").lower()
                model = vehicle.get("model", "").lower()

                # Add make-specific tips
                if make == "honda" and "catalyst" in step.get("action", "").lower():
                    step["vehicle_note"] = "Honda catalysts typically last 100k+ miles with proper maintenance"
                elif make == "toyota" and "o2 sensor" in step.get("action", "").lower():
                    step["vehicle_note"] = "Toyota O2 sensors are known for longevity, check wiring first"

        return steps

    def _estimate_parts(
        self,
        code_info: Dict,
        vehicle: Optional[Dict]
    ) -> List[Dict[str, Any]]:
        """Estimate parts needed with costs"""
        parts = code_info.get("parts_needed", [])

        for part in parts:
            # Add currency if not present
            if "currency" not in part:
                part["currency"] = "SGD"

            # Add OEM vs aftermarket note
            if part.get("oem_recommended"):
                part["note"] = "OEM recommended for this repair"
            else:
                part["note"] = "Aftermarket acceptable, ensure quality brand"

        return parts

    def _generate_repair_guidance(
        self,
        code_info: Dict,
        vehicle: Optional[Dict]
    ) -> Dict[str, Any]:
        """Generate repair difficulty and feasibility assessment"""
        diy_info = code_info.get("diy_feasibility", {})

        return {
            "diy_diagnosis_difficulty": diy_info.get("diagnosis", "unknown"),
            "diy_repair_difficulty": diy_info.get("repair", "unknown"),
            "explanation": diy_info.get("explanation", "Consult professional for assessment"),
            "estimated_shop_time": self._estimate_shop_labor(code_info),
            "special_tools_required": self._list_special_tools(code_info)
        }

    def _estimate_shop_labor(self, code_info: Dict) -> str:
        """Estimate professional shop labor time"""
        steps = code_info.get("diagnostic_steps", [])
        total_minutes = sum(self._parse_time(step.get("estimated_time", "0")) for step in steps)

        # Add repair time estimate
        diy = code_info.get("diy_feasibility", {})
        if diy.get("repair") == "difficult":
            total_minutes += 120  # Add 2 hours for difficult repairs
        elif diy.get("repair") == "moderate":
            total_minutes += 60
        else:
            total_minutes += 30

        hours = total_minutes / 60
        return f"{hours:.1f} hours (diagnostic + repair)"

    def _parse_time(self, time_str: str) -> int:
        """Parse time string to minutes"""
        if "hour" in time_str:
            return int(time_str.split()[0]) * 60
        elif "minute" in time_str:
            return int(time_str.split()[0])
        return 0

    def _list_special_tools(self, code_info: Dict) -> List[str]:
        """List special tools needed from diagnostic steps"""
        tools = set()
        for step in code_info.get("diagnostic_steps", []):
            tools.update(step.get("tools_needed", []))
        return sorted(list(tools))

    def _estimate_total_cost(
        self,
        code_info: Dict,
        vehicle: Optional[Dict]
    ) -> Dict[str, Any]:
        """Estimate total repair cost range"""
        parts = code_info.get("parts_needed", [])
        causes = code_info.get("common_causes", [])

        # Get likely repair cost (highest probability cause)
        if causes:
            likely_cost = causes[0].get("cost_estimate", {})
            min_cost = likely_cost.get("min", 0)
            max_cost = likely_cost.get("max", 0)
        else:
            min_cost = sum(p.get("typical_cost", 0) for p in parts) * 0.8
            max_cost = sum(p.get("typical_cost", 0) for p in parts) * 1.5

        # Add labor (assume $80-120/hour in Singapore)
        labor_hours = float(self._estimate_shop_labor(code_info).split()[0])
        labor_min = labor_hours * 80
        labor_max = labor_hours * 120

        return {
            "parts_cost": {"min": int(min_cost * 0.7), "max": int(max_cost), "currency": "SGD"},
            "labor_cost": {"min": int(labor_min), "max": int(labor_max), "currency": "SGD"},
            "total_estimate": {
                "min": int(min_cost * 0.7 + labor_min),
                "max": int(max_cost + labor_max),
                "currency": "SGD"
            },
            "explanation": "Estimate includes parts and labor. Actual cost depends on root cause and shop rates."
        }

    def _generate_recommendations(
        self,
        code_info: Dict,
        vehicle: Optional[Dict],
        symptoms: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Generate actionable recommendations"""
        safety = code_info.get("immediate_safety", {})

        return {
            "immediate_action": safety.get("explanation", "Consult professional mechanic"),
            "urgency": self._assess_urgency(code_info, symptoms),
            "diy_feasible": code_info.get("diy_feasibility", {}).get("repair") in ["easy", "moderate"],
            "professional_recommended": code_info.get("diy_feasibility", {}).get("repair") == "difficult",
            "prevention_tips": code_info.get("prevention", "Regular maintenance per manufacturer schedule")
        }

    def _assess_urgency(self, code_info: Dict, symptoms: Optional[List[str]]) -> str:
        """Assess repair urgency"""
        severity = code_info.get("severity", "moderate")
        safety = code_info.get("immediate_safety", {})
        driveable = safety.get("driveable", True)

        if not driveable or severity == "high":
            return "immediate"
        elif severity == "moderate":
            return "within_week"
        else:
            return "within_month"

    def _list_assumptions(
        self,
        vehicle: Optional[Dict],
        context: Optional[Dict]
    ) -> List[str]:
        """List assumptions made in analysis"""
        assumptions = []

        if not vehicle or not vehicle.get("mileage"):
            assumptions.append("Assumed vehicle has typical mileage for year (15k miles/year)")

        if not context or not context.get("maintenance_history"):
            assumptions.append("Assumed regular maintenance has been performed")

        assumptions.append("No accident damage or modifications to relevant systems")
        assumptions.append("Diagnosis based on OBD-II standard, vehicle-specific factors may vary")
        assumptions.append("Cost estimates based on Singapore market rates")

        return assumptions

    def _generate_next_steps(
        self,
        code_info: Dict,
        vehicle: Optional[Dict]
    ) -> List[str]:
        """Generate prioritized next steps"""
        steps = []
        diy = code_info.get("diy_feasibility", {})

        # Step 1: Immediate diagnostic
        diagnostic_steps = code_info.get("diagnostic_steps", [])
        if diagnostic_steps:
            first_step = diagnostic_steps[0]
            steps.append(f"Perform: {first_step.get('action', 'Initial diagnostic')}")

        # Step 2: Cost consideration
        cost = self._estimate_total_cost(code_info, vehicle)
        total = cost.get("total_estimate", {})
        steps.append(f"Budget ${total.get('min', 0)}-{total.get('max', 0)} SGD for repair")

        # Step 3: DIY or professional
        if diy.get("diagnosis") in ["easy", "moderate"]:
            steps.append("DIY diagnosis possible with proper tools")
        else:
            steps.append("Recommend professional diagnostic ($80-150)")

        if diy.get("repair") == "easy":
            steps.append("DIY repair feasible for mechanically inclined")
        elif diy.get("repair") == "difficult":
            steps.append("Professional repair strongly recommended")

        # Step 4: Parts sourcing
        steps.append("Source parts from reputable suppliers (OEM or quality aftermarket)")

        return steps[:5]  # Limit to 5 steps

    def _calculate_confidence(
        self,
        code_info: Dict,
        vehicle: Optional[Dict]
    ) -> float:
        """Calculate confidence in analysis"""
        confidence = 0.8  # Base confidence

        # Adjust based on information available
        if vehicle:
            if vehicle.get("year"):
                confidence += 0.05
            if vehicle.get("make"):
                confidence += 0.05
            if vehicle.get("mileage"):
                confidence += 0.05

        # Well-documented codes get higher confidence
        if len(code_info.get("common_causes", [])) > 3:
            confidence += 0.05

        return min(confidence, 0.95)

    def _get_vehicle_specific_notes(
        self,
        code: str,
        vehicle: Optional[Dict]
    ) -> Optional[str]:
        """Get vehicle-specific notes for common issues"""
        if not vehicle:
            return None

        make = vehicle.get("make", "").lower()
        model = vehicle.get("model", "").lower()

        # Common make-specific issues
        notes = {
            ("honda", "p0420"): "Honda Civics 2012-2015 have known catalyst issues around 80k miles",
            ("toyota", "p0420"): "Toyota vehicles typically have long-lasting catalysts, check O2 sensors first",
            ("nissan", "p0300"): "Nissan ignition coils are known weak points, consider replacing all at once"
        }

        key = (make, code.lower())
        return notes.get(key)

    def _handle_unknown_code(
        self,
        fault_code: str,
        vehicle: Optional[Dict],
        symptoms: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Handle unknown fault codes gracefully"""
        return {
            "success": False,
            "fault_code": fault_code,
            "message": f"Fault code {fault_code} not found in database",
            "explanation": "This code may be manufacturer-specific or less common. Recommend professional diagnostic.",
            "general_guidance": {
                "code_format": self._identify_code_format(fault_code),
                "system_area": self._guess_system_from_code(fault_code),
                "recommendations": [
                    "Consult vehicle-specific service manual",
                    "Use professional-grade diagnostic scanner",
                    "Contact dealership or specialist mechanic",
                    f"Search manufacturer bulletins for {fault_code}"
                ]
            },
            "next_steps": [
                "Verify code with professional scanner",
                "Check manufacturer-specific code database",
                "Consult dealership service department"
            ]
        }

    def _identify_code_format(self, code: str) -> str:
        """Identify DTC code format"""
        if code.startswith("P0"):
            return "Generic Powertrain"
        elif code.startswith("P1"):
            return "Manufacturer-Specific Powertrain"
        elif code.startswith("B"):
            return "Body"
        elif code.startswith("C"):
            return "Chassis"
        elif code.startswith("U"):
            return "Network/Communication"
        else:
            return "Unknown format"

    def _guess_system_from_code(self, code: str) -> str:
        """Guess affected system from code structure"""
        if code.startswith("P"):
            if code[1] == "0":
                return "Engine/Powertrain (generic)"
            elif code[1] == "1":
                return "Engine/Powertrain (manufacturer-specific)"
            elif code[1] == "2":
                return "Fuel and Air Metering"
            elif code[1] == "3":
                return "Ignition System"
        elif code.startswith("C"):
            return "Chassis (ABS, suspension, steering)"
        elif code.startswith("B"):
            return "Body (airbags, climate control)"

        return "Unknown system"


# Singleton instance
_diagnostics_service = None


def get_diagnostics_service() -> DiagnosticsService:
    """Get or create diagnostics service instance"""
    global _diagnostics_service
    if _diagnostics_service is None:
        _diagnostics_service = DiagnosticsService()
    return _diagnostics_service
