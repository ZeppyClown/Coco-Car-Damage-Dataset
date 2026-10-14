"""Keep job-sheet photos and per-job download files in the database, so hosts without a disk do not lose them.
Let the owner remove the made-up example jobs: the PostgreSQL guards on issued invoices and checked revisions now
allow deleting a row only when it belongs to an example job and the app has switched removal on for that transaction."""
from alembic import op
import sqlalchemy as sa

revision = "20261016_files_in_database"
down_revision = "20261015_users_hosting"
branch_labels = None
depends_on = None

EXAMPLE_REVISION = "OLD.record->>'data_origin' = 'synthetic_demo'"
EXAMPLE_INVOICE = ("EXISTS (SELECT 1 FROM workshop_job_revisions r WHERE r.id = OLD.revision_id "
                   "AND r.record->>'data_origin' = 'synthetic_demo')")
SWITCH = "TG_OP = 'DELETE' AND current_setting('workshop.remove_examples', true) = 'on'"


def _guard(name: str, message: str, allow: str | None):
    escape = f"IF {SWITCH} AND {allow} THEN RETURN OLD; END IF; " if allow else ""
    op.execute(f"""CREATE OR REPLACE FUNCTION {name}() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN {escape}RAISE EXCEPTION '{message}'; END; $$""")


def upgrade():
    # Older rows keep content NULL and are still read from the storage folder.
    op.add_column("workshop_documents", sa.Column("content", sa.LargeBinary()))
    op.add_column("workshop_exports", sa.Column("content", sa.LargeBinary()))
    if op.get_bind().dialect.name == "postgresql":
        _guard("workshop_invoice_immutable", "Issued invoices cannot change", EXAMPLE_INVOICE)
        _guard("reject_workshop_revision_change", "Reviewed revisions cannot change; create a new reviewed version", EXAMPLE_REVISION)


def downgrade():
    if op.get_bind().dialect.name == "postgresql":
        _guard("workshop_invoice_immutable", "Issued invoices cannot change", None)
        _guard("reject_workshop_revision_change", "Reviewed revisions cannot change; create a new reviewed version", None)
    op.drop_column("workshop_exports", "content")
    op.drop_column("workshop_documents", "content")
