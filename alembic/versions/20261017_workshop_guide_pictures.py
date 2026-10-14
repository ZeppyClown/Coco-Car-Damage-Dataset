"""Keep the paper guide pictures in the database, so the hosted copy (which has no folder) can show them."""
from alembic import op
import sqlalchemy as sa

revision = "20261017_guide_pictures"
down_revision = "20261016_files_in_database"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "workshop_guide_pictures",
        sa.Column("name", sa.String(200), primary_key=True),
        sa.Column("media_type", sa.String(50), nullable=False),
        sa.Column("content", sa.LargeBinary(), nullable=False),
        sa.Column("updated_by", sa.String(200), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    if op.get_bind().dialect.name == "postgresql":
        # Same as every workshop table: no access through Supabase's public data API.
        op.execute("ALTER TABLE workshop_guide_pictures ENABLE ROW LEVEL SECURITY")


def downgrade():
    op.drop_table("workshop_guide_pictures")
