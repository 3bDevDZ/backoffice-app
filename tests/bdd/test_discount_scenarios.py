"""BDD tests for discount application scenarios."""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from app.services.pricing_service import PricingService
from app.domain.models.product import Product, ProductPriceList, ProductVolumePricing, ProductPromotionalPrice, PriceList
from app.domain.models.customer import Customer, CommercialConditions
from app.domain.models.quote import Quote, QuoteLine
from app.domain.models.user import User


class TestDiscountScenarios:
    """BDD tests for different discount application scenarios."""
    
    # ==================== SCENARIO 1: Client avec Price List ====================
    
    def test_scenario_1_client_with_price_list_no_discount(self, db_session, sample_product, sample_b2b_customer):
        """
        SCENARIO 1: Client avec Price List
        GIVEN: Un produit avec prix de base 100€
        AND: Une price list avec prix 90€ assignée au client
        AND: Le client a une remise par défaut de 10%
        WHEN: On calcule le prix pour ce client
        THEN: Le prix utilisé est 90€ (price list)
        AND: Aucune remise n'est appliquée
        """
        # Setup: Create price list
        price_list = PriceList(
            name="Test Price List",
            description="Test PL",
            is_active=True
        )
        db_session.add(price_list)
        db_session.flush()
        
        # Add product to price list
        product_price_list = ProductPriceList(
            price_list_id=price_list.id,
            product_id=sample_product.id,
            price=Decimal("90.00")
        )
        db_session.add(product_price_list)
        
        # Assign price list to customer
        sample_b2b_customer.commercial_conditions.price_list_id = price_list.id
        sample_b2b_customer.commercial_conditions.default_discount_percent = Decimal("10.00")
        db_session.commit()
        db_session.refresh(sample_b2b_customer)
        db_session.refresh(sample_b2b_customer.commercial_conditions)
        
        # Execute: Get price for customer
        pricing_service = PricingService(db_session)
        result = pricing_service.get_price_for_customer(
            product_id=sample_product.id,
            customer_id=sample_b2b_customer.id,
            quantity=Decimal("1.00")
        )
        
        # Assert: Price list price is used, no discount
        assert result.source == 'price_list', f"Expected 'price_list', got '{result.source}'"
        assert result.final_price == Decimal("90.00"), f"Expected 90.00, got {result.final_price}"
        assert result.applied_discount_percent == Decimal("0"), f"Expected 0%, got {result.applied_discount_percent}%"
        assert result.discount_amount == Decimal("0"), f"Expected 0, got {result.discount_amount}"
        assert result.base_price == Decimal("99.99"), f"Expected base price 99.99, got {result.base_price}"
    
    # ==================== SCENARIO 2: Client avec Remise par Défaut (sans Price List) ====================
    
    def test_scenario_2_client_with_default_discount_no_price_list(self, db_session, sample_product, sample_b2b_customer):
        """
        SCENARIO 2: Client avec Remise par Défaut (sans Price List)
        GIVEN: Un produit avec prix de base 100€
        AND: Le client a une remise par défaut de 10%
        AND: Aucune price list n'est assignée au client
        WHEN: On calcule le prix pour ce client
        THEN: Le prix utilisé est 100€ (prix de base)
        AND: Une remise de 10% est appliquée
        AND: Le prix final est 90€
        """
        # Setup: Set customer discount, no price list
        sample_b2b_customer.commercial_conditions.default_discount_percent = Decimal("10.00")
        sample_b2b_customer.commercial_conditions.price_list_id = None
        db_session.commit()
        db_session.refresh(sample_b2b_customer)
        db_session.refresh(sample_b2b_customer.commercial_conditions)
        
        # Execute: Get price for customer
        pricing_service = PricingService(db_session)
        result = pricing_service.get_price_for_customer(
            product_id=sample_product.id,
            customer_id=sample_b2b_customer.id,
            quantity=Decimal("1.00")
        )
        
        # Assert: Customer discount is applied
        assert result.source == 'customer_discount', f"Expected 'customer_discount', got '{result.source}'"
        assert result.base_price == Decimal("99.99"), f"Expected base price 99.99, got {result.base_price}"
        assert result.applied_discount_percent == Decimal("10.00"), f"Expected 10%, got {result.applied_discount_percent}%"
        expected_price = Decimal("99.99") * (Decimal("1") - Decimal("10.00") / Decimal("100"))
        assert abs(result.final_price - expected_price) < Decimal("0.01"), f"Expected {expected_price}, got {result.final_price}"
        assert result.discount_amount > Decimal("0"), f"Expected discount amount > 0, got {result.discount_amount}"
    
    # ==================== SCENARIO 3: Client avec Price List + Remise Manuelle ====================
    
    def test_scenario_3_price_list_with_manual_discount(self, db_session, sample_product, sample_b2b_customer, sample_user):
        """
        SCENARIO 3: Client avec Price List + Remise Manuelle
        GIVEN: Un produit avec prix de base 100€
        AND: Une price list avec prix 90€ assignée au client
        AND: Une remise manuelle de 5% est appliquée sur la ligne
        WHEN: On crée une ligne de devis avec cette remise manuelle
        THEN: Le prix utilisé est 90€ (price list)
        AND: La remise manuelle de 5% est appliquée
        AND: Le prix final est 85.50€
        """
        # Setup: Create price list
        price_list = PriceList(name="Test PL", description="Test", is_active=True)
        db_session.add(price_list)
        db_session.flush()
        
        db_session.add(ProductPriceList(
            price_list_id=price_list.id,
            product_id=sample_product.id,
            price=Decimal("90.00")
        ))
        
        sample_b2b_customer.commercial_conditions.price_list_id = price_list.id
        db_session.commit()
        db_session.refresh(sample_b2b_customer)
        db_session.refresh(sample_b2b_customer.commercial_conditions)
        
        # Execute: Create quote with manual discount
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id
        )
        db_session.add(quote)
        db_session.commit()
        db_session.refresh(quote)
        
        # Add line with manual discount (5%)
        line = quote.add_line(
            product_id=sample_product.id,
            quantity=Decimal("1.00"),
            unit_price=Decimal("90.00"),  # Price list price
            discount_percent=Decimal("5.00")  # Manual discount
        )
        db_session.add(line)
        db_session.commit()
        db_session.refresh(line)
        
        # Assert: Manual discount is applied on price list price
        assert line.unit_price == Decimal("90.00"), f"Expected 90.00, got {line.unit_price}"
        assert line.discount_percent == Decimal("5.00"), f"Expected 5%, got {line.discount_percent}%"
        expected_line_total = Decimal("90.00") * (Decimal("1") - Decimal("5.00") / Decimal("100"))
        assert abs(line.line_total_ht - expected_line_total) < Decimal("0.01"), f"Expected {expected_line_total}, got {line.line_total_ht}"
    
    # ==================== SCENARIO 4: Prix Promotionnel Actif ====================
    
    def test_scenario_4_promotional_price_active_no_discount(self, db_session, sample_product, sample_b2b_customer):
        """
        SCENARIO 4: Prix Promotionnel Actif
        GIVEN: Un produit avec prix de base 100€
        AND: Un prix promotionnel actif de 75€
        AND: Le client a une remise par défaut de 10%
        WHEN: On calcule le prix pour ce client
        THEN: Le prix utilisé est 75€ (promotional price)
        AND: Aucune remise n'est appliquée
        """
        # Setup: Create promotional price
        now = datetime.now()
        promo = ProductPromotionalPrice(
            product_id=sample_product.id,
            price=Decimal("75.00"),
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=30),
            is_active=True
        )
        db_session.add(promo)
        
        sample_b2b_customer.commercial_conditions.default_discount_percent = Decimal("10.00")
        db_session.commit()
        db_session.refresh(sample_b2b_customer)
        db_session.refresh(sample_b2b_customer.commercial_conditions)
        
        # Execute: Get price for customer
        pricing_service = PricingService(db_session)
        result = pricing_service.get_price_for_customer(
            product_id=sample_product.id,
            customer_id=sample_b2b_customer.id,
            quantity=Decimal("1.00")
        )
        
        # Assert: Promotional price is used, no discount
        assert result.source == 'promotional_price', f"Expected 'promotional_price', got '{result.source}'"
        assert result.final_price == Decimal("75.00"), f"Expected 75.00, got {result.final_price}"
        assert result.applied_discount_percent == Decimal("0"), f"Expected 0%, got {result.applied_discount_percent}%"
        assert result.discount_amount == Decimal("0"), f"Expected 0, got {result.discount_amount}"
    
    # ==================== SCENARIO 5: Volume Pricing + Price List ====================
    
    def test_scenario_5_volume_pricing_overrides_price_list(self, db_session, sample_product, sample_b2b_customer):
        """
        SCENARIO 5: Volume Pricing + Price List
        GIVEN: Un produit avec prix de base 100€
        AND: Une price list avec prix 90€ assignée au client
        AND: Un volume pricing de 85€ pour quantité >= 10
        AND: La quantité commandée est 10 unités
        WHEN: On calcule le prix pour ce client
        THEN: Le prix utilisé est 85€ (volume pricing - priorité sur price list)
        AND: Aucune remise n'est appliquée
        """
        # Setup: Create price list and volume pricing
        price_list = PriceList(name="Test PL", description="Test", is_active=True)
        db_session.add(price_list)
        db_session.flush()
        
        db_session.add(ProductPriceList(
            price_list_id=price_list.id,
            product_id=sample_product.id,
            price=Decimal("90.00")
        ))
        
        db_session.add(ProductVolumePricing(
            product_id=sample_product.id,
            min_quantity=Decimal("10.000"),
            price=Decimal("85.00")
        ))
        
        sample_b2b_customer.commercial_conditions.price_list_id = price_list.id
        db_session.commit()
        db_session.refresh(sample_b2b_customer)
        db_session.refresh(sample_b2b_customer.commercial_conditions)
        
        # Execute: Get price for customer with quantity >= 10
        pricing_service = PricingService(db_session)
        result = pricing_service.get_price_for_customer(
            product_id=sample_product.id,
            customer_id=sample_b2b_customer.id,
            quantity=Decimal("10.00")
        )
        
        # Assert: Volume pricing overrides price list
        assert result.source == 'volume_pricing', f"Expected 'volume_pricing', got '{result.source}'"
        assert result.final_price == Decimal("85.00"), f"Expected 85.00, got {result.final_price}"
        assert result.applied_discount_percent == Decimal("0"), f"Expected 0%, got {result.applied_discount_percent}%"
        assert result.discount_amount == Decimal("0"), f"Expected 0, got {result.discount_amount}"
    
    # ==================== SCENARIO 6: Pas de Double Application de Remise ====================
    
    def test_scenario_6_no_double_discount_application(self, db_session, sample_product, sample_b2b_customer, sample_user):
        """
        SCENARIO 6: Pas de Double Application de Remise
        GIVEN: Un produit avec prix de base 100€
        AND: Le client a une remise par défaut de 10%
        WHEN: On ajoute une ligne de devis
        THEN: Le unit_price est 100€ (prix de base)
        AND: Le discount_percent est 10%
        AND: Le line_total_ht est 90€ (100€ - 10%)
        AND: Le discount n'est PAS appliqué deux fois
        """
        # Setup: Set customer discount
        sample_b2b_customer.commercial_conditions.default_discount_percent = Decimal("10.00")
        sample_b2b_customer.commercial_conditions.price_list_id = None
        db_session.commit()
        db_session.refresh(sample_b2b_customer)
        db_session.refresh(sample_b2b_customer.commercial_conditions)
        
        # Execute: Create quote and add line
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id
        )
        db_session.add(quote)
        db_session.commit()
        db_session.refresh(quote)
        
        # Add line (unit_price = 0 will trigger PricingService)
        from app.application.sales.quotes.commands.handlers import AddQuoteLineHandler
        from app.application.sales.quotes.commands.commands import AddQuoteLineCommand
        
        command = AddQuoteLineCommand(
            quote_id=quote.id,
            product_id=sample_product.id,
            quantity=Decimal("1.00"),
            unit_price=Decimal("0"),  # Will trigger PricingService
            discount_percent=Decimal("0")
        )
        handler = AddQuoteLineHandler()
        handler.handle(command)
        
        # Get line from test session (handler uses its own session, so we query from test session)
        from app.domain.models.quote import QuoteLine
        line = db_session.query(QuoteLine).filter(QuoteLine.quote_id == quote.id).first()
        
        # Assert: No double discount application
        # unit_price should be base_price (99.99), not final_price (90.00)
        assert line.unit_price == Decimal("99.99"), f"Expected base price 99.99, got {line.unit_price}"
        assert line.discount_percent == Decimal("10.00"), f"Expected 10%, got {line.discount_percent}%"
        expected_line_total = Decimal("99.99") * (Decimal("1") - Decimal("10.00") / Decimal("100"))
        assert abs(line.line_total_ht - expected_line_total) < Decimal("0.01"), f"Expected {expected_line_total}, got {line.line_total_ht}"
        
        # Verify discount is not applied twice
        # If discount was applied twice, line_total_ht would be ~81€ (90€ - 10%)
        # But it should be ~90€ (99.99€ - 10%)
        assert line.line_total_ht > Decimal("85.00"), "Discount appears to be applied twice!"
    
    # ==================== SCENARIO 7: Remise sur Prix de Base avec Quote ====================
    
    def test_scenario_7_discount_on_base_price_in_quote(self, db_session, sample_product, sample_b2b_customer, sample_user):
        """
        SCENARIO 7: Remise sur Prix de Base avec Quote
        GIVEN: Un produit avec prix de base 100€
        AND: Le client a une remise par défaut de 15%
        AND: Aucune price list, promo, ou volume pricing
        WHEN: On crée un devis avec ce produit
        THEN: Le prix unitaire est 100€ (prix de base)
        AND: La remise de 15% est appliquée
        AND: Le total HT de la ligne est 85€
        """
        # Setup: Set customer discount
        sample_b2b_customer.commercial_conditions.default_discount_percent = Decimal("15.00")
        sample_b2b_customer.commercial_conditions.price_list_id = None
        db_session.commit()
        db_session.refresh(sample_b2b_customer)
        db_session.refresh(sample_b2b_customer.commercial_conditions)
        
        # Execute: Create quote with line
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id
        )
        db_session.add(quote)
        db_session.commit()
        db_session.refresh(quote)
        
        # Add line using PricingService
        from app.application.sales.quotes.commands.handlers import AddQuoteLineHandler
        from app.application.sales.quotes.commands.commands import AddQuoteLineCommand
        
        command = AddQuoteLineCommand(
            quote_id=quote.id,
            product_id=sample_product.id,
            quantity=Decimal("1.00"),
            unit_price=Decimal("0"),  # Will trigger PricingService
            discount_percent=Decimal("0")
        )
        handler = AddQuoteLineHandler()
        handler.handle(command)
        
        # Get line from test session
        from app.domain.models.quote import QuoteLine
        line = db_session.query(QuoteLine).filter(QuoteLine.quote_id == quote.id).first()
        db_session.refresh(quote)
        
        # Assert: Discount is applied correctly
        assert line.unit_price == Decimal("99.99"), f"Expected base price 99.99, got {line.unit_price}"
        assert line.discount_percent == Decimal("15.00"), f"Expected 15%, got {line.discount_percent}%"
        expected_line_total = Decimal("99.99") * (Decimal("1") - Decimal("15.00") / Decimal("100"))
        assert abs(line.line_total_ht - expected_line_total) < Decimal("0.01"), f"Expected {expected_line_total}, got {line.line_total_ht}"
    
    # ==================== SCENARIO 8: Prix Promotionnel Priorité sur Tout ====================
    
    def test_scenario_8_promotional_price_highest_priority(self, db_session, sample_product, sample_b2b_customer):
        """
        SCENARIO 8: Prix Promotionnel Priorité sur Tout
        GIVEN: Un produit avec prix de base 100€
        AND: Une price list avec prix 90€
        AND: Un volume pricing de 85€ (quantité >= 10)
        AND: Un prix promotionnel de 70€ (actif)
        AND: Le client a une remise de 10%
        WHEN: On calcule le prix avec quantité 10
        THEN: Le prix utilisé est 70€ (promotional price - priorité maximale)
        AND: Aucune remise n'est appliquée
        """
        # Setup: Create all pricing mechanisms
        price_list = PriceList(name="Test PL", description="Test", is_active=True)
        db_session.add(price_list)
        db_session.flush()
        
        db_session.add(ProductPriceList(
            price_list_id=price_list.id,
            product_id=sample_product.id,
            price=Decimal("90.00")
        ))
        
        db_session.add(ProductVolumePricing(
            product_id=sample_product.id,
            min_quantity=Decimal("10.000"),
            price=Decimal("85.00")
        ))
        
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
        
        # Execute: Get price for customer
        pricing_service = PricingService(db_session)
        result = pricing_service.get_price_for_customer(
            product_id=sample_product.id,
            customer_id=sample_b2b_customer.id,
            quantity=Decimal("10.00")
        )
        
        # Assert: Promotional price has highest priority
        assert result.source == 'promotional_price', f"Expected 'promotional_price', got '{result.source}'"
        assert result.final_price == Decimal("70.00"), f"Expected 70.00, got {result.final_price}"
        assert result.applied_discount_percent == Decimal("0"), f"Expected 0%, got {result.applied_discount_percent}%"
        assert result.discount_amount == Decimal("0"), f"Expected 0, got {result.discount_amount}"
    
    # ==================== SCENARIO 9: Remise Document sur Price List ====================
    
    def test_scenario_9_document_discount_on_price_list(self, db_session, sample_product, sample_b2b_customer, sample_user):
        """
        SCENARIO 9: Remise Document sur Price List
        GIVEN: Un produit avec prix de base 100€
        AND: Une price list avec prix 90€ assignée au client
        AND: Un devis avec remise document de 5%
        WHEN: On crée une ligne avec le produit
        THEN: Le prix unitaire est 90€ (price list)
        AND: La remise ligne est 0%
        AND: La remise document de 5% est appliquée sur le total
        """
        # Setup: Create price list
        price_list = PriceList(name="Test PL", description="Test", is_active=True)
        db_session.add(price_list)
        db_session.flush()
        
        db_session.add(ProductPriceList(
            price_list_id=price_list.id,
            product_id=sample_product.id,
            price=Decimal("90.00")
        ))
        
        sample_b2b_customer.commercial_conditions.price_list_id = price_list.id
        db_session.commit()
        db_session.refresh(sample_b2b_customer)
        db_session.refresh(sample_b2b_customer.commercial_conditions)
        
        # Execute: Create quote with document discount
        quote = Quote.create(
            customer_id=sample_b2b_customer.id,
            created_by=sample_user.id,
            discount_percent=Decimal("5.00")  # Document discount
        )
        db_session.add(quote)
        db_session.commit()
        db_session.refresh(quote)
        
        # Add line
        line = quote.add_line(
            product_id=sample_product.id,
            quantity=Decimal("1.00"),
            unit_price=Decimal("90.00"),  # Price list price
            discount_percent=Decimal("0")  # No line discount
        )
        db_session.add(line)
        db_session.commit()
        db_session.refresh(line)
        db_session.refresh(quote)
        
        # Assert: Price list price used, document discount applied
        assert line.unit_price == Decimal("90.00"), f"Expected 90.00, got {line.unit_price}"
        assert line.discount_percent == Decimal("0"), f"Expected 0%, got {line.discount_percent}%"
        assert line.line_total_ht == Decimal("90.00"), f"Expected 90.00, got {line.line_total_ht}"
        assert quote.discount_percent == Decimal("5.00"), f"Expected 5%, got {quote.discount_percent}%"
        expected_subtotal = Decimal("90.00") * (Decimal("1") - Decimal("5.00") / Decimal("100"))
        assert abs(quote.subtotal - expected_subtotal) < Decimal("0.01"), f"Expected {expected_subtotal}, got {quote.subtotal}"

