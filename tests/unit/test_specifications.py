"""Tests for specifications endpoint"""

import pytest
from app.db.models import Vehicle, Specification


def test_get_specifications_success(client, test_db):
    """Test getting specifications for a valid VIN"""
    # Setup: Create test data
    db = test_db
    vehicle = Vehicle(
        vin="1HGCM82633A004352",
        make="Test",
        model="Vehicle",
        year=2020,
        trim="Base"
    )
    db.add(vehicle)
    db.commit()

    spec = Specification(
        vehicle_id=vehicle.id,
        spec_type="engine",
        spec_key="type",
        spec_value="2.0L 4-Cylinder"
    )
    db.add(spec)
    db.commit()

    # Test
    response = client.get("/api/v1/specifications/1HGCM82633A004352")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["vin"] == "1HGCM82633A004352"
    assert data["vehicle"]["make"] == "Test"
    assert data["vehicle"]["model"] == "Vehicle"
    assert data["vehicle"]["year"] == 2020
    assert "engine" in data["specifications"]
    assert data["specifications"]["engine"]["type"] == "2.0L 4-Cylinder"

    # Cleanup
    db = test_db
    db.delete(spec)
    db.delete(vehicle)
    db.commit()


def test_get_specifications_invalid_vin_length(client):
    """Test that short VINs are rejected"""
    response = client.get("/api/v1/specifications/SHORT")
    assert response.status_code == 400
    data = response.json()
    assert "VIN must be 17 characters" in data["detail"]


def test_get_specifications_not_found(client):
    """Test getting specifications for non-existent VIN"""
    response = client.get("/api/v1/specifications/1HGCM82633A004353")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()
