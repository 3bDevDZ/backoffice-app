"""Add site_id column to stock_items if missing

Revision ID: 0011_add_site_id_to_stock_items
Revises: 0010_add_multi_location_tables
Create Date: 2025-11-20
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0011_add_site_id_to_stock_items'
down_revision = '0010_add_multi_location_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if site_id column exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('stock_items')]
    
    if 'site_id' not in columns:
        # Add site_id column to stock_items table using batch mode for SQLite
        with op.batch_alter_table('stock_items', schema=None) as batch_op:
            batch_op.add_column(sa.Column('site_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                'fk_stock_items_site_id',
                'sites',
                ['site_id'], ['id']
            )
    
    # Check if site_id column exists in locations
    locations_columns = [col['name'] for col in inspector.get_columns('locations')]
    if 'site_id' not in locations_columns:
        # Add site_id column to locations table using batch mode for SQLite
        with op.batch_alter_table('locations', schema=None) as batch_op:
            batch_op.add_column(sa.Column('site_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                'fk_locations_site_id',
                'sites',
                ['site_id'], ['id']
            )


def downgrade() -> None:
    # Remove site_id column from stock_items
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('stock_items')]
    
    if 'site_id' in columns:
        with op.batch_alter_table('stock_items', schema=None) as batch_op:
            batch_op.drop_constraint('fk_stock_items_site_id', type_='foreignkey')
            batch_op.drop_column('site_id')
    
    # Remove site_id column from locations
    locations_columns = [col['name'] for col in inspector.get_columns('locations')]
    if 'site_id' in locations_columns:
        with op.batch_alter_table('locations', schema=None) as batch_op:
            batch_op.drop_constraint('fk_locations_site_id', type_='foreignkey')
            batch_op.drop_column('site_id')

