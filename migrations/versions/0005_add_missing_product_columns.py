"""Add missing product columns

Revision ID: 0005_add_missing_product_columns
Revises: 0004_add_outbox_events
Create Date: 2025-11-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '0005_add_missing_product_columns'
down_revision = '0004_add_outbox_events'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to products table
    # Use batch mode for SQLite compatibility when adding columns
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.add_column(sa.Column("cost", sa.Numeric(12, 2), nullable=True))
        batch_op.add_column(sa.Column("unit_of_measure", sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column("barcode", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), nullable=False, server_default=func.now()))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=func.now()))
    
    # For non-SQLite databases, also create unique constraint on barcode
    try:
        op.create_unique_constraint("uq_products_barcode", "products", ["barcode"])
    except (NotImplementedError, ValueError):
        pass  # SQLite doesn't support this, or constraint already exists


def downgrade() -> None:
    # Remove columns from products table
    with op.batch_alter_table("products", schema=None) as batch_op:
        try:
            batch_op.drop_constraint("uq_products_barcode", type_="unique")
        except (NotImplementedError, ValueError):
            pass  # SQLite doesn't support dropping constraints this way
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")
        batch_op.drop_column("barcode")
        batch_op.drop_column("unit_of_measure")
        batch_op.drop_column("cost")

