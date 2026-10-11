"""Successful demonstration output identities; no external delivery records."""
from alembic import op
import sqlalchemy as sa

revision = "20261011_exports"
down_revision = "20261011_review_guard"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "workshop_exports",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("revision_id", sa.Uuid(), sa.ForeignKey("workshop_job_revisions.id"), nullable=False),
        sa.Column("mapping_version", sa.String(40), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
        sa.Column("storage_key", sa.String(120), nullable=False, unique=True),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("revision_id", "mapping_version", name="uq_workshop_export_identity"),
        sa.CheckConstraint("byte_size > 0", name="ck_workshop_export_size"),
    )


def downgrade():
    op.drop_table("workshop_exports")
