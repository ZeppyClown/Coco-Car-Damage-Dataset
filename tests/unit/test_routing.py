from app.api.v1 import query
from app.services.entity_extractor import EntityExtractor
from app.services.external.nhtsa import NHTSAService


def test_seven_routes_and_request_id(client):
    paths = client.get("/openapi.json").json()["paths"]
    assert len([path for path in paths if path.startswith("/api/v1/")]) == 7
    assert client.get("/health").headers["x-request-id"]


def route_intent(monkeypatch, intent):
    class Service:
        def process_query(self, text):
            return {"intent": intent, "confidence": 1.0, "entities": EntityExtractor().extract(text)}
    monkeypatch.setattr(query, "get_query_service", Service)


def test_valuation_zero_mileage_executes(client, monkeypatch):
    route_intent(monkeypatch, "vehicle_valuation")
    data = client.post("/api/v1/query", data={"text": "2018 Toyota Camry with 0 km"}).json()
    assert data["success"] and data["result"]["module_executed"] == "valuation_service"
    assert data["metadata"]["entities"]["year"] == 2018
    assert data["result"]["comparable_listings"] == []


def test_parts_dispatch_calls_search(client, monkeypatch):
    route_intent(monkeypatch, "parts_identification")
    calls = []
    class Engine:
        def search(self, **kwargs):
            calls.append(kwargs)
            return {"results": [], "total_results": 0}
    monkeypatch.setattr(query, "get_search_engine", Engine)
    data = client.post("/api/v1/query", data={"text": "Find brake pads for 2015 Honda Civic"}).json()
    assert data["success"] and calls[0]["vehicle"]["year"] == 2015
    assert "functionality ready" not in str(data)


def test_specs_dispatch_requires_and_uses_vin(client, monkeypatch):
    route_intent(monkeypatch, "specifications")
    missing = client.post("/api/v1/query", data={"text": "specs 2015 Honda Civic"}).json()
    assert missing["result"]["missing_fields"] == ["VIN"]
    async def decode(*args):
        return {"make": "Honda", "model": "Civic", "year": "2015", "engine": {"type": "2.0L"}}
    monkeypatch.setattr(NHTSAService, "decode_vin", decode)
    data = client.post("/api/v1/query", data={"text": "specs VIN 1HGCM82633A004352"}).json()
    assert data["result"]["specifications"]["engine"]["type"] == "2.0L"


def test_query_length_and_negative_mileage_rejected(client):
    assert client.post("/api/v1/query", data={"text": "A" * 4001}).status_code == 422
    assert client.post("/api/v1/valuation/estimate", json={"vehicle": {"make": "Honda", "model": "Civic", "year": 2015},
        "mileage": -1, "condition": "good"}).status_code == 422
