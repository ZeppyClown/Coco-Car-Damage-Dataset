"""Add isolated workshop source, draft and revision storage."""
from alembic import op
import sqlalchemy as sa

revision = "20261011_workshop"
down_revision = "20261009_complete"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "workshop_documents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("checksum", sa.String(64), nullable=False, unique=True),
        sa.Column("storage_key", sa.String(120), nullable=False, unique=True),
        sa.Column("media_type", sa.String(20), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("data_origin", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("byte_size > 0", name="ck_workshop_document_size"),
        sa.CheckConstraint("data_origin IN ('synthetic_demo', 'private_source')", name="ck_workshop_document_origin"),
        sa.CheckConstraint("media_type IN ('image/jpeg', 'image/png')", name="ck_workshop_document_media"),
    )
    op.create_table(
        "workshop_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("source_document_id", sa.Uuid(), sa.ForeignKey("workshop_documents.id")),
        sa.Column("draft", sa.JSON(), nullable=False),
        sa.Column("draft_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("draft_version >= 1", name="ck_workshop_job_version"),
    )
    op.create_table(
        "workshop_job_revisions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("workshop_jobs.id"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("record", sa.JSON(), nullable=False),
        sa.Column("reviewer", sa.String(200), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("job_id", "version", name="uq_workshop_job_revision"),
        sa.CheckConstraint("version >= 1", name="ck_workshop_revision_version"),
    )


def downgrade():
    op.drop_table("workshop_job_revisions")
    op.drop_table("workshop_jobs")
    op.drop_table("workshop_documents")
