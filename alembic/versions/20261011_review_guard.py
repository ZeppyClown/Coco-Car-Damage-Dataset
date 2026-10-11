"""Reject updates/deletes of reviewed snapshots in PostgreSQL."""
from alembic import op
import sqlalchemy as sa

revision = "20261011_review_guard"
down_revision = "20261011_workshop"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("workshop_job_revisions", sa.Column("source_document_id", sa.Uuid(), nullable=True))
    op.create_foreign_key("fk_workshop_revision_source", "workshop_job_revisions", "workshop_documents", ["source_document_id"], ["id"])
    if op.get_bind().dialect.name == "postgresql":
        op.execute("""UPDATE workshop_job_revisions SET source_document_id=(record->>'source_document_id')::uuid
                      WHERE record->>'source_document_id' IS NOT NULL""")
        op.execute("""
            CREATE FUNCTION reject_workshop_revision_change() RETURNS trigger AS $$
            BEGIN
                RAISE EXCEPTION 'Reviewed revisions cannot change; create a new reviewed version';
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER workshop_revision_immutable
            BEFORE UPDATE OR DELETE ON workshop_job_revisions
            FOR EACH ROW EXECUTE FUNCTION reject_workshop_revision_change();
        """)


def downgrade():
    if op.get_bind().dialect.name == "postgresql":
        op.execute("DROP TRIGGER workshop_revision_immutable ON workshop_job_revisions")
        op.execute("DROP FUNCTION reject_workshop_revision_change()")
    op.drop_constraint("fk_workshop_revision_source", "workshop_job_revisions", type_="foreignkey")
    op.drop_column("workshop_job_revisions", "source_document_id")
