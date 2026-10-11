"""Fixtures use an isolated in-memory database; no application sessions."""
import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["USE_GOOGLE_CSE"] = "false"
os.environ["USE_EBAY_API"] = "false"
import pytest
from pydantic import SecretStr
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.models import Base
from app.db.session import get_db
from app.services.external.nhtsa import NHTSAService
from app.core.config import settings
from app.core.workshop_auth import hash_password

TEST_OPERATOR = "fictional-test-operator"
TEST_PASSWORD = "Fictional tests only password 2026"
TEST_PASSWORD_HASH = hash_password(TEST_PASSWORD)


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
    monkeypatch.setattr(settings, "WORKSHOP_AUTH_USERNAME", TEST_OPERATOR)
    monkeypatch.setattr(settings, "WORKSHOP_AUTH_PASSWORD_HASH", SecretStr(TEST_PASSWORD_HASH))
    monkeypatch.setattr(settings, "WORKSHOP_ORIGIN", "http://127.0.0.1")
    async def empty(*args, **kwargs):
        return None
    async def no_recalls(*args, **kwargs):
        return []
    monkeypatch.setattr(NHTSAService, "decode_vin", empty)
    monkeypatch.setattr(NHTSAService, "get_recalls", no_recalls)
    monkeypatch.setattr(NHTSAService, "get_recalls_by_make_model_year", no_recalls)
    app.dependency_overrides[get_db] = lambda: test_db
    try:
        with TestClient(app, base_url="http://127.0.0.1") as client:
            client.auth = (TEST_OPERATOR, TEST_PASSWORD)
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def mock_vehicle():
    return {"make": "Honda", "model": "Civic", "year": 2015, "trim": "LX"}
