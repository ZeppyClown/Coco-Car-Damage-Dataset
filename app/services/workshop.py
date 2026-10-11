"""Local draft persistence; review/export and authentication are later features."""
from uuid import UUID, uuid4
from hashlib import sha256
from io import BytesIO
import os
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import update, func, select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import Session
from PIL import Image, UnidentifiedImageError

from app.db.models import WorkshopDocument, WorkshopJob
from app.core.config import settings
from app.schemas.workshop import WorkshopDraft, WorkshopDraftUpdate, WorkshopDocumentResponse, DataOrigin


MAX_UPLOAD_BYTES = 8 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000
MAX_IMAGE_DIMENSION = 6000


def storage_directory() -> Path:
    directory = settings.WORKSHOP_STORAGE_DIR.resolve()
    static = (Path(__file__).resolve().parents[1] / "static").resolve()
    if directory == static or static in directory.parents:
        raise HTTPException(status_code=503, detail="Workshop storage must be outside static files")
    return directory


def document_file(document: WorkshopDocument) -> Path:
    directory = storage_directory()
    path = (directory / document.storage_key).resolve()
    if path.parent != directory:
        raise HTTPException(status_code=503, detail="Stored source is unavailable")
    try:
        if path.stat().st_size != document.byte_size or sha256(path.read_bytes()).hexdigest() != document.checksum:
            raise HTTPException(status_code=503, detail="Stored source failed its integrity check")
    except OSError:
        raise HTTPException(status_code=503, detail="Stored source is unavailable") from None
    return path


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
    directory = storage_directory()
    path = directory / (document_id.hex + suffix)
    created = False
    # shortcut: a process crash can orphan a file; reconcile storage during F12.
    try:
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "wb") as output:
            created = True
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        document = WorkshopDocument(
            id=document_id, checksum=checksum, storage_key=path.name, media_type=actual_type,
            byte_size=len(content), data_origin=origin,
        )
        db.add(document)
        db.commit()
    except IntegrityError:
        db.rollback()
        if created:
            path.unlink(missing_ok=True)
        existing = db.scalar(select(WorkshopDocument).where(WorkshopDocument.checksum == checksum))
        if existing is None:
            raise
        return _document_response(existing, origin, True)
    except (SQLAlchemyError, OSError) as error:
        db.rollback()
        if created:
            path.unlink(missing_ok=True)
        if isinstance(error, OSError):
            raise HTTPException(status_code=503, detail="Source storage failed") from None
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


def create_job(db: Session, draft: WorkshopDraft) -> WorkshopJob:
    _validate_source(db, draft)
    job = WorkshopJob(draft=draft.model_dump(mode="json"), source_document_id=draft.source_document_id)
    try:
        db.add(job)
        db.commit()
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
                draft_version=WorkshopJob.draft_version + 1,
                updated_at=func.now(),
            )
            .execution_options(synchronize_session=False)
        )
        if result.rowcount != 1:
            db.rollback()
            raise HTTPException(status_code=409, detail="Draft changed; reload before saving")
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    db.refresh(job)
    return job
