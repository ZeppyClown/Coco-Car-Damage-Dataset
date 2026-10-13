"""Add staff logins, keep the blank form picture in the database, and close the tables to hosted data APIs."""
from alembic import op
import sqlalchemy as sa

revision = "20261015_users_hosting"
down_revision = "20261014_company_expenses"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "workshop_users",
        sa.Column("username", sa.String(50), primary_key=True),
        sa.Column("password_hash", sa.String(200), nullable=False),
        sa.Column("role", sa.String(10), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("role IN ('owner', 'staff')", name="ck_workshop_user_role"),
    )
    op.add_column("workshop_company", sa.Column("sheet_template", sa.LargeBinary()))
    connection = op.get_bind()
    if connection.dialect.name == "postgresql":
        # Hosted Postgres services such as Supabase publish every table in the public schema through a web API
        # unless row level security is on. With it on and no policies, only the app's own database login gets in.
        schema = connection.exec_driver_sql("SELECT current_schema()").scalar()
        for table in sa.inspect(connection).get_table_names():
            if table != "alembic_version":
                op.execute(sa.text(f'ALTER TABLE "{schema}"."{table}" ENABLE ROW LEVEL SECURITY'))


def downgrade():
    op.drop_column("workshop_company", "sheet_template")
    op.drop_table("workshop_users")
