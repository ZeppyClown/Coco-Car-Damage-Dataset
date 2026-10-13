"""Add payment and refund entries against issued workshop invoices."""
from alembic import op
import sqlalchemy as sa

revision = "20261013_payments"
down_revision = "20261012_invoices"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "workshop_payments",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("invoice_id", sa.Uuid(), sa.ForeignKey("workshop_invoices.id"), nullable=False, index=True),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("method", sa.String(20), nullable=False),
        sa.Column("paid_on", sa.Date(), nullable=False),
        sa.Column("note", sa.String(500), nullable=False),
        sa.Column("recorded_by", sa.String(200), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("workshop_payments")
