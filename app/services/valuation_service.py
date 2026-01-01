"""
Intelligent Vehicle Valuation Service
Provides market value analysis with reasoning and explanations
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from app.core.logging import get_logger

logger = get_logger(__name__)


# Singapore vehicle depreciation reference data
# Based on COE (Certificate of Entitlement) depreciation + vehicle depreciation
SINGAPORE_VEHICLE_DATA = {
    "depreciation_rates": {
        # Year 0-1: 15-20%, Year 1-3: 12-15%, Year 3-5: 10-12%, Year 5+: 8-10%
        "year_1": 0.18,
        "year_2": 0.14,
        "year_3": 0.13,
        "year_4": 0.11,
        "year_5": 0.10,
        "year_6_plus": 0.08
    },
    "base_values": {
        # Approximate new car prices in Singapore (SGD)
        "toyota": {
            "corolla": 120000,
            "camry": 180000,
            "rav4": 200000,
            "vios": 95000
        },
        "honda": {
            "civic": 130000,
            "accord": 190000,
            "cr-v": 210000,
            "jazz": 100000
        },
        "mazda": {
            "3": 120000,
            "6": 175000,
            "cx-5": 190000
        },
        "bmw": {
            "3 series": 280000,
            "5 series": 380000,
            "x3": 320000
        },
        "mercedes-benz": {
            "c-class": 290000,
            "e-class": 400000,
            "glc": 350000
        },
        "hyundai": {
            "elantra": 110000,
            "sonata": 160000,
            "tucson": 170000
        },
        "kia": {
            "cerato": 105000,
            "optima": 155000,
            "sportage": 165000
        }
    },
    "market_factors": {
        # Popularity factors (multiplier)
        "high_demand": ["toyota", "honda", "mazda"],
        "moderate_demand": ["hyundai", "kia", "nissan"],
        "luxury": ["bmw", "mercedes-benz", "audi", "lexus"],
        "depreciation_resistant": ["toyota corolla", "honda civic", "mazda 3"]
    }
}


class ValuationService:
    """
    Intelligent vehicle valuation service for Singapore market

    Provides:
    - Market value estimates with reasoning
    - Depreciation factor analysis
    - Comparable listings
    - Market trend analysis
    - Selling tips
    """

    def estimate_value(
        self,
        vehicle: Dict[str, Any],
        mileage: int,
        condition: str,
        location: str = "Singapore",
        modifications: Optional[List[str]] = None,
        accident_history: Optional[bool] = None,
        service_history: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estimate vehicle market value with comprehensive analysis

        Args:
            vehicle: Vehicle information {make, model, year}
            mileage: Current mileage in km
            condition: excellent, good, fair, poor
            location: Location (default Singapore)
            modifications: List of modifications
            accident_history: Whether vehicle has accident history
            service_history: full, partial, or unknown

        Returns:
            Comprehensive valuation with explanations and reasoning
        """
        logger.info("valuation_start", vehicle=vehicle, mileage=mileage, condition=condition)

        make = vehicle.get("make", "").lower()
        model = vehicle.get("model", "").lower()
        year = vehicle.get("year")

        if not year:
            return self._handle_insufficient_data(vehicle, "Vehicle year is required")

        current_year = datetime.now().year
        vehicle_age = current_year - year

        # Calculate base value with depreciation
        base_value = self._calculate_base_value(make, model, year, vehicle_age)

        # Apply adjustments
        depreciation_factors = []
        adjusted_value = base_value

        # Mileage adjustment
        mileage_factor = self._calculate_mileage_adjustment(mileage, vehicle_age)
        depreciation_factors.append(mileage_factor)
        adjusted_value *= (1 + mileage_factor["impact"] / 100)

        # Condition adjustment
        condition_factor = self._calculate_condition_adjustment(condition)
        depreciation_factors.append(condition_factor)
        adjusted_value *= (1 + condition_factor["impact"] / 100)

        # Accident history adjustment
        if accident_history:
            accident_factor = {
                "factor": "Accident History",
                "impact": -15.0,
                "explanation": "Previous accident typically reduces value by 10-20% due to structural concerns and insurance history"
            }
            depreciation_factors.append(accident_factor)
            adjusted_value *= 0.85

        # Service history adjustment
        service_factor = self._calculate_service_history_adjustment(service_history)
        if service_factor:
            depreciation_factors.append(service_factor)
            adjusted_value *= (1 + service_factor["impact"] / 100)

        # Modifications impact
        if modifications:
            mod_factor = self._calculate_modification_impact(modifications)
            depreciation_factors.append(mod_factor)
            adjusted_value *= (1 + mod_factor["impact"] / 100)

        # Market demand adjustment
        market_factor = self._calculate_market_demand(make, model)
        depreciation_factors.append(market_factor)
        adjusted_value *= (1 + market_factor["impact"] / 100)

        # Calculate value ranges
        private_party_value = adjusted_value
        retail_value = private_party_value * 1.15  # Dealers add 10-20% markup
        trade_in_value = private_party_value * 0.75  # Dealers offer 70-80% of market value

        # Generate comparable listings
        comparables = self._generate_comparable_listings(make, model, year, mileage, condition)

        # Market analysis
        market_analysis = self._analyze_market(make, model, vehicle_age)

        # Generate assumptions
        assumptions = self._list_assumptions(vehicle, accident_history, service_history, modifications)

        # Generate selling tips
        selling_tips = self._generate_selling_tips(condition, mileage, vehicle_age, make, model)

        # Generate intent summary
        intent_understood = f"User wants to know the market value of their {year} {make.title()} {model.title()} with {mileage:,} km"

        # Calculate confidence
        confidence = self._calculate_confidence(vehicle, accident_history, service_history)

        # Generate reasoning
        reasoning = self._generate_reasoning(
            make, model, year, base_value, adjusted_value,
            depreciation_factors, market_analysis
        )

        return {
            "success": True,
            "intent_understood": intent_understood,
            "valuation_estimate": {
                "retail_value": {
                    "min": int(retail_value * 0.9),
                    "max": int(retail_value * 1.1),
                    "currency": "SGD"
                },
                "private_party": {
                    "min": int(private_party_value * 0.92),
                    "max": int(private_party_value * 1.08),
                    "currency": "SGD"
                },
                "trade_in_value": {
                    "min": int(trade_in_value * 0.9),
                    "max": int(trade_in_value * 1.1),
                    "currency": "SGD"
                },
                "explanation": f"Based on {vehicle_age}-year depreciation, {condition} condition, and {mileage:,} km mileage in Singapore market",
                "confidence": confidence
            },
            "depreciation_factors": depreciation_factors,
            "comparable_listings": comparables,
            "market_analysis": market_analysis,
            "selling_tips": selling_tips,
            "assumptions": assumptions,
            "reasoning": reasoning,
            "metadata": {
                "base_value": int(base_value),
                "adjusted_value": int(adjusted_value),
                "total_depreciation": round((1 - adjusted_value / base_value) * 100, 1),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "market": "Singapore"
            }
        }

    def _calculate_base_value(self, make: str, model: str, year: int, age: int) -> float:
        """Calculate base vehicle value with depreciation"""
        # Get initial value
        base_data = SINGAPORE_VEHICLE_DATA["base_values"]
        initial_value = 150000  # Default average car price in Singapore

        if make in base_data:
            if model in base_data[make]:
                initial_value = base_data[make][model]
            else:
                # Use average for the make
                initial_value = sum(base_data[make].values()) / len(base_data[make])

        # Apply depreciation by year
        current_value = initial_value
        rates = SINGAPORE_VEHICLE_DATA["depreciation_rates"]

        for year_num in range(1, age + 1):
            if year_num == 1:
                rate = rates["year_1"]
            elif year_num == 2:
                rate = rates["year_2"]
            elif year_num == 3:
                rate = rates["year_3"]
            elif year_num == 4:
                rate = rates["year_4"]
            elif year_num == 5:
                rate = rates["year_5"]
            else:
                rate = rates["year_6_plus"]

            current_value *= (1 - rate)

        return current_value

    def _calculate_mileage_adjustment(self, mileage: int, age: int) -> Dict[str, Any]:
        """Calculate mileage impact on value"""
        # Average mileage in Singapore: ~15,000 km/year
        expected_mileage = age * 15000
        mileage_diff = mileage - expected_mileage

        if mileage_diff < -10000:
            impact = 5.0  # Low mileage adds value
            explanation = f"Below average mileage ({mileage:,} km vs expected {expected_mileage:,} km) indicates less wear"
        elif mileage_diff < 10000:
            impact = 0.0
            explanation = f"Mileage ({mileage:,} km) is typical for vehicle age"
        elif mileage_diff < 30000:
            impact = -5.0
            explanation = f"Above average mileage ({mileage:,} km vs expected {expected_mileage:,} km) indicates more wear"
        else:
            impact = -12.0
            explanation = f"High mileage ({mileage:,} km vs expected {expected_mileage:,} km) significantly impacts value"

        return {
            "factor": "Mileage",
            "impact": impact,
            "explanation": explanation
        }

    def _calculate_condition_adjustment(self, condition: str) -> Dict[str, Any]:
        """Calculate condition impact on value"""
        condition_impacts = {
            "excellent": {
                "impact": 10.0,
                "explanation": "Excellent condition: minimal wear, no visible damage, well-maintained"
            },
            "good": {
                "impact": 0.0,
                "explanation": "Good condition: normal wear for age, minor cosmetic issues acceptable"
            },
            "fair": {
                "impact": -15.0,
                "explanation": "Fair condition: visible wear, some mechanical or cosmetic issues need attention"
            },
            "poor": {
                "impact": -30.0,
                "explanation": "Poor condition: significant mechanical or cosmetic issues, major repairs needed"
            }
        }

        condition_data = condition_impacts.get(condition.lower(), condition_impacts["good"])

        return {
            "factor": "Condition",
            "impact": condition_data["impact"],
            "explanation": condition_data["explanation"]
        }

    def _calculate_service_history_adjustment(self, service_history: Optional[str]) -> Optional[Dict[str, Any]]:
        """Calculate service history impact"""
        if not service_history or service_history == "unknown":
            return {
                "factor": "Service History",
                "impact": -5.0,
                "explanation": "Unknown service history reduces buyer confidence and value"
            }
        elif service_history == "full":
            return {
                "factor": "Service History",
                "impact": 5.0,
                "explanation": "Complete service records increase buyer confidence and value"
            }
        elif service_history == "partial":
            return {
                "factor": "Service History",
                "impact": 0.0,
                "explanation": "Partial service history - neutral impact on value"
            }
        return None

    def _calculate_modification_impact(self, modifications: List[str]) -> Dict[str, Any]:
        """Calculate modifications impact"""
        # Most modifications reduce value in Singapore due to LTA regulations
        mod_count = len(modifications)

        if mod_count == 0:
            return {
                "factor": "Modifications",
                "impact": 0.0,
                "explanation": "No modifications - original condition preferred by buyers"
            }
        elif mod_count <= 2:
            return {
                "factor": "Modifications",
                "impact": -3.0,
                "explanation": f"Minor modifications ({', '.join(modifications)}) may limit buyer pool"
            }
        else:
            return {
                "factor": "Modifications",
                "impact": -8.0,
                "explanation": f"Multiple modifications ({mod_count} items) typically reduce value and buyer interest"
            }

    def _calculate_market_demand(self, make: str, model: str) -> Dict[str, Any]:
        """Calculate market demand impact"""
        factors = SINGAPORE_VEHICLE_DATA["market_factors"]
        vehicle_full = f"{make} {model}"

        if make in factors["luxury"]:
            return {
                "factor": "Market Segment",
                "impact": -5.0,
                "explanation": f"Luxury vehicles ({make.title()}) depreciate faster due to higher maintenance costs"
            }
        elif vehicle_full in factors["depreciation_resistant"]:
            return {
                "factor": "Market Demand",
                "impact": 8.0,
                "explanation": f"{make.title()} {model.title()} holds value well due to strong reliability reputation"
            }
        elif make in factors["high_demand"]:
            return {
                "factor": "Market Demand",
                "impact": 5.0,
                "explanation": f"{make.title()} brand has strong demand in Singapore market"
            }
        elif make in factors["moderate_demand"]:
            return {
                "factor": "Market Demand",
                "impact": 0.0,
                "explanation": f"{make.title()} has moderate demand in Singapore market"
            }
        else:
            return {
                "factor": "Market Demand",
                "impact": -3.0,
                "explanation": "Lower market demand for this make/model combination"
            }

    def _generate_comparable_listings(
        self,
        make: str,
        model: str,
        year: int,
        mileage: int,
        condition: str
    ) -> List[Dict[str, Any]]:
        """Generate comparable vehicle listings"""
        # In production, this would query real listing APIs
        # For now, generate representative comparables

        base_price_variation = 0.15  # ±15% variation
        comparables = []

        # Generate 5 comparable listings
        sources = ["Carousell", "sgCarMart", "OneShift", "Carro", "Motor.sg"]

        for i, source in enumerate(sources):
            # Simulate slight variation in year, mileage, price
            comp_year = year + (i - 2 if i > 2 else 0)
            comp_mileage = int(mileage * (0.85 + i * 0.1))
            comp_price_factor = 0.9 + i * 0.05

            # Base comparable price (would come from actual listings)
            base_comparable = self._calculate_base_value(make, model, comp_year, datetime.now().year - comp_year)
            comp_price = base_comparable * comp_price_factor

            similarity = 1.0 - abs(i - 2) * 0.1  # Middle listing is most similar

            comparables.append({
                "source": source,
                "price": int(comp_price),
                "currency": "SGD",
                "mileage": comp_mileage,
                "year": comp_year,
                "condition": condition,
                "location": "Singapore",
                "listing_url": f"https://{source.lower()}.sg/listing-example",
                "date_listed": (datetime.now() - timedelta(days=i * 5)).strftime("%Y-%m-%d"),
                "similarity_score": round(similarity, 2),
                "notes": f"Similar {make.title()} {model.title()}, {abs(comp_year - year)} year difference"
            })

        return comparables

    def _analyze_market(self, make: str, model: str, age: int) -> Dict[str, Any]:
        """Analyze current market conditions"""
        factors = SINGAPORE_VEHICLE_DATA["market_factors"]

        # Determine demand level
        if make in factors["high_demand"]:
            demand = "high"
            supply = "adequate"
            trend = "stable"
            days_to_sell = "14-28 days"
            explanation = f"{make.title()} vehicles sell quickly in Singapore due to strong reliability reputation"
        elif make in factors["luxury"]:
            demand = "moderate"
            supply = "limited"
            trend = "stable"
            days_to_sell = "30-60 days"
            explanation = f"Luxury segment has selective buyers. {make.title()} typically sells within 1-2 months"
        else:
            demand = "moderate"
            supply = "adequate"
            trend = "stable"
            days_to_sell = "21-45 days"
            explanation = f"Average market conditions for {make.title()} {model.title()}"

        # Older vehicles take longer to sell
        if age > 8:
            days_to_sell = "45-90 days"
            explanation += ". Older vehicles may take longer to find the right buyer"

        return {
            "demand_level": demand,
            "supply_level": supply,
            "market_trend": trend,
            "explanation": explanation,
            "typical_days_to_sell": days_to_sell
        }

    def _generate_selling_tips(
        self,
        condition: str,
        mileage: int,
        age: int,
        make: str,
        model: str
    ) -> List[str]:
        """Generate tips to maximize sale value"""
        tips = []

        # Condition-based tips
        if condition in ["fair", "poor"]:
            tips.append("Consider minor cosmetic repairs - fresh paint and interior cleaning can add 5-10% value")
            tips.append("Fix any mechanical issues before listing - buyers will negotiate harder on visible problems")

        # Documentation tips
        tips.append("Gather all service records and maintenance receipts - buyers pay more for documented history")
        tips.append("Prepare vehicle inspection report from reputable workshop to build buyer confidence")

        # Timing tips
        if make in SINGAPORE_VEHICLE_DATA["market_factors"]["high_demand"]:
            tips.append(f"{make.title()} vehicles sell well year-round - list at fair market price")
        else:
            tips.append("Consider listing during Chinese New Year period when car buying activity peaks")

        # Presentation tips
        tips.append("Professional photos with clean car in good lighting increase interest by 30-40%")

        # Pricing tips
        tips.append("Price slightly above your target to allow negotiation room (buyers expect 5-8% discount)")

        return tips[:5]  # Limit to 5 most relevant tips

    def _list_assumptions(
        self,
        vehicle: Dict,
        accident_history: Optional[bool],
        service_history: Optional[str],
        modifications: Optional[List[str]]
    ) -> List[str]:
        """List assumptions made in valuation"""
        assumptions = []

        assumptions.append("Valuation based on Singapore COE car market rates")
        assumptions.append("Assumed vehicle has valid COE with reasonable remaining period")

        if not accident_history:
            assumptions.append("Assumed no accident history (reduces value 10-20% if present)")

        if not service_history or service_history == "unknown":
            assumptions.append("Applied -5% adjustment for unknown service history")

        if not modifications:
            assumptions.append("Assumed vehicle is in stock/original condition")

        assumptions.append("Market conditions based on current Singapore automotive trends")
        assumptions.append("Prices exclude COE renewal costs")

        return assumptions

    def _calculate_confidence(
        self,
        vehicle: Dict,
        accident_history: Optional[bool],
        service_history: Optional[str]
    ) -> float:
        """Calculate confidence in valuation"""
        confidence = 0.75  # Base confidence

        # More complete information increases confidence
        if vehicle.get("make") and vehicle.get("model"):
            confidence += 0.05

        if vehicle.get("year"):
            confidence += 0.05

        if accident_history is not None:
            confidence += 0.05

        if service_history and service_history != "unknown":
            confidence += 0.05

        # Known makes get higher confidence
        if vehicle.get("make", "").lower() in SINGAPORE_VEHICLE_DATA["base_values"]:
            confidence += 0.05

        return min(confidence, 0.95)

    def _generate_reasoning(
        self,
        make: str,
        model: str,
        year: int,
        base_value: float,
        adjusted_value: float,
        factors: List[Dict],
        market_analysis: Dict
    ) -> str:
        """Generate overall reasoning for valuation"""
        total_impact = sum(f["impact"] for f in factors)

        reasoning = (
            f"The {year} {make.title()} {model.title()} has a base market value of "
            f"${int(base_value):,} SGD based on depreciation from original price. "
        )

        # Major factors
        major_factors = [f for f in factors if abs(f["impact"]) >= 5]
        if major_factors:
            factor_desc = ", ".join([f"{f['factor']} ({f['impact']:+.0f}%)" for f in major_factors[:3]])
            reasoning += f"Key value factors include: {factor_desc}. "

        reasoning += (
            f"After adjustments ({total_impact:+.0f}% total), "
            f"estimated market value is ${int(adjusted_value):,} SGD. "
        )

        reasoning += f"Market analysis shows {market_analysis['demand_level']} demand with {market_analysis['market_trend']} trend."

        return reasoning

    def _handle_insufficient_data(self, vehicle: Dict, reason: str) -> Dict[str, Any]:
        """Handle cases with insufficient data"""
        return {
            "success": False,
            "message": "Insufficient data for valuation",
            "reason": reason,
            "required_fields": ["make", "model", "year", "mileage"],
            "provided": vehicle
        }


# Singleton instance
_valuation_service = None


def get_valuation_service() -> ValuationService:
    """Get or create valuation service instance"""
    global _valuation_service
    if _valuation_service is None:
        _valuation_service = ValuationService()
    return _valuation_service
