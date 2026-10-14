"""Job sheets: photo, draft, checked versions and the per-job download."""
from uuid import UUID, uuid4
from hashlib import sha256
from io import BytesIO, StringIO
import csv
import re
from datetime import date, datetime, time, timezone
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import update, func, select, or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from PIL import Image, UnidentifiedImageError
from pydantic import ValidationError

from app.db.models import WorkshopDocument, WorkshopJob, WorkshopJobRevision, WorkshopExport
from app.core.config import settings
from app.schemas.workshop import (
    WorkshopDraft, WorkshopDraftUpdate, WorkshopDocumentResponse, DataOrigin,
    WorkshopConfirmRequest, WorkshopReviewedDraft, WorkshopRevisionResponse,
    WorkshopExportResponse,
    WorkshopLookupResult, WorkshopLookupResponse,
)


MAX_UPLOAD_BYTES = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
MAX_IMAGE_DIMENSION = 6000


def storage_directory() -> Path:
    directory = settings.WORKSHOP_STORAGE_DIR.resolve()
    static = (Path(__file__).resolve().parents[1] / "static").resolve()
    if directory == static or static in directory.parents:
        raise HTTPException(status_code=503, detail="Workshop storage must be outside static files")
    return directory


def _stored_bytes(record, label: str) -> bytes:
    """The saved file, checked against its recorded size and checksum. Rows from before files moved into the database
    have no content and are read from the storage folder."""
    content = record.content
    if content is None:
        directory = storage_directory()
        path = (directory / record.storage_key).resolve()
        if path.parent != directory:
            raise HTTPException(status_code=503, detail=f"Stored {label} is unavailable")
        try:
            content = path.read_bytes()
        except OSError:
            raise HTTPException(status_code=503, detail=f"Stored {label} is unavailable") from None
    if len(content) != record.byte_size or sha256(content).hexdigest() != record.checksum:
        raise HTTPException(status_code=503, detail=f"Stored {label} failed its integrity check")
    return content


def document_file(document: WorkshopDocument) -> bytes:
    return _stored_bytes(document, "source")


def get_document(db: Session, document_id: UUID) -> WorkshopDocument:
    document = db.get(WorkshopDocument, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Workshop source not found")
    return document


def _document_response(document: WorkshopDocument, origin: DataOrigin, duplicate: bool):
    if document.data_origin != origin:
        raise HTTPException(status_code=422, detail="Existing source has a different data origin")
    document_file(document)
    return WorkshopDocumentResponse(
        id=document.id, media_type=document.media_type, byte_size=document.byte_size,
        data_origin=document.data_origin, duplicate=duplicate,
    )


def attach_document(db: Session, content: bytes, filename: str, media_type: str, origin: DataOrigin):
    if not content or len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Source must contain 1 byte to 8 MiB")
    try:
        with Image.open(BytesIO(content)) as image:
            actual_type = {"PNG": "image/png", "JPEG": "image/jpeg"}.get(image.format)
            if actual_type is None:
                raise HTTPException(status_code=415, detail="Only JPEG and PNG sources are supported")
            width, height = image.size
            if max(width, height) > MAX_IMAGE_DIMENSION or width * height > MAX_IMAGE_PIXELS:
                raise HTTPException(status_code=413, detail="Source exceeds 6000 pixels per side or 20 megapixels")
            if getattr(image, "n_frames", 1) != 1:
                raise HTTPException(status_code=415, detail="Animated sources are unsupported")
            image.verify()
        with Image.open(BytesIO(content)) as image:
            image.load()
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError):
        raise HTTPException(status_code=422, detail="Source image is corrupt or unsupported") from None
    allowed_suffixes = {"image/png": {".png"}, "image/jpeg": {".jpg", ".jpeg"}}
    if media_type != actual_type or Path(filename).suffix.lower() not in allowed_suffixes[actual_type]:
        raise HTTPException(status_code=415, detail="Filename and content type must match the decoded image")
    checksum = sha256(content).hexdigest()
    existing = db.scalar(select(WorkshopDocument).where(WorkshopDocument.checksum == checksum))
    if existing is not None:
        return _document_response(existing, origin, True)
    document_id = uuid4()
    suffix = ".png" if actual_type == "image/png" else ".jpg"
    # ponytail: photos live in the database (Supabase free: 500 MB, about 60+ photos at the 8 MB limit, far more at
    # phone sizes); move them to object storage if the database fills up.
    try:
        document = WorkshopDocument(
            id=document_id, checksum=checksum, storage_key=document_id.hex + suffix, media_type=actual_type,
            byte_size=len(content), data_origin=origin, content=content,
        )
        db.add(document)
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(select(WorkshopDocument).where(WorkshopDocument.checksum == checksum))
        if existing is None:
            raise
        return _document_response(existing, origin, True)
    except SQLAlchemyError:
        db.rollback()
        raise
    return _document_response(document, origin, False)


def get_job(db: Session, job_id: UUID) -> WorkshopJob:
    job = db.get(WorkshopJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Workshop job not found")
    return job


def _validate_source(db: Session, draft: WorkshopDraft) -> None:
    if draft.source_document_id is None:
        return
    document = db.get(WorkshopDocument, draft.source_document_id)
    if document is None:
        raise HTTPException(status_code=422, detail="Source document does not exist")
    if document.data_origin != draft.data_origin:
        raise HTTPException(status_code=422, detail="Source and draft origins must match")


def number_key(text: str | None) -> str | None:
    """One key per job no. however it is typed: letters and digits only, upper case."""
    return re.sub(r"[^A-Z0-9]", "", (text or "").upper()) or None


def job_number(draft: WorkshopDraft) -> str | None:
    return number_key(draft.job_reference)


def _duplicate_number(draft: WorkshopDraft) -> HTTPException:
    return HTTPException(status_code=409, detail=f"Job no. {draft.job_reference} is already used by another job. "
                         "Use Find job to open it, or give this job a different number.")


def create_job(db: Session, draft: WorkshopDraft) -> WorkshopJob:
    _validate_source(db, draft)
    job = WorkshopJob(draft=draft.model_dump(mode="json"), source_document_id=draft.source_document_id,
                      job_number=job_number(draft))
    try:
        db.add(job)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _duplicate_number(draft) from None
    except SQLAlchemyError:
        db.rollback()
        raise
    db.refresh(job)
    return job


def update_job(db: Session, job_id: UUID, request: WorkshopDraftUpdate) -> WorkshopJob:
    job = get_job(db, job_id)
    if job.draft["data_origin"] != request.draft.data_origin:
        raise HTTPException(status_code=422, detail="A job's data origin cannot be changed")
    _validate_source(db, request.draft)
    try:
        result = db.execute(
            update(WorkshopJob)
            .where(WorkshopJob.id == job_id, WorkshopJob.draft_version == request.expected_version)
            .values(
                draft=request.draft.model_dump(mode="json"),
                source_document_id=request.draft.source_document_id,
                job_number=job_number(request.draft),
                draft_version=WorkshopJob.draft_version + 1,
                updated_at=func.now(),
            )
            .execution_options(synchronize_session=False)
        )
        if result.rowcount != 1:
            db.rollback()
            raise HTTPException(status_code=409, detail="Draft changed; reload before saving")
        db.commit()
    except IntegrityError:
        db.rollback()
        raise _duplicate_number(request.draft) from None
    except SQLAlchemyError:
        db.rollback()
        raise
    db.refresh(job)
    return job


def _revision_response(revision: WorkshopJobRevision) -> WorkshopRevisionResponse:
    reviewed_at = revision.reviewed_at
    # SQLite drops timezone metadata; test/local timestamps are written in UTC.
    if reviewed_at.tzinfo is None:
        reviewed_at = reviewed_at.replace(tzinfo=timezone.utc)
    reviewed_at = reviewed_at.astimezone(timezone.utc)
    return WorkshopRevisionResponse(
        id=revision.id, job_id=revision.job_id, version=revision.version,
        record=revision.record, reviewer=revision.reviewer, reviewer_identity=revision.reviewer_identity, reviewed_at=reviewed_at,
    )


def list_revisions(db: Session, job_id: UUID, limit: int = 20, offset: int = 0):
    get_job(db, job_id)
    revisions = db.scalars(select(WorkshopJobRevision).where(WorkshopJobRevision.job_id == job_id)
                           .order_by(WorkshopJobRevision.version.desc()).limit(limit).offset(offset))
    return [_revision_response(revision) for revision in revisions]


def lookup_jobs(db: Session, *, q: str | None = None, job_id: UUID | None = None,
                customer: str | None = None, vehicle: str | None = None, reference: str | None = None,
                stage: str | None = None, reviewed_from: date | None = None, reviewed_to: date | None = None,
                limit: int = 20, offset: int = 0):
    if reviewed_from and reviewed_to and reviewed_from > reviewed_to:
        raise HTTPException(status_code=422, detail="Reviewed-from date must not be after reviewed-to date")
    latest = select(WorkshopJobRevision.job_id, func.max(WorkshopJobRevision.version).label("version")).group_by(WorkshopJobRevision.job_id).subquery()
    query = select(WorkshopJobRevision, WorkshopJob.draft_version).join(
        latest, (WorkshopJobRevision.job_id == latest.c.job_id) & (WorkshopJobRevision.version == latest.c.version)
    ).join(WorkshopJob, WorkshopJob.id == WorkshopJobRevision.job_id)
    record = WorkshopJobRevision.record
    if job_id is not None:
        query = query.where(WorkshopJobRevision.job_id == job_id)
    for key, value in (("customer_reference", customer), ("vehicle_reference", vehicle), ("job_reference", reference)):
        if value and value.strip():
            query = query.where(record[key].as_string().icontains(value.strip(), autoescape=True))
    if stage:
        query = query.where(record["record_stage"].as_string() == stage)
    if reviewed_from:
        query = query.where(WorkshopJobRevision.reviewed_at >= datetime.combine(reviewed_from, time.min, tzinfo=timezone.utc))
    if reviewed_to:
        query = query.where(WorkshopJobRevision.reviewed_at <= datetime.combine(reviewed_to, time.max, tzinfo=timezone.utc))
    if q and q.strip():
        fields = [record[name].as_string() for name in (
            "job_reference", "customer_reference", "vehicle_reference", "make", "model", "diagram_notes", "diagram_notes_raw", "date_note_raw",
        )]
        if db.get_bind().dialect.name == "postgresql":
            items = func.json_array_elements(record["items"]).table_valued("value")
            item_fields = [items.c.value.op("->>")(name) for name in ("description", "description_raw", "amount_raw")]
        else:
            items = func.json_each(record["items"]).table_valued("value")
            item_fields = [func.json_extract(items.c.value, "$." + name) for name in ("description", "description_raw", "amount_raw")]
        item_match = select(1).select_from(items).where(or_(*(
            field.icontains(q.strip(), autoescape=True) for field in item_fields
        ))).correlate(WorkshopJobRevision).exists()
        query = query.where(or_(*(field.icontains(q.strip(), autoescape=True) for field in fields), item_match))
    matches = db.execute(query.order_by(WorkshopJobRevision.reviewed_at.desc(), WorkshopJobRevision.job_id)
                         .offset(offset).limit(limit + 1)).all()
    results = [WorkshopLookupResult(**_revision_response(revision).model_dump(), draft_version=draft_version,
                                   has_unreviewed_changes=draft_version > revision.version)
               for revision, draft_version in matches[:limit]]
    return WorkshopLookupResponse(results=results, limit=limit, offset=offset, has_more=len(matches) > limit)


def confirm_job(db: Session, job_id: UUID, request: WorkshopConfirmRequest, *, authenticated: bool = False):
    try:
        job = db.scalar(select(WorkshopJob).where(WorkshopJob.id == job_id).with_for_update()
                        .execution_options(populate_existing=True))
        if job is None:
            raise HTTPException(status_code=404, detail="Workshop job not found")
        if job.draft_version != request.expected_version:
            raise HTTPException(status_code=409, detail="Draft changed; reload before confirming")
        existing = db.scalar(select(WorkshopJobRevision).where(
            WorkshopJobRevision.job_id == job_id, WorkshopJobRevision.version == job.draft_version))
        if existing is not None:
            response = _revision_response(existing)
            db.commit()
            return response
        try:
            record = WorkshopReviewedDraft.model_validate(job.draft)
        except ValidationError as error:
            raise HTTPException(status_code=422, detail=[
                {"loc": ["draft", *issue["loc"]], "msg": issue["msg"], "type": issue["type"]}
                for issue in error.errors()
            ]) from None
        if record.diagram_notes is not None and record.manual_provenance is None:
            raise HTTPException(status_code=422, detail="Review of diagram meaning requires stated clarification context in manual provenance")
        _validate_source(db, record)
        if record.source_document_id is not None:
            document_file(get_document(db, record.source_document_id))
        revision = WorkshopJobRevision(
            job_id=job.id, version=job.draft_version, record=record.model_dump(mode="json"),
            source_document_id=record.source_document_id,
            reviewer=request.reviewer, reviewed_at=datetime.now(timezone.utc),
            reviewer_identity="authenticated" if authenticated else "self_reported",
        )
        db.add(revision)
        db.flush()
        response = _revision_response(revision)
        db.commit()
        return response
    except (SQLAlchemyError, HTTPException):
        db.rollback()
        raise


MAPPING_VERSION = "workshop-job-v2"
CSV_COLUMNS = (
    "mapping_version", "output_kind", "job_id", "revision_id", "revision", "data_origin", "record_stage",
    "job_reference", "customer_reference", "vehicle_reference", "make", "model", "currency",
    "line_number", "cancelled", "description", "amount", "description_raw", "amount_raw",
    "diagram_notes", "diagram_notes_raw", "written_total", "written_adjustment", "written_grand_total",
    "date_note_raw", "quotation_date", "date_in", "date_out", "reviewer", "reviewed_at",
    "source_document_id", "manual_provenance",
)


def _csv_cell(value):
    text = "" if value is None else str(value)
    # Prefix dangerous cells without changing the canonical reviewed record.
    if text.startswith(("\t", "\r", "\n")) or text.lstrip().startswith(tuple("=+-@＝＋－＠")):
        return "'" + text
    return text


def job_csv(revision: WorkshopRevisionResponse) -> bytes:
    record = revision.record.model_dump(mode="json")
    common = {name: record.get(name) for name in CSV_COLUMNS}
    common.update(mapping_version=MAPPING_VERSION, output_kind="JOB_LINES",
                  job_id=str(revision.job_id), revision_id=str(revision.id), revision=revision.version,
                  reviewer=revision.reviewer, reviewed_at=revision.reviewed_at.isoformat())
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_COLUMNS, lineterminator="\r\n")
    writer.writeheader()
    for index, item in enumerate(record["items"], 1):
        row = {**common, "line_number": index, "cancelled": "true" if item["cancelled"] else "false",
               "description_raw": item["description_raw"], "amount_raw": item["amount_raw"],
               "description": None if item["cancelled"] else item["description"],
               "amount": None if item["cancelled"] else item["amount"]}
        writer.writerow({key: _csv_cell(value) for key, value in row.items()})
    return output.getvalue().encode("utf-8-sig")


def get_export(db: Session, export_id: UUID) -> WorkshopExport:
    export = db.get(WorkshopExport, export_id)
    if export is None:
        raise HTTPException(status_code=404, detail="Workshop export not found")
    return export


def export_file(export: WorkshopExport) -> bytes:
    return _stored_bytes(export, "job download")


def _export_response(export: WorkshopExport):
    created_at = export.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return WorkshopExportResponse(
        id=export.id, revision_id=export.revision_id, mapping_version=export.mapping_version,
        checksum=export.checksum, byte_size=export.byte_size, created_at=created_at.astimezone(timezone.utc),
    )


def generate_export(db: Session, revision_id: UUID):
    try:
        revision = db.scalar(select(WorkshopJobRevision).where(WorkshopJobRevision.id == revision_id)
                             .with_for_update().execution_options(populate_existing=True))
        if revision is None:
            raise HTTPException(status_code=404, detail="Reviewed workshop revision not found")
        content = job_csv(_revision_response(revision))
        checksum = sha256(content).hexdigest()
        existing = db.scalar(select(WorkshopExport).where(
            WorkshopExport.revision_id == revision_id, WorkshopExport.mapping_version == MAPPING_VERSION))
        if existing is not None:
            if existing.checksum != checksum:
                raise HTTPException(status_code=503, detail="Download layout no longer matches its recorded output")
            export_file(existing)
            response = _export_response(existing)
            db.commit()
            return response
        export_id = uuid4()
        export = WorkshopExport(id=export_id, revision_id=revision_id, mapping_version=MAPPING_VERSION,
                                checksum=checksum, storage_key=export_id.hex + ".csv", byte_size=len(content), content=content)
        db.add(export)
        db.flush()
        response = _export_response(export)
        db.commit()
        return response
    except (SQLAlchemyError, HTTPException):
        db.rollback()
        raise
