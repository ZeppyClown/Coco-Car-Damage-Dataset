"""
Google Custom Search API Adapter for Parts Search
Searches Singapore marketplaces: Lazada.sg, Shopee.sg, Carousell.sg

HYBRID SYSTEM: Active data source for real-time pricing
"""
import logging
from typing import List, Dict, Optional
import httpx
from datetime import datetime
from app.core.config import settings
from app.services.external.parts.base_adapter import BasePartsAdapter

logger = logging.getLogger(__name__)


class GoogleCSEAdapter(BasePartsAdapter):
    """
    Google Custom Search Engine adapter for automotive parts

    Searches across Singapore marketplaces without requiring seller accounts:
    - Lazada.sg
    - Shopee.sg
    - Carousell.sg
    - Amazon.sg

    Free tier: 100 queries/day
    Paid tier: $5 per 1,000 queries after free limit
    """

    def __init__(self):
        super().__init__(
            name="Google CSE",
            rate_limit=settings.GOOGLE_CSE_RATE_LIMIT
        )
        self.api_key = settings.GOOGLE_API_KEY
        self.cse_id = settings.GOOGLE_CSE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"

        # Target marketplaces for Singapore
        self.target_sites = [
            "lazada.sg",
            "shopee.sg",
            "carousell.sg",
            "amazon.sg"
        ]

    def search_parts(
        self,
        query: str,
        vehicle_context: Optional[Dict] = None,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for automotive parts across Singapore marketplaces

        Args:
            query: Search query (e.g., "brake pads Honda Civic")
            vehicle_context: Optional vehicle info {make, model, year}
            filters: Optional filters {price_min, price_max, condition}

        Returns:
            List of normalized part results
        """
        if not self.api_key or not self.cse_id:
            logger.warning("Google CSE credentials not configured")
            return []

        # Check rate limit
        if not self._check_rate_limit():
            logger.warning(f"Rate limit exceeded for {self.name}")
            return []

        # Build search query
        search_query = self._build_search_query(query, vehicle_context)

        # Execute search
        try:
            results = self._execute_search(search_query, num_results=10)

            # Normalize results
            normalized = []
            for result in results:
                normalized_part = self._normalize_result(result)
                if normalized_part and self._filter_singapore(normalized_part):
                    normalized.append(normalized_part)

            logger.info(f"Google CSE found {len(normalized)} parts for: {search_query}")
            return normalized

        except Exception as e:
            logger.error(f"Google CSE search failed: {e}")
            return []

    def get_part_details(self, part_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific part

        Note: Google CSE doesn't support direct part lookup
        Returns None as details are already in search results
        """
        logger.info("Google CSE doesn't support direct part lookup")
        return None

    def _build_search_query(
        self,
        query: str,
        vehicle_context: Optional[Dict] = None
    ) -> str:
        """Build optimized search query"""
        # Start with base query
        search_terms = [query]

        # Add vehicle context if provided
        if vehicle_context:
            if vehicle_context.get("make"):
                search_terms.append(vehicle_context["make"])
            if vehicle_context.get("model"):
                search_terms.append(vehicle_context["model"])
            if vehicle_context.get("year"):
                search_terms.append(str(vehicle_context["year"]))

        # Add automotive context
        search_terms.append("car parts")
        search_terms.append("Singapore")

        return " ".join(search_terms)

    def _execute_search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Execute Google Custom Search API request"""
        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "num": num_results,
            "gl": "sg",  # Geolocation: Singapore
            "lr": "lang_en",  # Language: English
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()

                data = response.json()
                return data.get("items", [])

        except httpx.HTTPError as e:
            logger.error(f"Google CSE HTTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Google CSE request failed: {e}")
            raise

    def _normalize_result(self, result: Dict) -> Optional[Dict]:
        """
        Normalize Google CSE result to standard format

        Google CSE returns:
        - title: Product title
        - link: Product URL
        - snippet: Product description
        - pagemap: Structured data (price, image, etc.)
        """
        try:
            # Extract basic info
            title = result.get("title", "")
            url = result.get("link", "")
            description = result.get("snippet", "")

            # Detect source marketplace
            source = self._detect_marketplace(url)
            if not source:
                return None  # Skip non-marketplace results

            # Extract structured data from pagemap
            pagemap = result.get("pagemap", {})

            # Try to extract price
            price_sgd = self._extract_price(pagemap, description)

            # Try to extract image
            image_url = self._extract_image(pagemap)

            # Extract seller info
            seller_info = self._extract_seller(source, url)

            # Generate part number (use URL hash as pseudo part number)
            part_number = f"{source.upper()}-{hash(url) % 1000000:06d}"

            return {
                "part_number": part_number,
                "name": title,
                "description": description,
                "source": source,
                "source_url": url,
                "price_sgd": price_sgd,
                "currency": "SGD",
                "image_url": image_url,
                "seller_name": seller_info.get("name"),
                "seller_rating": seller_info.get("rating"),
                "ships_to_singapore": True,
                "availability": "unknown",  # Google CSE doesn't provide stock info
                "condition": "new",  # Assume new unless specified
                "brand": self._extract_brand(title),
                "retrieved_at": datetime.utcnow().isoformat(),
                "data_source": "google_cse"  # HYBRID SYSTEM: Mark as Google CSE data
            }

        except Exception as e:
            logger.error(f"Failed to normalize Google CSE result: {e}")
            return None

    def _detect_marketplace(self, url: str) -> Optional[str]:
        """Detect which marketplace the result is from"""
        url_lower = url.lower()

        if "lazada.sg" in url_lower:
            return "lazada"
        elif "shopee.sg" in url_lower:
            return "shopee"
        elif "carousell.sg" in url_lower:
            return "carousell"
        elif "amazon.sg" in url_lower:
            return "amazon"
        else:
            return None  # Not a target marketplace

    def _extract_price(self, pagemap: Dict, description: str) -> Optional[float]:
        """Extract price from pagemap or description"""
        # Try pagemap first (structured data)
        if "offer" in pagemap and pagemap["offer"]:
            offer = pagemap["offer"][0]
            if "price" in offer:
                try:
                    return float(offer["price"])
                except (ValueError, TypeError):
                    pass

        if "product" in pagemap and pagemap["product"]:
            product = pagemap["product"][0]
            if "price" in product:
                try:
                    return float(product["price"])
                except (ValueError, TypeError):
                    pass

        # Try to extract from description (fallback)
        import re
        price_pattern = r'\$\s*(\d+(?:\.\d{2})?)'
        match = re.search(price_pattern, description)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass

        return None

    def _extract_image(self, pagemap: Dict) -> Optional[str]:
        """Extract product image URL"""
        # Try metatags
        if "metatags" in pagemap and pagemap["metatags"]:
            metatag = pagemap["metatags"][0]
            for key in ["og:image", "twitter:image", "image"]:
                if key in metatag:
                    return metatag[key]

        # Try cse_image
        if "cse_image" in pagemap and pagemap["cse_image"]:
            return pagemap["cse_image"][0].get("src")

        return None

    def _extract_seller(self, source: str, url: str) -> Dict:
        """Extract seller information"""
        # Basic seller info based on marketplace
        sellers = {
            "lazada": {"name": "Lazada Seller", "rating": None},
            "shopee": {"name": "Shopee Seller", "rating": None},
            "carousell": {"name": "Carousell Seller", "rating": None},
            "amazon": {"name": "Amazon Seller", "rating": None}
        }
        return sellers.get(source, {"name": "Unknown Seller", "rating": None})

    def _extract_brand(self, title: str) -> Optional[str]:
        """Try to extract brand from title"""
        # Common automotive brands
        brands = [
            "Bosch", "Brembo", "Denso", "NGK", "Michelin", "Continental",
            "Bridgestone", "Castrol", "Mobil", "Shell", "3M", "Akebono",
            "ACDelco", "Monroe", "KYB", "Bilstein", "OEM", "Original"
        ]

        title_upper = title.upper()
        for brand in brands:
            if brand.upper() in title_upper:
                return brand

        return None

    def _filter_singapore(self, part: Dict) -> bool:
        """Filter for Singapore availability"""
        # Google CSE results are already filtered for Singapore
        # Additional check for ships_to_singapore flag
        return part.get("ships_to_singapore", False)
