"""Real migrations/transactions, only in random schemas of a local yap_test DB."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import os
from threading import Barrier
from uuid import uuid4

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from fastapi import HTTPException
import pytest
from sqlalchemy import create_engine, inspect, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Base, Vehicle, WorkshopJob, WorkshopJobRevision
from app.schemas.workshop import WorkshopDraft, WorkshopDraftUpdate
from app.services.workshop import create_job, get_job, update_job


@pytest.fixture
def workshop_postgres():
    url = os.getenv("YAP_TEST_POSTGRES_URL")
    if not url:
        pytest.skip("Set YAP_TEST_POSTGRES_URL to a disposable local yap_test database")
    parsed = make_url(url)
    assert parsed.get_backend_name() == "postgresql"
    assert parsed.host in {"127.0.0.1", "localhost"} and (parsed.database or "").startswith("yap_test")
    schema = "workshop_" + uuid4().hex
    admin = create_engine(url)
    with admin.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_engine(url, connect_args={"options": f"-csearch_path={schema}"})
    try:
        yield engine
    finally:
        engine.dispose()
        with admin.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        admin.dispose()


def migrate(engine, revision="head"):
    config = Config("alembic.ini")
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, revision)


@pytest.mark.parametrize("previous_head", [False, True], ids=["fresh", "existing"])
def test_additive_migration_alignment_and_existing_data(workshop_postgres, previous_head):
    engine = workshop_postgres
    if previous_head:
        migrate(engine, "20261009_complete")
        with Session(engine) as db:
            db.add(Vehicle(make="Fictional", model="Migration fixture", year=2026))
            db.commit()
    migrate(engine)
    with engine.connect() as connection:
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == "20261011_workshop"
        assert {"workshop_documents", "workshop_jobs", "workshop_job_revisions"} <= set(inspect(connection).get_table_names())
        assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
    if previous_head:
        with Session(engine) as db:
            assert db.scalar(select(Vehicle)).model == "Migration fixture"


def test_draft_survives_new_session_and_stale_update(workshop_postgres):
    engine = workshop_postgres
    migrate(engine)
    draft = WorkshopDraft(data_origin="synthetic_demo", job_reference="DEMO-PG", diagram_notes_raw="示例", written_adjustment="-2.50")
    with Session(engine) as db:
        job = create_job(db, draft)
        job_id = job.id
        assert job.created_at.tzinfo is not None
    with Session(engine) as db:
        restored = get_job(db, job_id)
        assert restored.draft["written_adjustment"] == "-2.50" and restored.draft["diagram_notes_raw"] == "示例"
        draft.job_reference = "DEMO-CORRECTED"
        updated = update_job(db, job_id, WorkshopDraftUpdate(expected_version=1, draft=draft))
        assert updated.draft_version == 2
        with pytest.raises(HTTPException) as error:
            update_job(db, job_id, WorkshopDraftUpdate(expected_version=1, draft=draft))
        assert error.value.status_code == 409
    with Session(engine) as db:
        assert get_job(db, job_id).draft["job_reference"] == "DEMO-CORRECTED"


def test_two_simultaneous_saves_cannot_overwrite(workshop_postgres):
    engine = workshop_postgres
    migrate(engine)
    with Session(engine) as db:
        job_id = create_job(db, WorkshopDraft(data_origin="synthetic_demo")).id
    barrier = Barrier(2)
    def save(reference):
        with Session(engine) as db:
            barrier.wait(timeout=10)
            try:
                update_job(db, job_id, WorkshopDraftUpdate(expected_version=1, draft=WorkshopDraft(data_origin="synthetic_demo", job_reference=reference)))
                return 200, reference
            except HTTPException as error:
                return error.status_code, reference
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(save, ["DEMO-A", "DEMO-B"]))
    assert sorted(status for status, _ in results) == [200, 409]
    winner = next(reference for status, reference in results if status == 200)
    with Session(engine) as db:
        job = get_job(db, job_id)
        assert job.draft_version == 2 and job.draft["job_reference"] == winner


def test_failed_transaction_keeps_no_partial_draft_or_revision(workshop_postgres):
    engine = workshop_postgres
    migrate(engine)
    with Session(engine) as db:
        job_id = create_job(db, WorkshopDraft(data_origin="synthetic_demo", job_reference="DEMO-ORIGINAL")).id
        job = get_job(db, job_id)
        job.draft = {**job.draft, "job_reference": "SHOULD ROLL BACK"}
        db.add(WorkshopJobRevision(job_id=job_id, version=0, record=job.draft, reviewer="Fictional reviewer", reviewed_at=datetime.now(timezone.utc)))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
    with Session(engine) as db:
        assert get_job(db, job_id).draft["job_reference"] == "DEMO-ORIGINAL"
        assert db.scalar(select(WorkshopJobRevision)) is None


def test_revision_identity_and_foreign_key_are_enforced(workshop_postgres):
    engine = workshop_postgres
    migrate(engine)
    with Session(engine) as db:
        job_id = create_job(db, WorkshopDraft(data_origin="synthetic_demo")).id
        values = dict(job_id=job_id, version=1, record={"data_origin": "synthetic_demo"}, reviewer="Fictional DB constraint fixture", reviewed_at=datetime.now(timezone.utc))
        db.add(WorkshopJobRevision(**values))
        db.commit()
        db.add(WorkshopJobRevision(**values))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
        db.add(WorkshopJobRevision(**{**values, "job_id": uuid4()}))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
        assert len(db.scalars(select(WorkshopJobRevision)).all()) == 1
