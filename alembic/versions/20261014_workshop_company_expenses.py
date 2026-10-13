"""Add workshop details, expenses, an invoice counter and a unique job number."""
import re

from alembic import op
import sqlalchemy as sa

revision = "20261014_company_expenses"
down_revision = "20261013_payments"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("workshop_jobs", sa.Column("job_number", sa.String(200)))
    # Give every earlier job its number. Where earlier jobs already share one, the oldest keeps it and the
    # later ones stay empty: they are refused when next saved until someone gives them their own number.
    jobs = sa.table("workshop_jobs", sa.column("id", sa.Uuid()), sa.column("draft", sa.JSON()),
                    sa.column("job_number", sa.String()), sa.column("created_at", sa.DateTime()))
    connection, taken = op.get_bind(), set()
    for job_id, draft in connection.execute(sa.select(jobs.c.id, jobs.c.draft).order_by(jobs.c.created_at, jobs.c.id)).all():
        key = re.sub(r"[^A-Z0-9]", "", str((draft or {}).get("job_reference") or "").upper())
        if key and key not in taken:
            taken.add(key)
            connection.execute(jobs.update().where(jobs.c.id == job_id).values(job_number=key))
    op.create_unique_constraint("uq_workshop_job_number", "workshop_jobs", ["job_number"])
    # Continue each year's invoice numbers after any that already follow the INV-YYYY-NNNN pattern.
    op.create_table("workshop_invoice_counters", sa.Column("year", sa.Integer(), primary_key=True),
                    sa.Column("last", sa.Integer(), nullable=False))
    last: dict[int, int] = {}
    for (number,) in connection.execute(sa.text("SELECT number FROM workshop_invoices")).all():
        match = re.fullmatch(r"INV-(\d{4})-(\d+)", number)
        if match:
            last[int(match[1])] = max(last.get(int(match[1]), 0), int(match[2]))
    for year, value in last.items():
        connection.execute(sa.text("INSERT INTO workshop_invoice_counters (year, last) VALUES (:year, :last)"), {"year": year, "last": value})
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
        sa.Column("job_number", sa.String(200), sa.ForeignKey("workshop_jobs.job_number", onupdate="CASCADE"), index=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("gst", sa.Numeric(12, 2), nullable=False),
        sa.Column("recorded_by", sa.String(200), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("workshop_expenses")
    op.drop_table("workshop_company")
    op.drop_table("workshop_invoice_counters")
    op.drop_constraint("uq_workshop_job_number", "workshop_jobs", type_="unique")
    op.drop_column("workshop_jobs", "job_number")
