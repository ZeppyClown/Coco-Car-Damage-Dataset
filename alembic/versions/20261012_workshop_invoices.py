"""Add immutable workshop invoice snapshots without changing record exports."""
from alembic import op
import sqlalchemy as sa

revision = "20261012_invoices"
down_revision = "20261011_auth"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "workshop_invoices",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("workshop_jobs.id"), nullable=False, unique=True),
        sa.Column("revision_id", sa.Uuid(), sa.ForeignKey("workshop_job_revisions.id"), nullable=False),
        sa.Column("number", sa.String(200), nullable=False, unique=True),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("issued_by", sa.String(200), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("html", sa.Text(), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=False),
    )
    op.execute("""CREATE FUNCTION workshop_invoice_immutable() RETURNS trigger
        LANGUAGE plpgsql AS $$ BEGIN
        RAISE EXCEPTION 'Issued invoices cannot change'; END; $$""")
    op.execute("""CREATE TRIGGER workshop_invoice_immutable
        BEFORE UPDATE OR DELETE ON workshop_invoices
        FOR EACH ROW EXECUTE FUNCTION workshop_invoice_immutable()""")


def downgrade():
    op.drop_table("workshop_invoices")
    op.execute("DROP FUNCTION workshop_invoice_immutable()")
