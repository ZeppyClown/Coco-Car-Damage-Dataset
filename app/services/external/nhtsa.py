"""NHTSA (National Highway Traffic Safety Administration) API Integration

Free government API for vehicle data and recalls.
API Documentation: https://vpic.nhtsa.dot.gov/api/
"""

import httpx
from typing import Optional, Dict, List, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


class NHTSAService:
    """NHTSA API service for VIN decoding and recall information"""

    BASE_URL = "https://vpic.nhtsa.dot.gov/api"
    TIMEOUT = 10.0

    async def decode_vin(self, vin: str) -> Optional[Dict[str, Any]]:
        """
        Decode a VIN and get vehicle specifications

        Args:
            vin: 17-character Vehicle Identification Number

        Returns:
            Dictionary containing vehicle specifications or None if error
        """
        logger.info("nhtsa_decode_vin", vin=vin)

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(
                    f"{self.BASE_URL}/vehicles/DecodeVin/{vin}?format=json"
                )
                response.raise_for_status()

                data = response.json()

                if data.get("Count") == 0:
                    logger.warning("nhtsa_no_data", vin=vin)
                    return None

                # Parse the results into a cleaner format
                results = data.get("Results", [])
                parsed_data = self._parse_vin_data(results)

                logger.info("nhtsa_decode_success", vin=vin, fields_count=len(parsed_data))
                return parsed_data

        except httpx.HTTPError as e:
            logger.error("nhtsa_http_error", vin=vin, error=str(e))
            return None
        except Exception as e:
            logger.error("nhtsa_decode_error", vin=vin, error=str(e), exc_info=True)
            return None

    async def get_recalls(self, vin: str) -> List[Dict[str, Any]]:
        """
        Get recall information for a VIN

        Args:
            vin: 17-character Vehicle Identification Number

        Returns:
            List of recall dictionaries
        """
        logger.info("nhtsa_get_recalls", vin=vin)

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(
                    f"{self.BASE_URL}/Recalls/GetRecallsByVIN/{vin}?format=json"
                )
                response.raise_for_status()

                data = response.json()
                recalls = data.get("Results", [])

                logger.info("nhtsa_recalls_found", vin=vin, count=len(recalls))
                return recalls

        except httpx.HTTPError as e:
            logger.error("nhtsa_recalls_http_error", vin=vin, error=str(e))
            return []
        except Exception as e:
            logger.error("nhtsa_recalls_error", vin=vin, error=str(e), exc_info=True)
            return []

    async def get_recalls_by_make_model_year(
        self, make: str, model: str, year: int
    ) -> List[Dict[str, Any]]:
        """
        Get recalls by make, model, and year

        Args:
            make: Vehicle make (e.g., "Honda")
            model: Vehicle model (e.g., "Civic")
            year: Model year

        Returns:
            List of recall dictionaries
        """
        logger.info("nhtsa_get_recalls_by_mmy", make=make, model=model, year=year)

        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(
                    f"{self.BASE_URL}/Recalls/GetRecallsByMakeModelYear/{make}/{model}/{year}?format=json"
                )
                response.raise_for_status()

                data = response.json()
                recalls = data.get("Results", [])

                logger.info("nhtsa_recalls_mmy_found", make=make, model=model, year=year, count=len(recalls))
                return recalls

        except httpx.HTTPError as e:
            logger.error("nhtsa_recalls_mmy_http_error", error=str(e))
            return []
        except Exception as e:
            logger.error("nhtsa_recalls_mmy_error", error=str(e), exc_info=True)
            return []

    def _parse_vin_data(self, results: List[Dict]) -> Dict[str, Any]:
        """
        Parse NHTSA VIN decode results into a structured format

        Args:
            results: Raw results from NHTSA API

        Returns:
            Structured vehicle data dictionary
        """
        # Create a lookup dictionary from the results
        data_dict = {}
        for item in results:
            variable = item.get("Variable")
            value = item.get("Value")
            if variable and value:
                data_dict[variable] = value

        # Extract and organize the most useful fields
        parsed = {
            # Basic vehicle info
            "make": data_dict.get("Make"),
            "model": data_dict.get("Model"),
            "year": data_dict.get("Model Year"),
            "trim": data_dict.get("Trim"),
            "body_class": data_dict.get("Body Class"),
            "vehicle_type": data_dict.get("Vehicle Type"),

            # Manufacturer info
            "manufacturer": data_dict.get("Manufacturer Name"),
            "plant_city": data_dict.get("Plant City"),
            "plant_country": data_dict.get("Plant Country"),

            # Engine specifications
            "engine": {
                "displacement_l": data_dict.get("Displacement (L)"),
                "displacement_cc": data_dict.get("Displacement (CC)"),
                "cylinders": data_dict.get("Engine Number of Cylinders"),
                "configuration": data_dict.get("Engine Configuration"),
                "fuel_type": data_dict.get("Fuel Type - Primary"),
                "horsepower": data_dict.get("Engine Brake (hp)"),
                "manufacturer": data_dict.get("Engine Manufacturer"),
                "model": data_dict.get("Engine Model"),
            },

            # Transmission
            "transmission": {
                "type": data_dict.get("Transmission Style"),
                "speeds": data_dict.get("Transmission Speeds"),
            },

            # Drivetrain
            "drive_type": data_dict.get("Drive Type"),

            # Dimensions
            "doors": data_dict.get("Doors"),
            "seats": data_dict.get("Seating Rows"),

            # Safety features
            "safety": {
                "airbag_locations": data_dict.get("Air Bag Locations"),
                "abs": data_dict.get("ABS"),
                "esc": data_dict.get("Electronic Stability Control (ESC)"),
                "traction_control": data_dict.get("Traction Control"),
            },

            # Series/trim info
            "series": data_dict.get("Series"),
            "series2": data_dict.get("Series2"),

            # Classification
            "ncsa_make": data_dict.get("NCSA Make"),
            "ncsa_model": data_dict.get("NCSA Model"),
            "ncsa_body_type": data_dict.get("NCSA Body Type"),

            # Additional useful fields
            "gross_vehicle_weight_rating": data_dict.get("Gross Vehicle Weight Rating From"),
            "base_price": data_dict.get("Base Price ($)"),
        }

        # Remove None values for cleaner output
        parsed = self._remove_none_values(parsed)

        return parsed

    def _remove_none_values(self, d: Dict) -> Dict:
        """Recursively remove None values from dictionary"""
        if isinstance(d, dict):
            return {
                k: self._remove_none_values(v)
                for k, v in d.items()
                if v is not None and v != "" and v != "Not Applicable"
            }
        return d
