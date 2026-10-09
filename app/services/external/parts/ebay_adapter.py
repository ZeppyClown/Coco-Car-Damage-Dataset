"""eBay Browse API adapter; Finding API is retired."""
from datetime import datetime, timedelta
import httpx
from app.core.config import settings
from .base_adapter import BasePartsAdapter


class EbayAdapter(BasePartsAdapter):
    def __init__(self):
        super().__init__({"name": "eBay", "rate_limit": settings.EBAY_RATE_LIMIT})
        self.base_url = "https://api.ebay.com"
        if settings.EBAY_ENVIRONMENT.upper() == "SANDBOX":
            self.base_url = "https://api.sandbox.ebay.com"
        self._token = None
        self._token_expires = datetime.min

    def _headers(self):
        if not settings.EBAY_APP_ID or not settings.EBAY_CLIENT_SECRET:
            raise ValueError("eBay client credentials are not configured")
        if self._token is None or datetime.utcnow() >= self._token_expires:
            response = httpx.post(
                self.base_url + "/identity/v1/oauth2/token",
                auth=(settings.EBAY_APP_ID, settings.EBAY_CLIENT_SECRET),
                data={"grant_type": "client_credentials", "scope": "https://api.ebay.com/oauth/api_scope"},
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json()
            self._token = payload["access_token"]
            self._token_expires = datetime.utcnow() + timedelta(seconds=max(0, int(payload["expires_in"]) - 60))
        return {"Authorization": "Bearer " + self._token,
                "X-EBAY-C-MARKETPLACE-ID": settings.EBAY_MARKETPLACE}

    def search_parts(self, query, vehicle=None, limit=20, filters=None):
        if not self._check_rate_limit():
            raise RuntimeError("eBay process quota exceeded")
        terms = [query] + [str(vehicle[k]) for k in ("make", "model", "year") if vehicle and vehicle.get(k)]
        response = httpx.get(self.base_url + "/buy/browse/v1/item_summary/search",
            headers=self._headers(), params={"q": " ".join(terms), "limit": min(limit, 200),
                "filter": "deliveryCountry:SG"}, timeout=15)
        response.raise_for_status()
        return [self._normalize_result(item) for item in response.json().get("itemSummaries", [])]

    def get_part_details(self, part_id):
        response = httpx.get(self.base_url + "/buy/browse/v1/item/" + part_id,
            headers=self._headers(), timeout=15)
        response.raise_for_status()
        return self._normalize_result(response.json())

    def _normalize_result(self, item):
        price = item.get("price", {})
        currency = price.get("currency")
        value = float(price["value"]) if price.get("value") is not None else None
        seller = item.get("seller", {})
        return {"source": "ebay", "source_id": item["itemId"], "part_number": "",
            "name": item["title"], "description": item.get("shortDescription", ""),
            "source_url": item.get("itemWebUrl"), "price": value, "currency": currency,
            "price_sgd": value if currency == "SGD" else None,
            "seller_name": seller.get("username"), "seller_rating": None,
            "ships_to_singapore": None, "condition": item.get("condition", "unknown"),
            "image_url": item.get("image", {}).get("imageUrl"), "availability": "unknown",
            "data_source": "ebay_api"}
