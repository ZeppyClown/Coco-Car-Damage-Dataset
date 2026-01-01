"""
Base adapter class for parts APIs

All parts API adapters (eBay, Lazada, Shopee) inherit from this base class
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.core.logging import get_logger

logger = get_logger(__name__)


class BasePartsAdapter(ABC):
    """Abstract base class for parts API adapters"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize adapter with configuration

        Args:
            config: Dictionary with API credentials and settings
        """
        self.config = config
        self.source_name = self.__class__.__name__.replace("Adapter", "").lower()
        logger.info(f"{self.source_name}_adapter_init", message="Adapter initialized")

    @abstractmethod
    async def search_parts(
        self,
        query: str,
        vehicle: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for parts

        Args:
            query: Search query text (e.g., "brake pads")
            vehicle: Optional vehicle context (make, model, year)
            limit: Maximum number of results
            filters: Optional filters (price range, brand, etc.)

        Returns:
            List of part dictionaries with standardized structure
        """
        pass

    @abstractmethod
    async def get_part_details(self, part_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific part

        Args:
            part_id: Part ID from the source API

        Returns:
            Part details dictionary or None if not found
        """
        pass

    def normalize_part_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize part data from API response to standard format

        Args:
            raw_data: Raw API response

        Returns:
            Standardized part dictionary
        """
        # This method can be overridden by subclasses
        # Default implementation returns the raw data
        return {
            "source": self.source_name,
            "source_id": str(raw_data.get("id", "")),
            "part_number": raw_data.get("part_number", ""),
            "name": raw_data.get("title", raw_data.get("name", "")),
            "description": raw_data.get("description", ""),
            "category": raw_data.get("category", ""),
            "brand": raw_data.get("brand", ""),
            "condition": raw_data.get("condition", "new"),
            "price": {
                "value": raw_data.get("price", {}).get("value", 0.0),
                "currency": raw_data.get("price", {}).get("currency", "SGD"),
            },
            "images": raw_data.get("images", []),
            "url": raw_data.get("url", ""),
            "seller": raw_data.get("seller", {}),
            "shipping": raw_data.get("shipping", {}),
        }

    def build_search_query(
        self,
        query: str,
        vehicle: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build search query string including vehicle context

        Args:
            query: Base search query
            vehicle: Vehicle context

        Returns:
            Enhanced query string
        """
        parts = [query]

        if vehicle:
            if vehicle.get("make"):
                parts.append(vehicle["make"])
            if vehicle.get("model"):
                parts.append(vehicle["model"])
            if vehicle.get("year"):
                parts.append(str(vehicle["year"]))

        return " ".join(parts)

    def filter_singapore_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter and prioritize results for Singapore

        Args:
            results: List of part results

        Returns:
            Filtered and sorted results prioritizing Singapore sellers
        """
        singapore_results = []
        other_results = []

        for result in results:
            shipping = result.get("shipping", {})
            seller = result.get("seller", {})

            # Check if ships to Singapore or seller is in Singapore
            ships_to_sg = shipping.get("ships_to_singapore", False)
            seller_in_sg = seller.get("location", "").upper().startswith("SG")

            if ships_to_sg or seller_in_sg:
                singapore_results.append(result)
            else:
                other_results.append(result)

        # Prioritize Singapore results
        return singapore_results + other_results

    async def check_rate_limit(self) -> bool:
        """
        Check if API rate limit has been reached

        Returns:
            True if OK to make request, False if rate limit reached
        """
        # This will be implemented with database tracking
        # For now, return True
        return True

    async def track_api_call(self, endpoint: str):
        """
        Track API call for rate limiting

        Args:
            endpoint: API endpoint that was called
        """
        # This will be implemented with database tracking
        logger.info(f"{self.source_name}_api_call", endpoint=endpoint)

    def handle_api_error(self, error: Exception, context: str = ""):
        """
        Handle API errors gracefully

        Args:
            error: Exception that occurred
            context: Additional context about the error
        """
        logger.error(
            f"{self.source_name}_api_error",
            error=str(error),
            context=context
        )

        # Return empty results instead of crashing
        return []
