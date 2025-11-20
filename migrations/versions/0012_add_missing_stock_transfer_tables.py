"""Add missing stock_transfers and stock_transfer_lines tables

Revision ID: 0012_add_missing_stock_transfer_tables
Revises: 0011_add_site_id_to_stock_items
Create Date: 2025-01-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '0012_add_missing_stock_transfer_tables'
down_revision = '0011_add_site_id_to_stock_items'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if stock_transfers table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    
    if 'stock_transfers' not in existing_tables:
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
    
    if 'stock_transfer_lines' not in existing_tables:
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
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()
    
    if 'stock_transfer_lines' in existing_tables:
        op.drop_table('stock_transfer_lines')
    
    # Drop stock_transfers table
    if 'stock_transfers' in existing_tables:
        op.drop_index('ix_stock_transfers_number', table_name='stock_transfers')
        op.drop_table('stock_transfers')

