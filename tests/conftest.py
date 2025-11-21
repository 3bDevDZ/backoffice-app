"""Pytest configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from datetime import date
from app.infrastructure.db import Base, init_db
from app.domain.models.product import Product
from app.domain.models.category import Category
from app.domain.models.user import User
from app.domain.models.customer import Customer, CommercialConditions
from app.domain.models.supplier import Supplier, SupplierConditions
from app.domain.models.purchase import PurchaseOrder
from app.domain.models.quote import Quote  # Import Quote to ensure table is created
from app.domain.models.order import Order  # Import Order to ensure table is created
from app.domain.models.stock import StockItem, Location, Site  # Import Stock models to ensure tables are created
from app.domain.models.settings import AppSettings, CompanySettings  # Import Settings models to ensure tables are created
from app.domain.models.invoice import Invoice, InvoiceLine  # Import Invoice models to ensure tables are created
from app.domain.models.payment import Payment, PaymentAllocation, PaymentReminder  # Import Payment models to ensure tables are created


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    # Use in-memory SQLite for tests with shared connection
    # This ensures handlers and tests use the same database
    from app.infrastructure.db import init_db
    init_db("sqlite:///:memory:")
    
    from app.infrastructure.db import SessionLocal
    session = SessionLocal()
    
    # Create all tables
    Base.metadata.create_all(session.bind)
    
    yield session
    
    session.close()
    Base.metadata.drop_all(session.bind)


@pytest.fixture
def sample_category(db_session):
    """Create a sample category for testing."""
    category = Category.create(
        name="Test Category",
        code="TEST-CAT",
        description="Test category description"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def sample_product(db_session, sample_category):
    """Create a sample product for testing."""
    from decimal import Decimal
    product = Product.create(
        code="TEST-PROD-001",
        name="Test Product",
        description="Test product description",
        price=Decimal("99.99"),
        cost=Decimal("50.00"),
        category_ids=[sample_category.id]
    )
    product.categories = [sample_category]
    db_session.add(product)
    db_session.flush()
    
    # Update domain event with product ID
    events = product.get_domain_events()
    for event in events:
        if hasattr(event, 'product_id') and event.product_id == 0:
            event.product_id = product.id
    
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def sample_variant(db_session, sample_product):
    """Create a sample product variant for testing."""
    from app.domain.models.product import ProductVariant
    variant = ProductVariant.create(
        product_id=sample_product.id,
        code="TEST-VAR-001",
        name="Test Variant",
        attributes='{"color": "red", "size": "L"}',
        price=Decimal("110.00"),
        cost=Decimal("55.00"),
        barcode="1234567890123"
    )
    db_session.add(variant)
    db_session.commit()
    db_session.refresh(variant)
    return variant


@pytest.fixture
def sample_b2b_customer(db_session):
    """Create a sample B2B customer for testing."""
    customer = Customer.create(
        type="B2B",
        name="Test Company",
        email="test.company@example.com",
        company_name="Test Company SARL",
        siret="12345678901234",
        vat_number="FR12345678901",
        phone="+33 1 23 45 67 89"
    )
    db_session.add(customer)
    db_session.flush()
    
    # Create commercial conditions
    commercial_conditions = CommercialConditions(
        customer_id=customer.id,
        payment_terms_days=30,
        default_discount_percent=Decimal("5.00"),
        credit_limit=Decimal("10000.00"),
        block_on_credit_exceeded=True
    )
    db_session.add(commercial_conditions)
    
    # Update domain event with customer ID
    events = customer.get_domain_events()
    for event in events:
        if hasattr(event, 'customer_id') and event.customer_id == 0:
            event.customer_id = customer.id
    
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def sample_b2c_customer(db_session):
    """Create a sample B2C customer for testing."""
    customer = Customer.create(
        type="B2C",
        name="John Doe",
        email="john.doe@example.com",
        first_name="John",
        last_name="Doe",
        birth_date=date(1990, 1, 15),
        phone="+33 6 12 34 56 78"
    )
    db_session.add(customer)
    db_session.flush()
    
    # Create commercial conditions
    commercial_conditions = CommercialConditions(
        customer_id=customer.id,
        payment_terms_days=0,
        default_discount_percent=Decimal("0"),
        credit_limit=Decimal("0"),
        block_on_credit_exceeded=False
    )
    db_session.add(commercial_conditions)
    
    # Update domain event with customer ID
    events = customer.get_domain_events()
    for event in events:
        if hasattr(event, 'customer_id') and event.customer_id == 0:
            event.customer_id = customer.id
    
    db_session.commit()
    db_session.refresh(customer)
    return customer


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(username="testuser", role="admin")
    user.set_password("testpass")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_supplier(db_session):
    """Create a sample supplier for testing."""
    supplier = Supplier.create(
        name="Test Supplier",
        email="test@supplier.com",
        phone="+33 1 23 45 67 89",
        company_name="Test Supplier SARL",
        siret="12345678901234"
    )
    db_session.add(supplier)
    db_session.flush()
    
    # Create supplier conditions
    conditions = SupplierConditions(
        supplier_id=supplier.id,
        payment_terms_days=30,
        default_discount_percent=Decimal("5.00"),
        minimum_order_amount=Decimal("500.00"),
        delivery_lead_time_days=7
    )
    db_session.add(conditions)
    
    # Update domain event with supplier ID
    events = supplier.get_domain_events()
    for event in events:
        if hasattr(event, 'supplier_id') and event.supplier_id == 0:
            event.supplier_id = supplier.id
    
    db_session.commit()
    db_session.refresh(supplier)
    return supplier


@pytest.fixture
def sample_purchase_order(db_session, sample_supplier, sample_user):
    """Create a sample purchase order for testing."""
    from datetime import date
    order = PurchaseOrder.create(
        supplier_id=sample_supplier.id,
        created_by=sample_user.id,
        expected_delivery_date=date(2025, 12, 1)
    )
    db_session.add(order)
    
    # Update domain event with order ID
    events = order.get_domain_events()
    for event in events:
        if hasattr(event, 'order_id') and event.order_id == 0:
            event.order_id = order.id
    
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture
def sample_volume_pricing(db_session, sample_product):
    """Create a sample volume pricing tier for testing."""
    from app.domain.models.product import ProductVolumePricing
    tier = ProductVolumePricing(
        product_id=sample_product.id,
        min_quantity=Decimal("10.000"),
        max_quantity=Decimal("50.000"),
        price=Decimal("90.00")
    )
    db_session.add(tier)
    db_session.commit()
    db_session.refresh(tier)
    return tier
