"""Local draft persistence; review/export and authentication are later features."""
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import update, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import WorkshopDocument, WorkshopJob
from app.schemas.workshop import WorkshopDraft, WorkshopDraftUpdate


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
