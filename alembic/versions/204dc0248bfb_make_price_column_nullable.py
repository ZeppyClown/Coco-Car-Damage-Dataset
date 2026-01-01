"""make_price_column_nullable

Revision ID: 204dc0248bfb
Revises: bed6722d7dce
Create Date: 2025-12-30 23:13:22.365126

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '204dc0248bfb'
down_revision: Union[str, None] = 'bed6722d7dce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make price column nullable since we now use price_sgd as primary
    op.alter_column('part_prices', 'price',
               existing_type=sa.Numeric(10, 2),
               nullable=True)


def downgrade() -> None:
    # Revert price column to NOT NULL
    op.alter_column('part_prices', 'price',
               existing_type=sa.Numeric(10, 2),
               nullable=False)
