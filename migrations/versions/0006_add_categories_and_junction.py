"""Add categories table and product_categories junction table

Revision ID: 0006_add_categories_and_junction
Revises: 0005_add_missing_product_columns
Create Date: 2025-11-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '0006_add_categories_and_junction'
down_revision = '0005_add_missing_product_columns'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=True, unique=True),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('categories.id'), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
    )
    
    # Create product_categories junction table
    op.create_table(
        'product_categories',
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), primary_key=True),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey('categories.id'), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table('product_categories')
    op.drop_table('categories')

