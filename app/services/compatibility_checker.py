"""
Compatibility Checker for Parts

Checks if a part is compatible with a specific vehicle using moderate rules
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.db.models import PartsCatalog, PartCompatibilityEnhanced
from app.core.logging import get_logger

logger = get_logger(__name__)


class CompatibilityLevel:
    """Compatibility confidence levels"""
    GUARANTEED = 1.0      # Perfect match, guaranteed fit
    HIGH = 0.9           # Very likely to fit
    MODERATE = 0.7       # Should fit with verification
    LOW = 0.5            # Might fit, needs expert confirmation
    UNIVERSAL = 1.0      # Universal part, fits all


class CompatibilityChecker:
    """Check part compatibility with vehicles"""

    def __init__(self):
        """Initialize compatibility checker"""
        logger.info("compatibility_checker_init")

    def check_compatibility(
        self,
        db: Session,
        part_id: int,
        vehicle: Dict[str, Any],
        strict: bool = False
    ) -> Dict[str, Any]:
        """
        Check if a part is compatible with a vehicle

        Args:
            db: Database session
            part_id: Part ID to check
            vehicle: Vehicle dict with make, model, year, etc.
            strict: If True, only return guaranteed fits

        Returns:
            Dictionary with compatibility info
        """
        make = vehicle.get("make")
        model = vehicle.get("model")
        year = vehicle.get("year")
        trim = vehicle.get("trim")
        engine = vehicle.get("engine")

        logger.info("check_compatibility",
                   part_id=part_id,
                   vehicle=f"{year} {make} {model}")

        # Check for universal parts first
        universal = db.query(PartCompatibilityEnhanced).filter(
            and_(
                PartCompatibilityEnhanced.part_id == part_id,
                PartCompatibilityEnhanced.is_universal == True
            )
        ).first()

        if universal:
            return {
                "compatible": True,
                "confidence": CompatibilityLevel.UNIVERSAL,
                "level": "universal",
                "message": "Universal part - fits all vehicles",
                "warnings": [],
                "requirements": []
            }

        # Check exact match
        exact_match = db.query(PartCompatibilityEnhanced).filter(
            and_(
                PartCompatibilityEnhanced.part_id == part_id,
                PartCompatibilityEnhanced.make == make,
                PartCompatibilityEnhanced.model == model,
                PartCompatibilityEnhanced.year_start <= year,
                PartCompatibilityEnhanced.year_end >= year
            )
        ).all()

        if exact_match:
            # Find best match considering trim and engine
            best_match = self._find_best_match(exact_match, trim, engine)

            confidence = float(best_match.confidence) if best_match.confidence else CompatibilityLevel.GUARANTEED
            warnings = []
            requirements = []

            # Add warnings based on specificity
            if best_match.trim and trim and best_match.trim != trim:
                warnings.append(f"Specified for {best_match.trim} trim, you have {trim}")
                confidence *= 0.9

            if best_match.engine and engine and best_match.engine != engine:
                warnings.append(f"Specified for {best_match.engine} engine")
                confidence *= 0.9

            if best_match.position:
                requirements.append(f"Position: {best_match.position}")

            return {
                "compatible": True,
                "confidence": confidence,
                "level": self._get_confidence_level(confidence),
                "message": f"Compatible with {year} {make} {model}",
                "warnings": warnings,
                "requirements": requirements,
                "notes": best_match.notes
            }

        # Check make and year range (moderate compatibility)
        if not strict:
            make_match = db.query(PartCompatibilityEnhanced).filter(
                and_(
                    PartCompatibilityEnhanced.part_id == part_id,
                    PartCompatibilityEnhanced.make == make,
                    PartCompatibilityEnhanced.year_start <= year,
                    PartCompatibilityEnhanced.year_end >= year
                )
            ).all()

            if make_match:
                compatible_models = [m.model for m in make_match]
                return {
                    "compatible": False,
                    "confidence": CompatibilityLevel.LOW,
                    "level": "possible",
                    "message": f"May fit {make} vehicles from {year}",
                    "warnings": [
                        f"Not specifically listed for {model}",
                        f"Compatible with: {', '.join(compatible_models)}"
                    ],
                    "requirements": ["Verify fitment before purchase"]
                }

        # No compatibility found
        return {
            "compatible": False,
            "confidence": 0.0,
            "level": "incompatible",
            "message": f"No compatibility data for {year} {make} {model}",
            "warnings": ["Part may not fit this vehicle"],
            "requirements": ["Contact seller for compatibility verification"]
        }

    def batch_check_compatibility(
        self,
        db: Session,
        part_ids: List[int],
        vehicle: Dict[str, Any]
    ) -> Dict[int, Dict[str, Any]]:
        """
        Check compatibility for multiple parts at once

        Args:
            db: Database session
            part_ids: List of part IDs
            vehicle: Vehicle information

        Returns:
            Dictionary mapping part_id to compatibility info
        """
        results = {}

        for part_id in part_ids:
            results[part_id] = self.check_compatibility(db, part_id, vehicle)

        logger.info("batch_compatibility_check",
                   parts_checked=len(part_ids),
                   compatible=sum(1 for r in results.values() if r["compatible"]))

        return results

    def _find_best_match(
        self,
        matches: List[PartCompatibilityEnhanced],
        trim: Optional[str],
        engine: Optional[str]
    ) -> PartCompatibilityEnhanced:
        """Find the best compatibility match from multiple options"""
        if len(matches) == 1:
            return matches[0]

        # Score each match
        scored_matches = []
        for match in matches:
            score = 0

            # Prefer matches with trim data
            if match.trim:
                if trim and match.trim == trim:
                    score += 10
                elif trim:
                    score -= 5

            # Prefer matches with engine data
            if match.engine:
                if engine and match.engine == engine:
                    score += 10
                elif engine:
                    score -= 5

            # Prefer higher confidence
            if match.confidence:
                score += float(match.confidence) * 5

            scored_matches.append((match, score))

        # Return highest scoring match
        scored_matches.sort(key=lambda x: x[1], reverse=True)
        return scored_matches[0][0]

    def _get_confidence_level(self, confidence: float) -> str:
        """Convert confidence score to text level"""
        if confidence >= 0.95:
            return "guaranteed"
        elif confidence >= 0.85:
            return "high"
        elif confidence >= 0.70:
            return "moderate"
        elif confidence >= 0.50:
            return "low"
        else:
            return "incompatible"

    def get_compatible_vehicles(
        self,
        db: Session,
        part_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get list of vehicles compatible with a part

        Args:
            db: Database session
            part_id: Part ID
            limit: Maximum vehicles to return

        Returns:
            List of compatible vehicle dictionaries
        """
        compat_records = db.query(PartCompatibilityEnhanced).filter(
            PartCompatibilityEnhanced.part_id == part_id
        ).limit(limit).all()

        vehicles = []
        for record in compat_records:
            if record.is_universal:
                vehicles.append({
                    "make": "All",
                    "model": "Universal",
                    "year_range": "All years",
                    "notes": "Universal part"
                })
                break
            else:
                vehicles.append({
                    "make": record.make,
                    "model": record.model,
                    "year_range": f"{record.year_start}-{record.year_end}",
                    "trim": record.trim,
                    "engine": record.engine,
                    "position": record.position,
                    "notes": record.notes
                })

        logger.info("get_compatible_vehicles",
                   part_id=part_id,
                   vehicles_found=len(vehicles))

        return vehicles


# Singleton instance
_compatibility_checker = None


def get_compatibility_checker() -> CompatibilityChecker:
    """Get or create compatibility checker instance"""
    global _compatibility_checker
    if _compatibility_checker is None:
        _compatibility_checker = CompatibilityChecker()
    return _compatibility_checker
