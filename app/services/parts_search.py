"""
Parts Search Engine with Semantic Search

Combines PostgreSQL full-text search with semantic similarity matching
"""

import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text, or_, and_

# Sentence-transformers disabled due to system compatibility issues
# Can be re-enabled later when needed
SENTENCE_TRANSFORMERS_AVAILABLE = False

from app.db.models import (
    PartsCatalog,
    PartPrice,
    PartCompatibilityEnhanced,
    SearchCache
)
from app.core.logging import get_logger
from app.core.config import settings

# HYBRID SYSTEM: Import API adapters
from app.services.external.parts.google_cse_adapter import GoogleCSEAdapter
from app.services.external.parts.ebay_adapter import EbayAdapter

logger = get_logger(__name__)


class PartsSearchEngine:
    """Advanced parts search engine with semantic capabilities"""

    def __init__(self):
        """Initialize search engine with semantic model and API adapters"""
        self.semantic_model = None
        self._load_semantic_model()

        # HYBRID SYSTEM: Initialize API adapters
        self.google_cse = GoogleCSEAdapter() if settings.USE_GOOGLE_CSE else None
        self.ebay_adapter = EbayAdapter() if settings.USE_EBAY_API else None

        logger.info("parts_search_engine_init",
                   semantic_enabled=self.semantic_model is not None,
                   google_cse_enabled=self.google_cse is not None,
                   ebay_enabled=self.ebay_adapter is not None)

    def _load_semantic_model(self):
        """Load sentence-transformer model for semantic search"""
        # Disabled for now due to compatibility issues
        logger.info("semantic_search_disabled", message="Semantic search disabled, using full-text search only")
        self.semantic_model = None

    def search(
        self,
        db: Session,
        query: str,
        vehicle: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        singapore_only: bool = True
    ) -> Dict[str, Any]:
        """
        Search for automotive parts

        Args:
            db: Database session
            query: Search query text
            vehicle: Optional vehicle context (make, model, year)
            limit: Maximum results to return
            filters: Optional filters (price range, brand, condition, etc.)
            use_cache: Whether to use cached results
            singapore_only: Filter for Singapore availability

        Returns:
            Dictionary with search results and metadata
        """
        start_time = datetime.utcnow()

        logger.info("parts_search_start",
                   query=query,
                   vehicle=vehicle,
                   limit=limit,
                   singapore_only=singapore_only)

        # Check cache first
        if use_cache:
            cached = self._get_cached_results(db, query, vehicle)
            if cached:
                logger.info("parts_search_cache_hit", query=query)
                return cached

        # Perform multi-stage search
        results = []

        # Stage 1: PostgreSQL full-text search
        fts_results = self._fulltext_search(db, query, limit * 2)  # Get more for filtering
        results.extend(fts_results)

        # Stage 2: Semantic search (if model available and not enough results)
        if self.semantic_model and len(results) < limit:
            semantic_results = self._semantic_search(db, query, limit * 2)
            results.extend(semantic_results)

        # Remove duplicates
        results = self._deduplicate_results(results)

        # Stage 2.5: HYBRID SYSTEM - Query external APIs if insufficient local results
        sources_queried = ["local_db"]
        if len(results) < limit:
            external_results = self._query_external_apis(db, query, vehicle, limit)
            results.extend(external_results)
            results = self._deduplicate_results(results)

            if self.google_cse:
                sources_queried.append("google_cse")
            if self.ebay_adapter:
                sources_queried.append("ebay")

        # Stage 3: Apply compatibility filtering if vehicle provided
        if vehicle:
            results = self._filter_by_compatibility(db, results, vehicle)

        # Stage 4: Apply additional filters
        if filters:
            results = self._apply_filters(db, results, filters)

        # Stage 5: Filter for Singapore if requested
        if singapore_only:
            results = self._filter_singapore(db, results)

        # Stage 6: Rank and score results
        results = self._rank_results(results, query, vehicle)

        # Limit results
        results = results[:limit]

        # Prepare response
        response = {
            "query": query,
            "vehicle": vehicle,
            "total_results": len(results),
            "results": results,
            "processing_time_ms": int((datetime.utcnow() - start_time).total_seconds() * 1000),
            "filters_applied": filters or {},
            "singapore_only": singapore_only,
            "sources_queried": sources_queried  # HYBRID SYSTEM: Track which sources were used
        }

        # Cache results
        if use_cache and results:
            self._cache_results(db, query, vehicle, response, sources_queried)

        logger.info("parts_search_complete",
                   query=query,
                   results_count=len(results),
                   processing_time_ms=response["processing_time_ms"])

        return response

    def _fulltext_search(
        self,
        db: Session,
        query: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        PostgreSQL full-text search on parts catalog

        Args:
            db: Database session
            query: Search query
            limit: Max results

        Returns:
            List of matching parts
        """
        try:
            # Use PostgreSQL full-text search with ts_vector
            sql = text("""
                SELECT
                    id,
                    part_number,
                    source,
                    source_id,
                    name,
                    description,
                    category,
                    brand,
                    oem_or_aftermarket,
                    condition,
                    ts_rank(
                        to_tsvector('english', name || ' ' || COALESCE(description, '')),
                        plainto_tsquery('english', :query)
                    ) as rank
                FROM parts_catalog
                WHERE to_tsvector('english', name || ' ' || COALESCE(description, ''))
                    @@ plainto_tsquery('english', :query)
                ORDER BY rank DESC
                LIMIT :limit
            """)

            result = db.execute(sql, {"query": query, "limit": limit})
            rows = result.fetchall()

            parts = []
            for row in rows:
                parts.append({
                    "id": row[0],
                    "part_number": row[1],
                    "source": row[2],
                    "source_id": row[3],
                    "name": row[4],
                    "description": row[5],
                    "category": row[6],
                    "brand": row[7],
                    "oem_or_aftermarket": row[8],
                    "condition": row[9],
                    "relevance_score": float(row[10]) if row[10] else 0.0,
                    "search_method": "fulltext"
                })

            logger.info("fulltext_search", query=query, results=len(parts))
            return parts

        except Exception as e:
            logger.error("fulltext_search_error", error=str(e))
            return []

    def _semantic_search(
        self,
        db: Session,
        query: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Semantic search using sentence transformers

        Args:
            db: Database session
            query: Search query
            limit: Max results

        Returns:
            List of semantically similar parts
        """
        if not self.semantic_model:
            return []

        try:
            # Get query embedding
            query_embedding = self.semantic_model.encode([query])[0]

            # Get all parts (TODO: optimize with vector database in production)
            parts = db.query(PartsCatalog).limit(1000).all()  # Limit for performance

            # Calculate similarities
            similarities = []
            for part in parts:
                # Create text representation of part
                part_text = f"{part.name} {part.description or ''} {part.brand or ''}"
                part_embedding = self.semantic_model.encode([part_text])[0]

                # Calculate cosine similarity
                similarity = np.dot(query_embedding, part_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(part_embedding)
                )

                if similarity > settings.MIN_SEARCH_CONFIDENCE:
                    similarities.append((part, float(similarity)))

            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)

            # Convert to result format
            results = []
            for part, score in similarities[:limit]:
                results.append({
                    "id": part.id,
                    "part_number": part.part_number,
                    "source": part.source,
                    "source_id": part.source_id,
                    "name": part.name,
                    "description": part.description,
                    "category": part.category,
                    "brand": part.brand,
                    "oem_or_aftermarket": part.oem_or_aftermarket,
                    "condition": part.condition,
                    "relevance_score": score,
                    "search_method": "semantic"
                })

            logger.info("semantic_search", query=query, results=len(results))
            return results

        except Exception as e:
            logger.error("semantic_search_error", error=str(e))
            return []

    def _filter_by_compatibility(
        self,
        db: Session,
        results: List[Dict[str, Any]],
        vehicle: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Filter results by vehicle compatibility"""
        filtered = []

        for result in results:
            part_id = result["id"]

            # Check compatibility
            compat = db.query(PartCompatibilityEnhanced).filter(
                and_(
                    PartCompatibilityEnhanced.part_id == part_id,
                    PartCompatibilityEnhanced.make == vehicle.get("make"),
                    PartCompatibilityEnhanced.model == vehicle.get("model"),
                    PartCompatibilityEnhanced.year_start <= vehicle.get("year", 9999),
                    PartCompatibilityEnhanced.year_end >= vehicle.get("year", 0)
                )
            ).first()

            if compat or db.query(PartCompatibilityEnhanced).filter(
                and_(
                    PartCompatibilityEnhanced.part_id == part_id,
                    PartCompatibilityEnhanced.is_universal == True
                )
            ).first():
                result["compatible"] = True
                result["compatibility_confidence"] = float(compat.confidence) if compat and compat.confidence else 1.0
                filtered.append(result)

        logger.info("compatibility_filter",
                   original=len(results),
                   filtered=len(filtered))

        return filtered

    def _apply_filters(
        self,
        db: Session,
        results: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply additional filters to results"""
        filtered = results

        # Price filter
        if "price_min" in filters or "price_max" in filters:
            price_min = filters.get("price_min", 0)
            price_max = filters.get("price_max", float('inf'))

            filtered_with_price = []
            for result in filtered:
                # Get price from database
                price = db.query(PartPrice).filter(
                    PartPrice.part_id == result["id"]
                ).first()

                if price and price_min <= float(price.price) <= price_max:
                    result["price"] = {
                        "value": float(price.price),
                        "currency": price.currency
                    }
                    filtered_with_price.append(result)

            filtered = filtered_with_price

        # Brand filter
        if "brand" in filters:
            filtered = [r for r in filtered if r.get("brand") == filters["brand"]]

        # Condition filter
        if "condition" in filters:
            filtered = [r for r in filtered if r.get("condition") == filters["condition"]]

        # OEM/Aftermarket filter
        if "oem_only" in filters and filters["oem_only"]:
            filtered = [r for r in filtered if r.get("oem_or_aftermarket") == "oem"]

        logger.info("filters_applied",
                   original=len(results),
                   filtered=len(filtered),
                   filters=filters)

        return filtered

    def _filter_singapore(
        self,
        db: Session,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter for parts available in Singapore"""
        singapore_results = []

        for result in results:
            # Get pricing info
            prices = db.query(PartPrice).filter(
                PartPrice.part_id == result["id"]
            ).all()

            # Check if any seller ships to Singapore
            for price in prices:
                if price.ships_to_singapore:
                    result["singapore_available"] = True
                    result["price"] = {
                        "value": float(price.price),
                        "currency": price.currency,
                        "seller": price.seller_name
                    }
                    singapore_results.append(result)
                    break

        logger.info("singapore_filter",
                   original=len(results),
                   singapore=len(singapore_results))

        return singapore_results

    def _rank_results(
        self,
        results: List[Dict[str, Any]],
        query: str,
        vehicle: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rank results by multiple factors"""
        for result in results:
            score = result.get("relevance_score", 0.0)

            # Boost if compatible
            if result.get("compatible"):
                score *= 1.5

            # Boost if Singapore available
            if result.get("singapore_available"):
                score *= 1.3

            # Boost OEM parts slightly
            if result.get("oem_or_aftermarket") == "oem":
                score *= 1.1

            result["final_score"] = score

        # Sort by final score
        results.sort(key=lambda x: x.get("final_score", 0), reverse=True)

        return results

    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate parts"""
        seen = set()
        unique = []

        for result in results:
            key = (result.get("source"), result.get("source_id"))
            if key not in seen:
                seen.add(key)
                unique.append(result)

        return unique

    def _query_external_apis(
        self,
        db: Session,
        query: str,
        vehicle: Optional[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        HYBRID SYSTEM: Query external APIs (Google CSE, eBay) for parts

        Results are automatically stored in database for future searches
        """
        external_results = []

        try:
            # Query Google Custom Search API
            if self.google_cse and settings.USE_GOOGLE_CSE:
                logger.info("querying_google_cse", query=query)
                google_results = self.google_cse.search_parts(query, vehicle)

                # Store results in database
                for result in google_results:
                    stored_part = self._store_external_part(db, result)
                    if stored_part:
                        external_results.append(stored_part)

            # Query eBay API
            if self.ebay_adapter and settings.USE_EBAY_API:
                logger.info("querying_ebay", query=query)
                ebay_results = self.ebay_adapter.search_parts(query, vehicle)

                # Store results in database
                for result in ebay_results:
                    stored_part = self._store_external_part(db, result)
                    if stored_part:
                        external_results.append(stored_part)

            logger.info("external_apis_queried",
                       query=query,
                       google_results=len([r for r in external_results if r.get("source") == "google_cse"]),
                       ebay_results=len([r for r in external_results if r.get("source") == "ebay"]),
                       total=len(external_results))

        except Exception as e:
            logger.error("external_api_query_error", error=str(e))

        return external_results

    def _store_external_part(
        self,
        db: Session,
        part_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Store external API result in database

        Prevents duplicate API calls by caching results locally
        """
        try:
            # Check if part already exists
            existing = db.query(PartsCatalog).filter(
                and_(
                    PartsCatalog.source == part_data.get("source"),
                    PartsCatalog.source_id == part_data.get("source_id")
                )
            ).first()

            if existing:
                # Update existing part
                existing.name = part_data.get("name")
                existing.description = part_data.get("description")
                existing.brand = part_data.get("brand")
                existing.condition = part_data.get("condition")
                existing.retrieved_at = datetime.utcnow()
                db.commit()
                part_id = existing.id
            else:
                # Create new part
                part = PartsCatalog(
                    part_number=part_data.get("part_number"),
                    source=part_data.get("source"),
                    source_id=part_data.get("source_id"),
                    name=part_data.get("name"),
                    description=part_data.get("description"),
                    category=None,  # Can be inferred later
                    brand=part_data.get("brand"),
                    oem_or_aftermarket=None,
                    condition=part_data.get("condition"),
                    image_url=part_data.get("image_url"),
                    ships_to_singapore=part_data.get("ships_to_singapore", True),
                    data_source=part_data.get("data_source"),  # HYBRID SYSTEM: Label
                    retrieved_at=datetime.utcnow()
                )
                db.add(part)
                db.flush()
                part_id = part.id

                # Store price information
                if part_data.get("price_sgd"):
                    price = PartPrice(
                        part_id=part_id,
                        currency=part_data.get("currency", "SGD"),
                        price_sgd=part_data.get("price_sgd"),
                        seller_name=part_data.get("seller_name"),
                        seller_rating=part_data.get("seller_rating"),
                        availability=part_data.get("availability", "unknown"),
                        condition=part_data.get("condition"),
                        ships_to_singapore=part_data.get("ships_to_singapore", True),
                        source_url=part_data.get("source_url"),
                        last_updated=datetime.utcnow()
                    )
                    db.add(price)

                db.commit()

            # Return in search result format
            return {
                "id": part_id,
                "part_number": part_data.get("part_number"),
                "source": part_data.get("source"),
                "source_id": part_data.get("source_id"),
                "name": part_data.get("name"),
                "description": part_data.get("description"),
                "brand": part_data.get("brand"),
                "condition": part_data.get("condition"),
                "relevance_score": 0.8,  # External results get default score
                "search_method": "external_api",
                "data_source": part_data.get("data_source")  # HYBRID SYSTEM: Label
            }

        except Exception as e:
            logger.error("store_external_part_error", error=str(e), part_data=part_data)
            db.rollback()
            return None

    def _get_cached_results(
        self,
        db: Session,
        query: str,
        vehicle: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Get cached search results"""
        query_hash = self._hash_query(query, vehicle)

        cached = db.query(SearchCache).filter(
            and_(
                SearchCache.query_hash == query_hash,
                SearchCache.expires_at > datetime.utcnow()
            )
        ).first()

        if cached:
            # Update hit count
            cached.hit_count += 1
            db.commit()

            return cached.results

        return None

    def _cache_results(
        self,
        db: Session,
        query: str,
        vehicle: Optional[Dict[str, Any]],
        results: Dict[str, Any],
        sources_queried: List[str]
    ):
        """Cache search results"""
        try:
            query_hash = self._hash_query(query, vehicle)
            expires_at = datetime.utcnow() + timedelta(seconds=settings.SEARCH_CACHE_TTL)

            cache_entry = SearchCache(
                query_hash=query_hash,
                query_text=query,
                vehicle_make=vehicle.get("make") if vehicle else None,
                vehicle_model=vehicle.get("model") if vehicle else None,
                vehicle_year=vehicle.get("year") if vehicle else None,
                results=results,
                result_count=results.get("total_results", 0),
                sources_queried=sources_queried,  # HYBRID SYSTEM: Track sources
                expires_at=expires_at
            )

            db.add(cache_entry)
            db.commit()

            logger.info("results_cached", query=query, expires_at=expires_at, sources=sources_queried)

        except Exception as e:
            logger.error("cache_error", error=str(e))
            db.rollback()

    def _hash_query(self, query: str, vehicle: Optional[Dict[str, Any]]) -> str:
        """Generate hash for query and vehicle"""
        parts = [query.lower().strip()]

        if vehicle:
            parts.append(vehicle.get("make", "").lower())
            parts.append(vehicle.get("model", "").lower())
            parts.append(str(vehicle.get("year", "")))

        combined = "|".join(parts)
        return hashlib.md5(combined.encode()).hexdigest()


# Singleton instance
_search_engine = None


def get_search_engine() -> PartsSearchEngine:
    """Get or create search engine instance"""
    global _search_engine
    if _search_engine is None:
        _search_engine = PartsSearchEngine()
    return _search_engine
