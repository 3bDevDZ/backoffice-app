"""Query handlers for order management."""
from app.application.common.cqrs import QueryHandler
from app.domain.models.order import Order, OrderLine, StockReservation
from app.domain.models.customer import Customer
from app.domain.models.product import Product
from app.domain.models.user import User
from app.domain.models.stock import StockItem, Location
from app.domain.models.quote import Quote
from app.infrastructure.db import get_session
from .queries import (
    ListOrdersQuery,
    GetOrderByIdQuery,
    GetOrderHistoryQuery
)
from .order_dto import (
    OrderDTO, OrderLineDTO, StockReservationDTO
)
from typing import List
from sqlalchemy import or_, func, and_
from sqlalchemy.orm import joinedload
from datetime import datetime


class ListOrdersHandler(QueryHandler):
    """Handler for listing orders with pagination and filtering."""
    
    def handle(self, query: ListOrdersQuery) -> dict:
        """List orders with pagination and filtering."""
        with get_session() as session:
            # Build query
            q = session.query(Order).join(Customer)
            
            # Apply filters
            if query.status:
                q = q.filter(Order.status == query.status)
            
            if query.customer_id:
                q = q.filter(Order.customer_id == query.customer_id)
            
            if query.search:
                search_term = f"%{query.search}%"
                q = q.filter(
                    or_(
                        Order.number.ilike(search_term),
                        Customer.name.ilike(search_term),
                        Customer.code.ilike(search_term)
                    )
                )
            
            # Date filters
            if query.date_from:
                q = q.filter(Order.created_at >= datetime.combine(query.date_from, datetime.min.time()))
            
            if query.date_to:
                q = q.filter(Order.created_at <= datetime.combine(query.date_to, datetime.max.time()))
            
            # Get total count
            total = q.count()
            
            # Apply pagination
            offset = (query.page - 1) * query.per_page
            orders = q.order_by(Order.created_at.desc()).offset(offset).limit(query.per_page).all()
            
            # Convert to DTOs
            order_dtos = []
            for order in orders:
                order_dto = OrderDTO(
                    id=order.id,
                    number=order.number,
                    customer_id=order.customer_id,
                    customer_code=order.customer.code if order.customer else None,
                    customer_name=order.customer.name if order.customer else None,
                    quote_id=order.quote_id,
                    quote_number=order.quote.number if order.quote else None,
                    status=order.status,
                    delivery_address_id=order.delivery_address_id,
                    delivery_date_requested=order.delivery_date_requested,
                    delivery_date_promised=order.delivery_date_promised,
                    delivery_date_actual=order.delivery_date_actual,
                    delivery_instructions=order.delivery_instructions,
                    subtotal=order.subtotal,
                    tax_amount=order.tax_amount,
                    total=order.total,
                    discount_percent=order.discount_percent,
                    discount_amount=order.discount_amount,
                    notes=order.notes,
                    confirmed_at=order.confirmed_at,
                    confirmed_by=order.confirmed_by,
                    confirmed_by_username=order.confirmed_by_user.username if order.confirmed_by_user else None,
                    created_by=order.created_by,
                    created_by_username=order.created_by_user.username if order.created_by_user else None,
                    created_at=order.created_at,
                    updated_at=order.updated_at,
                    lines=None,  # Not included in list view
                    stock_reservations=None
                )
                order_dtos.append(order_dto)
            
            return {
                'items': order_dtos,
                'total': total,
                'page': query.page,
                'per_page': query.per_page,
                'pages': (total + query.per_page - 1) // query.per_page
            }


class GetOrderByIdHandler(QueryHandler):
    """Handler for getting an order by ID."""
    
    def handle(self, query: GetOrderByIdQuery) -> OrderDTO:
        """Get an order by ID with optional relationships."""
        with get_session() as session:
            # Build query with eager loading
            q = session.query(Order).join(Customer)
            
            if query.include_lines:
                q = q.options(joinedload(Order.lines).joinedload(OrderLine.product))
            
            if query.include_reservations:
                q = q.options(
                    joinedload(Order.stock_reservations).joinedload(StockReservation.stock_item)
                    .joinedload(StockItem.location)
                )
            
            order = q.filter(Order.id == query.order_id).first()
            
            if not order:
                raise ValueError(f"Order with ID {query.order_id} not found.")
            
            # Convert lines to DTOs
            lines_dto = None
            if query.include_lines and order.lines:
                lines_dto = [
                    OrderLineDTO(
                        id=line.id,
                        order_id=line.order_id,
                        product_id=line.product_id,
                        product_code=line.product.code if line.product else None,
                        product_name=line.product.name if line.product else None,
                        variant_id=line.variant_id,
                        quantity=line.quantity,
                        unit_price=line.unit_price,
                        discount_percent=line.discount_percent,
                        discount_amount=line.discount_amount,
                        tax_rate=line.tax_rate,
                        line_total_ht=line.line_total_ht,
                        line_total_ttc=line.line_total_ttc,
                        quantity_delivered=line.quantity_delivered,
                        quantity_invoiced=line.quantity_invoiced,
                        sequence=line.sequence
                    )
                    for line in order.lines
                ]
            
            # Convert reservations to DTOs
            reservations_dto = None
            if query.include_reservations and order.stock_reservations:
                reservations_dto = [
                    StockReservationDTO(
                        id=reservation.id,
                        order_id=reservation.order_id,
                        order_line_id=reservation.order_line_id,
                        stock_item_id=reservation.stock_item_id,
                        location_id=reservation.stock_item.location_id if reservation.stock_item else None,
                        location_code=reservation.stock_item.location.code if reservation.stock_item and reservation.stock_item.location else None,
                        quantity=reservation.quantity,
                        status=reservation.status,
                        reserved_at=reservation.reserved_at,
                        released_at=reservation.released_at
                    )
                    for reservation in order.stock_reservations
                ]
            
            return OrderDTO(
                id=order.id,
                number=order.number,
                customer_id=order.customer_id,
                customer_code=order.customer.code if order.customer else None,
                customer_name=order.customer.name if order.customer else None,
                quote_id=order.quote_id,
                quote_number=order.quote.number if order.quote else None,
                status=order.status,
                delivery_address_id=order.delivery_address_id,
                delivery_date_requested=order.delivery_date_requested,
                delivery_date_promised=order.delivery_date_promised,
                delivery_date_actual=order.delivery_date_actual,
                delivery_instructions=order.delivery_instructions,
                subtotal=order.subtotal,
                tax_amount=order.tax_amount,
                total=order.total,
                discount_percent=order.discount_percent,
                discount_amount=order.discount_amount,
                notes=order.notes,
                confirmed_at=order.confirmed_at,
                confirmed_by=order.confirmed_by,
                confirmed_by_username=order.confirmed_by_user.username if order.confirmed_by_user else None,
                created_by=order.created_by,
                created_by_username=order.created_by_user.username if order.created_by_user else None,
                created_at=order.created_at,
                updated_at=order.updated_at,
                lines=lines_dto,
                stock_reservations=reservations_dto
            )


class GetOrderHistoryHandler(QueryHandler):
    """Handler for getting order history."""
    
    def handle(self, query: GetOrderHistoryQuery) -> dict:
        """
        Get order history.
        
        For now, this returns basic order information.
        In the future, this could be extended to track status changes
        via domain events or a dedicated history table.
        """
        with get_session() as session:
            # Verify order exists
            order = session.get(Order, query.order_id)
            if not order:
                raise ValueError(f"Order with ID {query.order_id} not found.")
            
            # For MVP, return order status changes based on timestamps
            # In the future, this could query a dedicated order_history table
            history_items = []
            
            # Add creation event
            if order.created_at:
                history_items.append({
                    'event': 'created',
                    'status': 'draft',
                    'timestamp': order.created_at,
                    'user_id': order.created_by,
                    'user_username': order.created_by_user.username if order.created_by_user else None
                })
            
            # Add confirmation event
            if order.confirmed_at:
                history_items.append({
                    'event': 'confirmed',
                    'status': 'confirmed',
                    'timestamp': order.confirmed_at,
                    'user_id': order.confirmed_by,
                    'user_username': order.confirmed_by_user.username if order.confirmed_by_user else None
                })
            
            # Sort by timestamp descending
            history_items.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Apply pagination
            total = len(history_items)
            offset = (query.page - 1) * query.per_page
            paginated_items = history_items[offset:offset + query.per_page]
            
            return {
                'items': paginated_items,
                'total': total,
                'page': query.page,
                'per_page': query.per_page,
                'pages': (total + query.per_page - 1) // query.per_page if query.per_page > 0 else 0
            }

