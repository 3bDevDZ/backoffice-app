"""Query handlers for Price List management."""
from datetime import datetime
from typing import List, Optional
from app.application.common.cqrs import QueryHandler
from app.domain.models.product import PriceList, ProductPriceList, Product, ProductVolumePricing, ProductPromotionalPrice
from app.infrastructure.db import get_session
from .queries import (
    ListPriceListsQuery,
    GetPriceListByIdQuery,
    GetProductsInPriceListQuery,
    GetVolumePricingQuery,
    GetActivePromotionalPricesQuery,
    GetPromotionalPricesByProductQuery
)
from .pricing_dto import PriceListDTO, ProductPriceListDTO, ProductVolumePricingDTO, ProductPromotionalPriceDTO
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload


class ListPriceListsHandler(QueryHandler):
    """Handler for listing price lists."""
    
    def handle(self, query: ListPriceListsQuery) -> dict:
        """
        List price lists with pagination and filtering.
        
        Args:
            query: ListPriceListsQuery with pagination and filter parameters
            
        Returns:
            Dictionary with 'items', 'total', 'page', 'per_page'
        """
        with get_session() as session:
            q = session.query(PriceList)
            
            # Filter by active status
            if query.is_active is not None:
                q = q.filter(PriceList.is_active == query.is_active)
            
            # Search by name or description
            if query.search:
                search_term = f"%{query.search}%"
                q = q.filter(
                    or_(
                        PriceList.name.ilike(search_term),
                        PriceList.description.ilike(search_term)
                    )
                )
            
            # Get total count before pagination
            total = q.count()
            
            # Apply pagination
            price_lists = q.order_by(PriceList.name).offset(
                (query.page - 1) * query.per_page
            ).limit(query.per_page).all()
            
            # Get product counts for each price list
            items = []
            for price_list in price_lists:
                product_count = session.query(func.count(ProductPriceList.id)).filter(
                    ProductPriceList.price_list_id == price_list.id
                ).scalar() or 0
                
                items.append(PriceListDTO(
                    id=price_list.id,
                    name=price_list.name,
                    description=price_list.description,
                    is_active=price_list.is_active,
                    created_at=price_list.created_at,
                    updated_at=price_list.updated_at,
                    product_count=product_count
                ))
            
            return {
                'items': items,
                'total': total,
                'page': query.page,
                'per_page': query.per_page
            }


class GetPriceListByIdHandler(QueryHandler):
    """Handler for getting a price list by ID."""
    
    def handle(self, query: GetPriceListByIdQuery) -> PriceListDTO:
        """
        Get a price list by ID.
        
        Args:
            query: GetPriceListByIdQuery with price list ID
            
        Returns:
            PriceListDTO
            
        Raises:
            ValueError: If price list not found
        """
        with get_session() as session:
            price_list = session.get(PriceList, query.id)
            if not price_list:
                raise ValueError(f"Price list with ID {query.id} not found.")
            
            # Get product count
            product_count = session.query(func.count(ProductPriceList.id)).filter(
                ProductPriceList.price_list_id == price_list.id
            ).scalar() or 0
            
            return PriceListDTO(
                id=price_list.id,
                name=price_list.name,
                description=price_list.description,
                is_active=price_list.is_active,
                created_at=price_list.created_at,
                updated_at=price_list.updated_at,
                product_count=product_count
            )


class GetProductsInPriceListHandler(QueryHandler):
    """Handler for getting all products in a price list."""
    
    def handle(self, query: GetProductsInPriceListQuery) -> dict:
        """
        Get all products in a price list with pagination.
        
        Args:
            query: GetProductsInPriceListQuery with price_list_id and pagination
            
        Returns:
            Dictionary with 'items', 'total', 'page', 'per_page'
            
        Raises:
            ValueError: If price list not found
        """
        with get_session() as session:
            # Verify price list exists
            price_list = session.get(PriceList, query.price_list_id)
            if not price_list:
                raise ValueError(f"Price list with ID {query.price_list_id} not found.")
            
            # Query products in price list - always join with Product for ordering
            q = session.query(ProductPriceList).options(
                joinedload(ProductPriceList.product)
            ).join(
                Product, ProductPriceList.product_id == Product.id
            ).filter(
                ProductPriceList.price_list_id == query.price_list_id
            )
            
            # Search by product name or code
            if query.search:
                search_term = f"%{query.search}%"
                q = q.filter(
                    or_(
                        Product.name.ilike(search_term),
                        Product.code.ilike(search_term)
                    )
                )
            
            # Get total count before pagination
            total = q.count()
            
            # Apply pagination with ordering
            product_price_lists = q.order_by(Product.name).offset(
                (query.page - 1) * query.per_page
            ).limit(query.per_page).all()
            
            items = []
            for ppl in product_price_lists:
                product = ppl.product
                items.append(ProductPriceListDTO(
                    id=ppl.id,
                    price_list_id=ppl.price_list_id,
                    price_list_name=price_list.name,
                    product_id=ppl.product_id,
                    product_code=product.code,
                    product_name=product.name,
                    price=ppl.price,
                    base_price=product.price,  # Product's base price
                    created_at=ppl.created_at,
                    updated_at=ppl.updated_at
                ))
            
            return {
                'items': items,
                'total': total,
                'page': query.page,
                'per_page': query.per_page
            }


# ProductVolumePricing Handler
class GetVolumePricingHandler(QueryHandler):
    """Handler for getting volume pricing tiers for a product."""
    
    def handle(self, query: GetVolumePricingQuery) -> List[ProductVolumePricingDTO]:
        """
        Get all volume pricing tiers for a product, ordered by min_quantity.
        
        Args:
            query: GetVolumePricingQuery with product_id
            
        Returns:
            List of ProductVolumePricingDTO ordered by min_quantity ascending
            
        Raises:
            ValueError: If product not found
        """
        with get_session() as session:
            # Verify product exists
            product = session.get(Product, query.product_id)
            if not product:
                raise ValueError(f"Product with ID {query.product_id} not found.")
            
            # Get all volume pricing tiers for this product, ordered by min_quantity
            volume_pricing_tiers = session.query(ProductVolumePricing).filter(
                ProductVolumePricing.product_id == query.product_id
            ).order_by(ProductVolumePricing.min_quantity.asc()).all()
            
            # Convert to DTOs
            items = []
            for tier in volume_pricing_tiers:
                items.append(ProductVolumePricingDTO(
                    id=tier.id,
                    product_id=tier.product_id,
                    min_quantity=tier.min_quantity,
                    max_quantity=tier.max_quantity,
                    price=tier.price,
                    created_at=tier.created_at,
                    updated_at=tier.updated_at
                ))
            
            return items


# ProductPromotionalPrice Handlers
class GetActivePromotionalPricesHandler(QueryHandler):
    """Handler for getting active promotional prices with filtering."""
    
    def handle(self, query: GetActivePromotionalPricesQuery) -> dict:
        from app.application.products.pricing.queries.queries import GetActivePromotionalPricesQuery
        from app.application.products.pricing.queries.pricing_dto import ProductPromotionalPriceDTO
        from datetime import date as date_type
        
        with get_session() as session:
            now = datetime.now()
            
            # Build query - join with Product for search
            db_query = session.query(ProductPromotionalPrice).join(Product)
            
            # Filter by product_id if provided
            if query.product_id is not None:
                db_query = db_query.filter(ProductPromotionalPrice.product_id == query.product_id)
            
            # Search filter (product name or code)
            if query.search:
                search_term = f"%{query.search}%"
                db_query = db_query.filter(
                    or_(
                        Product.name.ilike(search_term),
                        Product.code.ilike(search_term)
                    )
                )
            
            # Date filters
            if query.date_from:
                try:
                    if isinstance(query.date_from, str):
                        date_from = datetime.fromisoformat(query.date_from).date()
                    else:
                        date_from = query.date_from
                    db_query = db_query.filter(ProductPromotionalPrice.start_date >= datetime.combine(date_from, datetime.min.time()))
                except (ValueError, AttributeError):
                    pass
            
            if query.date_to:
                try:
                    if isinstance(query.date_to, str):
                        date_to = datetime.fromisoformat(query.date_to).date()
                    else:
                        date_to = query.date_to
                    db_query = db_query.filter(ProductPromotionalPrice.end_date <= datetime.combine(date_to, datetime.max.time()))
                except (ValueError, AttributeError):
                    pass
            
            # Get all promotions (we'll filter by status after)
            promotional_prices = db_query.order_by(ProductPromotionalPrice.start_date.desc()).all()
            
            items = []
            for promo in promotional_prices:
                # Determine status
                promo_status = 'active'
                if promo.end_date < now:
                    promo_status = 'expired'
                elif promo.start_date > now:
                    promo_status = 'upcoming'
                
                # Filter by status if provided
                if query.status and query.status != 'all':
                    if promo_status != query.status:
                        continue
                
                # Only include active promotions (is_active flag)
                if not promo.is_active:
                    continue
                
                # Get product info for DTO
                product = session.get(Product, promo.product_id)
                
                items.append(ProductPromotionalPriceDTO(
                    id=promo.id,
                    product_id=promo.product_id,
                    product_code=product.code if product else None,
                    product_name=product.name if product else None,
                    price=promo.price,
                    start_date=promo.start_date,
                    end_date=promo.end_date,
                    description=promo.description,
                    is_active=promo.is_active,
                    created_at=promo.created_at,
                    updated_at=promo.updated_at,
                    created_by=promo.created_by
                ))
            
            # Get total count before pagination
            total = len(items)
            
            # Apply pagination
            start = (query.page - 1) * query.per_page
            end = start + query.per_page
            items = items[start:end]
            
            return {
                'items': items,
                'total': total,
                'page': query.page,
                'per_page': query.per_page,
                'pages': (total + query.per_page - 1) // query.per_page if query.per_page > 0 else 1
            }


class GetPromotionalPricesByProductHandler(QueryHandler):
    """Handler for getting all promotional prices for a product."""
    
    def handle(self, query: GetPromotionalPricesByProductQuery) -> List[ProductPromotionalPriceDTO]:
        from app.application.products.pricing.queries.pricing_dto import ProductPromotionalPriceDTO
        
        with get_session() as session:
            product = session.get(Product, query.product_id)
            if not product:
                raise ValueError(f"Product with ID {query.product_id} not found.")
            
            db_query = session.query(ProductPromotionalPrice).filter(
                ProductPromotionalPrice.product_id == query.product_id
            )
            
            if not query.include_expired:
                now = datetime.now()
                db_query = db_query.filter(
                    ProductPromotionalPrice.end_date >= now
                )
            
            promotional_prices = db_query.order_by(ProductPromotionalPrice.start_date.desc()).all()
            
            items = []
            for promo in promotional_prices:
                items.append(ProductPromotionalPriceDTO(
                    id=promo.id,
                    product_id=promo.product_id,
                    price=promo.price,
                    start_date=promo.start_date,
                    end_date=promo.end_date,
                    description=promo.description,
                    is_active=promo.is_active,
                    created_at=promo.created_at,
                    updated_at=promo.updated_at,
                    created_by=promo.created_by
                ))
            
            return items

