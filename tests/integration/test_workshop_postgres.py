"""Real migrations/transactions, only in random schemas of a local yap_test DB."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess
from threading import Barrier
from uuid import uuid4

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from fastapi import HTTPException
import pytest
from sqlalchemy import create_engine, inspect, select, text, Table, MetaData
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy.orm import Session

from app.db.models import Base, Vehicle, WorkshopJob, WorkshopJobRevision
from app.schemas.workshop import WorkshopDraft, WorkshopDraftUpdate, WorkshopConfirmRequest
from app.services.workshop import create_job, get_job, update_job
from app.services.workshop import attach_document, confirm_job, list_revisions
from app.services.workshop import get_document, document_file, get_export
from app.core.config import settings
from app.db.models import WorkshopDocument
from app.db.models import WorkshopExport
from app.services.workshop import generate_export, export_file, lookup_jobs


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
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
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
        assert connection.scalar(text("SELECT version_num FROM alembic_version")) == ScriptDirectory.from_config(Config("alembic.ini")).get_current_head()
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


def test_concurrent_identical_sources_reuse_one_row_and_file(workshop_postgres, tmp_path, monkeypatch):
    engine = workshop_postgres
    migrate(engine)
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", tmp_path / "sources")
    content = (Path(__file__).parents[1] / "fixtures/workshop/synthetic-sheet.png").read_bytes()
    barrier = Barrier(2)
    def attach(_):
        with Session(engine) as db:
            barrier.wait(timeout=10)
            return attach_document(db, content, "fixture.png", "image/png", "synthetic_demo")
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attach, range(2)))
    assert results[0].id == results[1].id
    assert sorted(result.duplicate for result in results) == [False, True]
    assert len(list(settings.WORKSHOP_STORAGE_DIR.iterdir())) == 1
    with Session(engine) as db:
        assert len(db.scalars(select(WorkshopDocument)).all()) == 1


def reviewed_fixture():
    import json
    data = json.loads((Path(__file__).parents[1] / "fixtures/workshop/examples.json").read_text())
    return WorkshopDraft.model_validate(data["examples"][0]["record"])


def test_simultaneous_confirmation_is_one_immutable_revision(workshop_postgres):
    engine = workshop_postgres
    migrate(engine)
    with Session(engine) as db:
        job_id = create_job(db, reviewed_fixture()).id
    barrier = Barrier(2)
    def confirm(name):
        with Session(engine) as db:
            barrier.wait(timeout=10)
            return confirm_job(db, job_id, WorkshopConfirmRequest(expected_version=1, reviewer=name, acknowledged=True))
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(confirm, ["Fictional A", "Fictional B"]))
    assert results[0].model_dump() == results[1].model_dump()
    with Session(engine) as db:
        revisions = list_revisions(db, job_id)
        assert len(revisions) == 1
        assert revisions[0].record.record_stage == "quote"
    for operation in ("UPDATE workshop_job_revisions SET reviewer='tampered'", "DELETE FROM workshop_job_revisions"):
        with pytest.raises(DBAPIError, match="Reviewed revisions cannot change"):
            with engine.begin() as connection:
                connection.execute(text(operation))
    with Session(engine) as db:
        assert list_revisions(db, job_id)[0].model_dump() == results[0].model_dump()


def test_stale_cached_job_cannot_confirm_and_correction_preserves_history(workshop_postgres):
    engine = workshop_postgres
    migrate(engine)
    draft = reviewed_fixture()
    with Session(engine) as db:
        job_id = create_job(db, draft).id
    with Session(engine) as stale, Session(engine) as other:
        cached = get_job(stale, job_id)
        assert cached.draft_version == 1
        draft.job_reference = "DEMO-CORRECTED"
        update_job(other, job_id, WorkshopDraftUpdate(expected_version=1, draft=draft))
        with pytest.raises(HTTPException) as error:
            confirm_job(stale, job_id, WorkshopConfirmRequest(expected_version=1, reviewer="Fictional", acknowledged=True))
        assert error.value.status_code == 409
        revision = confirm_job(stale, job_id, WorkshopConfirmRequest(expected_version=2, reviewer="Fictional", acknowledged=True))
        assert revision.record.job_reference == "DEMO-CORRECTED"
        draft.job_reference = "DEMO-THIRD"
        update_job(other, job_id, WorkshopDraftUpdate(expected_version=2, draft=draft))
        assert list_revisions(stale, job_id)[0].record.job_reference == "DEMO-CORRECTED"


def test_review_guard_upgrade_preserves_existing_snapshot(workshop_postgres, tmp_path, monkeypatch):
    engine = workshop_postgres
    migrate(engine, "20261011_workshop")
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", tmp_path)
    draft = reviewed_fixture()
    revision_id = uuid4()
    reviewed_at = datetime.now(timezone.utc)
    with Session(engine) as db:
        content = (Path(__file__).parents[1] / "fixtures/workshop/synthetic-sheet.png").read_bytes()
        source = attach_document(db, content, "demo.png", "image/png", "synthetic_demo")
        draft.source_document_id = source.id
        job_id = create_job(db, draft).id
    # Insert using the old table shape; current ORM requires the new source column.
    previous = Table("workshop_job_revisions", MetaData(), autoload_with=engine)
    with engine.begin() as connection:
        connection.execute(previous.insert().values(
            id=revision_id, job_id=job_id, version=1, record=draft.model_dump(mode="json"),
            reviewer="Fictional migration reviewer", reviewed_at=reviewed_at,
        ))
    migrate(engine)
    with Session(engine) as db:
        revision = list_revisions(db, job_id)[0]
        assert revision.id == revision_id and revision.reviewed_at == reviewed_at
        assert revision.record.model_dump(mode="json") == draft.model_dump(mode="json")
        assert revision.reviewer == "Fictional migration reviewer"
        assert db.get(WorkshopJobRevision, revision_id).source_document_id == source.id


def test_detaching_current_source_cannot_delete_reviewed_source(workshop_postgres, tmp_path, monkeypatch):
    engine = workshop_postgres
    migrate(engine)
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", tmp_path)
    content = (Path(__file__).parents[1] / "fixtures/workshop/synthetic-sheet.png").read_bytes()
    with Session(engine) as db:
        source = attach_document(db, content, "demo.png", "image/png", "synthetic_demo")
        draft = reviewed_fixture()
        draft.source_document_id = source.id
        job_id = create_job(db, draft).id
        confirm_job(db, job_id, WorkshopConfirmRequest(expected_version=1, reviewer="Fictional", acknowledged=True))
        draft.source_document_id = None
        update_job(db, job_id, WorkshopDraftUpdate(expected_version=1, draft=draft))
        assert db.scalar(select(WorkshopJobRevision)).source_document_id == source.id
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(WorkshopDocument.__table__.delete().where(WorkshopDocument.id == source.id))
    with Session(engine) as db:
        assert db.get(WorkshopDocument, source.id) is not None


def test_export_migration_and_simultaneous_generation(workshop_postgres, tmp_path, monkeypatch):
    engine = workshop_postgres
    migrate(engine, "20261011_review_guard")
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", tmp_path)
    with Session(engine) as db:
        job_id = create_job(db, reviewed_fixture()).id
        revision = confirm_job(db, job_id, WorkshopConfirmRequest(expected_version=1, reviewer="Fictional", acknowledged=True))
    migrate(engine)
    barrier = Barrier(2)
    def generate(_):
        with Session(engine) as db:
            barrier.wait(timeout=10)
            return generate_export(db, revision.id)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(generate, range(2)))
    assert results[0].model_dump() == results[1].model_dump()
    with Session(engine) as db:
        exports = db.scalars(select(WorkshopExport)).all()
        assert len(exports) == 1 and len(list(tmp_path.iterdir())) == 1
        assert export_file(exports[0]).read_bytes().startswith(b"\xef\xbb\xbf")
        assert list_revisions(db, job_id)[0].model_dump() == revision.model_dump()


def test_postgres_latest_review_lookup_literal_json_and_pagination(workshop_postgres):
    engine = workshop_postgres
    migrate(engine)
    draft = reviewed_fixture()
    draft.customer_reference = "Fictional Same % Name"
    with Session(engine) as db:
        first = create_job(db, draft)
        first_id = first.id
        first_review = confirm_job(db, first_id, WorkshopConfirmRequest(expected_version=1, reviewer="Fictional", acknowledged=True))
        draft.job_reference = "DEMO-SECOND"
        second_id = create_job(db, draft).id
        confirm_job(db, second_id, WorkshopConfirmRequest(expected_version=1, reviewer="Fictional", acknowledged=True))
        create_job(db, WorkshopDraft(data_origin="synthetic_demo", job_reference="DRAFT-ONLY"))
        draft.customer_reference = "Fictional corrected name"
        update_job(db, first_id, WorkshopDraftUpdate(expected_version=1, draft=draft))
        matches = lookup_jobs(db, customer="%", q="filter", limit=1)
        assert matches.has_more and len(matches.results) == 1
        all_results = lookup_jobs(db, customer="%", limit=100).results
        assert {r.job_id for r in all_results} == {first_id, second_id}
        assert next(r for r in all_results if r.job_id == first_id).has_unreviewed_changes
        confirm_job(db, first_id, WorkshopConfirmRequest(expected_version=2, reviewer="Fictional", acknowledged=True))
        assert [r.job_id for r in lookup_jobs(db, customer="%").results] == [second_id]
        assert lookup_jobs(db, q="' OR 1=1 --").results == []
        day = first_review.reviewed_at.date()
        assert len(lookup_jobs(db, reviewed_from=day, reviewed_to=day).results) == 2


def test_disposable_dump_restore_recovers_history_sources_outputs_and_guards(workshop_postgres, tmp_path, monkeypatch):
    if not all(shutil.which(tool) for tool in ("pg_dump", "pg_restore")):
        pytest.skip("PostgreSQL client tools are required for the disposable recovery drill")
    engine = workshop_postgres
    migrate(engine)
    live = tmp_path / "live-private"
    backup_files = tmp_path / "backup-private"
    restored_files = tmp_path / "restored-private"
    monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", live)
    content = (Path(__file__).parents[1] / "fixtures/workshop/synthetic-sheet.png").read_bytes()
    draft = reviewed_fixture()
    with Session(engine) as db:
        source = attach_document(db, content, "fictional.png", "image/png", "synthetic_demo")
        draft.source_document_id = source.id
        job_id = create_job(db, draft).id
        first = confirm_job(db, job_id, WorkshopConfirmRequest(expected_version=1, reviewer="Fictional recovery reviewer", acknowledged=True))
        first_output = generate_export(db, first.id)
        draft.source_document_id = None
        draft.job_reference = "DEMO-RECOVERY-CORRECTION"
        update_job(db, job_id, WorkshopDraftUpdate(expected_version=1, draft=draft))
        second = confirm_job(db, job_id, WorkshopConfirmRequest(expected_version=2, reviewer="Fictional recovery reviewer", acknowledged=True))
        second_output = generate_export(db, second.id)
        expected_job = get_job(db, job_id).draft
        expected_history = [row.model_dump(mode="json") for row in list_revisions(db, job_id)]
        schema = db.scalar(text("SELECT current_schema()"))
    assert schema.startswith("workshop_")
    url = engine.url
    environment = {**os.environ, "PGHOST":url.host, "PGPORT":str(url.port or 5432), "PGDATABASE":url.database,
                   "PGPASSWORD":url.password or "", "PGCONNECT_TIMEOUT":"5", "PGOPTIONS":"-csearch_path=pg_catalog"}
    if url.username:
        environment["PGUSER"] = url.username
    else:
        environment.pop("PGUSER", None)
    dump = tmp_path / "workshop-recovery.dump"
    dump.touch(mode=0o600)
    subprocess.run(["pg_dump", "--format=custom", "--no-owner", "--no-acl", "--schema", schema, "--file", str(dump)],
                   env=environment, check=True, capture_output=True, timeout=30)
    shutil.copytree(live, backup_files)
    engine.dispose()
    archived = schema + "_before_restore"
    admin = create_engine(os.environ["YAP_TEST_POSTGRES_URL"])
    try:
        with admin.begin() as connection:
            connection.execute(text(f'ALTER SCHEMA "{schema}" RENAME TO "{archived}"'))
        subprocess.run(["pg_restore", "--exit-on-error", "--no-owner", "--no-acl", "--dbname", url.database, str(dump)],
                       env=environment, check=True, capture_output=True, timeout=30)
        monkeypatch.setattr(settings, "WORKSHOP_STORAGE_DIR", restored_files)
        with Session(engine) as db:
            with pytest.raises(HTTPException) as missing:
                document_file(get_document(db, source.id))
            assert missing.value.status_code == 503, "A database dump alone is not a source backup"
        shutil.copytree(backup_files, restored_files)
        with Session(engine) as db:
            assert get_job(db, job_id).draft == expected_job and get_job(db, job_id).draft_version == 2
            assert [row.model_dump(mode="json") for row in list_revisions(db, job_id)] == expected_history
            assert document_file(get_document(db, source.id)).read_bytes() == content
            for expected in (first_output, second_output):
                assert generate_export(db, expected.revision_id).model_dump() == expected.model_dump()
                restored = export_file(get_export(db, expected.id))
                assert restored.read_bytes() == (live / restored.name).read_bytes()
            assert len(list(restored_files.iterdir())) == 3
        with engine.connect() as connection:
            assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
            assert connection.scalar(text("SELECT version_num FROM alembic_version")) == ScriptDirectory.from_config(Config("alembic.ini")).get_current_head()
        with pytest.raises(DBAPIError, match="Reviewed revisions cannot change"):
            with engine.begin() as connection:
                connection.execute(text("UPDATE workshop_job_revisions SET reviewer='tampered'"))
        with pytest.raises(IntegrityError):
            with engine.begin() as connection:
                connection.execute(WorkshopDocument.__table__.delete().where(WorkshopDocument.id == source.id))
    finally:
        with admin.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{archived}" CASCADE'))
        admin.dispose()
