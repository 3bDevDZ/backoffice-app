from app.application.common.cqrs import QueryHandler
from app.domain.models.product import Product
from app.domain.models.category import Category
from app.infrastructure.db import get_session
from .queries import (
    GetProductByIdQuery,
    ListProductsQuery,
    SearchProductsQuery,
    GetCategoryByIdQuery,
    ListCategoriesQuery,
    GetPriceHistoryQuery,
    GetCostHistoryQuery
)
from .product_dto import ProductDTO, CategoryDTO, ProductPriceHistoryDTO, ProductCostHistoryDTO
from typing import List
from sqlalchemy import or_


# Product Query Handlers
class GetProductByIdHandler(QueryHandler):
    def handle(self, query: GetProductByIdQuery) -> ProductDTO:
        with get_session() as session:
            product = session.query(Product).get(query.id)
            if not product:
                raise ValueError("Product not found")
            
            # Load categories
            category_dtos = [
                CategoryDTO(
                    id=cat.id,
                    name=cat.name,
                    code=cat.code,
                    parent_id=cat.parent_id,
                    description=cat.description
                )
                for cat in product.categories
            ]
            
            return ProductDTO(
                id=product.id,
                code=product.code,
                name=product.name,
                description=product.description,
                price=product.price,
                cost=product.cost,
                unit_of_measure=product.unit_of_measure,
                barcode=product.barcode,
                status=product.status,
                category_ids=[cat.id for cat in product.categories],
                categories=category_dtos
            )


class ListProductsHandler(QueryHandler):
    def handle(self, query: ListProductsQuery) -> List[ProductDTO]:
        with get_session() as session:
            # Build query with filters
            q = session.query(Product)
            
            # Search filter
            if query.search:
                search_term = f"%{query.search}%"
                q = q.filter(
                    or_(
                        Product.name.ilike(search_term),
                        Product.code.ilike(search_term),
                        Product.description.ilike(search_term)
                    )
                )
            
            # Category filter
            if query.category_id:
                q = q.join(Product.categories).filter(Category.id == query.category_id)
            
            # Status filter
            if query.status:
                q = q.filter(Product.status == query.status)
            
            # Pagination
            products = q.offset((query.page - 1) * query.per_page).limit(query.per_page).all()
            
            return [
                ProductDTO(
                    id=product.id,
                    code=product.code,
                    name=product.name,
                    description=product.description,
                    price=product.price,
                    cost=product.cost,
                    unit_of_measure=product.unit_of_measure,
                    barcode=product.barcode,
                    status=product.status,
                    category_ids=[cat.id for cat in product.categories],
                    categories=[
                        CategoryDTO(
                            id=cat.id,
                            name=cat.name,
                            code=cat.code,
                            parent_id=cat.parent_id,
                            description=cat.description
                        )
                        for cat in product.categories
                    ]
                )
                for product in products
            ]


class SearchProductsHandler(QueryHandler):
    def handle(self, query: SearchProductsQuery) -> List[ProductDTO]:
        with get_session() as session:
            search_term = f"%{query.search_term}%"
            products = session.query(Product).filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.code.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            ).limit(query.limit).all()
            
            return [
                ProductDTO(
                    id=product.id,
                    code=product.code,
                    name=product.name,
                    description=product.description,
                    price=product.price,
                    cost=product.cost,
                    unit_of_measure=product.unit_of_measure,
                    barcode=product.barcode,
                    status=product.status,
                    category_ids=[cat.id for cat in product.categories]
                )
                for product in products
            ]


# Category Query Handlers
class GetCategoryByIdHandler(QueryHandler):
    def handle(self, query: GetCategoryByIdQuery) -> CategoryDTO:
        with get_session() as session:
            category = session.query(Category).get(query.id)
            if not category:
                raise ValueError("Category not found")
            
            return CategoryDTO(
                id=category.id,
                name=category.name,
                code=category.code,
                parent_id=category.parent_id,
                description=category.description
            )


class ListCategoriesHandler(QueryHandler):
    def handle(self, query: ListCategoriesQuery) -> List[CategoryDTO]:
        with get_session() as session:
            q = session.query(Category)
            
            if query.parent_id is not None:
                q = q.filter(Category.parent_id == query.parent_id)
            
            categories = q.all()
            
            return [
                CategoryDTO(
                    id=cat.id,
                    name=cat.name,
                    code=cat.code,
                    parent_id=cat.parent_id,
                    description=cat.description
                )
                for cat in categories
            ]


# Price History Query Handler
class GetPriceHistoryHandler(QueryHandler):
    """Handler for retrieving product price history."""
    
    def handle(self, query: GetPriceHistoryQuery) -> List[ProductPriceHistoryDTO]:
        """
        Get price history for a product.
        
        Args:
            query: GetPriceHistoryQuery with product_id and optional limit
            
        Returns:
            List of ProductPriceHistoryDTO ordered by changed_at (newest first)
        """
        with get_session() as session:
            from app.domain.models.product import ProductPriceHistory
            from app.domain.models.user import User
            from sqlalchemy.orm import joinedload
            
            # Query price history with user information
            history_query = session.query(ProductPriceHistory).options(
                joinedload(ProductPriceHistory.user)
            ).filter(
                ProductPriceHistory.product_id == query.product_id
            ).order_by(
                ProductPriceHistory.changed_at.desc()
            )
            
            if query.limit:
                history_query = history_query.limit(query.limit)
            
            history_entries = history_query.all()
            
            return [
                ProductPriceHistoryDTO(
                    id=entry.id,
                    product_id=entry.product_id,
                    old_price=entry.old_price,
                    new_price=entry.new_price,
                    changed_by=entry.changed_by,
                    changed_by_username=entry.user.username if entry.user else None,
                    changed_at=entry.changed_at,
                    reason=entry.reason
                )
                for entry in history_entries
            ]


# Cost History Query Handler
class GetCostHistoryHandler(QueryHandler):
    """Handler for retrieving product cost history."""
    
    def handle(self, query: GetCostHistoryQuery) -> List[ProductCostHistoryDTO]:
        """
        Get cost history for a product.
        
        Args:
            query: GetCostHistoryQuery with product_id and optional limit
            
        Returns:
            List of ProductCostHistoryDTO ordered by changed_at (newest first)
        """
        with get_session() as session:
            from app.domain.models.product import ProductCostHistory
            from app.domain.models.user import User
            from sqlalchemy.orm import joinedload
            
            # Query cost history with user information
            history_query = session.query(ProductCostHistory).options(
                joinedload(ProductCostHistory.user)
            ).filter(
                ProductCostHistory.product_id == query.product_id
            ).order_by(
                ProductCostHistory.changed_at.desc()
            )
            
            if query.limit:
                history_query = history_query.limit(query.limit)
            
            history_entries = history_query.all()
            
            return [
                ProductCostHistoryDTO(
                    id=entry.id,
                    product_id=entry.product_id,
                    old_cost=entry.old_cost,
                    new_cost=entry.new_cost,
                    old_stock=entry.old_stock,
                    new_stock=entry.new_stock,
                    purchase_price=entry.purchase_price,
                    quantity_received=entry.quantity_received,
                    changed_by=entry.changed_by,
                    changed_by_username=entry.user.username if entry.user else None,
                    changed_at=entry.changed_at,
                    reason=entry.reason,
                    purchase_order_id=entry.purchase_order_id,
                    purchase_order_line_id=entry.purchase_order_line_id
                )
                for entry in history_entries
            ]