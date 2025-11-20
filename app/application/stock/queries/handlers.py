"""Query handlers for stock management."""
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import joinedload

from app.application.common.cqrs import QueryHandler
from app.infrastructure.db import get_session
from app.domain.models.stock import StockItem, StockMovement, Location, Site
from app.domain.models.product import Product
from app.domain.models.user import User
from app.domain.models.order import Order
from app.domain.models.purchase import PurchaseOrder

from .queries import (
    GetStockLevelsQuery,
    GetStockAlertsQuery,
    GetStockMovementsQuery,
    GetLocationHierarchyQuery,
    GetStockItemByIdQuery,
    GetLocationByIdQuery,
    GlobalStockQuery
)
from .stock_dto import (
    StockItemDTO,
    StockMovementDTO,
    StockAlertDTO,
    LocationDTO,
    GlobalStockItemDTO
)


class GetStockLevelsHandler(QueryHandler):
    """Handler for GetStockLevelsQuery."""
    
    def handle(self, query: GetStockLevelsQuery) -> List[StockItemDTO]:
        with get_session() as session:
            # Build query
            q = session.query(StockItem).options(
                joinedload(StockItem.product),
                joinedload(StockItem.location)
            )
            
            # Apply filters
            if query.product_id:
                q = q.filter(StockItem.product_id == query.product_id)
            
            if query.location_id:
                q = q.filter(StockItem.location_id == query.location_id)
            
            if query.variant_id is not None:
                q = q.filter(StockItem.variant_id == query.variant_id)
            # Note: By default, we include both products without variants (variant_id is None) 
            # and products with variants (variant_id is not None)
            
            if query.min_quantity is not None:
                q = q.filter(StockItem.physical_quantity >= query.min_quantity)
            
            if not query.include_zero:
                q = q.filter(StockItem.physical_quantity > 0)
            
            # Search by product code or name
            if query.search:
                search_term = f"%{query.search}%"
                q = q.join(Product).filter(
                    or_(
                        Product.code.ilike(search_term),
                        Product.name.ilike(search_term)
                    )
                )
            
            # Pagination
            total = q.count()
            offset = (query.page - 1) * query.per_page
            items = q.offset(offset).limit(query.per_page).all()
            
            # Pre-load variants for all items to avoid N+1 queries
            variant_ids = [item.variant_id for item in items if item.variant_id]
            variants_dict = {}
            if variant_ids:
                from app.domain.models.product import ProductVariant
                variants = session.query(ProductVariant).filter(ProductVariant.id.in_(variant_ids)).all()
                variants_dict = {v.id: v for v in variants}
            
            # Convert to DTOs
            return [
                self._to_stock_item_dto(item, variants_dict)
                for item in items
            ]
    
    def _to_stock_item_dto(self, item: StockItem, variants_dict: dict = None) -> StockItemDTO:
        """Convert StockItem to DTO."""
        is_below_minimum = item.is_below_minimum() if item.min_stock else False
        is_out_of_stock = item.physical_quantity <= 0
        is_overstock = item.max_stock and item.physical_quantity > item.max_stock
        
        # Get variant info if exists
        variant_code = None
        variant_name = None
        if item.variant_id and variants_dict:
            variant = variants_dict.get(item.variant_id)
            if variant:
                variant_code = variant.code
                variant_name = variant.name
        
        return StockItemDTO(
            id=item.id,
            product_id=item.product_id,
            product_code=item.product.code if item.product else None,
            product_name=item.product.name if item.product else None,
            variant_id=item.variant_id,
            variant_code=variant_code,
            variant_name=variant_name,
            location_id=item.location_id,
            location_code=item.location.code if item.location else None,
            location_name=item.location.name if item.location else None,
            physical_quantity=item.physical_quantity,
            reserved_quantity=item.reserved_quantity,
            available_quantity=item.available_quantity,
            min_stock=item.min_stock,
            max_stock=item.max_stock,
            reorder_point=item.reorder_point,
            reorder_quantity=item.reorder_quantity,
            valuation_method=item.valuation_method,
            last_movement_at=item.last_movement_at,
            created_at=item.created_at,
            updated_at=item.updated_at,
            is_below_minimum=is_below_minimum,
            is_out_of_stock=is_out_of_stock,
            is_overstock=is_overstock
        )


class GetStockAlertsHandler(QueryHandler):
    """Handler for GetStockAlertsQuery."""
    
    def handle(self, query: GetStockAlertsQuery) -> List[StockAlertDTO]:
        with get_session() as session:
            # Build query for stock items with alerts
            q = session.query(StockItem).options(
                joinedload(StockItem.product),
                joinedload(StockItem.location)
            )
            
            # Filter by location if specified
            if query.location_id:
                q = q.filter(StockItem.location_id == query.location_id)
            
            # Get all stock items
            items = q.all()
            
            alerts = []
            
            for item in items:
                # Check for out of stock
                if item.physical_quantity <= 0:
                    if not query.alert_type or query.alert_type == 'out_of_stock':
                        alerts.append(StockAlertDTO(
                            stock_item_id=item.id,
                            product_id=item.product_id,
                            product_code=item.product.code if item.product else '',
                            product_name=item.product.name if item.product else '',
                            location_id=item.location_id,
                            location_code=item.location.code if item.location else '',
                            location_name=item.location.name if item.location else '',
                            alert_type='out_of_stock',
                            current_quantity=item.physical_quantity,
                            message=f"Stock épuisé pour {item.product.name if item.product else 'produit'} à {item.location.name if item.location else 'emplacement'}",
                            threshold=None
                        ))
                
                # Check for low stock (below minimum)
                elif item.min_stock and item.physical_quantity < item.min_stock:
                    if not query.alert_type or query.alert_type == 'low_stock':
                        alerts.append(StockAlertDTO(
                            stock_item_id=item.id,
                            product_id=item.product_id,
                            product_code=item.product.code if item.product else '',
                            product_name=item.product.name if item.product else '',
                            location_id=item.location_id,
                            location_code=item.location.code if item.location else '',
                            location_name=item.location.name if item.location else '',
                            alert_type='low_stock',
                            current_quantity=item.physical_quantity,
                            threshold=item.min_stock,
                            message=f"Stock faible ({item.physical_quantity} < {item.min_stock}) pour {item.product.name if item.product else 'produit'} à {item.location.name if item.location else 'emplacement'}"
                        ))
                
                # Check for overstock (above maximum)
                elif item.max_stock and item.physical_quantity > item.max_stock:
                    if not query.alert_type or query.alert_type == 'overstock':
                        alerts.append(StockAlertDTO(
                            stock_item_id=item.id,
                            product_id=item.product_id,
                            product_code=item.product.code if item.product else '',
                            product_name=item.product.name if item.product else '',
                            location_id=item.location_id,
                            location_code=item.location.code if item.location else '',
                            location_name=item.location.name if item.location else '',
                            alert_type='overstock',
                            current_quantity=item.physical_quantity,
                            threshold=item.max_stock,
                            message=f"Surstock ({item.physical_quantity} > {item.max_stock}) pour {item.product.name if item.product else 'produit'} à {item.location.name if item.location else 'emplacement'}"
                        ))
            
            # Pagination
            total = len(alerts)
            offset = (query.page - 1) * query.per_page
            return alerts[offset:offset + query.per_page]


class GetStockMovementsHandler(QueryHandler):
    """Handler for GetStockMovementsQuery."""
    
    def handle(self, query: GetStockMovementsQuery) -> List[StockMovementDTO]:
        with get_session() as session:
            # Build query
            q = session.query(StockMovement).options(
                joinedload(StockMovement.product),
                joinedload(StockMovement.location_from),
                joinedload(StockMovement.location_to),
                joinedload(StockMovement.user)
            )
            
            # Apply filters
            if query.stock_item_id:
                q = q.filter(StockMovement.stock_item_id == query.stock_item_id)
            
            if query.product_id:
                q = q.filter(StockMovement.product_id == query.product_id)
            
            if query.variant_id is not None:
                q = q.filter(StockMovement.variant_id == query.variant_id)
            
            if query.location_id:
                q = q.filter(
                    or_(
                        StockMovement.location_from_id == query.location_id,
                        StockMovement.location_to_id == query.location_id
                    )
                )
            
            if query.movement_type:
                q = q.filter(StockMovement.type == query.movement_type)
            
            if query.related_document_type:
                q = q.filter(StockMovement.related_document_type == query.related_document_type)
            
            if query.related_document_id:
                q = q.filter(StockMovement.related_document_id == query.related_document_id)
            
            if query.date_from:
                q = q.filter(StockMovement.created_at >= query.date_from)
            
            if query.date_to:
                q = q.filter(StockMovement.created_at <= query.date_to)
            
            # Order by most recent first
            q = q.order_by(StockMovement.created_at.desc())
            
            # Pagination
            total = q.count()
            offset = (query.page - 1) * query.per_page
            movements = q.offset(offset).limit(query.per_page).all()
            
            # Pre-load related documents to avoid N+1 queries
            order_ids = [m.related_document_id for m in movements if m.related_document_type == 'order' and m.related_document_id]
            po_ids = [m.related_document_id for m in movements if m.related_document_type == 'purchase_order' and m.related_document_id]
            
            orders_dict = {}
            if order_ids:
                orders = session.query(Order).filter(Order.id.in_(order_ids)).all()
                orders_dict = {order.id: order.number for order in orders}
            
            pos_dict = {}
            if po_ids:
                pos = session.query(PurchaseOrder).filter(PurchaseOrder.id.in_(po_ids)).all()
                pos_dict = {po.id: po.number for po in pos}
            
            # Pre-load variants
            variant_ids = [m.variant_id for m in movements if m.variant_id]
            variants_dict = {}
            if variant_ids:
                from app.domain.models.product import ProductVariant
                variants = session.query(ProductVariant).filter(ProductVariant.id.in_(variant_ids)).all()
                variants_dict = {v.id: v for v in variants}
            
            # Convert to DTOs
            return [
                self._to_stock_movement_dto(movement, orders_dict, pos_dict, variants_dict)
                for movement in movements
            ]
    
    def _to_stock_movement_dto(self, movement: StockMovement, orders_dict: dict = None, pos_dict: dict = None, variants_dict: dict = None) -> StockMovementDTO:
        """Convert StockMovement to DTO."""
        # Get related document number if exists
        related_document_number = None
        if movement.related_document_type and movement.related_document_id:
            if movement.related_document_type == 'order' and orders_dict:
                related_document_number = orders_dict.get(movement.related_document_id)
            elif movement.related_document_type == 'purchase_order' and pos_dict:
                related_document_number = pos_dict.get(movement.related_document_id)
        
        # Get variant info if exists
        variant_code = None
        variant_name = None
        if movement.variant_id and variants_dict:
            variant = variants_dict.get(movement.variant_id)
            if variant:
                variant_code = variant.code
                variant_name = variant.name
        
        return StockMovementDTO(
            id=movement.id,
            stock_item_id=movement.stock_item_id,
            product_id=movement.product_id,
            product_code=movement.product.code if movement.product else None,
            product_name=movement.product.name if movement.product else None,
            variant_id=movement.variant_id,
            variant_code=variant_code,
            variant_name=variant_name,
            location_from_id=movement.location_from_id,
            location_from_code=movement.location_from.code if movement.location_from else None,
            location_from_name=movement.location_from.name if movement.location_from else None,
            location_to_id=movement.location_to_id,
            location_to_code=movement.location_to.code if movement.location_to else None,
            location_to_name=movement.location_to.name if movement.location_to else None,
            quantity=movement.quantity,
            type=movement.type,
            reason=movement.reason,
            user_id=movement.user_id,
            user_name=movement.user.username if movement.user else None,
            related_document_type=movement.related_document_type,
            related_document_id=movement.related_document_id,
            related_document_number=related_document_number,
            created_at=movement.created_at
        )


class GetLocationHierarchyHandler(QueryHandler):
    """Handler for GetLocationHierarchyQuery."""
    
    def handle(self, query: GetLocationHierarchyQuery) -> List[LocationDTO]:
        with get_session() as session:
            # Build query
            q = session.query(Location)
            
            # Filter by parent
            if query.parent_id is None:
                # Root locations (no parent)
                q = q.filter(Location.parent_id.is_(None))
            else:
                q = q.filter(Location.parent_id == query.parent_id)
            
            # Filter by type
            if query.location_type:
                q = q.filter(Location.type == query.location_type)
            
            # Filter active/inactive
            if not query.include_inactive:
                q = q.filter(Location.is_active == True)
            
            # Order by code
            q = q.order_by(Location.code)
            
            locations = q.all()
            
            # Convert to DTOs with children
            return [
                self._to_location_dto(session, loc, query.include_inactive)
                for loc in locations
            ]
    
    def _to_location_dto(self, session, location: Location, include_inactive: bool) -> LocationDTO:
        """Convert Location to DTO with children."""
        # Get parent name if exists
        parent_name = None
        if location.parent_id:
            parent = session.query(Location).get(location.parent_id)
            if parent:
                parent_name = parent.name
        
        # Get children
        children_query = session.query(Location).filter(Location.parent_id == location.id)
        if not include_inactive:
            children_query = children_query.filter(Location.is_active == True)
        children = children_query.order_by(Location.code).all()
        
        children_dtos = [
            self._to_location_dto(session, child, include_inactive)
            for child in children
        ] if children else None
        
        return LocationDTO(
            id=location.id,
            code=location.code,
            name=location.name,
            type=location.type,
            parent_id=location.parent_id,
            parent_name=parent_name,
            capacity=location.capacity,
            is_active=location.is_active,
            children=children_dtos,
            created_at=location.created_at
        )


class GetStockItemByIdHandler(QueryHandler):
    """Handler for GetStockItemByIdQuery."""
    
    def handle(self, query: GetStockItemByIdQuery) -> StockItemDTO:
        with get_session() as session:
            item = session.query(StockItem).options(
                joinedload(StockItem.product),
                joinedload(StockItem.location)
            ).get(query.id)
            
            if not item:
                raise ValueError("Stock item not found")
            
            handler = GetStockLevelsHandler()
            return handler._to_stock_item_dto(item)


class GetLocationByIdHandler(QueryHandler):
    """Handler for GetLocationByIdQuery."""
    
    def handle(self, query: GetLocationByIdQuery) -> LocationDTO:
        with get_session() as session:
            location = session.query(Location).get(query.id)
            
            if not location:
                raise ValueError("Location not found")
            
            handler = GetLocationHierarchyHandler()
            return handler._to_location_dto(session, location, include_inactive=True)


class GlobalStockHandler(QueryHandler):
    """Handler for GlobalStockQuery - consolidated stock view across all sites."""
    
    def handle(self, query: GlobalStockQuery) -> List[GlobalStockItemDTO]:
        """
        Get consolidated stock view across all sites (or specific site).
        
        Args:
            query: GlobalStockQuery with filters
            
        Returns:
            List of GlobalStockItemDTO with aggregated stock by product/variant
        """
        with get_session() as session:
            # Build base query
            q = session.query(
                StockItem.product_id,
                StockItem.variant_id,
                func.sum(StockItem.physical_quantity).label('total_physical'),
                func.sum(StockItem.reserved_quantity).label('total_reserved')
            ).join(Product)
            
            # Apply filters
            if query.product_id:
                q = q.filter(StockItem.product_id == query.product_id)
            
            if query.variant_id is not None:
                q = q.filter(StockItem.variant_id == query.variant_id)
            
            if query.site_id:
                q = q.filter(StockItem.site_id == query.site_id)
            
            if not query.include_zero:
                q = q.filter(StockItem.physical_quantity > 0)
            
            # Search by product code or name
            if query.search:
                search_term = f"%{query.search}%"
                q = q.filter(
                    or_(
                        Product.code.ilike(search_term),
                        Product.name.ilike(search_term)
                    )
                )
            
            # Group by product and variant
            q = q.group_by(StockItem.product_id, StockItem.variant_id)
            
            # Get total count for pagination
            total = q.count()
            
            # Pagination
            offset = (query.page - 1) * query.per_page
            aggregated = q.offset(offset).limit(query.per_page).all()
            
            # Pre-load products and variants
            product_ids = [row.product_id for row in aggregated]
            products_dict = {}
            if product_ids:
                products = session.query(Product).filter(Product.id.in_(product_ids)).all()
                products_dict = {p.id: p for p in products}
            
            variant_ids = [row.variant_id for row in aggregated if row.variant_id]
            variants_dict = {}
            if variant_ids:
                from app.domain.models.product import ProductVariant
                variants = session.query(ProductVariant).filter(ProductVariant.id.in_(variant_ids)).all()
                variants_dict = {v.id: v for v in variants}
            
            # Get detailed stock by site for each product/variant
            result = []
            for row in aggregated:
                product = products_dict.get(row.product_id)
                product_code = getattr(product, 'code', None) if product else None
                product_name = getattr(product, 'name', None) if product else None
                
                variant_code = None
                variant_name = None
                if row.variant_id and variants_dict:
                    variant = variants_dict.get(row.variant_id)
                    if variant:
                        variant_code = getattr(variant, 'code', None)
                        variant_name = getattr(variant, 'name', None)
                
                # Get stock breakdown by site
                site_query = session.query(
                    StockItem.site_id,
                    func.sum(StockItem.physical_quantity).label('site_physical'),
                    func.sum(StockItem.reserved_quantity).label('site_reserved')
                ).filter(
                    StockItem.product_id == row.product_id,
                    StockItem.variant_id == row.variant_id
                )
                
                if query.site_id:
                    site_query = site_query.filter(StockItem.site_id == query.site_id)
                
                site_query = site_query.group_by(StockItem.site_id)
                site_breakdown = site_query.all()
                
                # Get site names
                site_ids = [b.site_id for b in site_breakdown if b.site_id]
                sites_dict = {}
                if site_ids:
                    sites = session.query(Site).filter(Site.id.in_(site_ids)).all()
                    sites_dict = {s.id: s for s in sites}
                
                by_site = []
                for site_row in site_breakdown:
                    site = sites_dict.get(site_row.site_id) if site_row.site_id else None
                    site_code = getattr(site, 'code', None) if site else None
                    site_name = getattr(site, 'name', None) if site else None
                    
                    site_physical = site_row.site_physical or Decimal('0')
                    site_reserved = site_row.site_reserved or Decimal('0')
                    site_available = site_physical - site_reserved
                    
                    by_site.append({
                        'site_id': site_row.site_id,
                        'site_code': site_code,
                        'site_name': site_name,
                        'physical_quantity': float(site_physical),
                        'reserved_quantity': float(site_reserved),
                        'available_quantity': float(site_available)
                    })
                
                total_physical = row.total_physical or Decimal('0')
                total_reserved = row.total_reserved or Decimal('0')
                total_available = total_physical - total_reserved
                
                result.append(GlobalStockItemDTO(
                    product_id=row.product_id,
                    product_code=product_code,
                    product_name=product_name,
                    variant_id=row.variant_id,
                    variant_code=variant_code,
                    variant_name=variant_name,
                    total_physical_quantity=total_physical,
                    total_reserved_quantity=total_reserved,
                    total_available_quantity=total_available,
                    by_site=by_site
                ))
            
            return result

