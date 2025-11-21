import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context

# Import SQLAlchemy Base metadata from the app
from app.infrastructure.db import Base

# Import all models to ensure they are registered with Base.metadata
from app.domain.models.user import User
from app.domain.models.product import Product, ProductVariant, ProductPriceHistory, ProductCostHistory, PriceList, ProductPriceList, ProductVolumePricing, ProductPromotionalPrice
from app.domain.models.category import Category
from app.domain.models.customer import Customer, Address, Contact, CommercialConditions
from app.domain.models.supplier import Supplier, SupplierAddress, SupplierContact, SupplierConditions
from app.domain.models.purchase import PurchaseOrder, PurchaseOrderLine, PurchaseRequest, PurchaseRequestLine, PurchaseReceipt, PurchaseReceiptLine, SupplierInvoice
from app.domain.models.stock import StockItem, StockMovement, Location, Site, StockTransfer, StockTransferLine
from app.domain.models.quote import Quote, QuoteLine, QuoteVersion
from app.domain.models.order import Order, OrderLine, StockReservation
from app.domain.models.invoice import Invoice, InvoiceLine, CreditNote
from app.domain.models.payment import Payment, PaymentAllocation, PaymentReminder
from app.infrastructure.outbox.outbox_event import OutboxEvent

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for 'autogenerate' support.
target_metadata = Base.metadata


def get_connection_url() -> str:
    # Prefer DATABASE_URL env var; fallback to SQLite for local development
    return os.getenv(
        "DATABASE_URL",
        "sqlite:///gmflow.db",
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation we
    keep resources low and only emit SQL to the script.
    """
    url = get_connection_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = create_engine(get_connection_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()