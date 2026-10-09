import pytest
from app.db.models import PartsCatalog, PartPrice, PartCompatibilityEnhanced
from app.services.parts_search import PartsSearchEngine
from app.services.external.parts.google_cse_adapter import GoogleCSEAdapter
from app.services.external.parts.ebay_adapter import EbayAdapter
from app.services.compatibility_checker import CompatibilityChecker


def catalogue(db, engine=None):
    part = PartsCatalog(part_number="REAL-123", name="Brake pads", source="fixture", source_id="123")
    db.add(part)
    db.flush()
    db.add(PartPrice(part_id=part.id, price_sgd=45, price=45, currency="SGD", ships_to_singapore=True))
    db.add(PartCompatibilityEnhanced(part_id=part.id, make="Honda", model="Civic", year_start=2010, year_end=2020,
                                    engine=engine, confidence=0.9))
    db.commit()
    return part


def test_adapter_contract_and_unknown_evidence():
    for adapter in (GoogleCSEAdapter(), EbayAdapter()):
        assert callable(adapter.search_parts) and callable(adapter.get_part_details)
    google = GoogleCSEAdapter()
    result = google._normalize_result({"title": "Brake pad", "link": "https://shopee.sg/item/123", "snippet": "No price"})
    assert result["source_id"]
    assert result["part_number"] == ""
    assert result["price_sgd"] is None
    assert result["ships_to_singapore"] is None
    assert google._normalize_result({"link": "https://shopee.sg.attacker.example/item"}) is None
    result = EbayAdapter()._normalize_result({"itemId": "a", "title": "Brake pad", "price": {"value": "12", "currency": "USD"}})
    assert result["price"] == 12 and result["price_sgd"] is None


def test_engine_constraint_does_not_claim_fit(test_db):
    part = catalogue(test_db, engine="K20")
    checker = CompatibilityChecker()
    result = checker.check_compatibility(test_db, part.id, {"make": "honda", "model": "civic", "year": 2015})
    assert not result["compatible"]
    result = checker.check_compatibility(test_db, part.id, {"make": "honda", "model": "civic", "year": 2015, "engine": "K20"})
    assert result["compatible"]


def test_compatibility_route_and_validation(client, test_db):
    part = catalogue(test_db)
    payload = {"part_id": part.id, "make": "Honda", "model": "Civic", "year": 2015}
    assert client.post("/api/v1/parts/compatibility", json=payload).json()["result"]["compatible"]
    assert client.post("/api/v1/parts/compatibility", json={**payload, "part_id": 999}).status_code == 404
    assert client.post("/api/v1/parts/compatibility", json={**payload, "year": 0}).status_code == 422
    assert client.post("/api/v1/parts/identify", files={"image": ("part.jpg", b"test", "image/jpeg")}).status_code == 501


def test_hash_separates_result_inputs():
    engine = PartsSearchEngine()
    keys = [engine._hash_query("pads", None), engine._hash_query("pads", None, {"brand": "Bosch"}),
            engine._hash_query("pads", None, limit=5), engine._hash_query("pads", None, singapore_only=False)]
    assert len(set(keys)) == 4


def test_external_refresh_keeps_unknown_price_and_is_idempotent(test_db):
    engine = PartsSearchEngine()
    data = {"source": "google_cse", "source_id": "a", "name": "Pads", "source_url": "https://shopee.sg/item", "currency": "SGD"}
    first = engine._store_external_part(test_db, data)
    engine._store_external_part(test_db, {**data, "price_sgd": 20, "ships_to_singapore": True})
    assert test_db.query(PartsCatalog).count() == 1
    assert test_db.query(PartPrice).count() == 1
    assert float(test_db.query(PartPrice).first().price_sgd) == 20
    assert first["id"] == test_db.query(PartsCatalog).first().id


def test_provider_failure_does_not_suppress_other_provider(test_db, monkeypatch):
    engine = PartsSearchEngine()
    monkeypatch.setattr(engine, "_fulltext_search", lambda *args: [])
    class Failed:
        def search_parts(self, *args, **kwargs):
            raise TimeoutError()
    class Working:
        def search_parts(self, *args, **kwargs):
            return [{"source": "ebay", "source_id": "a", "name": "Pads", "currency": "SGD", "price_sgd": 25, "ships_to_singapore": True}]
    engine.google_cse, engine.ebay_adapter = Failed(), Working()
    result = engine.search(test_db, "pads", use_cache=False)
    assert result["sources_failed"] == ["google_cse"]
    assert result["total_results"] == 1


def test_cache_and_fallback_after_fit_filtering(test_db, monkeypatch):
    engine = PartsSearchEngine()
    part = catalogue(test_db, engine="K20")
    monkeypatch.setattr(engine, "_fulltext_search", lambda *args: [engine._result(part, 1)])
    calls = []
    class Provider:
        def search_parts(self, *args, **kwargs):
            calls.append(True)
            return []
    engine.google_cse = Provider()
    engine.search(test_db, "pads", vehicle={"make": "Toyota", "model": "Corolla", "year": 2015})
    assert calls
    engine.google_cse = None
    first = engine.search(test_db, "pads", use_cache=True)
    second = engine.search(test_db, "pads", use_cache=True)
    assert first["total_results"] == 1 and second["cache_hit"]


def test_google_prices_require_explicit_sgd_currency():
    adapter = GoogleCSEAdapter()
    assert adapter._extract_price({"offer": [{"price": "20", "pricecurrency": "USD"}]}, "$20") is None
    assert adapter._extract_price({"offer": [{"price": "20", "pricecurrency": "SGD"}]}, "") == 20
    assert adapter._extract_price({"offer": [{"price": "nan", "pricecurrency": "SGD"}]}, "") is None
    assert adapter._extract_price({}, "SGD 1,200.50") == 1200.5
    assert adapter._extract_price({}, "S$20.00") == 20


def test_parts_failure_does_not_expose_provider_secrets(client, monkeypatch):
    from app.api.v1 import parts
    class Broken:
        def search(self, **kwargs):
            raise RuntimeError("api_key=private-secret")
    monkeypatch.setattr(parts, "get_search_engine", lambda: Broken())
    response = client.post("/api/v1/parts/identify", data={"description": "pads"})
    assert response.status_code == 500
    assert "private-secret" not in response.text
    assert response.headers["X-Request-ID"]


def test_fit_selection_is_case_insensitive(test_db):
    part = catalogue(test_db, engine="K20")
    test_db.add(PartCompatibilityEnhanced(part_id=part.id, make="Honda", model="Civic", year_start=2010,
        year_end=2020, engine="K24", confidence=1.0))
    test_db.commit()
    result = CompatibilityChecker().check_compatibility(test_db, part.id,
        {"make": "Honda", "model": "Civic", "year": 2015, "engine": "k20"}, strict=True)
    assert result["compatible"]


def test_cache_key_changes_when_provider_is_activated():
    engine = PartsSearchEngine()
    engine.google_cse = engine.ebay_adapter = None
    original = engine._hash_query('pads', None)
    engine.ebay_adapter = object()
    assert engine._hash_query('pads', None) != original


def test_identify_price_range_excludes_nonshipping_offer(client, test_db, monkeypatch):
    from app.api.v1 import parts
    part = catalogue(test_db)
    test_db.add(PartPrice(part_id=part.id, price_sgd=10, price=10, currency='SGD', ships_to_singapore=False))
    test_db.commit()
    engine = PartsSearchEngine()
    engine._fulltext_search = lambda *args: [engine._result(part, 0.5)]
    monkeypatch.setattr(parts, 'get_search_engine', lambda: engine)
    response = client.post('/api/v1/parts/identify', data={'description': 'brake pads'})
    assert response.status_code == 200
    assert response.json()['matches'][0]['price_range'] == {'min': 45.0, 'max': 45.0, 'currency': 'SGD'}
