"""Unit tests for PaymentAutoAllocationService."""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from app.services.payment_auto_allocation_service import PaymentAutoAllocationService
from app.domain.models.invoice import Invoice, InvoiceLine, InvoiceStatus
from app.domain.models.customer import Customer, CommercialConditions
from app.domain.models.product import Product
from app.domain.models.category import Category


@pytest.fixture
def sample_customer_with_invoices(db_session):
    """Create a customer with multiple unpaid invoices for testing."""
    # Create category and product
    category = Category.create(
        name="Test Category",
        code="TEST-CAT",
        description="Test category"
    )
    db_session.add(category)
    db_session.flush()
    
    product = Product.create(
        code="PROD-001",
        name="Test Product",
        description="Test product",
        price=Decimal("100.00"),
        cost=Decimal("50.00"),
        category_ids=[category.id]
    )
    product.categories = [category]
    db_session.add(product)
    db_session.flush()
    
    # Create customer
    customer = Customer.create(
        type="B2B",
        name="Test Company",
        email="test@example.com",
        company_name="Test Company",
        code="CUST-001"
    )
    db_session.add(customer)
    db_session.flush()
    
    # Create commercial conditions
    commercial_conditions = CommercialConditions(
        customer_id=customer.id,
        payment_terms_days=30,
        default_discount_percent=Decimal("0"),
        credit_limit=Decimal("10000.00"),
        block_on_credit_exceeded=False
    )
    db_session.add(commercial_conditions)
    db_session.flush()
    
    # Create multiple unpaid invoices with different due dates
    invoices = []
    today = date.today()
    
    # Invoice 1: Oldest, due 60 days ago, remaining 500.00
    invoice1 = Invoice.create(
        customer_id=customer.id,
        order_id=None,
        invoice_date=today - timedelta(days=90),
        due_date=today - timedelta(days=60),
        created_by=1
    )
    invoice1.number = "INV-001"
    invoice1.status = InvoiceStatus.SENT.value
    invoice1.subtotal = Decimal("500.00")
    invoice1.tax_amount = Decimal("100.00")
    invoice1.total = Decimal("600.00")
    invoice1.paid_amount = Decimal("100.00")
    invoice1.remaining_amount = Decimal("500.00")
    db_session.add(invoice1)
    db_session.flush()
    
    line1 = InvoiceLine(
        invoice_id=invoice1.id,
        product_id=product.id,
        quantity=Decimal("5.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        line_total_ht=Decimal("500.00"),
        line_total_ttc=Decimal("600.00"),
        sequence=1
    )
    db_session.add(line1)
    invoices.append(invoice1)
    
    # Invoice 2: Due 30 days ago, remaining 300.00
    invoice2 = Invoice.create(
        customer_id=customer.id,
        order_id=None,
        invoice_date=today - timedelta(days=60),
        due_date=today - timedelta(days=30),
        created_by=1
    )
    invoice2.number = "INV-002"
    invoice2.status = InvoiceStatus.SENT.value
    invoice2.subtotal = Decimal("300.00")
    invoice2.tax_amount = Decimal("60.00")
    invoice2.total = Decimal("360.00")
    invoice2.paid_amount = Decimal("60.00")
    invoice2.remaining_amount = Decimal("300.00")
    db_session.add(invoice2)
    db_session.flush()
    
    line2 = InvoiceLine(
        invoice_id=invoice2.id,
        product_id=product.id,
        quantity=Decimal("3.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        line_total_ht=Decimal("300.00"),
        line_total_ttc=Decimal("360.00"),
        sequence=1
    )
    db_session.add(line2)
    invoices.append(invoice2)
    
    # Invoice 3: Due 10 days ago, remaining 200.00
    invoice3 = Invoice.create(
        customer_id=customer.id,
        order_id=None,
        invoice_date=today - timedelta(days=40),
        due_date=today - timedelta(days=10),
        created_by=1
    )
    invoice3.number = "INV-003"
    invoice3.status = InvoiceStatus.SENT.value
    invoice3.subtotal = Decimal("200.00")
    invoice3.tax_amount = Decimal("40.00")
    invoice3.total = Decimal("240.00")
    invoice3.paid_amount = Decimal("40.00")
    invoice3.remaining_amount = Decimal("200.00")
    db_session.add(invoice3)
    db_session.flush()
    
    line3 = InvoiceLine(
        invoice_id=invoice3.id,
        product_id=product.id,
        quantity=Decimal("2.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        line_total_ht=Decimal("200.00"),
        line_total_ttc=Decimal("240.00"),
        sequence=1
    )
    db_session.add(line3)
    invoices.append(invoice3)
    
    db_session.commit()
    
    return customer, invoices


class TestPaymentAutoAllocationService:
    """Unit tests for PaymentAutoAllocationService."""
    
    def test_allocate_fifo_full_payment_covers_oldest_invoices(self, db_session, sample_customer_with_invoices):
        """Test FIFO allocation: payment covers oldest invoices first."""
        customer, invoices = sample_customer_with_invoices
        
        service = PaymentAutoAllocationService(db_session)
        payment_amount = Decimal("600.00")  # Enough to cover invoice1 (500) and part of invoice2 (100)
        
        allocations = service.allocate_payment(
            customer_id=customer.id,
            payment_amount=payment_amount,
            strategy='fifo'
        )
        
        assert len(allocations) == 2
        assert allocations[0]['invoice_id'] == invoices[0].id  # Oldest invoice first
        assert allocations[0]['amount'] == Decimal("500.00")  # Full amount of invoice1
        assert allocations[1]['invoice_id'] == invoices[1].id  # Second oldest
        assert allocations[1]['amount'] == Decimal("100.00")  # Partial payment of invoice2
    
    def test_allocate_fifo_partial_payment_single_invoice(self, db_session, sample_customer_with_invoices):
        """Test FIFO allocation: partial payment covers only oldest invoice partially."""
        customer, invoices = sample_customer_with_invoices
        
        service = PaymentAutoAllocationService(db_session)
        payment_amount = Decimal("200.00")  # Partial payment
        
        allocations = service.allocate_payment(
            customer_id=customer.id,
            payment_amount=payment_amount,
            strategy='fifo'
        )
        
        assert len(allocations) == 1
        assert allocations[0]['invoice_id'] == invoices[0].id  # Oldest invoice
        assert allocations[0]['amount'] == Decimal("200.00")  # Partial amount
    
    def test_allocate_fifo_exact_amount_multiple_invoices(self, db_session, sample_customer_with_invoices):
        """Test FIFO allocation: exact amount covers multiple invoices exactly."""
        customer, invoices = sample_customer_with_invoices
        
        service = PaymentAutoAllocationService(db_session)
        payment_amount = Decimal("800.00")  # Exactly invoice1 (500) + invoice2 (300)
        
        allocations = service.allocate_payment(
            customer_id=customer.id,
            payment_amount=payment_amount,
            strategy='fifo'
        )
        
        assert len(allocations) == 2
        assert allocations[0]['invoice_id'] == invoices[0].id
        assert allocations[0]['amount'] == Decimal("500.00")
        assert allocations[1]['invoice_id'] == invoices[1].id
        assert allocations[1]['amount'] == Decimal("300.00")
    
    def test_allocate_proportional_distributes_by_remaining_amount(self, db_session, sample_customer_with_invoices):
        """Test proportional allocation: distributes payment proportionally."""
        customer, invoices = sample_customer_with_invoices
        
        service = PaymentAutoAllocationService(db_session)
        payment_amount = Decimal("500.00")  # Total remaining is 1000, so 50% of each
        
        allocations = service.allocate_payment(
            customer_id=customer.id,
            payment_amount=payment_amount,
            strategy='proportional'
        )
        
        assert len(allocations) == 3
        
        # Calculate expected proportions
        # Invoice1: 500/1000 = 50% of 500 = 250
        # Invoice2: 300/1000 = 30% of 500 = 150
        # Invoice3: 200/1000 = 20% of 500 = 100
        # But last invoice gets remaining to avoid rounding errors
        
        total_allocated = sum(alloc['amount'] for alloc in allocations)
        assert total_allocated == payment_amount
        
        # Verify all invoices are included
        invoice_ids = [alloc['invoice_id'] for alloc in allocations]
        assert invoices[0].id in invoice_ids
        assert invoices[1].id in invoice_ids
        assert invoices[2].id in invoice_ids
    
    def test_allocate_proportional_small_payment(self, db_session, sample_customer_with_invoices):
        """Test proportional allocation with small payment amount."""
        customer, invoices = sample_customer_with_invoices
        
        service = PaymentAutoAllocationService(db_session)
        payment_amount = Decimal("100.00")  # Small payment
        
        allocations = service.allocate_payment(
            customer_id=customer.id,
            payment_amount=payment_amount,
            strategy='proportional'
        )
        
        assert len(allocations) > 0
        total_allocated = sum(alloc['amount'] for alloc in allocations)
        assert total_allocated == payment_amount
        
        # Verify no allocation exceeds invoice remaining amount
        for alloc in allocations:
            invoice = db_session.query(Invoice).filter(Invoice.id == alloc['invoice_id']).first()
            assert alloc['amount'] <= invoice.remaining_amount
    
    def test_allocate_no_unpaid_invoices_returns_empty(self, db_session, sample_b2b_customer):
        """Test allocation when customer has no unpaid invoices."""
        service = PaymentAutoAllocationService(db_session)
        
        allocations = service.allocate_payment(
            customer_id=sample_b2b_customer.id,
            payment_amount=Decimal("1000.00"),
            strategy='fifo'
        )
        
        assert allocations == []
    
    def test_allocate_invalid_strategy_raises_error(self, db_session, sample_b2b_customer):
        """Test that invalid strategy raises ValueError."""
        service = PaymentAutoAllocationService(db_session)
        
        with pytest.raises(ValueError, match="Invalid allocation strategy"):
            service.allocate_payment(
                customer_id=sample_b2b_customer.id,
                payment_amount=Decimal("100.00"),
                strategy='invalid_strategy'
            )
    
    def test_allocate_fifo_respects_invoice_remaining_amount(self, db_session, sample_customer_with_invoices):
        """Test FIFO: allocation never exceeds invoice remaining amount."""
        customer, invoices = sample_customer_with_invoices
        
        service = PaymentAutoAllocationService(db_session)
        payment_amount = Decimal("2000.00")  # More than total remaining (1000)
        
        allocations = service.allocate_payment(
            customer_id=customer.id,
            payment_amount=payment_amount,
            strategy='fifo'
        )
        
        # Should allocate to all invoices but not exceed remaining amounts
        total_allocated = sum(alloc['amount'] for alloc in allocations)
        assert total_allocated == Decimal("1000.00")  # Total remaining
        
        for alloc in allocations:
            invoice = db_session.query(Invoice).filter(Invoice.id == alloc['invoice_id']).first()
            assert alloc['amount'] <= invoice.remaining_amount
    
    def test_allocate_proportional_respects_invoice_remaining_amount(self, db_session, sample_customer_with_invoices):
        """Test proportional: allocation never exceeds invoice remaining amount."""
        customer, invoices = sample_customer_with_invoices
        
        service = PaymentAutoAllocationService(db_session)
        payment_amount = Decimal("2000.00")  # More than total remaining (1000)
        
        allocations = service.allocate_payment(
            customer_id=customer.id,
            payment_amount=payment_amount,
            strategy='proportional'
        )
        
        # Should allocate to all invoices but not exceed remaining amounts
        total_allocated = sum(alloc['amount'] for alloc in allocations)
        assert total_allocated == Decimal("1000.00")  # Total remaining
        
        for alloc in allocations:
            invoice = db_session.query(Invoice).filter(Invoice.id == alloc['invoice_id']).first()
            assert alloc['amount'] <= invoice.remaining_amount

