"""Pricing service for complex price calculation and discount application."""
from typing import List, Optional, Dict, Any
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.domain.models.product import Product, ProductPromotionalPrice, ProductVolumePricing, ProductPriceList
from app.domain.models.customer import Customer, CommercialConditions
from app.domain.models.quote import Quote, QuoteLine


@dataclass
class PriceCalculationResult:
    """Result of a price calculation."""
    base_price: Decimal
    customer_price: Decimal
    applied_discount_percent: Decimal
    final_price: Decimal
    discount_amount: Decimal
    source: str  # 'base', 'customer_discount', 'price_list', etc.


@dataclass
class DiscountSuggestion:
    """Suggestion for applying a discount."""
    type: str  # 'volume', 'loyalty', 'seasonal', 'threshold'
    description: str
    discount_percent: Decimal
    condition: str  # Description of condition to meet
    current_value: Decimal
    threshold_value: Decimal


@dataclass
class MarginCalculation:
    """Result of margin calculation."""
    total_cost: Decimal
    total_revenue: Decimal
    gross_margin: Decimal
    gross_margin_percent: Decimal
    net_margin: Decimal  # After additional costs (future)
    net_margin_percent: Decimal


class PricingService:
    """
    Service for complex pricing calculations and discount application.
    Contains business logic that spans multiple aggregates (Product, Customer, Quote).
    """
    
    def __init__(self, session: Session):
        """
        Initialize the pricing service.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
    
    # ==================== Price Calculation Methods ====================
    
    def get_base_price(self, product_id: int) -> Decimal:
        """
        Get the base price of a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            Base price of the product
            
        Raises:
            ValueError: If product not found
        """
        product = self.session.get(Product, product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found.")
        
        return product.price
    
    def get_price_for_customer(
        self,
        product_id: int,
        customer_id: int,
        quantity: Decimal = Decimal(1)
    ) -> PriceCalculationResult:
        """
        Get price for a product considering customer's commercial conditions.
        
        Args:
            product_id: Product ID
            customer_id: Customer ID
            quantity: Quantity (for future volume discounts)
            
        Returns:
            PriceCalculationResult with calculated price and applied discounts
        """
        # Get base price
        base_price = self.get_base_price(product_id)
        
        # Get customer and commercial conditions
        customer = self.session.get(Customer, customer_id)
        if not customer:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        
        # Start with base price
        customer_price = base_price
        applied_discount_percent = Decimal(0)
        source = 'base'
        
        # PRIORITY 1: Check active promotional prices (HIGHEST PRIORITY)
        now = datetime.now()
        promotional_price = self.session.query(ProductPromotionalPrice).filter(
            ProductPromotionalPrice.product_id == product_id,
            ProductPromotionalPrice.is_active == True,
            ProductPromotionalPrice.start_date <= now,
            ProductPromotionalPrice.end_date >= now
        ).order_by(ProductPromotionalPrice.start_date.desc()).first()
        
        if promotional_price:
            customer_price = promotional_price.price
            source = 'promotional_price'
        
        # PRIORITY 2: Check volume pricing tiers (quantity-based pricing)
        # This takes precedence over price list if quantity matches a tier
        elif quantity > 0:
            # Get volume pricing tiers for this product, ordered by min_quantity descending
            # to find the highest applicable tier first
            volume_tier = self.session.query(ProductVolumePricing).filter(
                ProductVolumePricing.product_id == product_id,
                ProductVolumePricing.min_quantity <= quantity,
                # Check if quantity is within tier range (max_quantity is NULL for unlimited)
                (
                    (ProductVolumePricing.max_quantity.is_(None)) |
                    (ProductVolumePricing.max_quantity >= quantity)
                )
            ).order_by(ProductVolumePricing.min_quantity.desc()).first()
            
            if volume_tier:
                # Use volume pricing tier price (overrides price list)
                customer_price = volume_tier.price
                source = 'volume_pricing'
        
        # PRIORITY 3: Check if customer has a price list assigned
        if source == 'base' and customer.commercial_conditions and customer.commercial_conditions.price_list_id:
            # Get price from price list
            product_price_list = self.session.query(ProductPriceList).filter(
                ProductPriceList.price_list_id == customer.commercial_conditions.price_list_id,
                ProductPriceList.product_id == product_id
            ).first()
            
            if product_price_list:
                # Use price list price
                customer_price = product_price_list.price
                source = 'price_list'
        
        # PRIORITY 4: Apply customer's default discount if exists (only if not using other pricing)
        if source == 'base' and customer.commercial_conditions:
            conditions = customer.commercial_conditions
            if conditions.default_discount_percent > 0:
                applied_discount_percent = conditions.default_discount_percent
                discount_amount = base_price * (applied_discount_percent / Decimal(100))
                customer_price = base_price - discount_amount
                source = 'customer_discount'
        
        # TODO: Future enhancements
        # - Apply negotiated prices
        
        final_price = customer_price
        
        # Only calculate discount_amount if we actually applied a discount (customer_discount)
        # For price lists, promotional prices, and volume pricing, the price difference
        # is NOT a discount, it's a different pricing tier
        discount_amount = Decimal(0)
        if source == 'customer_discount':
            discount_amount = base_price - final_price
        elif applied_discount_percent > 0:
            # If we have a discount percent but source is not customer_discount,
            # something is wrong - reset it
            applied_discount_percent = Decimal(0)
        
        return PriceCalculationResult(
            base_price=base_price,
            customer_price=customer_price,
            applied_discount_percent=applied_discount_percent,
            final_price=final_price,
            discount_amount=discount_amount,
            source=source
        )
    
    def calculate_line_discount(
        self,
        line: QuoteLine,
        customer_id: int
    ) -> Decimal:
        """
        Calculate discount for a quote line considering customer conditions.
        
        Args:
            line: Quote line
            customer_id: Customer ID
            
        Returns:
            Suggested discount percentage
        """
        # Get customer conditions
        customer = self.session.get(Customer, customer_id)
        if not customer:
            return Decimal(0)
        
        suggested_discount = Decimal(0)
        
        # Apply customer's default discount if not already applied
        if customer.commercial_conditions:
            conditions = customer.commercial_conditions
            if conditions.default_discount_percent > 0:
                # Only suggest if line doesn't already have a discount
                if line.discount_percent == 0:
                    suggested_discount = conditions.default_discount_percent
        
        return suggested_discount
    
    def calculate_document_discount(
        self,
        customer_id: int,
        current_discount_percent: Decimal = Decimal(0)
    ) -> Decimal:
        """
        Calculate document-level discount for a customer.
        
        Args:
            customer_id: Customer ID
            current_discount_percent: Current discount on quote (to avoid duplicate)
            
        Returns:
            Suggested discount percentage
        """
        # Get customer conditions
        customer = self.session.get(Customer, customer_id)
        if not customer:
            return Decimal(0)
        
        suggested_discount = Decimal(0)
        
        # Apply customer's default discount if not already applied
        if customer.commercial_conditions:
            conditions = customer.commercial_conditions
            if conditions.default_discount_percent > 0:
                # Only suggest if quote doesn't already have a discount
                if current_discount_percent == 0:
                    suggested_discount = conditions.default_discount_percent
        
        return suggested_discount
    
    def suggest_discounts(self, quote: Quote) -> List[DiscountSuggestion]:
        """
        Suggest applicable discounts for a quote.
        
        Args:
            quote: Quote to analyze
            
        Returns:
            List of discount suggestions
        """
        suggestions = []
        
        if not quote.lines:
            return suggestions
        
        # Calculate totals
        subtotal = sum(line.line_total_ht for line in quote.lines)
        
        # Get customer conditions
        customer = self.session.get(Customer, quote.customer_id)
        if customer and customer.commercial_conditions:
            conditions = customer.commercial_conditions
            
            # Suggestion: Customer default discount
            if conditions.default_discount_percent > 0 and quote.discount_percent == 0:
                suggestions.append(DiscountSuggestion(
                    type='customer_default',
                    description=f"Remise client par défaut ({conditions.default_discount_percent}%)",
                    discount_percent=conditions.default_discount_percent,
                    condition="Appliquer la remise client par défaut",
                    current_value=Decimal(0),
                    threshold_value=Decimal(0)
                ))
        
        # Suggestion: Volume discount thresholds (future)
        # Example: "Vous êtes à 50€ du seuil pour une remise de 5%"
        volume_thresholds = [
            (Decimal('1000'), Decimal('2')),
            (Decimal('5000'), Decimal('5')),
            (Decimal('10000'), Decimal('10')),
        ]
        
        for threshold, discount in volume_thresholds:
            if subtotal < threshold:
                remaining = threshold - subtotal
                suggestions.append(DiscountSuggestion(
                    type='volume_threshold',
                    description=f"Remise volume de {discount}%",
                    discount_percent=discount,
                    condition=f"Ajouter {remaining:.2f} € pour atteindre le seuil",
                    current_value=subtotal,
                    threshold_value=threshold
                ))
                break  # Only show next threshold
        
        # Suggestion: Quantity-based discounts (future)
        # Could suggest discounts based on total quantity across all lines
        
        return suggestions
    
    # ==================== Validation Methods ====================
    
    def validate_minimum_price(
        self,
        product_id: int,
        unit_price: Decimal,
        customer_id: Optional[int] = None
    ) -> bool:
        """
        Validate that a price meets minimum requirements.
        
        Args:
            product_id: Product ID
            unit_price: Unit price to validate
            customer_id: Optional customer ID for customer-specific rules
            
        Returns:
            True if price is valid, False otherwise
        """
        product = self.session.get(Product, product_id)
        if not product:
            return False
        
        # Check if product has a minimum price (future: product.min_price)
        # For now, just check that price is not negative
        if unit_price < 0:
            return False
        
        # TODO: Future validations
        # - Check product.min_price if exists
        # - Check customer-specific minimum prices
        # - Check price list minimums
        
        return True
    
    def validate_price_rules(self, quote: Quote) -> List[str]:
        """
        Validate all pricing rules for a quote.
        
        Args:
            quote: Quote to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not quote.lines:
            return errors
        
        # Validate each line
        for line in quote.lines:
            # Validate minimum price
            if not self.validate_minimum_price(line.product_id, line.unit_price, quote.customer_id):
                errors.append(
                    f"Prix invalide pour le produit {line.product_id}: "
                    f"{line.unit_price} (doit être >= 0)"
                )
            
            # Validate discount percentage
            if line.discount_percent < 0 or line.discount_percent > 100:
                errors.append(
                    f"Remise invalide pour la ligne {line.id}: "
                    f"{line.discount_percent}% (doit être entre 0 et 100)"
                )
        
        # Validate document discount
        if quote.discount_percent < 0 or quote.discount_percent > 100:
            errors.append(
                f"Remise document invalide: {quote.discount_percent}% "
                f"(doit être entre 0 et 100)"
            )
        
        return errors
    
    # ==================== Margin Calculation Methods ====================
    
    def calculate_margin(self, quote: Quote) -> MarginCalculation:
        """
        Calculate margin for a quote.
        
        Args:
            quote: Quote to calculate margin for
            
        Returns:
            MarginCalculation with margin details
        """
        total_cost = Decimal(0)
        total_revenue = Decimal(0)
        
        if not quote.lines:
            return MarginCalculation(
                total_cost=Decimal(0),
                total_revenue=Decimal(0),
                gross_margin=Decimal(0),
                gross_margin_percent=Decimal(0),
                net_margin=Decimal(0),
                net_margin_percent=Decimal(0)
            )
        
        # Calculate cost and revenue for each line
        for line in quote.lines:
            product = self.session.get(Product, line.product_id)
            if product and product.cost:
                # Cost for this line
                line_cost = product.cost * line.quantity
                total_cost += line_cost
            
            # Revenue for this line (HT)
            total_revenue += line.line_total_ht
        
        # Calculate margins
        gross_margin = total_revenue - total_cost
        gross_margin_percent = (
            (gross_margin / total_revenue * Decimal(100))
            if total_revenue > 0 else Decimal(0)
        )
        
        # Net margin (same as gross for now, no additional costs)
        net_margin = gross_margin
        net_margin_percent = gross_margin_percent
        
        return MarginCalculation(
            total_cost=total_cost,
            total_revenue=total_revenue,
            gross_margin=gross_margin,
            gross_margin_percent=gross_margin_percent,
            net_margin=net_margin,
            net_margin_percent=net_margin_percent
        )
    
    def calculate_profitability(self, quote: Quote) -> Dict[str, Any]:
        """
        Calculate profitability metrics for a quote.
        
        Args:
            quote: Quote to analyze
            
        Returns:
            Dictionary with profitability metrics
        """
        margin = self.calculate_margin(quote)
        
        return {
            'total_cost': float(margin.total_cost),
            'total_revenue_ht': float(margin.total_revenue),
            'total_revenue_ttc': float(quote.total),
            'gross_margin': float(margin.gross_margin),
            'gross_margin_percent': float(margin.gross_margin_percent),
            'net_margin': float(margin.net_margin),
            'net_margin_percent': float(margin.net_margin_percent),
            'is_profitable': margin.gross_margin > 0,
            'profitability_level': (
                'high' if margin.gross_margin_percent > 30 else
                'medium' if margin.gross_margin_percent > 15 else
                'low' if margin.gross_margin_percent > 0 else
                'negative'
            )
        }
    
    # ==================== Price Application Methods ====================
    
    def apply_customer_pricing(self, quote: Quote) -> Quote:
        """
        Apply customer pricing rules to a quote (suggest prices and discounts).
        This method does not modify the quote, but can be used to get suggestions.
        
        Args:
            quote: Quote to apply pricing to
            
        Returns:
            Quote (unchanged, but ready for suggestions)
        """
        # This method can be extended to automatically apply customer pricing
        # For now, it just validates and returns the quote
        
        # Validate pricing rules
        errors = self.validate_price_rules(quote)
        if errors:
            raise ValueError(f"Pricing validation errors: {', '.join(errors)}")
        
        return quote
    
    def apply_volume_discounts(
        self,
        lines: List[QuoteLine],
        customer_id: int
    ) -> Dict[str, Any]:
        """
        Calculate and suggest volume discounts based on quantities.
        
        Args:
            lines: List of quote lines
            customer_id: Customer ID
            
        Returns:
            Dictionary with discount suggestions
        """
        total_quantity = sum(line.quantity for line in lines)
        total_amount = sum(line.line_total_ht for line in lines)
        
        suggestions = {
            'total_quantity': float(total_quantity),
            'total_amount': float(total_amount),
            'volume_discounts': []
        }
        
        # Volume discount rules (future: could be in database)
        volume_rules = [
            {'min_quantity': Decimal('100'), 'discount': Decimal('3')},
            {'min_quantity': Decimal('500'), 'discount': Decimal('5')},
            {'min_quantity': Decimal('1000'), 'discount': Decimal('10')},
        ]
        
        for rule in volume_rules:
            if total_quantity >= rule['min_quantity']:
                suggestions['volume_discounts'].append({
                    'threshold': float(rule['min_quantity']),
                    'discount_percent': float(rule['discount']),
                    'applicable': True
                })
            else:
                remaining = rule['min_quantity'] - total_quantity
                suggestions['volume_discounts'].append({
                    'threshold': float(rule['min_quantity']),
                    'discount_percent': float(rule['discount']),
                    'applicable': False,
                    'remaining_quantity': float(remaining)
                })
        
        return suggestions

