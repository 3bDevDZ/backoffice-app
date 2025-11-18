"""Service for purchase request management and automatic generation."""
from decimal import Decimal
from typing import List, Optional
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.domain.models.purchase import PurchaseRequest, PurchaseRequestLine
from app.domain.models.stock import StockItem
from app.domain.models.product import Product


class PurchaseRequestService:
    """Service for managing purchase requests and automatic generation."""
    
    def __init__(self, session: Session):
        """
        Initialize the service.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
    
    def generate_from_low_stock(
        self,
        requested_by: int,
        min_stock_threshold: Optional[Decimal] = None,
        location_id: Optional[int] = None,
        required_date: Optional[date] = None
    ) -> PurchaseRequest:
        """
        Automatically generate a purchase request from products with low stock.
        
        Args:
            requested_by: User ID who creates the request
            min_stock_threshold: Minimum stock threshold (uses product.min_stock if None)
            location_id: Specific location to check (default location if None)
            required_date: When items are needed
            
        Returns:
            PurchaseRequest instance with lines for low stock products
        """
        # Build query for low stock items
        query = self.session.query(StockItem).join(Product)
        
        if location_id:
            query = query.filter(StockItem.location_id == location_id)
        
        # Filter for low stock
        if min_stock_threshold is not None:
            # Use provided threshold
            query = query.filter(
                StockItem.physical_quantity <= min_stock_threshold
            )
        else:
            # Use product's min_stock if available, otherwise use 0
            query = query.filter(
                or_(
                    StockItem.physical_quantity <= Product.min_stock,
                    and_(
                        Product.min_stock.is_(None),
                        StockItem.physical_quantity <= Decimal(0)
                    )
                )
            )
        
        low_stock_items = query.all()
        
        if not low_stock_items:
            raise ValueError("No products with low stock found.")
        
        # Create purchase request
        request = PurchaseRequest.create(
            requested_by=requested_by,
            required_date=required_date
        )
        self.session.add(request)
        self.session.flush()  # Get request.id
        
        # Add lines for each low stock product
        for stock_item in low_stock_items:
            product = stock_item.product
            
            # Calculate quantity to order
            # Order enough to reach max_stock, or at least min_stock if max_stock not set
            current_qty = stock_item.physical_quantity
            min_stock = product.min_stock or Decimal(0)
            max_stock = product.max_stock
            
            if max_stock:
                # Order to reach max_stock
                quantity_to_order = max_stock - current_qty
            else:
                # Order to reach at least min_stock + safety margin (50% of min_stock)
                safety_margin = min_stock * Decimal('0.5')
                target_qty = min_stock + safety_margin
                quantity_to_order = max(Decimal(0), target_qty - current_qty)
            
            # Only add line if we need to order something
            if quantity_to_order > Decimal(0):
                # Get estimated price from product (cost or price)
                unit_price_estimate = product.cost or product.price or None
                
                request.add_line(
                    product_id=product.id,
                    quantity=quantity_to_order,
                    unit_price_estimate=unit_price_estimate
                )
        
        if not request.lines:
            raise ValueError("No products need to be ordered (all are at sufficient stock levels).")
        
        return request
    
    def convert_to_purchase_order(
        self,
        purchase_request_id: int,
        supplier_id: int,
        created_by: int,
        order_date: Optional[date] = None,
        expected_delivery_date: Optional[date] = None
    ):
        """
        Convert an approved purchase request to a purchase order.
        
        Args:
            purchase_request_id: Purchase request ID
            supplier_id: Supplier ID for the purchase order
            created_by: User ID who creates the order
            order_date: Order date (defaults to today)
            expected_delivery_date: Expected delivery date
            
        Returns:
            PurchaseOrder instance
        """
        from app.domain.models.purchase import PurchaseOrder, PurchaseOrderLine
        
        # Get purchase request
        request = self.session.get(PurchaseRequest, purchase_request_id)
        if not request:
            raise ValueError(f"Purchase request with ID {purchase_request_id} not found.")
        
        if request.status != 'approved':
            raise ValueError(f"Cannot convert purchase request in status '{request.status}'. Must be 'approved'.")
        
        # Create purchase order
        po = PurchaseOrder.create(
            supplier_id=supplier_id,
            created_by=created_by,
            order_date=order_date,
            expected_delivery_date=expected_delivery_date or request.required_date,
            notes=f"Converted from purchase request {request.number}",
            internal_notes=request.internal_notes
        )
        self.session.add(po)
        self.session.flush()  # Get po.id
        
        # Convert lines
        for req_line in request.lines:
            # Get product to determine price
            product = self.session.get(Product, req_line.product_id)
            if not product:
                continue
            
            # Use estimated price if available, otherwise use product cost or price
            unit_price = req_line.unit_price_estimate
            if unit_price is None:
                unit_price = product.cost or product.price or Decimal(0)
            
            po.add_line(
                product_id=req_line.product_id,
                quantity=req_line.quantity,
                unit_price=unit_price,
                notes=req_line.notes
            )
        
        # Mark request as converted
        request.mark_converted(po.id)
        
        return po

