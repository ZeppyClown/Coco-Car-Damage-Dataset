"""Run only against an explicitly supplied local disposable yap_test database."""
import os
from uuid import uuid4
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from app.db.models import Base, PartsCatalog, PartPrice, PartCompatibilityEnhanced
from app.services.parts_search import PartsSearchEngine


@pytest.fixture
def postgres_db():
    url = os.getenv("YAP_TEST_POSTGRES_URL")
    if not url:
        pytest.skip("Set YAP_TEST_POSTGRES_URL to a disposable local yap_test database")
    parsed = make_url(url)
    assert parsed.host in {"127.0.0.1", "localhost"} and parsed.database.startswith("yap_test")
    engine = create_engine(url)
    schema = "build_" + uuid4().hex
    with engine.connect() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        connection.execute(text(f'SET search_path TO "{schema}"'))
        connection.commit()
        Base.metadata.create_all(connection)
        connection.commit()
        with Session(bind=connection) as db:
            yield db
        connection.rollback()
        connection.execute(text('SET search_path TO public'))
        connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        connection.commit()
    engine.dispose()


def test_real_fulltext_fit_price_cache_and_refresh(postgres_db):
    db = postgres_db
    part = PartsCatalog(part_number="FIXTURE", name="Brake pads", description="Ceramic brake pad set",
                        source="fixture", source_id="one", data_source="synthetic")
    db.add(part)
    db.flush()
    db.add(PartPrice(part_id=part.id, price_sgd=45, price=45, currency="SGD", ships_to_singapore=True))
    db.add(PartCompatibilityEnhanced(part_id=part.id, make="Honda", model="Civic", year_start=2010, year_end=2020,
                                    confidence=0.9))
    db.commit()
    engine = PartsSearchEngine()
    result = engine.search(db, "brake pads", vehicle={"make": "honda", "model": "civic", "year": 2015}, limit=1)
    assert result["total_results"] == 1 and result["results"][0]["price"]["value"] == 45
    assert engine.search(db, "brake pads", vehicle={"make": "honda", "model": "civic", "year": 2015}, limit=1)["cache_hit"]
    assert engine.search(db, "brake pads", filters={"price_max": 40})["total_results"] == 0
    assert engine.search(db, "brake pads", vehicle={"make": "Toyota", "model": "Corolla", "year": 2015})["total_results"] == 0
    assert engine.search(db, "unrelated bolt")['total_results'] == 0
