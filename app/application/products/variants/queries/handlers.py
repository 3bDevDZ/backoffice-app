"""Query handlers for Product Variant management."""
from app.application.common.cqrs import QueryHandler
from app.domain.models.product import ProductVariant
from app.infrastructure.db import get_session
from .queries import (
    GetVariantByIdQuery,
    GetVariantsByProductQuery,
    ListVariantsQuery
)
from .variant_dto import ProductVariantDTO
from typing import List
from sqlalchemy import or_


class GetVariantByIdHandler(QueryHandler):
    """Handler for getting a variant by ID."""
    
    def handle(self, query: GetVariantByIdQuery) -> ProductVariantDTO:
        """
        Get a variant by ID.
        
        Args:
            query: GetVariantByIdQuery with variant ID
            
        Returns:
            ProductVariantDTO
            
        Raises:
            ValueError: If variant not found
        """
        with get_session() as session:
            variant = session.get(ProductVariant, query.id)
            if not variant:
                raise ValueError(f"Variant with ID {query.id} not found.")
            
            return ProductVariantDTO(
                id=variant.id,
                product_id=variant.product_id,
                product_code=variant.product.code,
                product_name=variant.product.name,
                code=variant.code,
                name=variant.name,
                attributes=variant.attributes,
                price=variant.price,
                cost=variant.cost,
                barcode=variant.barcode,
                status=variant.status,
                created_at=variant.created_at
            )


class GetVariantsByProductHandler(QueryHandler):
    """Handler for getting all variants for a product."""
    
    def handle(self, query: GetVariantsByProductQuery) -> List[ProductVariantDTO]:
        """
        Get all variants for a product.
        
        Args:
            query: GetVariantsByProductQuery with product ID
            
        Returns:
            List of ProductVariantDTO
        """
        with get_session() as session:
            q = session.query(ProductVariant).filter(
                ProductVariant.product_id == query.product_id
            )
            
            if not query.include_archived:
                q = q.filter(ProductVariant.status == 'active')
            
            variants = q.order_by(ProductVariant.code).all()
            
            return [
                ProductVariantDTO(
                    id=variant.id,
                    product_id=variant.product_id,
                    product_code=variant.product.code,
                    product_name=variant.product.name,
                    code=variant.code,
                    name=variant.name,
                    attributes=variant.attributes,
                    price=variant.price,
                    cost=variant.cost,
                    barcode=variant.barcode,
                    status=variant.status,
                    created_at=variant.created_at
                )
                for variant in variants
            ]


class ListVariantsHandler(QueryHandler):
    """Handler for listing variants with filters."""
    
    def handle(self, query: ListVariantsQuery) -> dict:
        """
        List variants with optional filters and pagination.
        
        Args:
            query: ListVariantsQuery with filters and pagination
            
        Returns:
            Dictionary with 'items' (list of DTOs) and 'total' (count)
        """
        with get_session() as session:
            q = session.query(ProductVariant)
            
            # Filter by product_id if provided
            if query.product_id:
                q = q.filter(ProductVariant.product_id == query.product_id)
            
            # Filter by status if provided
            if query.status:
                q = q.filter(ProductVariant.status == query.status)
            
            # Search filter (code, name, or product name)
            if query.search:
                search_term = f"%{query.search}%"
                from app.domain.models.product import Product
                q = q.join(Product, ProductVariant.product_id == Product.id).filter(
                    or_(
                        ProductVariant.code.ilike(search_term),
                        ProductVariant.name.ilike(search_term),
                        Product.name.ilike(search_term)
                    )
                )
            
            # Get total count
            total = q.count()
            
            # Apply pagination
            offset = (query.page - 1) * query.per_page
            variants = q.order_by(ProductVariant.product_id, ProductVariant.code).offset(offset).limit(query.per_page).all()
            
            items = [
                ProductVariantDTO(
                    id=variant.id,
                    product_id=variant.product_id,
                    product_code=variant.product.code,
                    product_name=variant.product.name,
                    code=variant.code,
                    name=variant.name,
                    attributes=variant.attributes,
                    price=variant.price,
                    cost=variant.cost,
                    barcode=variant.barcode,
                    status=variant.status,
                    created_at=variant.created_at
                )
                for variant in variants
            ]
            
            return {
                'items': items,
                'total': total,
                'page': query.page,
                'per_page': query.per_page
            }

