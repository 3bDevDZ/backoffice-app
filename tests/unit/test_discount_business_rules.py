"""Unit tests for discount business rules and pricing scenarios."""
import pytest
from decimal import Decimal
from datetime import date, datetime, timedelta
from app.services.pricing_service import PricingService, PriceCalculationResult
from app.domain.models.product import Product, ProductPriceList, ProductVolumePricing, ProductPromotionalPrice, PriceList
from app.domain.models.customer import Customer, CommercialConditions
from app.domain.models.quote import Quote, QuoteLine
from app.domain.models.user import User


class TestDiscountValidation:
    """Test discount validation rules (0-100%)."""
    
    def test_quote_line_discount_validation_valid_range(self, db_session, sample_product, sample_user, sample_b2b_customer):
        """Test that discount validation accepts values between 0 and 100."""
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id
        )
        db_session.add(quote)
        db_session.commit()
        db_session.refresh(quote)
        
        # Valid discounts
        for discount in [0, 10, 50, 100]:
            line = QuoteLine.create(
                quote_id=quote.id,
                product_id=sample_product.id,
                quantity=Decimal("1.00"),
                unit_price=Decimal("100.00"),
                discount_percent=Decimal(str(discount))
            )
            assert line.discount_percent == Decimal(str(discount))
    
    def test_quote_line_discount_validation_invalid_negative(self, db_session, sample_product, sample_user, sample_b2b_customer):
        """Test that discount validation rejects negative values."""
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id
        )
        db_session.add(quote)
        db_session.commit()
        db_session.refresh(quote)
        
        with pytest.raises(ValueError, match="Discount percent must be between 0 and 100"):
            QuoteLine.create(
                quote_id=quote.id,
                product_id=sample_product.id,
                quantity=Decimal("1.00"),
                unit_price=Decimal("100.00"),
                discount_percent=Decimal("-5.00")
            )
    
    def test_quote_line_discount_validation_invalid_over_100(self, db_session, sample_product, sample_user, sample_b2b_customer):
        """Test that discount validation rejects values over 100%."""
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id
        )
        db_session.add(quote)
        db_session.commit()
        db_session.refresh(quote)
        
        with pytest.raises(ValueError, match="Discount percent must be between 0 and 100"):
            QuoteLine.create(
                quote_id=quote.id,
                product_id=sample_product.id,
                quantity=Decimal("1.00"),
                unit_price=Decimal("100.00"),
                discount_percent=Decimal("150.00")
            )
    
    def test_quote_document_discount_validation(self, db_session, sample_user, sample_b2b_customer):
        """Test document-level discount validation."""
        # Valid
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id,
            discount_percent=Decimal("10.00")
        )
        assert quote.discount_percent == Decimal("10.00")
        
        # Invalid - negative
        with pytest.raises(ValueError, match="Discount percent must be between 0 and 100"):
            Quote.create(
                customer_id=sample_b2b_customer.id,
                created_by=sample_user.id,
                discount_percent=Decimal("-5.00")
            )
        
        # Invalid - over 100
        with pytest.raises(ValueError, match="Discount percent must be between 0 and 100"):
            Quote.create(
                customer_id=sample_b2b_customer.id,
                created_by=sample_user.id,
                discount_percent=Decimal("150.00")
            )


class TestPriceVsDiscountDistinction:
    """Test that price lists, volume pricing, and promotional prices are NOT discounts."""
    
    def test_price_list_is_not_a_discount(self, db_session, sample_product, sample_b2b_customer):
        """Test that price list price is NOT treated as a discount."""
        # Create price list
        price_list = PriceList(
            name="Test Price List",
            description="Test",
            is_active=True
        )
        db_session.add(price_list)
        db_session.flush()
        
        # Add product to price list with lower price
        product_price_list = ProductPriceList(
            price_list_id=price_list.id,
            product_id=sample_product.id,
            price=Decimal("80.00")  # Lower than base price 99.99
        )
        db_session.add(product_price_list)
        
        # Assign price list to customer
        sample_b2b_customer.commercial_conditions.price_list_id = price_list.id
        db_session.commit()
        db_session.refresh(sample_b2b_customer)
        db_session.refresh(sample_b2b_customer.commercial_conditions)
        
        # Get price for customer
        pricing_service = PricingService(db_session)
        result = pricing_service.get_price_for_customer(
            product_id=sample_product.id,
            customer_id=sample_b2b_customer.id,
            quantity=Decimal("1.00")
        )
        
        # Verify: price list price is used, but NO discount
        assert result.source == 'price_list'
        assert result.final_price == Decimal("80.00")
        assert result.applied_discount_percent == Decimal("0")  # No discount!
        assert result.discount_amount == Decimal("0")  # No discount!
        assert result.customer_price == Decimal("80.00")
    
    def test_volume_pricing_is_not_a_discount(self, db_session, sample_product, sample_b2b_customer):
        """Test that volume pricing is NOT treated as a discount."""
        # Create volume pricing tier
        volume_tier = ProductVolumePricing(
            product_id=sample_product.id,
            min_quantity=Decimal("10.000"),
            max_quantity=None,  # Unlimited
            price=Decimal("85.00")  # Lower than base price 99.99
        )
        db_session.add(volume_tier)
        db_session.commit()
        
        # Get price for customer with quantity >= 10
        pricing_service = PricingService(db_session)
        result = pricing_service.get_price_for_customer(
            product_id=sample_product.id,
            customer_id=sample_b2b_customer.id,
            quantity=Decimal("10.00")
        )
        
        # Verify: volume pricing is used, but NO discount
        assert result.source == 'volume_pricing'
        assert result.final_price == Decimal("85.00")
        assert result.applied_discount_percent == Decimal("0")  # No discount!
        assert result.discount_amount == Decimal("0")  # No discount!
        assert result.customer_price == Decimal("85.00")
    
    def test_promotional_price_is_not_a_discount(self, db_session, sample_product, sample_b2b_customer):
        """Test that promotional price is NOT treated as a discount."""
        # Create promotional price
        now = datetime.now()
        promo = ProductPromotionalPrice(
            product_id=sample_product.id,
            price=Decimal("75.00"),  # Lower than base price 99.99
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=30),
            is_active=True
        )
        db_session.add(promo)
        db_session.commit()
        
        # Get price for customer
        pricing_service = PricingService(db_session)
        result = pricing_service.get_price_for_customer(
            product_id=sample_product.id,
            customer_id=sample_b2b_customer.id,
            quantity=Decimal("1.00")
        )
        
        # Verify: promotional price is used, but NO discount
        assert result.source == 'promotional_price'
        assert result.final_price == Decimal("75.00")
        assert result.applied_discount_percent == Decimal("0")  # No discount!
        assert result.discount_amount == Decimal("0")  # No discount!
        assert result.customer_price == Decimal("75.00")
    
    def test_customer_discount_is_a_real_discount(self, db_session, sample_product, sample_b2b_customer):
        """Test that customer default discount IS treated as a real discount."""
        # Set customer default discount
        sample_b2b_customer.commercial_conditions.default_discount_percent = Decimal("15.00")
        db_session.commit()
        
        # Get price for customer (no price list, no promo, no volume)
        pricing_service = PricingService(db_session)
        result = pricing_service.get_price_for_customer(
            product_id=sample_product.id,
            customer_id=sample_b2b_customer.id,
            quantity=Decimal("1.00")
        )
        
        # Verify: customer discount is applied
        assert result.source == 'customer_discount'
        assert result.base_price == Decimal("99.99")
        assert result.applied_discount_percent == Decimal("15.00")
        expected_price = Decimal("99.99") * (Decimal("1") - Decimal("15.00") / Decimal("100"))
        assert result.final_price == expected_price
        assert result.discount_amount > Decimal("0")  # Has discount amount!
        assert result.discount_amount == Decimal("99.99") - result.final_price


class TestPricePriorityOrder:
    """Test the priority order of pricing mechanisms."""
    
    def test_promotional_price_has_highest_priority(self, db_session, sample_product, sample_b2b_customer):
        """Test that promotional price overrides everything else."""
        # Setup: Create price list, volume pricing, and promotional price
        price_list = PriceList(name="PL", description="Test PL", is_active=True)
        db_session.add(price_list)
        db_session.flush()
        
        db_session.add(ProductPriceList(price_list_id=price_list.id, product_id=sample_product.id, price=Decimal("90.00")))
        db_session.add(ProductVolumePricing(product_id=sample_product.id, min_quantity=Decimal("5.000"), price=Decimal("85.00")))
        
        now = datetime.now()
        db_session.add(ProductPromotionalPrice(
            product_id=sample_product.id,
            price=Decimal("70.00"),
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=30),
            is_active=True
        ))
        
        sample_b2b_customer.commercial_conditions.price_list_id = price_list.id
        sample_b2b_customer.commercial_conditions.default_discount_percent = Decimal("10.00")
        db_session.commit()
        db_session.refresh(sample_b2b_customer)
        db_session.refresh(sample_b2b_customer.commercial_conditions)
        
        # Get price
        pricing_service = PricingService(db_session)
        result = pricing_service.get_price_for_customer(
            product_id=sample_product.id,
            customer_id=sample_b2b_customer.id,
            quantity=Decimal("10.00")
        )
        
        # Promotional price should win
        assert result.source == 'promotional_price'
        assert result.final_price == Decimal("70.00")
    
    def test_volume_pricing_overrides_price_list(self, db_session, sample_product, sample_b2b_customer):
        """Test that volume pricing overrides price list when quantity matches."""
        # Setup: Create price list and volume pricing (no promo)
        price_list = PriceList(name="PL", description="Test PL", is_active=True)
        db_session.add(price_list)
        db_session.flush()
        
        db_session.add(ProductPriceList(price_list_id=price_list.id, product_id=sample_product.id, price=Decimal("90.00")))
        db_session.add(ProductVolumePricing(product_id=sample_product.id, min_quantity=Decimal("5.000"), price=Decimal("85.00")))
        
        sample_b2b_customer.commercial_conditions.price_list_id = price_list.id
        db_session.commit()
        db_session.refresh(sample_b2b_customer)
        db_session.refresh(sample_b2b_customer.commercial_conditions)
        
        # Get price with quantity >= 5
        pricing_service = PricingService(db_session)
        result = pricing_service.get_price_for_customer(
            product_id=sample_product.id,
            customer_id=sample_b2b_customer.id,
            quantity=Decimal("10.00")
        )
        
        # Volume pricing should win over price list
        assert result.source == 'volume_pricing'
        assert result.final_price == Decimal("85.00")
    
    def test_price_list_overrides_customer_discount(self, db_session, sample_product, sample_b2b_customer):
        """Test that price list overrides customer default discount."""
        # Setup: Create price list and customer discount (no promo, no volume)
        price_list = PriceList(name="PL", description="Test PL", is_active=True)
        db_session.add(price_list)
        db_session.flush()
        
        db_session.add(ProductPriceList(price_list_id=price_list.id, product_id=sample_product.id, price=Decimal("90.00")))
        
        sample_b2b_customer.commercial_conditions.price_list_id = price_list.id
        sample_b2b_customer.commercial_conditions.default_discount_percent = Decimal("10.00")
        db_session.commit()
        db_session.refresh(sample_b2b_customer)
        db_session.refresh(sample_b2b_customer.commercial_conditions)
        
        # Get price
        pricing_service = PricingService(db_session)
        result = pricing_service.get_price_for_customer(
            product_id=sample_product.id,
            customer_id=sample_b2b_customer.id,
            quantity=Decimal("1.00")
        )
        
        # Price list should win over customer discount
        assert result.source == 'price_list'
        assert result.final_price == Decimal("90.00")
        assert result.applied_discount_percent == Decimal("0")  # No discount applied


class TestDiscountCalculation:
    """Test discount calculation formulas."""
    
    def test_line_discount_calculation(self, db_session, sample_product, sample_user, sample_b2b_customer):
        """Test that line discount is calculated correctly."""
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id
        )
        db_session.add(quote)
        db_session.commit()
        db_session.refresh(quote)
        
        # Create line with discount
        line = QuoteLine.create(
            quote_id=quote.id,
            product_id=sample_product.id,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            discount_percent=Decimal("15.00")
        )
        
        # Verify calculation
        expected_subtotal = Decimal("10.00") * Decimal("100.00")  # 1000.00
        expected_discount = expected_subtotal * Decimal("15.00") / Decimal("100")  # 150.00
        expected_line_total = expected_subtotal - expected_discount  # 850.00
        
        assert line.discount_amount == expected_discount
        assert line.line_total_ht == expected_line_total
    
    def test_document_discount_calculation(self, db_session, sample_product, sample_user, sample_b2b_customer):
        """Test that document discount is calculated correctly on lines subtotal."""
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id,
            discount_percent=Decimal("10.00")
        )
        db_session.add(quote)
        db_session.commit()
        db_session.refresh(quote)
        
        # Add lines without discount using quote.add_line (which calls calculate_totals)
        line1 = quote.add_line(
            product_id=sample_product.id,
            quantity=Decimal("5.00"),
            unit_price=Decimal("100.00"),
            discount_percent=Decimal("0")
        )
        line2 = quote.add_line(
            product_id=sample_product.id,
            quantity=Decimal("3.00"),
            unit_price=Decimal("50.00"),
            discount_percent=Decimal("0")
        )
        db_session.add(line1)
        db_session.add(line2)
        db_session.commit()
        db_session.refresh(quote)
        db_session.refresh(line1)
        db_session.refresh(line2)
        
        # Verify calculation
        lines_subtotal = line1.line_total_ht + line2.line_total_ht  # 500 + 150 = 650
        expected_discount = lines_subtotal * Decimal("10.00") / Decimal("100")  # 65.00
        expected_subtotal = lines_subtotal - expected_discount  # 585.00
        
        assert quote.discount_amount == expected_discount
        assert quote.subtotal == expected_subtotal
    
    def test_line_and_document_discount_combined(self, db_session, sample_product, sample_user, sample_b2b_customer):
        """Test that line discount and document discount are applied sequentially."""
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id,
            discount_percent=Decimal("5.00")  # Document discount
        )
        db_session.add(quote)
        db_session.commit()
        db_session.refresh(quote)
        
        # Add line with line discount using quote.add_line (which calls calculate_totals)
        line = quote.add_line(
            product_id=sample_product.id,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            discount_percent=Decimal("10.00")  # Line discount
        )
        db_session.add(line)
        db_session.commit()
        db_session.refresh(quote)
        db_session.refresh(line)
        
        # Verify line discount first
        line_subtotal = Decimal("10.00") * Decimal("100.00")  # 1000.00
        line_discount = line_subtotal * Decimal("10.00") / Decimal("100")  # 100.00
        line_total_ht = line_subtotal - line_discount  # 900.00
        assert line.line_total_ht == line_total_ht
        
        # Verify document discount on line total
        document_discount = line_total_ht * Decimal("5.00") / Decimal("100")  # 45.00
        expected_subtotal = line_total_ht - document_discount  # 855.00
        assert quote.discount_amount == document_discount
        assert quote.subtotal == expected_subtotal


class TestTaxCalculationAfterDiscount:
    """Test that tax is calculated on price after discount."""
    
    def test_tax_calculated_on_price_after_line_discount(self, db_session, sample_product, sample_user, sample_b2b_customer):
        """Test that tax is calculated on line total HT after discount."""
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id
        )
        db_session.add(quote)
        db_session.commit()
        db_session.refresh(quote)
        
        # Create line with discount and tax
        line = QuoteLine.create(
            quote_id=quote.id,
            product_id=sample_product.id,
            quantity=Decimal("10.00"),
            unit_price=Decimal("100.00"),
            discount_percent=Decimal("10.00"),
            tax_rate=Decimal("20.00")
        )
        
        # Verify tax calculation
        line_subtotal = Decimal("10.00") * Decimal("100.00")  # 1000.00
        line_discount = line_subtotal * Decimal("10.00") / Decimal("100")  # 100.00
        line_total_ht = line_subtotal - line_discount  # 900.00
        expected_tax = line_total_ht * Decimal("20.00") / Decimal("100")  # 180.00
        expected_total_ttc = line_total_ht + expected_tax  # 1080.00
        
        assert line.line_total_ht == line_total_ht
        assert line.line_total_ttc == expected_total_ttc
        assert line.line_total_ttc - line.line_total_ht == expected_tax


class TestDiscountEdgeCases:
    """Test edge cases for discounts."""
    
    def test_zero_discount(self, db_session, sample_product, sample_user, sample_b2b_customer):
        """Test that zero discount works correctly."""
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id,
            discount_percent=Decimal("0")
        )
        db_session.add(quote)
        db_session.commit()
        db_session.refresh(quote)
        
        line = QuoteLine.create(
            quote_id=quote.id,
            product_id=sample_product.id,
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            discount_percent=Decimal("0")
        )
        
        assert line.discount_amount == Decimal("0")
        assert line.line_total_ht == Decimal("100.00")
    
    def test_100_percent_discount(self, db_session, sample_product, sample_user, sample_b2b_customer):
        """Test that 100% discount results in zero price."""
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id
        )
        db_session.add(quote)
        db_session.commit()
        db_session.refresh(quote)
        
        line = QuoteLine.create(
            quote_id=quote.id,
            product_id=sample_product.id,
            quantity=Decimal("1.00"),
            unit_price=Decimal("100.00"),
            discount_percent=Decimal("100.00")
        )
        
        assert line.discount_amount == Decimal("100.00")
        assert line.line_total_ht == Decimal("0")
    
    def test_discount_on_zero_price(self, db_session, sample_product, sample_user, sample_b2b_customer):
        """Test that discount on zero price results in zero."""
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id
        )
        db_session.add(quote)
        db_session.commit()
        db_session.refresh(quote)
        
        line = QuoteLine.create(
            quote_id=quote.id,
            product_id=sample_product.id,
            quantity=Decimal("1.00"),
            unit_price=Decimal("0.00"),
            discount_percent=Decimal("50.00")
        )
        
        assert line.discount_amount == Decimal("0")
        assert line.line_total_ht == Decimal("0")


class TestDiscountNotAppliedToPriceLists:
    """Test that discounts are NOT automatically applied when using price lists."""
    
    def test_discount_not_applied_when_price_list_exists(self, db_session, sample_product, sample_b2b_customer):
        """Test that customer discount is NOT applied when price list is used."""
        # Setup: Create price list
        price_list = PriceList(name="PL", description="Test PL", is_active=True)
        db_session.add(price_list)
        db_session.flush()
        
        db_session.add(ProductPriceList(price_list_id=price_list.id, product_id=sample_product.id, price=Decimal("90.00")))
        
        # Set customer with price list AND default discount
        sample_b2b_customer.commercial_conditions.price_list_id = price_list.id
        sample_b2b_customer.commercial_conditions.default_discount_percent = Decimal("10.00")
        db_session.commit()
        db_session.refresh(sample_b2b_customer)
        db_session.refresh(sample_b2b_customer.commercial_conditions)
        
        # Get price
        pricing_service = PricingService(db_session)
        result = pricing_service.get_price_for_customer(
            product_id=sample_product.id,
            customer_id=sample_b2b_customer.id,
            quantity=Decimal("1.00")
        )
        
        # Price list should be used, discount should NOT be applied
        assert result.source == 'price_list'
        assert result.final_price == Decimal("90.00")
        assert result.applied_discount_percent == Decimal("0")
        assert result.discount_amount == Decimal("0")

