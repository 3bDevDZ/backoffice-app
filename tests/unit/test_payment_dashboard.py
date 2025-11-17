"""Unit tests for payment dashboard queries and handlers."""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from app.application.billing.payments.queries.queries import (
    GetAgingReportQuery,
    GetOverdueInvoicesQuery
)
from app.application.billing.payments.queries.handlers import (
    GetAgingReportHandler,
    GetOverdueInvoicesHandler
)
from app.domain.models.invoice import Invoice, InvoiceLine, InvoiceStatus
from app.domain.models.customer import Customer, CommercialConditions
from app.domain.models.product import Product
from app.domain.models.category import Category
from app.domain.models.user import User


@pytest.fixture
def sample_customer_with_invoices(db_session, sample_user, sample_product):
    """Create a customer with multiple invoices in different aging buckets."""
    customer = Customer.create(
        type="B2B",
        name="Test Customer",
        email="test@example.com",
        company_name="Test Customer SARL"
    )
    customer.code = "CUST-001"
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
    db_session.commit()
    db_session.refresh(customer)
    
    # Create invoices in different aging buckets
    today = date.today()
    
    # Invoice 1: 0-30 days (due 15 days ago)
    invoice1 = Invoice.create(
        customer_id=customer.id,
        order_id=None,
        invoice_date=today - timedelta(days=45),
        due_date=today - timedelta(days=15),
        created_by=sample_user.id
    )
    invoice1.number = "INV-001"
    invoice1.status = InvoiceStatus.SENT.value
    invoice1.subtotal = Decimal("1000.00")
    invoice1.tax_amount = Decimal("200.00")
    invoice1.total = Decimal("1200.00")
    invoice1.paid_amount = Decimal("0.00")
    invoice1.remaining_amount = Decimal("1200.00")
    db_session.add(invoice1)
    db_session.flush()
    
    line1 = InvoiceLine(
        invoice_id=invoice1.id,
        product_id=sample_product.id,
        quantity=Decimal("10.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        line_total_ht=Decimal("1000.00"),
        line_total_ttc=Decimal("1200.00"),
        sequence=1
    )
    db_session.add(line1)
    
    # Invoice 2: 31-60 days (due 45 days ago)
    invoice2 = Invoice.create(
        customer_id=customer.id,
        order_id=None,
        invoice_date=today - timedelta(days=75),
        due_date=today - timedelta(days=45),
        created_by=sample_user.id
    )
    invoice2.number = "INV-002"
    invoice2.status = InvoiceStatus.PARTIALLY_PAID.value
    invoice2.subtotal = Decimal("2000.00")
    invoice2.tax_amount = Decimal("400.00")
    invoice2.total = Decimal("2400.00")
    invoice2.paid_amount = Decimal("1000.00")
    invoice2.remaining_amount = Decimal("1400.00")
    db_session.add(invoice2)
    db_session.flush()
    
    line2 = InvoiceLine(
        invoice_id=invoice2.id,
        product_id=sample_product.id,
        quantity=Decimal("20.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        line_total_ht=Decimal("2000.00"),
        line_total_ttc=Decimal("2400.00"),
        sequence=1
    )
    db_session.add(line2)
    
    # Invoice 3: 61-90 days (due 75 days ago)
    invoice3 = Invoice.create(
        customer_id=customer.id,
        order_id=None,
        invoice_date=today - timedelta(days=105),
        due_date=today - timedelta(days=75),
        created_by=sample_user.id
    )
    invoice3.number = "INV-003"
    invoice3.status = InvoiceStatus.OVERDUE.value
    invoice3.subtotal = Decimal("1500.00")
    invoice3.tax_amount = Decimal("300.00")
    invoice3.total = Decimal("1800.00")
    invoice3.paid_amount = Decimal("0.00")
    invoice3.remaining_amount = Decimal("1800.00")
    db_session.add(invoice3)
    db_session.flush()
    
    line3 = InvoiceLine(
        invoice_id=invoice3.id,
        product_id=sample_product.id,
        quantity=Decimal("15.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        line_total_ht=Decimal("1500.00"),
        line_total_ttc=Decimal("1800.00"),
        sequence=1
    )
    db_session.add(line3)
    
    # Invoice 4: 90+ days (due 120 days ago)
    invoice4 = Invoice.create(
        customer_id=customer.id,
        order_id=None,
        invoice_date=today - timedelta(days=150),
        due_date=today - timedelta(days=120),
        created_by=sample_user.id
    )
    invoice4.number = "INV-004"
    invoice4.status = InvoiceStatus.OVERDUE.value
    invoice4.subtotal = Decimal("500.00")
    invoice4.tax_amount = Decimal("100.00")
    invoice4.total = Decimal("600.00")
    invoice4.paid_amount = Decimal("0.00")
    invoice4.remaining_amount = Decimal("600.00")
    db_session.add(invoice4)
    db_session.flush()
    
    line4 = InvoiceLine(
        invoice_id=invoice4.id,
        product_id=sample_product.id,
        quantity=Decimal("5.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        line_total_ht=Decimal("500.00"),
        line_total_ttc=Decimal("600.00"),
        sequence=1
    )
    db_session.add(line4)
    
    # Invoice 5: Paid invoice (should not appear in aging report if include_paid=False)
    invoice5 = Invoice.create(
        customer_id=customer.id,
        order_id=None,
        invoice_date=today - timedelta(days=30),
        due_date=today - timedelta(days=10),
        created_by=sample_user.id
    )
    invoice5.number = "INV-005"
    invoice5.status = InvoiceStatus.PAID.value
    invoice5.subtotal = Decimal("800.00")
    invoice5.tax_amount = Decimal("160.00")
    invoice5.total = Decimal("960.00")
    invoice5.paid_amount = Decimal("960.00")
    invoice5.remaining_amount = Decimal("0.00")
    db_session.add(invoice5)
    db_session.flush()
    
    line5 = InvoiceLine(
        invoice_id=invoice5.id,
        product_id=sample_product.id,
        quantity=Decimal("8.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        line_total_ht=Decimal("800.00"),
        line_total_ttc=Decimal("960.00"),
        sequence=1
    )
    db_session.add(line5)
    
    db_session.commit()
    
    return customer


@pytest.fixture
def sample_customer2_with_invoices(db_session, sample_user, sample_product):
    """Create a second customer with overdue invoices."""
    customer = Customer.create(
        type="B2B",
        name="Test Customer 2",
        email="test2@example.com",
        company_name="Test Customer 2 SARL"
    )
    customer.code = "CUST-002"
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
    db_session.commit()
    db_session.refresh(customer)
    
    today = date.today()
    
    # Overdue invoice
    invoice = Invoice.create(
        customer_id=customer.id,
        order_id=None,
        invoice_date=today - timedelta(days=50),
        due_date=today - timedelta(days=20),
        created_by=sample_user.id
    )
    invoice.number = "INV-006"
    invoice.status = InvoiceStatus.SENT.value
    invoice.subtotal = Decimal("3000.00")
    invoice.tax_amount = Decimal("600.00")
    invoice.total = Decimal("3600.00")
    invoice.paid_amount = Decimal("0.00")
    invoice.remaining_amount = Decimal("3600.00")
    db_session.add(invoice)
    db_session.flush()
    
    line = InvoiceLine(
        invoice_id=invoice.id,
        product_id=sample_product.id,
        quantity=Decimal("30.00"),
        unit_price=Decimal("100.00"),
        tax_rate=Decimal("20.00"),
        line_total_ht=Decimal("3000.00"),
        line_total_ttc=Decimal("3600.00"),
        sequence=1
    )
    db_session.add(line)
    db_session.commit()
    
    return customer


class TestGetAgingReportHandler:
    """Test GetAgingReportHandler."""
    
    def test_get_aging_report_all_customers(self, db_session, sample_customer_with_invoices, sample_customer2_with_invoices):
        """Test getting aging report for all customers."""
        handler = GetAgingReportHandler()
        query = GetAgingReportQuery(
            customer_id=None,
            as_of_date=date.today(),
            include_paid=False
        )
        
        result = handler.handle(query)
        
        # Should have 2 customers
        assert len(result) == 2
        
        # Find customer 1
        customer1_report = next((r for r in result if r.customer_id == sample_customer_with_invoices.id), None)
        assert customer1_report is not None
        assert customer1_report.customer_code == "CUST-001"
        assert customer1_report.customer_name == "Test Customer SARL"  # Uses company_name for B2B customers
        
        # Check total outstanding for customer 1
        # 1200 (0-30) + 1400 (31-60) + 1800 (61-90) + 600 (90+) = 5000
        assert customer1_report.total_outstanding == Decimal("5000.00")
        
        # Check buckets
        buckets = {b.bucket_name: b for b in customer1_report.buckets}
        assert "0-30" in buckets
        assert buckets["0-30"].total_amount == Decimal("1200.00")
        assert buckets["0-30"].invoice_count == 1
        
        assert "31-60" in buckets
        assert buckets["31-60"].total_amount == Decimal("1400.00")
        assert buckets["31-60"].invoice_count == 1
        
        assert "61-90" in buckets
        assert buckets["61-90"].total_amount == Decimal("1800.00")
        assert buckets["61-90"].invoice_count == 1
        
        assert "90+" in buckets
        assert buckets["90+"].total_amount == Decimal("600.00")
        assert buckets["90+"].invoice_count == 1
        
        # Check customer 2
        customer2_report = next((r for r in result if r.customer_id == sample_customer2_with_invoices.id), None)
        assert customer2_report is not None
        assert customer2_report.total_outstanding == Decimal("3600.00")
        
        # Should be sorted by total outstanding (highest first)
        assert result[0].total_outstanding >= result[1].total_outstanding
    
    def test_get_aging_report_specific_customer(self, db_session, sample_customer_with_invoices):
        """Test getting aging report for a specific customer."""
        handler = GetAgingReportHandler()
        query = GetAgingReportQuery(
            customer_id=sample_customer_with_invoices.id,
            as_of_date=date.today(),
            include_paid=False
        )
        
        result = handler.handle(query)
        
        # Should have only 1 customer
        assert len(result) == 1
        assert result[0].customer_id == sample_customer_with_invoices.id
        assert result[0].total_outstanding == Decimal("5000.00")
    
    def test_get_aging_report_include_paid(self, db_session, sample_customer_with_invoices):
        """Test getting aging report including paid invoices."""
        handler = GetAgingReportHandler()
        query = GetAgingReportQuery(
            customer_id=sample_customer_with_invoices.id,
            as_of_date=date.today(),
            include_paid=True
        )
        
        result = handler.handle(query)
        
        # Should still have only unpaid invoices (paid invoice has remaining_amount = 0)
        assert len(result) == 1
        assert result[0].total_outstanding == Decimal("5000.00")
    
    def test_get_aging_report_empty_result(self, db_session):
        """Test getting aging report when no invoices exist."""
        handler = GetAgingReportHandler()
        query = GetAgingReportQuery(
            customer_id=None,
            as_of_date=date.today(),
            include_paid=False
        )
        
        result = handler.handle(query)
        
        assert result == []
    
    def test_get_aging_report_custom_date(self, db_session, sample_customer_with_invoices):
        """Test getting aging report with a custom as_of_date."""
        handler = GetAgingReportHandler()
        # Use a date 10 days in the future
        as_of_date = date.today() + timedelta(days=10)
        query = GetAgingReportQuery(
            customer_id=sample_customer_with_invoices.id,
            as_of_date=as_of_date,
            include_paid=False
        )
        
        result = handler.handle(query)
        
        # All invoices will be 10 days more overdue
        assert len(result) == 1
        # The buckets should shift
        buckets = {b.bucket_name: b for b in result[0].buckets}
        # Invoice 1 (was 15 days overdue) is now 25 days overdue (still 0-30)
        # Invoice 2 (was 45 days overdue) is now 55 days overdue (still 31-60)
        # Invoice 3 (was 75 days overdue) is now 85 days overdue (still 61-90)
        # Invoice 4 (was 120 days overdue) is now 130 days overdue (still 90+)
        assert result[0].total_outstanding == Decimal("5000.00")


class TestGetOverdueInvoicesHandler:
    """Test GetOverdueInvoicesHandler."""
    
    def test_get_overdue_invoices_all_customers(self, db_session, sample_customer_with_invoices, sample_customer2_with_invoices):
        """Test getting overdue invoices for all customers."""
        handler = GetOverdueInvoicesHandler()
        query = GetOverdueInvoicesQuery(
            customer_id=None,
            days_overdue=None,
            page=1,
            per_page=100
        )
        
        result = handler.handle(query)
        
        # Should have 5 overdue invoices total
        # Customer 1: 4 invoices (INV-001, INV-002, INV-003, INV-004)
        # Customer 2: 1 invoice (INV-006)
        assert len(result) == 5
        
        # Check that all invoices are overdue
        for invoice in result:
            assert invoice.days_overdue > 0
            assert invoice.remaining_amount > 0
        
        # Check customer info
        customer1_invoices = [inv for inv in result if inv.customer_id == sample_customer_with_invoices.id]
        assert len(customer1_invoices) == 4
        
        customer2_invoices = [inv for inv in result if inv.customer_id == sample_customer2_with_invoices.id]
        assert len(customer2_invoices) == 1
        assert customer2_invoices[0].invoice_number == "INV-006"
        assert customer2_invoices[0].remaining_amount == Decimal("3600.00")
    
    def test_get_overdue_invoices_specific_customer(self, db_session, sample_customer_with_invoices):
        """Test getting overdue invoices for a specific customer."""
        handler = GetOverdueInvoicesHandler()
        query = GetOverdueInvoicesQuery(
            customer_id=sample_customer_with_invoices.id,
            days_overdue=None,
            page=1,
            per_page=100
        )
        
        result = handler.handle(query)
        
        # Should have 4 invoices for customer 1
        assert len(result) == 4
        for invoice in result:
            assert invoice.customer_id == sample_customer_with_invoices.id
    
    def test_get_overdue_invoices_minimum_days(self, db_session, sample_customer_with_invoices):
        """Test getting overdue invoices with minimum days overdue filter."""
        handler = GetOverdueInvoicesHandler()
        query = GetOverdueInvoicesQuery(
            customer_id=None,
            days_overdue=30,  # Only invoices overdue by at least 30 days
            page=1,
            per_page=100
        )
        
        result = handler.handle(query)
        
        # Should have only invoices overdue by 30+ days
        # Customer 1: INV-002 (45 days), INV-003 (75 days), INV-004 (120 days) = 3
        # Customer 2: INV-006 (20 days) = 0 (not included)
        assert len(result) == 3
        
        for invoice in result:
            assert invoice.days_overdue >= 30
    
    def test_get_overdue_invoices_pagination(self, db_session, sample_customer_with_invoices, sample_customer2_with_invoices):
        """Test pagination for overdue invoices."""
        handler = GetOverdueInvoicesHandler()
        query = GetOverdueInvoicesQuery(
            customer_id=None,
            days_overdue=None,
            page=1,
            per_page=3
        )
        
        result = handler.handle(query)
        
        # Should have only 3 invoices (first page)
        assert len(result) == 3
        
        # Get second page
        query2 = GetOverdueInvoicesQuery(
            customer_id=None,
            days_overdue=None,
            page=2,
            per_page=3
        )
        result2 = handler.handle(query2)
        
        # Should have remaining 2 invoices
        assert len(result2) == 2
    
    def test_get_overdue_invoices_empty_result(self, db_session):
        """Test getting overdue invoices when none exist."""
        handler = GetOverdueInvoicesHandler()
        query = GetOverdueInvoicesQuery(
            customer_id=None,
            days_overdue=None,
            page=1,
            per_page=100
        )
        
        result = handler.handle(query)
        
        assert result == []
    
    def test_get_overdue_invoices_days_overdue_calculation(self, db_session, sample_customer_with_invoices):
        """Test that days_overdue is calculated correctly."""
        handler = GetOverdueInvoicesHandler()
        query = GetOverdueInvoicesQuery(
            customer_id=sample_customer_with_invoices.id,
            days_overdue=None,
            page=1,
            per_page=100
        )
        
        result = handler.handle(query)
        
        today = date.today()
        
        # Find invoice 1 (due 15 days ago)
        inv1 = next((inv for inv in result if inv.invoice_number == "INV-001"), None)
        assert inv1 is not None
        expected_days = (today - inv1.due_date).days
        assert inv1.days_overdue == expected_days
        assert inv1.days_overdue == 15
        
        # Find invoice 4 (due 120 days ago)
        inv4 = next((inv for inv in result if inv.invoice_number == "INV-004"), None)
        assert inv4 is not None
        expected_days = (today - inv4.due_date).days
        assert inv4.days_overdue == expected_days
        assert inv4.days_overdue == 120


class TestPaymentDashboardKPIs:
    """Test KPI calculations for payment dashboard."""
    
    def test_dashboard_kpi_calculations(self, db_session, sample_customer_with_invoices, sample_customer2_with_invoices):
        """Test that dashboard KPIs are calculated correctly from aging report and overdue invoices."""
        from app.application.billing.payments.queries.handlers import GetAgingReportHandler, GetOverdueInvoicesHandler
        from app.application.billing.payments.queries.queries import GetAgingReportQuery, GetOverdueInvoicesQuery
        
        # Get aging report using handler directly
        aging_handler = GetAgingReportHandler()
        aging_query = GetAgingReportQuery(
            customer_id=None,
            as_of_date=date.today(),
            include_paid=False
        )
        aging_report = aging_handler.handle(aging_query)
        
        # Calculate total outstanding
        total_outstanding = sum(customer.total_outstanding for customer in aging_report)
        assert total_outstanding == Decimal("8600.00")  # 5000 + 3600
        
        # Calculate by buckets
        bucket_0_30 = Decimal(0)
        bucket_31_60 = Decimal(0)
        bucket_61_90 = Decimal(0)
        bucket_90_plus = Decimal(0)
        
        for customer in aging_report:
            if customer.buckets:
                for bucket in customer.buckets:
                    if bucket.bucket_name == '0-30':
                        bucket_0_30 += bucket.total_amount
                    elif bucket.bucket_name == '31-60':
                        bucket_31_60 += bucket.total_amount
                    elif bucket.bucket_name == '61-90':
                        bucket_61_90 += bucket.total_amount
                    elif bucket.bucket_name == '90+':
                        bucket_90_plus += bucket.total_amount
        
        # Customer 1: 1200 (0-30), 1400 (31-60), 1800 (61-90), 600 (90+)
        # Customer 2: 3600 (0-30) - invoice due 20 days ago
        assert bucket_0_30 == Decimal("4800.00")  # 1200 + 3600
        assert bucket_31_60 == Decimal("1400.00")  # Only customer 1
        assert bucket_61_90 == Decimal("1800.00")
        assert bucket_90_plus == Decimal("600.00")
        
        # Get overdue invoices using handler directly
        overdue_handler = GetOverdueInvoicesHandler()
        overdue_query = GetOverdueInvoicesQuery(
            customer_id=None,
            days_overdue=None,
            page=1,
            per_page=10000
        )
        overdue_invoices = overdue_handler.handle(overdue_query)
        
        total_overdue_count = len(overdue_invoices)
        assert total_overdue_count == 5
        
        total_overdue_amount = sum(inv.remaining_amount for inv in overdue_invoices)
        assert total_overdue_amount == Decimal("8600.00")
        
        # Calculate percentage distribution
        if total_outstanding > 0:
            pct_0_30 = (bucket_0_30 / total_outstanding * 100).quantize(Decimal('0.01'))
            pct_31_60 = (bucket_31_60 / total_outstanding * 100).quantize(Decimal('0.01'))
            pct_61_90 = (bucket_61_90 / total_outstanding * 100).quantize(Decimal('0.01'))
            pct_90_plus = (bucket_90_plus / total_outstanding * 100).quantize(Decimal('0.01'))
        else:
            pct_0_30 = pct_31_60 = pct_61_90 = pct_90_plus = Decimal(0)
        
        # Verify percentages (approximately)
        assert pct_0_30 == Decimal("55.81")  # 4800 / 8600 * 100
        assert pct_31_60 == Decimal("16.28")  # 1400 / 8600 * 100
        assert pct_61_90 == Decimal("20.93")  # 1800 / 8600 * 100
        assert pct_90_plus == Decimal("6.98")  # 600 / 8600 * 100
        
        # Verify percentages sum to 100
        total_pct = pct_0_30 + pct_31_60 + pct_61_90 + pct_90_plus
        assert total_pct == Decimal("100.00")
    
    def test_dashboard_top_customers(self, db_session, sample_customer_with_invoices, sample_customer2_with_invoices):
        """Test that top customers are correctly identified."""
        from app.application.billing.payments.queries.handlers import GetAgingReportHandler
        from app.application.billing.payments.queries.queries import GetAgingReportQuery
        
        aging_handler = GetAgingReportHandler()
        aging_query = GetAgingReportQuery(
            customer_id=None,
            as_of_date=date.today(),
            include_paid=False
        )
        aging_report = aging_handler.handle(aging_query)
        
        # Get top 10 customers by outstanding amount
        top_customers = sorted(aging_report, key=lambda x: x.total_outstanding, reverse=True)[:10]
        
        assert len(top_customers) == 2
        # Customer 2 should be first (3600) - wait, no, customer 1 has 5000
        assert top_customers[0].total_outstanding == Decimal("5000.00")
        assert top_customers[1].total_outstanding == Decimal("3600.00")

