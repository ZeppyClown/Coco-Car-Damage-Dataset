"""add_hybrid_system_fields_to_parts

Revision ID: bed6722d7dce
Revises: 11fc65d41081
Create Date: 2025-12-30 23:12:43.789716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bed6722d7dce'
down_revision: Union[str, None] = '11fc65d41081'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new fields to parts_catalog table
    op.add_column('parts_catalog', sa.Column('image_url', sa.String(1000), nullable=True))
    op.add_column('parts_catalog', sa.Column('ships_to_singapore', sa.Boolean(), nullable=True, server_default='true'))
    op.add_column('parts_catalog', sa.Column('data_source', sa.String(50), nullable=True))
    op.add_column('parts_catalog', sa.Column('retrieved_at', sa.DateTime(), nullable=True))

    # Create indexes for new fields
    op.create_index('ix_parts_catalog_ships_to_singapore', 'parts_catalog', ['ships_to_singapore'])
    op.create_index('ix_parts_catalog_data_source', 'parts_catalog', ['data_source'])

    # Add new fields to part_prices table
    op.add_column('part_prices', sa.Column('price_sgd', sa.Numeric(10, 2), nullable=True))
    op.add_column('part_prices', sa.Column('availability', sa.String(50), nullable=True))
    op.add_column('part_prices', sa.Column('condition', sa.String(50), nullable=True))
    op.add_column('part_prices', sa.Column('source_url', sa.String(1000), nullable=True))
    op.add_column('part_prices', sa.Column('last_updated', sa.DateTime(), nullable=True))

    # Create index for price_sgd
    op.create_index('ix_part_prices_price_sgd', 'part_prices', ['price_sgd'])


def downgrade() -> None:
    # Remove indexes first
    op.drop_index('ix_part_prices_price_sgd', 'part_prices')
    op.drop_index('ix_parts_catalog_data_source', 'parts_catalog')
    op.drop_index('ix_parts_catalog_ships_to_singapore', 'parts_catalog')

    # Remove columns from part_prices
    op.drop_column('part_prices', 'last_updated')
    op.drop_column('part_prices', 'source_url')
    op.drop_column('part_prices', 'condition')
    op.drop_column('part_prices', 'availability')
    op.drop_column('part_prices', 'price_sgd')

    # Remove columns from parts_catalog
    op.drop_column('parts_catalog', 'retrieved_at')
    op.drop_column('parts_catalog', 'data_source')
    op.drop_column('parts_catalog', 'ships_to_singapore')
    op.drop_column('parts_catalog', 'image_url')
