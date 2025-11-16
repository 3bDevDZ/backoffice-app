"""Add customer tables: addresses, contacts, commercial_conditions

Revision ID: 0007_add_customer_tables
Revises: 0006_add_categories_and_junction
Create Date: 2025-11-15 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '0007_add_customer_tables'
down_revision = '0006_add_categories_and_junction'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to customers table
    op.add_column('customers', sa.Column('code', sa.String(length=50), nullable=True))
    op.add_column('customers', sa.Column('phone', sa.String(length=20), nullable=True))
    op.add_column('customers', sa.Column('mobile', sa.String(length=20), nullable=True))
    op.add_column('customers', sa.Column('status', sa.String(length=20), nullable=False, server_default='active'))
    op.add_column('customers', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('customers', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()))
    op.add_column('customers', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()))
    
    # B2B fields
    op.add_column('customers', sa.Column('company_name', sa.String(length=200), nullable=True))
    op.add_column('customers', sa.Column('siret', sa.String(length=14), nullable=True))
    op.add_column('customers', sa.Column('vat_number', sa.String(length=50), nullable=True))
    op.add_column('customers', sa.Column('rcs', sa.String(length=50), nullable=True))
    op.add_column('customers', sa.Column('legal_form', sa.String(length=50), nullable=True))
    
    # B2C fields
    op.add_column('customers', sa.Column('first_name', sa.String(length=100), nullable=True))
    op.add_column('customers', sa.Column('last_name', sa.String(length=100), nullable=True))
    op.add_column('customers', sa.Column('birth_date', sa.Date(), nullable=True))
    
    # Update type column to use 'B2B' or 'B2C' instead of 'Entreprise'/'Particulier'
    # This will be handled by data migration if needed
    
    # Create unique constraint on code
    try:
        op.create_unique_constraint('uq_customers_code', 'customers', ['code'])
    except NotImplementedError:
        # SQLite doesn't support ALTER TABLE ADD CONSTRAINT
        pass
    
    # Create addresses table
    op.create_table(
        'addresses',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('is_default_billing', sa.Boolean(), default=False),
        sa.Column('is_default_delivery', sa.Boolean(), default=False),
        sa.Column('street', sa.String(length=200), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('postal_code', sa.String(length=20), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False, server_default='France'),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
    )
    
    # Create contacts table
    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id'), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('function', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=200), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('mobile', sa.String(length=20), nullable=True),
        sa.Column('is_primary', sa.Boolean(), default=False),
        sa.Column('receives_quotes', sa.Boolean(), default=True),
        sa.Column('receives_invoices', sa.Boolean(), default=False),
        sa.Column('receives_orders', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
    )
    
    # Create commercial_conditions table
    op.create_table(
        'commercial_conditions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('customer_id', sa.Integer(), sa.ForeignKey('customers.id'), nullable=False, unique=True),
        sa.Column('payment_terms_days', sa.Integer(), default=30),
        sa.Column('price_list_id', sa.Integer(), nullable=True),
        sa.Column('default_discount_percent', sa.Numeric(5, 2), default=0),
        sa.Column('credit_limit', sa.Numeric(12, 2), default=0),
        sa.Column('block_on_credit_exceeded', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=func.now(), onupdate=func.now()),
    )
    
    # Create indexes
    try:
        op.create_index('ix_addresses_customer_id', 'addresses', ['customer_id'])
        op.create_index('ix_contacts_customer_id', 'contacts', ['customer_id'])
    except NotImplementedError:
        pass


def downgrade() -> None:
    # Drop indexes
    try:
        op.drop_index('ix_contacts_customer_id', table_name='contacts')
        op.drop_index('ix_addresses_customer_id', table_name='addresses')
    except NotImplementedError:
        pass
    
    # Drop tables
    op.drop_table('commercial_conditions')
    op.drop_table('contacts')
    op.drop_table('addresses')
    
    # Drop unique constraint
    try:
        op.drop_constraint('uq_customers_code', 'customers', type_='unique')
    except NotImplementedError:
        pass
    
    # Remove columns from customers table
    op.drop_column('customers', 'birth_date')
    op.drop_column('customers', 'last_name')
    op.drop_column('customers', 'first_name')
    op.drop_column('customers', 'legal_form')
    op.drop_column('customers', 'rcs')
    op.drop_column('customers', 'vat_number')
    op.drop_column('customers', 'siret')
    op.drop_column('customers', 'company_name')
    op.drop_column('customers', 'updated_at')
    op.drop_column('customers', 'created_at')
    op.drop_column('customers', 'notes')
    op.drop_column('customers', 'status')
    op.drop_column('customers', 'mobile')
    op.drop_column('customers', 'phone')
    op.drop_column('customers', 'code')

