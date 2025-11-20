"""Add multi-location tables: sites, stock_transfers, stock_transfer_lines and extend locations, stock_items with site_id

Revision ID: 0010_add_multi_location_tables
Revises: 0009_add_stock_tables
Create Date: 2025-11-18
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '0010_add_multi_location_tables'
down_revision = '0009_add_stock_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sites table
    op.create_table(
        'sites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('manager_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()),
        sa.ForeignKeyConstraint(['manager_id'], ['users.id'], name='fk_sites_manager_id'),
        sa.PrimaryKeyConstraint('id', name='pk_sites'),
        sa.UniqueConstraint('code', name='uq_sites_code')
    )
    
    # Add site_id column to locations table
    op.add_column('locations', sa.Column('site_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_locations_site_id',
        'locations', 'sites',
        ['site_id'], ['id']
    )
    
    # Add site_id column to stock_items table
    op.add_column('stock_items', sa.Column('site_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_stock_items_site_id',
        'stock_items', 'sites',
        ['site_id'], ['id']
    )
    
    # Create stock_transfers table
    op.create_table(
        'stock_transfers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.String(length=50), nullable=False),
        sa.Column('source_site_id', sa.Integer(), nullable=False),
        sa.Column('destination_site_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default=sa.text("'created'")),
        sa.Column('requested_date', sa.DateTime(), nullable=True),
        sa.Column('shipped_date', sa.DateTime(), nullable=True),
        sa.Column('received_date', sa.DateTime(), nullable=True),
        sa.Column('shipped_by', sa.Integer(), nullable=True),
        sa.Column('received_by', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()),
        sa.ForeignKeyConstraint(['source_site_id'], ['sites.id'], name='fk_stock_transfers_source_site_id'),
        sa.ForeignKeyConstraint(['destination_site_id'], ['sites.id'], name='fk_stock_transfers_destination_site_id'),
        sa.ForeignKeyConstraint(['shipped_by'], ['users.id'], name='fk_stock_transfers_shipped_by'),
        sa.ForeignKeyConstraint(['received_by'], ['users.id'], name='fk_stock_transfers_received_by'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_stock_transfers_created_by'),
        sa.PrimaryKeyConstraint('id', name='pk_stock_transfers'),
        sa.UniqueConstraint('number', name='uq_stock_transfers_number')
    )
    op.create_index('ix_stock_transfers_number', 'stock_transfers', ['number'])
    
    # Create stock_transfer_lines table
    op.create_table(
        'stock_transfer_lines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transfer_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('variant_id', sa.Integer(), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column('quantity_received', sa.Numeric(precision=12, scale=3), nullable=False, server_default=sa.text('0')),
        sa.Column('sequence', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['transfer_id'], ['stock_transfers.id'], name='fk_stock_transfer_lines_transfer_id'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='fk_stock_transfer_lines_product_id'),
        sa.ForeignKeyConstraint(['variant_id'], ['product_variants.id'], name='fk_stock_transfer_lines_variant_id'),
        sa.PrimaryKeyConstraint('id', name='pk_stock_transfer_lines')
    )


def downgrade() -> None:
    # Drop stock_transfer_lines table
    op.drop_table('stock_transfer_lines')
    
    # Drop stock_transfers table
    op.drop_index('ix_stock_transfers_number', table_name='stock_transfers')
    op.drop_table('stock_transfers')
    
    # Remove site_id column from stock_items
    op.drop_constraint('fk_stock_items_site_id', 'stock_items', type_='foreignkey')
    op.drop_column('stock_items', 'site_id')
    
    # Remove site_id column from locations
    op.drop_constraint('fk_locations_site_id', 'locations', type_='foreignkey')
    op.drop_column('locations', 'site_id')
    
    # Drop sites table
    op.drop_table('sites')


