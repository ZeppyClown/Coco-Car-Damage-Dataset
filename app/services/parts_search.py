"""PostgreSQL catalogue retrieval with independent external-provider fallback."""
import hashlib
import json
from datetime import datetime, timedelta
from time import monotonic
from sqlalchemy import text
from app.db.models import PartsCatalog, PartPrice, SearchCache
from app.core.config import settings
from app.core.logging import get_logger
from app.services.compatibility_checker import get_compatibility_checker
from app.services.external.parts.google_cse_adapter import GoogleCSEAdapter
from app.services.external.parts.ebay_adapter import EbayAdapter

logger = get_logger(__name__)


class PartsSearchEngine:
    def __init__(self):
        self.semantic_model = None
        self.google_cse = GoogleCSEAdapter() if settings.USE_GOOGLE_CSE and settings.GOOGLE_API_KEY and settings.GOOGLE_CSE_ID else None
        self.ebay_adapter = EbayAdapter() if settings.USE_EBAY_API and settings.EBAY_APP_ID and settings.EBAY_CLIENT_SECRET else None

    def search(self, db, query, vehicle=None, limit=20, filters=None, use_cache=True, singapore_only=True):
        if not query.strip() or not 1 <= limit <= 100:
            raise ValueError("Nonempty query and limit from 1 to 100 required")
        started = monotonic()
        key = self._hash_query(query, vehicle, filters, limit, singapore_only)
        cached = db.query(SearchCache).filter(SearchCache.query_hash == key, SearchCache.expires_at > datetime.utcnow()).first() if use_cache else None
        if cached:
            cached.hit_count = (cached.hit_count or 0) + 1
            db.commit()
            return {**cached.results, "cache_hit": True}
        results = self._eligible(db, self._fulltext_search(db, query, limit * 3), vehicle, filters, singapore_only)
        sources, failures = ["local_db"], []
        if len(results) < limit:
            for source, adapter in (("google_cse", self.google_cse), ("ebay", self.ebay_adapter)):
                if adapter is None:
                    continue
                sources.append(source)
                try:
                    external = adapter.search_parts(query, vehicle=vehicle, limit=limit, filters=filters)
                    stored = [self._store_external_part(db, part) for part in external]
                    results.extend(self._eligible(db, stored, vehicle, filters, singapore_only))
                except Exception as exc:
                    db.rollback()
                    failures.append(source)
                    logger.warning("provider_failed", source=source, error_type=type(exc).__name__)
        unique = {result["id"]: result for result in results}
        results = list(unique.values())
        for result in results:
            score = result["relevance_score"]
            if result.get("compatible"):
                score *= 1.5
            if result.get("singapore_available"):
                score *= 1.3
            if result.get("oem_or_aftermarket") == "oem":
                score *= 1.1
            result["final_score"] = score
        results.sort(key=lambda result: (-result["final_score"], result["id"]))
        response = {"query": query, "vehicle": vehicle, "results": results[:limit],
            "total_results": min(len(results), limit), "sources_queried": sources,
            "sources_failed": failures, "filters_applied": filters or {},
            "singapore_only": singapore_only, "cache_hit": False,
            "processing_time_ms": round((monotonic() - started) * 1000)}
        if use_cache and results and not failures:
            entry = db.query(SearchCache).filter_by(query_hash=key).first()
            if entry is None:
                entry = SearchCache(query_hash=key, query_text=query)
                db.add(entry)
            entry.results = response
            entry.result_count = response["total_results"]
            entry.sources_queried = sources
            entry.expires_at = datetime.utcnow() + timedelta(seconds=settings.SEARCH_CACHE_TTL)
            db.commit()
        return response

    def _fulltext_search(self, db, query, limit):
        rows = db.execute(text("""
            SELECT id, ts_rank(to_tsvector('english', name || ' ' || COALESCE(description, '')),
                plainto_tsquery('english', :query)) AS rank
            FROM parts_catalog
            WHERE to_tsvector('english', name || ' ' || COALESCE(description, ''))
                @@ plainto_tsquery('english', :query)
            AND (:use_synthetic OR data_source IS NULL OR data_source != 'synthetic')
            ORDER BY rank DESC, id LIMIT :limit
        """), {"query": query, "limit": limit, "use_synthetic": settings.USE_SYNTHETIC_DATA}).all()
        return [self._result(db.get(PartsCatalog, row.id), float(row.rank)) for row in rows]

    @staticmethod
    def _result(part, score):
        return {"id": part.id, "part_number": part.part_number, "name": part.name,
            "description": part.description, "source": part.source, "source_id": part.source_id,
            "brand": part.brand, "condition": part.condition, "oem_or_aftermarket": part.oem_or_aftermarket,
            "image_url": part.image_url, "data_source": part.data_source, "relevance_score": score}

    def _eligible(self, db, results, vehicle, filters, singapore_only):
        eligible = []
        for result in results:
            if vehicle:
                fit = get_compatibility_checker().check_compatibility(db, result["id"], vehicle, strict=True)
                result["compatible"] = fit["compatible"]
                result["compatibility_confidence"] = fit["confidence"]
                if not fit["compatible"]:
                    continue
            filters = filters or {}
            if any(filters.get(k) is not None and filters[k] != result.get(k) for k in ("brand", "condition")):
                continue
            if filters.get("oem_only") and result.get("oem_or_aftermarket") != "oem":
                continue
            prices = db.query(PartPrice).filter_by(part_id=result["id"]).all()
            if singapore_only:
                prices = [price for price in prices if price.ships_to_singapore is True]
                if not prices:
                    continue
            if "price_min" in filters or "price_max" in filters:
                prices = [price for price in prices if price.price_sgd is not None and
                    filters.get("price_min", 0) <= float(price.price_sgd) <= filters.get("price_max", float("inf"))]
                if not prices:
                    continue
            if prices:
                result["source_url"] = next((price.source_url for price in prices if price.source_url), None)
                result["singapore_available"] = any(price.ships_to_singapore is True for price in prices)
                sg_prices = [price for price in prices if price.price_sgd is not None]
                if sg_prices:
                    price = min(sg_prices, key=lambda price: price.price_sgd)
                    result["price"] = {"value": float(price.price_sgd), "currency": "SGD", "seller": price.seller_name}
            eligible.append(result)
        return eligible

    def _store_external_part(self, db, data):
        if not data.get("source") or not data.get("source_id") or not data.get("name"):
            raise ValueError("Provider result requires source, source_id and name")
        part = db.query(PartsCatalog).filter_by(source=data["source"], source_id=data["source_id"]).first()
        if part is None:
            part = PartsCatalog(source=data["source"], source_id=data["source_id"], part_number=data.get("part_number") or "", name=data["name"])
            db.add(part)
        for field in ("name", "description", "brand", "condition", "image_url", "data_source"):
            setattr(part, field, data.get(field))
        part.ships_to_singapore = data.get("ships_to_singapore")
        part.retrieved_at = datetime.utcnow()
        db.flush()
        price = db.query(PartPrice).filter_by(part_id=part.id, source_url=data.get("source_url")).first()
        if price is None:
            price = PartPrice(part_id=part.id, source_url=data.get("source_url"), currency=data.get("currency") or "SGD")
            db.add(price)
        for field in ("price", "price_sgd", "seller_name", "seller_rating", "availability", "condition", "ships_to_singapore"):
            setattr(price, field, data.get(field))
        price.currency = data.get("currency") or "SGD"
        price.last_updated = datetime.utcnow()
        db.commit()
        return self._result(part, 0.8)

    def _hash_query(self, query, vehicle, filters=None, limit=20, singapore_only=True):
        payload = {"query": query.strip().casefold(), "vehicle": vehicle or {}, "filters": filters or {},
                   "limit": limit, "singapore_only": singapore_only, "synthetic": settings.USE_SYNTHETIC_DATA}
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


_search_engine = None


def get_search_engine():
    global _search_engine
    if _search_engine is None:
        _search_engine = PartsSearchEngine()
    return _search_engine
