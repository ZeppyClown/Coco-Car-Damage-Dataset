import httpx
import pytest
from app.services.external.nhtsa import NHTSAService
from app.db.models import Vehicle

@pytest.mark.asyncio
async def test_supported_recalls_url_and_errors_propagate(monkeypatch):
    original = httpx.AsyncClient
    calls = []
    def handle(request):
        calls.append(request)
        return httpx.Response(200, json={'results': [{'NHTSACampaignNumber': 'fixture'}]})
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kwargs: original(transport=httpx.MockTransport(handle), **kwargs))
    result = await NHTSAService().get_recalls_by_make_model_year('Honda', 'Accord', 2003)
    assert result[0]['NHTSACampaignNumber'] == 'fixture'
    assert str(calls[0].url).startswith('https://api.nhtsa.gov/recalls/recallsByVehicle?')
    assert calls[0].url.params['modelYear'] == '2003'
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kwargs: original(transport=httpx.MockTransport(lambda request: httpx.Response(503)), **kwargs))
    with pytest.raises(httpx.HTTPStatusError):
        await NHTSAService().get_recalls_by_make_model_year('Honda', 'Accord', 2003)

@pytest.mark.asyncio
async def test_invalid_vpic_decode_is_not_a_vehicle(monkeypatch):
    original = httpx.AsyncClient
    rows = [{'Variable': 'Make', 'Value': 'HONDA'}, {'Variable': 'Model', 'Value': 'Accord'},
            {'Variable': 'Model Year', 'Value': '2003'}, {'Variable': 'Error Code', 'Value': '7'}]
    monkeypatch.setattr(httpx, 'AsyncClient', lambda **kwargs: original(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json={'Count': 4, 'Results': rows})), **kwargs))
    assert await NHTSAService().decode_vin('AAAAAAAAAAAAAAAAA') is None


def test_recalls_failure_is_unknown_not_an_empty_clearance(client, test_db, monkeypatch):
    test_db.add(Vehicle(vin='1HGCM82633A004352', make='Honda', model='Accord', year=2003))
    test_db.commit()
    async def unavailable(*args):
        raise RuntimeError('private-provider-detail')
    monkeypatch.setattr(NHTSAService, 'get_recalls_by_make_model_year', unavailable)
    result = client.get('/api/v1/specifications/1HGCM82633A004352')
    assert result.status_code == 502
    assert 'unknown' in result.text and 'private-provider-detail' not in result.text


def test_forced_spec_refresh_updates_vehicle_and_is_idempotent(client, test_db, monkeypatch):
    from app.db.models import Specification
    vehicle = Vehicle(vin='1HGCM82633A004352', make='Wrong', model='Wrong', year=2015)
    test_db.add(vehicle)
    test_db.flush()
    test_db.add(Specification(vehicle_id=vehicle.id, spec_type='engine', spec_key='obsolete', spec_value='old'))
    test_db.add(Specification(vehicle_id=vehicle.id, spec_type='owner_note', spec_key='note', spec_value='preserve'))
    test_db.commit()
    async def decode(*args):
        return {'make': 'Honda', 'model': 'Accord', 'year': '2003', 'engine': {'type': 'test'}, 'safety': {'abs': 'test'}}
    monkeypatch.setattr(NHTSAService, 'decode_vin', decode)
    for _ in range(2):
        response = client.get('/api/v1/specifications/1HGCM82633A004352?use_cache=false')
        assert response.status_code == 200
        assert response.json()['vehicle']['year'] == 2003
        assert response.json()['metadata']['vin_recall_completion_status'] == 'not_checked'
    assert test_db.query(Specification).filter_by(vehicle_id=vehicle.id).count() == 3
    cached = client.get('/api/v1/specifications/1HGCM82633A004352').json()
    assert cached['specifications']['safety']['abs'] == 'test'
    assert 'obsolete' not in cached['specifications']['engine']
