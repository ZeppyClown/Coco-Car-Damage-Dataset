"""Distinguish verified account attribution from older self-reported reviewers."""
from alembic import op
import sqlalchemy as sa

revision = "20261011_auth"
down_revision = "20261011_exports"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("workshop_job_revisions", sa.Column("reviewer_identity", sa.String(20), nullable=False, server_default="self_reported"))
    op.create_check_constraint("ck_workshop_reviewer_identity", "workshop_job_revisions", "reviewer_identity IN ('self_reported', 'authenticated')")


def downgrade():
    op.drop_constraint("ck_workshop_reviewer_identity", "workshop_job_revisions", type_="check")
    op.drop_column("workshop_job_revisions", "reviewer_identity")
