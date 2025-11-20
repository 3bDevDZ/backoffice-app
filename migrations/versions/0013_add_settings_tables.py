"""Add settings tables for company and application configuration

Revision ID: 0013_add_settings_tables
Revises: 0012_add_missing_stock_transfer_tables
Create Date: 2025-01-20
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '0013_add_settings_tables'
down_revision = '0012_add_missing_stock_transfer_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create company_settings table
    op.create_table(
        'company_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False, server_default='CommerceFlow'),
        sa.Column('legal_name', sa.String(length=200), nullable=True),
        sa.Column('siret', sa.String(length=14), nullable=True),
        sa.Column('vat_number', sa.String(length=50), nullable=True),
        sa.Column('rcs', sa.String(length=50), nullable=True),
        sa.Column('legal_form', sa.String(length=50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True, server_default='France'),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.Column('logo_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()),
        sa.PrimaryKeyConstraint('id', name='pk_company_settings')
    )
    
    # Create app_settings table
    op.create_table(
        'app_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stock_management_mode', sa.String(length=20), nullable=False, server_default='simple'),
        sa.Column('default_currency', sa.String(length=3), nullable=False, server_default='EUR'),
        sa.Column('default_tax_rate', sa.Numeric(precision=5, scale=2), nullable=True, server_default=sa.text('20.00')),
        sa.Column('default_language', sa.String(length=5), nullable=False, server_default='fr'),
        sa.Column('invoice_prefix', sa.String(length=10), nullable=True, server_default='INV'),
        sa.Column('invoice_footer', sa.Text(), nullable=True),
        sa.Column('purchase_order_prefix', sa.String(length=10), nullable=True, server_default='PO'),
        sa.Column('receipt_prefix', sa.String(length=10), nullable=True, server_default='REC'),
        sa.Column('quote_prefix', sa.String(length=10), nullable=True, server_default='QUO'),
        sa.Column('quote_validity_days', sa.Integer(), nullable=True, server_default=sa.text('30')),
        sa.Column('email_notifications_enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('email_order_confirmation', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('email_invoice_sent', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()),
        sa.PrimaryKeyConstraint('id', name='pk_app_settings')
    )


def downgrade() -> None:
    op.drop_table('app_settings')
    op.drop_table('company_settings')

