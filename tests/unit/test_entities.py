import pytest
from app.services.entity_extractor import EntityExtractor


@pytest.mark.parametrize("text,expected", [
    ("2018 Honda Civic with 75k km", {"year": 2018, "make": "Honda", "model": "Civic", "mileage": 75000}),
    ("Toyota Camry 75,000 km", {"mileage": 75000}),
    ("Toyota Camry 75000km", {"mileage": 75000}),
    ("Toyota Camry 0 km", {"mileage": 0}),
    ("Toyota Camry 7.5k km", {"mileage": 7500}),
    ("Toyota Camry 100 miles", {"mileage": 161}),
    ("Mercedes-Benz C-Class p0300 P0420 p0300", {"make": "Mercedes-Benz", "model": "C-Class", "fault_codes": ["P0300", "P0420"]}),
    ("Land Rover 2019", {"make": "Land Rover", "year": 2019}),
    ("vin 1hgcm82633a004352", {"vin": "1HGCM82633A004352"}),
    ("code p0a80", {"fault_codes": ["P0A80"]}),
])
def test_typed_entities(text, expected):
    result = EntityExtractor().extract(text)
    assert all(result[key] == value for key, value in expected.items())


@pytest.mark.parametrize("text", ["N52 engine", "75k", "part ABC2018DEF", "-50 km", "code P0300", "2007 BMW"])
def test_no_invented_distance(text):
    assert "mileage" not in EntityExtractor().extract(text)
