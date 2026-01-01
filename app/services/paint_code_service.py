"""
Intelligent Paint Code Lookup Service
Provides paint code identification with actionable guidance
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from app.core.logging import get_logger

logger = get_logger(__name__)


# Paint code location database by manufacturer
PAINT_CODE_LOCATIONS = {
    "toyota": {
        "locations": [
            {
                "location": "Driver's door jamb",
                "description": "Look for a white or silver sticker on the driver's door jamb. Paint code is listed after 'C/TR:' or 'COLOR:'"
            },
            {
                "location": "Under the hood",
                "description": "Some models have the paint code on a sticker near the radiator support"
            }
        ],
        "code_format": "3-digit code (e.g., 040, 1G3, 8S6)",
        "common_colors": {
            "040": {"name": "Super White", "years": "2000-present"},
            "1G3": {"name": "Magnetic Gray Metallic", "years": "2010-present"},
            "8S6": {"name": "Celestial Silver Metallic", "years": "2015-present"},
            "070": {"name": "Blizzard Pearl", "years": "2010-present"},
            "202": {"name": "Black", "years": "2000-present"}
        }
    },
    "honda": {
        "locations": [
            {
                "location": "Driver's door jamb",
                "description": "Paint code is on the information label. Look for the 3-character code after 'COLOR' or 'C'"
            },
            {
                "location": "Inside glove compartment",
                "description": "Some older models have the code sticker inside the glove box"
            }
        ],
        "code_format": "3-character code (e.g., NH-731P, B-92P)",
        "common_colors": {
            "NH-731P": {"name": "Crystal Black Pearl", "years": "2006-present"},
            "NH-797M": {"name": "Modern Steel Metallic", "years": "2016-present"},
            "R-81": {"name": "Milano Red", "years": "2012-present"},
            "NH-830M": {"name": "Lunar Silver Metallic", "years": "2016-present"}
        }
    },
    "mazda": {
        "locations": [
            {
                "location": "Driver's door jamb",
                "description": "Look for paint code on the certification label. It's usually a 2-3 character code"
            },
            {
                "location": "Engine bay firewall",
                "description": "Some models have the code stamped on the firewall"
            }
        ],
        "code_format": "2-3 character code (e.g., 46G, 41V, 25D)",
        "common_colors": {
            "46G": {"name": "Soul Red Crystal Metallic", "years": "2017-present"},
            "41V": {"name": "Machine Gray Metallic", "years": "2016-present"},
            "25D": {"name": "Snowflake White Pearl Mica", "years": "2014-present"}
        }
    },
    "bmw": {
        "locations": [
            {
                "location": "Strut tower",
                "description": "Under the hood on the passenger side strut tower. Look for paint code after 'Lack:' or color code section"
            },
            {
                "location": "Driver's door jamb",
                "description": "Some models have a sticker on the driver's door jamb with the paint code"
            }
        ],
        "code_format": "3-digit code (e.g., A96, C10, 475)",
        "common_colors": {
            "300": {"name": "Alpine White", "years": "2000-present"},
            "668": {"name": "Black Sapphire Metallic", "years": "2010-present"},
            "A96": {"name": "Mineral White Metallic", "years": "2015-present"}
        }
    },
    "mercedes-benz": {
        "locations": [
            {
                "location": "Driver's door jamb",
                "description": "Paint code is on the certification sticker. Look for code after 'Paint No.' or color code field"
            },
            {
                "location": "Under the hood",
                "description": "Some models have an additional paint code plate on the radiator support"
            }
        ],
        "code_format": "3-4 digit code (e.g., 149, 9040, 197)",
        "common_colors": {
            "149": {"name": "Brilliant Silver Metallic", "years": "2000-present"},
            "9040": {"name": "Obsidian Black Metallic", "years": "2015-present"},
            "197": {"name": "Obsidian Black", "years": "2000-2014"}
        }
    },
    "hyundai": {
        "locations": [
            {
                "location": "Driver's door jamb",
                "description": "Paint code is on the certification label, usually a 2-3 character code after 'COLOR' or 'PAINT'"
            }
        ],
        "code_format": "2-3 character code (e.g., UD, SWP, TB)",
        "common_colors": {
            "UD": {"name": "Phantom Black", "years": "2015-present"},
            "SWP": {"name": "Polar White", "years": "2010-present"},
            "TB": {"name": "Machine Gray", "years": "2018-present"}
        }
    },
    "kia": {
        "locations": [
            {
                "location": "Driver's door jamb",
                "description": "Look for the paint code on the certification label. Usually labeled as 'PAINT' followed by 2-3 characters"
            }
        ],
        "code_format": "2-3 character code (e.g., UD, SWP, ABP)",
        "common_colors": {
            "UD": {"name": "Aurora Black Pearl", "years": "2015-present"},
            "SWP": {"name": "Snow White Pearl", "years": "2010-present"},
            "ABP": {"name": "Aurora Black Pearl", "years": "2018-present"}
        }
    }
}


# Singapore paint product suppliers
SINGAPORE_PAINT_SUPPLIERS = {
    "touch_up_pens": [
        {
            "brand": "OEM (Manufacturer)",
            "where_to_buy": "Authorized dealership parts department",
            "price_range": "$15-30 SGD",
            "notes": "Most accurate color match, recommended for small chips"
        },
        {
            "brand": "Dupli-Color",
            "where_to_buy": "Hardware stores, Sim Lim Square",
            "price_range": "$10-20 SGD",
            "notes": "Good quality aftermarket option"
        }
    ],
    "spray_cans": [
        {
            "brand": "OEM Aerosol",
            "where_to_buy": "Authorized dealership",
            "price_range": "$35-60 SGD",
            "notes": "Best color match for larger areas"
        },
        {
            "brand": "Nippon Paint",
            "where_to_buy": "Paint suppliers, automotive shops",
            "price_range": "$25-45 SGD",
            "notes": "Professional quality, color matching service available"
        }
    ],
    "professional_paint": [
        {
            "brand": "Custom Mixed",
            "where_to_buy": "Auto paint shops (e.g., Sin Ming area)",
            "price_range": "$80-200 SGD per liter",
            "notes": "Professional mixing from paint code, recommended for panel repaints"
        }
    ]
}


class PaintCodeService:
    """
    Intelligent paint code lookup service

    Provides:
    - Paint code identification
    - Physical location guidance
    - Verification steps
    - Product recommendations
    - Professional advice
    """

    def lookup_paint_code(
        self,
        vin: Optional[str] = None,
        make: Optional[str] = None,
        model: Optional[str] = None,
        year: Optional[int] = None,
        color_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lookup paint code with comprehensive guidance

        Args:
            vin: Vehicle VIN (not fully decoded, but can validate format)
            make: Vehicle make
            model: Vehicle model
            year: Vehicle year
            color_description: User's description of color

        Returns:
            Comprehensive paint code guidance with locations and products
        """
        logger.info("paint_code_lookup_start", vin=vin, make=make, model=model, year=year)

        if not make:
            return self._handle_insufficient_data("Vehicle make is required")

        make_lower = make.lower()

        # Get paint code locations for this make
        location_data = PAINT_CODE_LOCATIONS.get(make_lower, self._get_generic_locations())

        # Try to identify paint code from color description
        suggested_code = None
        color_name = None
        alternative_names = []
        confidence = 0.5

        if color_description and make_lower in PAINT_CODE_LOCATIONS:
            suggested_code, color_name, confidence = self._match_color_description(
                color_description, make_lower
            )

        # Get paint code locations
        paint_code_locations = [
            {
                "location": loc["location"],
                "description": loc["description"],
                "image_url": None  # Could add diagram URLs in production
            }
            for loc in location_data["locations"]
        ]

        # Generate verification steps
        verification_steps = self._generate_verification_steps(make_lower, suggested_code)

        # Get recommended products
        recommended_products = self._get_recommended_products(make_lower)

        # Generate professional advice
        professional_advice = self._generate_professional_advice(suggested_code, color_description)

        # Generate assumptions
        assumptions = self._list_assumptions(vin, make, model, year, color_description)

        # Generate intent summary
        intent_parts = [f"find the paint code for their {make.title()}"]
        if model:
            intent_parts.append(model.title())
        if year:
            intent_parts.append(f"({year})")
        intent_understood = f"User wants to " + " ".join(intent_parts)

        # Generate reasoning
        reasoning = self._generate_reasoning(
            make_lower, suggested_code, color_name, color_description, confidence
        )

        # Get alternative color names
        if suggested_code and make_lower in PAINT_CODE_LOCATIONS:
            color_info = PAINT_CODE_LOCATIONS[make_lower]["common_colors"].get(suggested_code, {})
            if color_info:
                # Some manufacturers use different names in different markets
                alternative_names = self._get_alternative_names(make_lower, suggested_code)

        return {
            "success": True,
            "intent_understood": intent_understood,
            "paint_code": suggested_code,
            "color_name": color_name,
            "alternative_names": alternative_names if alternative_names else None,
            "paint_code_locations": paint_code_locations,
            "verification_steps": verification_steps,
            "recommended_products": recommended_products,
            "professional_advice": professional_advice,
            "assumptions": assumptions,
            "confidence": confidence,
            "reasoning": reasoning,
            "metadata": {
                "code_format": location_data.get("code_format", "Varies by model"),
                "common_location": location_data["locations"][0]["location"],
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
        }

    def _match_color_description(
        self,
        color_desc: str,
        make: str
    ) -> tuple[Optional[str], Optional[str], float]:
        """Match user's color description to paint code"""
        color_lower = color_desc.lower()
        common_colors = PAINT_CODE_LOCATIONS[make]["common_colors"]

        # Simple keyword matching
        keywords = {
            "white": ["white", "pearl", "ivory"],
            "black": ["black", "obsidian", "phantom", "crystal black"],
            "silver": ["silver", "gray", "grey", "metallic"],
            "red": ["red", "ruby", "crimson", "milano"],
            "blue": ["blue", "sapphire", "azure"]
        }

        for code, info in common_colors.items():
            color_name = info["name"].lower()

            # Direct match in color name
            for base_color, variants in keywords.items():
                if any(variant in color_lower for variant in variants):
                    if base_color in color_name or any(variant in color_name for variant in variants):
                        return code, info["name"], 0.75

        # No match
        return None, None, 0.3

    def _generate_verification_steps(
        self,
        make: str,
        suggested_code: Optional[str]
    ) -> List[str]:
        """Generate steps to verify paint code"""
        steps = []

        # Step 1: Find the sticker
        location_data = PAINT_CODE_LOCATIONS.get(make, self._get_generic_locations())
        primary_location = location_data["locations"][0]["location"]
        steps.append(f"Locate the paint code sticker on your vehicle's {primary_location}")

        # Step 2: Identify the code
        code_format = location_data.get("code_format", "varies")
        steps.append(f"Look for the paint code - it should be a {code_format}")

        # Step 3: Write it down
        steps.append("Write down the exact code including any letters, numbers, and dashes")

        # Step 4: Verify at dealer
        steps.append(f"Verify the code with a {make.title()} dealership parts department for 100% accuracy")

        # Step 5: Test match
        if suggested_code:
            steps.append(f"If the code matches '{suggested_code}', you can proceed with ordering paint products")
        else:
            steps.append("Once you have the code, you can order exact-match paint products")

        return steps

    def _get_recommended_products(self, make: str) -> List[Dict[str, Any]]:
        """Get recommended paint products for Singapore market"""
        products = []

        # Touch-up pen (for small chips)
        for pen in SINGAPORE_PAINT_SUPPLIERS["touch_up_pens"]:
            products.append({
                "product_type": "Touch-up pen",
                "brand": pen["brand"],
                "product_name": f"{make.title()} Paint Touch-Up Pen",
                "estimated_price": pen["price_range"],
                "where_to_buy": pen["where_to_buy"],
                "notes": pen["notes"]
            })

        # Spray can (for larger areas)
        products.append({
            "product_type": "Spray can",
            "brand": SINGAPORE_PAINT_SUPPLIERS["spray_cans"][0]["brand"],
            "product_name": f"{make.title()} OEM Aerosol Paint",
            "estimated_price": SINGAPORE_PAINT_SUPPLIERS["spray_cans"][0]["price_range"],
            "where_to_buy": SINGAPORE_PAINT_SUPPLIERS["spray_cans"][0]["where_to_buy"],
            "notes": SINGAPORE_PAINT_SUPPLIERS["spray_cans"][0]["notes"]
        })

        # Professional paint (for panel repaint)
        products.append({
            "product_type": "Professional paint",
            "brand": "Custom mixed automotive paint",
            "product_name": "Color-matched basecoat + clearcoat",
            "estimated_price": "$80-200 SGD per liter",
            "where_to_buy": "Auto paint shops (Sin Ming, Woodlands industrial areas)",
            "notes": "Recommended for panel repaints or extensive touch-up work"
        })

        return products

    def _generate_professional_advice(
        self,
        suggested_code: Optional[str],
        color_description: Optional[str]
    ) -> str:
        """Generate advice on when to consult professionals"""
        if not suggested_code:
            return (
                "Since we couldn't determine your exact paint code from the description, "
                "we strongly recommend visiting your dealership parts department. They can "
                "look up the code from your VIN or help you locate it on your vehicle. "
                "Using the wrong paint code will result in a color mismatch."
            )

        return (
            "For small chips and scratches, DIY touch-up is feasible. However, for larger areas "
            "(bigger than a credit card), we recommend professional repainting to ensure proper "
            "color match, blending, and clearcoat application. Modern metallic and pearl paints "
            "require specific application techniques for invisible repairs."
        )

    def _list_assumptions(
        self,
        vin: Optional[str],
        make: Optional[str],
        model: Optional[str],
        year: Optional[int],
        color_description: Optional[str]
    ) -> List[str]:
        """List assumptions made in analysis"""
        assumptions = []

        assumptions.append("Paint code location information based on common configurations for this make")

        if not vin:
            assumptions.append("Without VIN, cannot decode exact paint code - provided location guidance instead")

        if color_description and not model:
            assumptions.append("Color matching based on description only - verification against actual code sticker required")

        if not year:
            assumptions.append("Paint code locations may vary by model year - check all suggested locations")

        assumptions.append("Product recommendations based on Singapore market availability")
        assumptions.append("Paint codes assumed to be in manufacturer's standard format")

        return assumptions

    def _generate_reasoning(
        self,
        make: str,
        suggested_code: Optional[str],
        color_name: Optional[str],
        color_description: Optional[str],
        confidence: float
    ) -> str:
        """Generate reasoning for the response"""
        if suggested_code:
            reasoning = (
                f"Based on your color description ('{color_description}'), "
                f"the most likely paint code is '{suggested_code}' ({color_name}), "
                f"which is a common {make.title()} color. However, verification against "
                f"your vehicle's paint code sticker is essential for 100% accuracy."
            )
        else:
            reasoning = (
                f"Without specific color information or VIN decoding capability, "
                f"we've provided guidance on where to find your {make.title()}'s paint code sticker "
                f"and how to verify it. The most reliable method is to physically locate "
                f"the code on your vehicle."
            )

        return reasoning

    def _get_generic_locations(self) -> Dict[str, Any]:
        """Get generic paint code locations for unknown makes"""
        return {
            "locations": [
                {
                    "location": "Driver's door jamb",
                    "description": "Most vehicles have a paint code sticker on the driver's side door jamb. Open the door and look on the door frame."
                },
                {
                    "location": "Under the hood",
                    "description": "Check the firewall, radiator support, or strut towers for a paint code sticker"
                },
                {
                    "location": "Glove compartment",
                    "description": "Some manufacturers place the paint code sticker inside the glove box"
                }
            ],
            "code_format": "Varies by manufacturer"
        }

    def _get_alternative_names(self, make: str, paint_code: str) -> List[str]:
        """Get alternative names for the color"""
        # Some colors have different names in different markets
        alternative_map = {
            "toyota": {
                "040": ["Super White II", "White"],
                "070": ["Blizzard White Pearl", "White Pearl"]
            },
            "honda": {
                "NH-731P": ["Black Pearl", "Crystal Black"]
            }
        }

        if make in alternative_map and paint_code in alternative_map[make]:
            return alternative_map[make][paint_code]

        return []

    def _handle_insufficient_data(self, reason: str) -> Dict[str, Any]:
        """Handle cases with insufficient data"""
        return {
            "success": False,
            "message": "Insufficient data for paint code lookup",
            "reason": reason,
            "required_fields": ["make"],
            "helpful_tip": "At minimum, we need your vehicle's make (manufacturer) to provide paint code location guidance"
        }


# Singleton instance
_paint_code_service = None


def get_paint_code_service() -> PaintCodeService:
    """Get or create paint code service instance"""
    global _paint_code_service
    if _paint_code_service is None:
        _paint_code_service = PaintCodeService()
    return _paint_code_service
