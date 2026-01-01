"""add_parts_tables_phase3

Revision ID: 11fc65d41081
Revises: 
Create Date: 2025-12-30 22:42:24.674432

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11fc65d41081'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Parts catalog table - main parts data from all sources
    op.create_table(
        'parts_catalog',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('part_number', sa.String(100), nullable=False),
        sa.Column('source', sa.String(50), nullable=False),  # ebay, lazada, shopee, etc.
        sa.Column('source_id', sa.String(200), nullable=True),  # ID from source API
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('subcategory', sa.String(100), nullable=True),
        sa.Column('brand', sa.String(100), nullable=True),
        sa.Column('oem_or_aftermarket', sa.String(20), nullable=True),
        sa.Column('condition', sa.String(50), nullable=True),  # new, used, refurbished
        sa.Column('attributes', sa.JSON(), nullable=True),  # flexible attributes
        sa.Column('image_urls', sa.JSON(), nullable=True),  # array of image URLs
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_sync', sa.DateTime(), nullable=True),  # last API sync
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for fast searching
    op.create_index('ix_parts_catalog_part_number', 'parts_catalog', ['part_number'])
    op.create_index('ix_parts_catalog_source', 'parts_catalog', ['source'])
    op.create_index('ix_parts_catalog_source_id', 'parts_catalog', ['source_id'])
    op.create_index('ix_parts_catalog_category', 'parts_catalog', ['category'])
    op.create_index('ix_parts_catalog_brand', 'parts_catalog', ['brand'])

    # Full-text search index on name and description
    op.execute("""
        CREATE INDEX ix_parts_catalog_search
        ON parts_catalog
        USING GIN (to_tsvector('english', name || ' ' || COALESCE(description, '')))
    """)

    # Part prices table - track pricing from different sources/sellers
    op.create_table(
        'part_prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('part_id', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False),  # SGD, USD, etc.
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('original_price', sa.Numeric(10, 2), nullable=True),  # for discounts
        sa.Column('shipping_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('seller_name', sa.String(200), nullable=True),
        sa.Column('seller_rating', sa.Numeric(3, 2), nullable=True),  # 0.00 - 5.00
        sa.Column('in_stock', sa.Boolean(), nullable=True),
        sa.Column('stock_quantity', sa.Integer(), nullable=True),
        sa.Column('ships_to_singapore', sa.Boolean(), nullable=True),
        sa.Column('delivery_days_min', sa.Integer(), nullable=True),
        sa.Column('delivery_days_max', sa.Integer(), nullable=True),
        sa.Column('url', sa.String(1000), nullable=True),
        sa.Column('valid_until', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['part_id'], ['parts_catalog.id'], ondelete='CASCADE')
    )

    op.create_index('ix_part_prices_part_id', 'part_prices', ['part_id'])
    op.create_index('ix_part_prices_currency', 'part_prices', ['currency'])
    op.create_index('ix_part_prices_price', 'part_prices', ['price'])
    op.create_index('ix_part_prices_ships_to_singapore', 'part_prices', ['ships_to_singapore'])

    # Part compatibility table - which parts fit which vehicles
    op.create_table(
        'part_compatibility_enhanced',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('part_id', sa.Integer(), nullable=False),
        sa.Column('make', sa.String(50), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('year_start', sa.Integer(), nullable=False),
        sa.Column('year_end', sa.Integer(), nullable=False),
        sa.Column('trim', sa.String(100), nullable=True),
        sa.Column('engine', sa.String(100), nullable=True),
        sa.Column('transmission', sa.String(50), nullable=True),
        sa.Column('drive_type', sa.String(20), nullable=True),  # FWD, RWD, AWD
        sa.Column('position', sa.String(50), nullable=True),  # front, rear, left, right
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Numeric(3, 2), nullable=True),  # 0.00 - 1.00
        sa.Column('is_universal', sa.Boolean(), default=False),  # fits all vehicles
        sa.Column('source', sa.String(50), nullable=True),  # where compatibility data came from
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['part_id'], ['parts_catalog.id'], ondelete='CASCADE')
    )

    op.create_index('ix_part_compat_part_id', 'part_compatibility_enhanced', ['part_id'])
    op.create_index('ix_part_compat_make', 'part_compatibility_enhanced', ['make'])
    op.create_index('ix_part_compat_model', 'part_compatibility_enhanced', ['model'])
    op.create_index('ix_part_compat_year', 'part_compatibility_enhanced', ['year_start', 'year_end'])
    op.create_index('ix_part_compat_universal', 'part_compatibility_enhanced', ['is_universal'])

    # Search cache table - cache API search results
    op.create_table(
        'search_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('query_hash', sa.String(64), nullable=False),  # MD5 hash of query params
        sa.Column('query_text', sa.String(500), nullable=False),
        sa.Column('vehicle_make', sa.String(50), nullable=True),
        sa.Column('vehicle_model', sa.String(100), nullable=True),
        sa.Column('vehicle_year', sa.Integer(), nullable=True),
        sa.Column('results', sa.JSON(), nullable=False),  # cached results
        sa.Column('result_count', sa.Integer(), nullable=False),
        sa.Column('sources_queried', sa.JSON(), nullable=True),  # which APIs were called
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('hit_count', sa.Integer(), default=0),  # how many times cache was used
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('query_hash')
    )

    op.create_index('ix_search_cache_hash', 'search_cache', ['query_hash'])
    op.create_index('ix_search_cache_expires', 'search_cache', ['expires_at'])
    op.create_index('ix_search_cache_query_text', 'search_cache', ['query_text'])

    # API rate limiting table - track API usage
    op.create_table(
        'api_rate_limits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(50), nullable=False),  # ebay, lazada, shopee
        sa.Column('endpoint', sa.String(200), nullable=False),
        sa.Column('call_count', sa.Integer(), default=0),
        sa.Column('reset_at', sa.DateTime(), nullable=False),
        sa.Column('daily_limit', sa.Integer(), nullable=True),
        sa.Column('remaining', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('ix_api_rate_source', 'api_rate_limits', ['source'])
    op.create_index('ix_api_rate_reset', 'api_rate_limits', ['reset_at'])


def downgrade() -> None:
    op.drop_table('api_rate_limits')
    op.drop_table('search_cache')
    op.drop_table('part_compatibility_enhanced')
    op.drop_table('part_prices')
    op.drop_table('parts_catalog')
