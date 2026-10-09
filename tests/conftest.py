"""Fixtures use an isolated in-memory database; no application sessions."""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["USE_GOOGLE_CSE"] = "false"
os.environ["USE_EBAY_API"] = "false"
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.models import Base
from app.db.session import get_db
from app.services.external.nhtsa import NHTSAService


@pytest.fixture
def test_db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as db:
        yield db
    engine.dispose()


@pytest.fixture
def client(test_db, monkeypatch):
    async def empty(*args, **kwargs):
        return None
    async def no_recalls(*args, **kwargs):
        return []
    monkeypatch.setattr(NHTSAService, "decode_vin", empty)
    monkeypatch.setattr(NHTSAService, "get_recalls", no_recalls)
    app.dependency_overrides[get_db] = lambda: test_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def mock_vehicle():
    return {"make": "Honda", "model": "Civic", "year": 2015, "trim": "LX"}
