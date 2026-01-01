"""
eBay Finding API Adapter for Automotive Parts
Searches eBay Singapore marketplace for automotive parts

HYBRID SYSTEM: Ready to activate when credentials are added
Status: COMMENTED OUT - Set USE_EBAY_API=True in config when ready
"""
import logging
from typing import List, Dict, Optional
import httpx
from datetime import datetime
import hashlib
from app.core.config import settings
from app.services.external.parts.base_adapter import BasePartsAdapter

logger = logging.getLogger(__name__)


class EbayAdapter(BasePartsAdapter):
    """
    eBay Finding API adapter for automotive parts

    API: eBay Finding API
    Marketplace: eBay Singapore (EBAY_SG)
    Rate Limit: 5,000 calls/day

    TO ACTIVATE:
    1. Get eBay developer credentials from: https://developer.ebay.com/
    2. Add to .env:
       EBAY_APP_ID=your_app_id
       EBAY_DEV_ID=your_dev_id
       EBAY_CERT_ID=your_cert_id
    3. Set USE_EBAY_API=True in config.py
    """

    def __init__(self):
        super().__init__(
            name="eBay",
            rate_limit=settings.EBAY_RATE_LIMIT
        )
        self.app_id = settings.EBAY_APP_ID
        self.dev_id = settings.EBAY_DEV_ID
        self.cert_id = settings.EBAY_CERT_ID
        self.environment = settings.EBAY_ENVIRONMENT
        self.marketplace = settings.EBAY_MARKETPLACE

        # eBay Finding API endpoint
        if self.environment == "PRODUCTION":
            self.base_url = "https://svcs.ebay.com/services/search/FindingService/v1"
        else:
            self.base_url = "https://svcs.sandbox.ebay.com/services/search/FindingService/v1"

        # eBay Motors category ID
        self.motors_category_id = "6000"  # eBay Motors > Parts & Accessories

    def search_parts(
        self,
        query: str,
        vehicle_context: Optional[Dict] = None,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search eBay Singapore for automotive parts

        Args:
            query: Search query (e.g., "brake pads")
            vehicle_context: Optional vehicle info {make, model, year}
            filters: Optional filters {price_min, price_max, condition}

        Returns:
            List of normalized part results
        """
        # Check if eBay is enabled
        if not settings.USE_EBAY_API:
            logger.info("eBay API is disabled. Set USE_EBAY_API=True to enable.")
            return []

        if not self.app_id:
            logger.warning("eBay credentials not configured")
            return []

        # Check rate limit
        if not self._check_rate_limit():
            logger.warning(f"Rate limit exceeded for {self.name}")
            return []

        # Build search query
        search_query = self._build_search_query(query, vehicle_context)

        # Build filters
        item_filters = self._build_filters(filters)

        # Execute search
        try:
            results = self._execute_search(search_query, item_filters)

            # Normalize results
            normalized = []
            for result in results:
                normalized_part = self._normalize_result(result)
                if normalized_part and self._filter_singapore(normalized_part):
                    normalized.append(normalized_part)

            logger.info(f"eBay found {len(normalized)} parts for: {search_query}")
            return normalized

        except Exception as e:
            logger.error(f"eBay search failed: {e}")
            return []

    def get_part_details(self, part_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific eBay listing

        Args:
            part_id: eBay item ID

        Returns:
            Detailed part information
        """
        if not settings.USE_EBAY_API or not self.app_id:
            return None

        # Note: Would use Shopping API for item details
        # For now, search results contain sufficient detail
        logger.info(f"Getting eBay details for item: {part_id}")
        return None

    def _build_search_query(
        self,
        query: str,
        vehicle_context: Optional[Dict] = None
    ) -> str:
        """Build optimized eBay search query"""
        search_terms = [query]

        # Add vehicle context if provided
        if vehicle_context:
            if vehicle_context.get("year"):
                search_terms.append(str(vehicle_context["year"]))
            if vehicle_context.get("make"):
                search_terms.append(vehicle_context["make"])
            if vehicle_context.get("model"):
                search_terms.append(vehicle_context["model"])

        return " ".join(search_terms)

    def _build_filters(self, filters: Optional[Dict] = None) -> List[Dict]:
        """Build eBay item filters"""
        item_filters = [
            {
                "name": "categoryId",
                "value": self.motors_category_id
            },
            {
                "name": "locatedIn",
                "value": "SG"  # Singapore only
            }
        ]

        if filters:
            # Price filter
            if filters.get("price_min"):
                item_filters.append({
                    "name": "MinPrice",
                    "value": str(filters["price_min"])
                })
            if filters.get("price_max"):
                item_filters.append({
                    "name": "MaxPrice",
                    "value": str(filters["price_max"])
                })

            # Condition filter
            if filters.get("condition"):
                condition_map = {
                    "new": "1000",  # New
                    "used": "3000"   # Used
                }
                if filters["condition"] in condition_map:
                    item_filters.append({
                        "name": "Condition",
                        "value": condition_map[filters["condition"]]
                    })

        return item_filters

    def _execute_search(
        self,
        query: str,
        item_filters: List[Dict],
        max_entries: int = 20
    ) -> List[Dict]:
        """Execute eBay Finding API search request"""
        params = {
            "OPERATION-NAME": "findItemsAdvanced",
            "SERVICE-VERSION": "1.0.0",
            "SECURITY-APPNAME": self.app_id,
            "RESPONSE-DATA-FORMAT": "JSON",
            "REST-PAYLOAD": "",
            "keywords": query,
            "paginationInput.entriesPerPage": str(max_entries),
            "GLOBAL-ID": self.marketplace
        }

        # Add item filters
        for i, item_filter in enumerate(item_filters):
            params[f"itemFilter({i}).name"] = item_filter["name"]
            params[f"itemFilter({i}).value"] = item_filter["value"]

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()

                data = response.json()

                # Extract search results
                search_result = data.get("findItemsAdvancedResponse", [{}])[0]
                search_result = search_result.get("searchResult", [{}])[0]
                items = search_result.get("item", [])

                return items

        except httpx.HTTPError as e:
            logger.error(f"eBay HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"eBay request failed: {e}")
            raise

    def _normalize_result(self, item: Dict) -> Optional[Dict]:
        """
        Normalize eBay listing to standard format

        eBay Finding API returns:
        - itemId: Unique item ID
        - title: Item title
        - sellingStatus: Price info
        - location: Seller location
        - galleryURL: Image URL
        - condition: Item condition
        """
        try:
            # Extract basic info
            item_id = item.get("itemId", [""])[0]
            title = item.get("title", [""])[0]

            # Extract price
            selling_status = item.get("sellingStatus", [{}])[0]
            price_data = selling_status.get("currentPrice", [{}])[0]
            price_sgd = float(price_data.get("__value__", 0))
            currency = price_data.get("@currencyId", "SGD")

            # Convert to SGD if needed (basic conversion)
            if currency != "SGD":
                # Note: Would use real exchange rate API in production
                logger.warning(f"Currency {currency} found, assuming SGD")

            # Extract other fields
            gallery_url = item.get("galleryURL", [""])[0]
            location = item.get("location", [""])[0]
            condition = item.get("condition", [{}])[0]
            condition_display = condition.get("conditionDisplayName", ["New"])[0]

            # Extract listing URL
            listing_url = item.get("viewItemURL", [""])[0]

            # Extract seller info
            seller_info = item.get("sellerInfo", [{}])[0]
            seller_name = seller_info.get("sellerUserName", ["Unknown"])[0]
            feedback_score = seller_info.get("feedbackScore", [0])[0]

            # Calculate seller rating (0-5 scale)
            seller_rating = min(5.0, int(feedback_score) / 1000 * 5)

            return {
                "part_number": f"EBAY-{item_id}",
                "name": title,
                "description": title,  # eBay Finding API doesn't return full description
                "source": "ebay",
                "source_id": item_id,
                "source_url": listing_url,
                "price_sgd": price_sgd,
                "currency": "SGD",
                "image_url": gallery_url,
                "seller_name": seller_name,
                "seller_rating": seller_rating,
                "seller_location": location,
                "ships_to_singapore": True,  # Filtered by locatedIn=SG
                "availability": "in_stock",  # Assume in stock if listed
                "condition": condition_display.lower(),
                "brand": self._extract_brand_from_title(title),
                "retrieved_at": datetime.utcnow().isoformat(),
                "data_source": "ebay_api"  # HYBRID SYSTEM: Mark as eBay data
            }

        except Exception as e:
            logger.error(f"Failed to normalize eBay result: {e}")
            return None

    def _extract_brand_from_title(self, title: str) -> Optional[str]:
        """Extract brand from item title"""
        # Common automotive brands
        brands = [
            "Bosch", "Brembo", "Denso", "NGK", "Michelin", "Continental",
            "Bridgestone", "Castrol", "Mobil", "Shell", "3M", "Akebono",
            "ACDelco", "Monroe", "KYB", "Bilstein", "OEM", "Original",
            "Genuine", "Toyota", "Honda", "Nissan", "Ford", "BMW", "Mercedes"
        ]

        title_upper = title.upper()
        for brand in brands:
            if brand.upper() in title_upper:
                return brand

        return None

    def _filter_singapore(self, part: Dict) -> bool:
        """Filter for Singapore sellers/shipping"""
        # Already filtered by eBay API (locatedIn=SG)
        return part.get("ships_to_singapore", False)


# ACTIVATION INSTRUCTIONS:
# ========================
# 1. Register for eBay Developer Account:
#    https://developer.ebay.com/join
#
# 2. Create an application to get credentials:
#    - Go to: https://developer.ebay.com/my/keys
#    - Create new keyset
#    - Note: APP_ID, DEV_ID, CERT_ID
#
# 3. Add credentials to .env file:
#    EBAY_APP_ID=YourAppID
#    EBAY_DEV_ID=YourDevID
#    EBAY_CERT_ID=YourCertID
#
# 4. Enable in config:
#    Set USE_EBAY_API=True in app/core/config.py
#
# 5. Test the integration:
#    The adapter will automatically be used when credentials are present
