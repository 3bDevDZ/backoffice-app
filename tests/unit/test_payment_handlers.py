"""Unit tests for payment command handlers."""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from app.application.billing.payments.commands.commands import (
    CreatePaymentCommand,
    AllocatePaymentCommand,
    ConfirmPaymentCommand,
    PaymentAllocationInput
)
from app.application.billing.payments.commands.handlers import (
    CreatePaymentHandler,
    AllocatePaymentHandler,
    ConfirmPaymentHandler
)
from app.domain.models.payment import Payment, PaymentAllocation, PaymentMethod, PaymentStatus
from app.domain.models.invoice import Invoice, InvoiceLine, InvoiceStatus
from app.domain.models.customer import Customer, CommercialConditions
from app.domain.models.product import Product
from app.domain.models.category import Category
from app.domain.models.user import User


@pytest.fixture
def sample_invoice_unpaid(db_session, sample_b2b_customer, sample_product, sample_user):
    """Create an unpaid invoice for testing."""
    invoice = Invoice.create(
        customer_id=sample_b2b_customer.id,
        order_id=None,
        invoice_date=date.today() - timedelta(days=30),
        due_date=date.today() - timedelta(days=10),
        created_by=sample_user.id
    )
    invoice.number = "INV-TEST-001"
    invoice.status = InvoiceStatus.SENT.value
    invoice.subtotal = Decimal("1000.00")
    invoice.tax_amount = Decimal("200.00")
    invoice.total = Decimal("1200.00")
    invoice.paid_amount = Decimal("0.00")
    invoice.remaining_amount = Decimal("1200.00")
    db_session.add(invoice)
    db_session.flush()
    
    line = InvoiceLine(
        invoice_id=invoice.id,
        product_id=sample_product.id,
        quantity=Decimal("10.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        line_total_ht=Decimal("1000.00"),
        line_total_ttc=Decimal("1200.00"),
        sequence=1
    )
    db_session.add(line)
    db_session.commit()
    db_session.refresh(invoice)
    return invoice


@pytest.fixture
def sample_invoices_multiple(db_session, sample_b2b_customer, sample_product, sample_user):
    """Create multiple unpaid invoices for testing."""
    invoices = []
    today = date.today()
    
    # Invoice 1: 500 remaining
    invoice1 = Invoice.create(
        customer_id=sample_b2b_customer.id,
        order_id=None,
        invoice_date=today - timedelta(days=60),
        due_date=today - timedelta(days=30),
        created_by=sample_user.id
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
        product_id=sample_product.id,
        quantity=Decimal("5.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        line_total_ht=Decimal("500.00"),
        line_total_ttc=Decimal("600.00"),
        sequence=1
    )
    db_session.add(line1)
    invoices.append(invoice1)
    
    # Invoice 2: 300 remaining
    invoice2 = Invoice.create(
        customer_id=sample_b2b_customer.id,
        order_id=None,
        invoice_date=today - timedelta(days=40),
        due_date=today - timedelta(days=10),
        created_by=sample_user.id
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
        product_id=sample_product.id,
        quantity=Decimal("3.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        line_total_ht=Decimal("300.00"),
        line_total_ttc=Decimal("360.00"),
        sequence=1
    )
    db_session.add(line2)
    invoices.append(invoice2)
    
    db_session.commit()
    for inv in invoices:
        db_session.refresh(inv)
    return invoices


class TestCreatePaymentHandler:
    """Unit tests for CreatePaymentHandler."""
    
    def test_create_payment_success(self, db_session, sample_b2b_customer, sample_user):
        """Test creating a payment successfully."""
        handler = CreatePaymentHandler()
        command = CreatePaymentCommand(
            customer_id=sample_b2b_customer.id,
            payment_method='cash',
            amount=Decimal("500.00"),
            payment_date=date.today(),
            created_by=sample_user.id
        )
        
        payment_id = handler.handle(command)
        
        # Verify payment was created
        payment = db_session.query(Payment).filter(Payment.id == payment_id).first()
        assert payment is not None
        assert payment.customer_id == sample_b2b_customer.id
        assert payment.amount == Decimal("500.00")
        assert payment.payment_method == PaymentMethod.CASH
        assert payment.status == PaymentStatus.CONFIRMED  # Should be auto-confirmed
        assert payment.created_by == sample_user.id
    
    def test_create_payment_with_manual_allocation(self, db_session, sample_b2b_customer, sample_invoice_unpaid, sample_user):
        """Test creating payment with manual allocation to invoice."""
        handler = CreatePaymentHandler()
        command = CreatePaymentCommand(
            customer_id=sample_b2b_customer.id,
            payment_method='bank_transfer',
            amount=Decimal("500.00"),
            payment_date=date.today(),
            created_by=sample_user.id,
            allocations=[
                PaymentAllocationInput(
                    invoice_id=sample_invoice_unpaid.id,
                    amount=Decimal("500.00")
                )
            ]
        )
        
        payment_id = handler.handle(command)
        
        # Verify payment and allocation
        payment = db_session.query(Payment).filter(Payment.id == payment_id).first()
        assert payment is not None
        assert len(payment.allocations) == 1
        assert payment.allocations[0].invoice_id == sample_invoice_unpaid.id
        assert payment.allocations[0].allocated_amount == Decimal("500.00")
        
        # Verify invoice was updated
        db_session.refresh(sample_invoice_unpaid)
        assert sample_invoice_unpaid.paid_amount == Decimal("500.00")
        assert sample_invoice_unpaid.remaining_amount == Decimal("700.00")
    
    def test_create_payment_with_auto_allocation_fifo(self, db_session, sample_b2b_customer, sample_invoices_multiple, sample_user):
        """Test creating payment with FIFO auto-allocation."""
        handler = CreatePaymentHandler()
        command = CreatePaymentCommand(
            customer_id=sample_b2b_customer.id,
            payment_method='check',
            amount=Decimal("600.00"),
            payment_date=date.today(),
            created_by=sample_user.id,
            auto_allocation_strategy='fifo'
        )
        
        payment_id = handler.handle(command)
        
        # Verify payment and allocations
        payment = db_session.query(Payment).filter(Payment.id == payment_id).first()
        assert payment is not None
        assert len(payment.allocations) == 2  # Should allocate to 2 invoices
        
        # FIFO: oldest invoice first (500) + part of second (100)
        allocations = sorted(payment.allocations, key=lambda a: a.allocated_amount, reverse=True)
        assert allocations[0].allocated_amount == Decimal("500.00")
        assert allocations[1].allocated_amount == Decimal("100.00")
        
        # Verify invoices were updated
        db_session.refresh(sample_invoices_multiple[0])
        db_session.refresh(sample_invoices_multiple[1])
        assert sample_invoices_multiple[0].paid_amount == Decimal("600.00")  # 100 + 500
        assert sample_invoices_multiple[1].paid_amount == Decimal("160.00")  # 60 + 100
    
    def test_create_payment_with_auto_allocation_proportional(self, db_session, sample_b2b_customer, sample_invoices_multiple, sample_user):
        """Test creating payment with proportional auto-allocation."""
        handler = CreatePaymentHandler()
        command = CreatePaymentCommand(
            customer_id=sample_b2b_customer.id,
            payment_method='bank_transfer',
            amount=Decimal("400.00"),
            payment_date=date.today(),
            created_by=sample_user.id,
            auto_allocation_strategy='proportional'
        )
        
        payment_id = handler.handle(command)
        
        # Verify payment and allocations
        payment = db_session.query(Payment).filter(Payment.id == payment_id).first()
        assert payment is not None
        assert len(payment.allocations) == 2  # Should allocate to both invoices
        
        total_allocated = sum(alloc.allocated_amount for alloc in payment.allocations)
        assert total_allocated == Decimal("400.00")
    
    def test_create_payment_invalid_amount_raises_error(self, db_session, sample_b2b_customer, sample_user):
        """Test that creating payment with zero or negative amount raises error."""
        handler = CreatePaymentHandler()
        command = CreatePaymentCommand(
            customer_id=sample_b2b_customer.id,
            payment_method='cash',
            amount=Decimal("0.00"),
            payment_date=date.today(),
            created_by=sample_user.id
        )
        
        with pytest.raises(ValueError, match="Payment amount must be greater than zero"):
            handler.handle(command)
    
    def test_create_payment_invalid_method_raises_error(self, db_session, sample_b2b_customer, sample_user):
        """Test that invalid payment method raises error."""
        handler = CreatePaymentHandler()
        command = CreatePaymentCommand(
            customer_id=sample_b2b_customer.id,
            payment_method='invalid_method',
            amount=Decimal("100.00"),
            payment_date=date.today(),
            created_by=sample_user.id
        )
        
        with pytest.raises(ValueError, match="Invalid payment method"):
            handler.handle(command)
    
    def test_create_payment_allocation_exceeds_available_raises_error(self, db_session, sample_b2b_customer, sample_invoice_unpaid, sample_user):
        """Test that allocating more than payment amount raises error."""
        handler = CreatePaymentHandler()
        command = CreatePaymentCommand(
            customer_id=sample_b2b_customer.id,
            payment_method='cash',
            amount=Decimal("500.00"),
            payment_date=date.today(),
            created_by=sample_user.id,
            allocations=[
                PaymentAllocationInput(
                    invoice_id=sample_invoice_unpaid.id,
                    amount=Decimal("600.00")  # More than payment amount
                )
            ]
        )
        
        with pytest.raises(ValueError, match="Cannot allocate"):
            handler.handle(command)
    
    def test_create_payment_allocation_invalid_invoice_raises_error(self, db_session, sample_b2b_customer, sample_user):
        """Test that allocating to non-existent invoice raises error."""
        handler = CreatePaymentHandler()
        command = CreatePaymentCommand(
            customer_id=sample_b2b_customer.id,
            payment_method='cash',
            amount=Decimal("500.00"),
            payment_date=date.today(),
            created_by=sample_user.id,
            allocations=[
                PaymentAllocationInput(
                    invoice_id=99999,  # Non-existent invoice
                    amount=Decimal("500.00")
                )
            ]
        )
        
        with pytest.raises(ValueError, match="Invoice with ID 99999 not found"):
            handler.handle(command)


class TestAllocatePaymentHandler:
    """Unit tests for AllocatePaymentHandler."""
    
    def test_allocate_payment_success(self, db_session, sample_b2b_customer, sample_invoice_unpaid, sample_user):
        """Test allocating payment to invoice successfully."""
        # Create payment first
        payment = Payment.create(
            customer_id=sample_b2b_customer.id,
            payment_method=PaymentMethod.CASH,
            amount=Decimal("500.00"),
            payment_date=date.today(),
            created_by=sample_user.id
        )
        payment.confirm()
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)
        
        handler = AllocatePaymentHandler()
        command = AllocatePaymentCommand(
            payment_id=payment.id,
            allocations=[
                PaymentAllocationInput(
                    invoice_id=sample_invoice_unpaid.id,
                    amount=Decimal("500.00")
                )
            ],
            created_by=sample_user.id
        )
        
        payment_id = handler.handle(command)
        
        # Verify allocation
        db_session.refresh(payment)
        assert len(payment.allocations) == 1
        assert payment.allocations[0].invoice_id == sample_invoice_unpaid.id
        assert payment.allocations[0].allocated_amount == Decimal("500.00")
        
        # Verify invoice was updated
        db_session.refresh(sample_invoice_unpaid)
        assert sample_invoice_unpaid.paid_amount == Decimal("500.00")
        assert sample_invoice_unpaid.remaining_amount == Decimal("700.00")
    
    def test_allocate_payment_multiple_invoices(self, db_session, sample_b2b_customer, sample_invoices_multiple, sample_user):
        """Test allocating payment to multiple invoices."""
        payment = Payment.create(
            customer_id=sample_b2b_customer.id,
            payment_method=PaymentMethod.BANK_TRANSFER,
            amount=Decimal("600.00"),
            payment_date=date.today(),
            created_by=sample_user.id
        )
        payment.confirm()
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)
        
        handler = AllocatePaymentHandler()
        command = AllocatePaymentCommand(
            payment_id=payment.id,
            allocations=[
                PaymentAllocationInput(
                    invoice_id=sample_invoices_multiple[0].id,
                    amount=Decimal("500.00")
                ),
                PaymentAllocationInput(
                    invoice_id=sample_invoices_multiple[1].id,
                    amount=Decimal("100.00")
                )
            ],
            created_by=sample_user.id
        )
        
        handler.handle(command)
        
        # Verify allocations
        db_session.refresh(payment)
        assert len(payment.allocations) == 2
        
        # Verify invoices were updated
        db_session.refresh(sample_invoices_multiple[0])
        db_session.refresh(sample_invoices_multiple[1])
        assert sample_invoices_multiple[0].paid_amount == Decimal("600.00")
        assert sample_invoices_multiple[1].paid_amount == Decimal("160.00")
    
    def test_allocate_payment_exceeds_available_raises_error(self, db_session, sample_b2b_customer, sample_invoice_unpaid, sample_user):
        """Test that allocating more than available amount raises error."""
        payment = Payment.create(
            customer_id=sample_b2b_customer.id,
            payment_method=PaymentMethod.CASH,
            amount=Decimal("500.00"),
            payment_date=date.today(),
            created_by=sample_user.id
        )
        payment.confirm()
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)
        
        handler = AllocatePaymentHandler()
        command = AllocatePaymentCommand(
            payment_id=payment.id,
            allocations=[
                PaymentAllocationInput(
                    invoice_id=sample_invoice_unpaid.id,
                    amount=Decimal("600.00")  # More than payment amount
                )
            ],
            created_by=sample_user.id
        )
        
        with pytest.raises(ValueError, match="Cannot allocate"):
            handler.handle(command)
    
    def test_allocate_payment_cancelled_payment_raises_error(self, db_session, sample_b2b_customer, sample_user):
        """Test that allocating cancelled payment raises error."""
        payment = Payment.create(
            customer_id=sample_b2b_customer.id,
            payment_method=PaymentMethod.CASH,
            amount=Decimal("500.00"),
            payment_date=date.today(),
            created_by=sample_user.id
        )
        payment.status = PaymentStatus.CANCELLED
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)
        
        handler = AllocatePaymentHandler()
        command = AllocatePaymentCommand(
            payment_id=payment.id,
            allocations=[],
            created_by=sample_user.id
        )
        
        with pytest.raises(ValueError, match="Cannot allocate cancelled payment"):
            handler.handle(command)
    
    def test_allocate_payment_draft_invoice_raises_error(self, db_session, sample_b2b_customer, sample_user):
        """Test that allocating to draft invoice raises error."""
        # Create draft invoice
        invoice = Invoice.create(
            customer_id=sample_b2b_customer.id,
            order_id=None,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            created_by=sample_user.id
        )
        invoice.status = InvoiceStatus.DRAFT.value
        db_session.add(invoice)
        db_session.commit()
        db_session.refresh(invoice)
        
        payment = Payment.create(
            customer_id=sample_b2b_customer.id,
            payment_method=PaymentMethod.CASH,
            amount=Decimal("500.00"),
            payment_date=date.today(),
            created_by=sample_user.id
        )
        payment.confirm()
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)
        
        handler = AllocatePaymentHandler()
        command = AllocatePaymentCommand(
            payment_id=payment.id,
            allocations=[
                PaymentAllocationInput(
                    invoice_id=invoice.id,
                    amount=Decimal("500.00")
                )
            ],
            created_by=sample_user.id
        )
        
        with pytest.raises(ValueError, match="Cannot allocate payment to invoice"):
            handler.handle(command)


class TestConfirmPaymentHandler:
    """Unit tests for ConfirmPaymentHandler."""
    
    def test_confirm_payment_success(self, db_session, sample_b2b_customer, sample_user):
        """Test confirming a pending payment successfully."""
        payment = Payment.create(
            customer_id=sample_b2b_customer.id,
            payment_method=PaymentMethod.CASH,
            amount=Decimal("500.00"),
            payment_date=date.today(),
            created_by=sample_user.id
        )
        # Payment is created as PENDING, so we don't confirm it
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)
        
        assert payment.status == PaymentStatus.PENDING
        
        handler = ConfirmPaymentHandler()
        command = ConfirmPaymentCommand(
            payment_id=payment.id,
            confirmed_by=sample_user.id
        )
        
        handler.handle(command)
        
        # Verify payment is confirmed
        db_session.refresh(payment)
        assert payment.status == PaymentStatus.CONFIRMED
    
    def test_confirm_already_confirmed_payment_raises_error(self, db_session, sample_b2b_customer, sample_user):
        """Test that confirming already confirmed payment raises error."""
        payment = Payment.create(
            customer_id=sample_b2b_customer.id,
            payment_method=PaymentMethod.CASH,
            amount=Decimal("500.00"),
            payment_date=date.today(),
            created_by=sample_user.id
        )
        payment.confirm()  # Already confirmed
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)
        
        handler = ConfirmPaymentHandler()
        command = ConfirmPaymentCommand(
            payment_id=payment.id,
            confirmed_by=sample_user.id
        )
        
        # Should raise error when trying to confirm already confirmed payment
        with pytest.raises(ValueError, match="Cannot confirm payment in status"):
            handler.handle(command)
    
    def test_confirm_nonexistent_payment_raises_error(self, db_session, sample_user):
        """Test that confirming non-existent payment raises error."""
        handler = ConfirmPaymentHandler()
        command = ConfirmPaymentCommand(
            payment_id=99999,  # Non-existent
            confirmed_by=sample_user.id
        )
        
        with pytest.raises(ValueError, match="Payment with ID 99999 not found"):
            handler.handle(command)

