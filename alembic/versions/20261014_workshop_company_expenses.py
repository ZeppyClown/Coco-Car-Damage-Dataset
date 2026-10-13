"""Add workshop details, expenses and a unique job number."""
from alembic import op
import sqlalchemy as sa

revision = "20261014_company_expenses"
down_revision = "20261013_payments"
branch_labels = None
depends_on = None


def upgrade():
    # Earlier jobs keep an empty job_number, so old duplicates do not block this; every job saved from now on is checked.
    op.add_column("workshop_jobs", sa.Column("job_number", sa.String(200)))
    op.create_unique_constraint("uq_workshop_job_number", "workshop_jobs", ["job_number"])
    op.create_table(
        "workshop_company",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("address", sa.String(2000), nullable=False),
        sa.Column("gst_registration_number", sa.String(200)),
        sa.Column("phone", sa.String(200), nullable=False, server_default=""),
        sa.Column("updated_by", sa.String(200), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_workshop_company_single"),
    )
    op.create_table(
        "workshop_expenses",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("spent_on", sa.Date(), nullable=False, index=True),
        sa.Column("supplier", sa.String(200), nullable=False),
        sa.Column("category", sa.String(20), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("supplier_invoice", sa.String(200), nullable=False),
        sa.Column("job_reference", sa.String(200), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("gst", sa.Numeric(12, 2), nullable=False),
        sa.Column("recorded_by", sa.String(200), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("workshop_expenses")
    op.drop_table("workshop_company")
    op.drop_constraint("uq_workshop_job_number", "workshop_jobs", type_="unique")
    op.drop_column("workshop_jobs", "job_number")
