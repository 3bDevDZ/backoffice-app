"""Service for stock transfer management operations."""
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.domain.models.stock import (
    Site, StockTransfer, StockTransferLine, StockItem, StockMovement, Location
)
from app.domain.models.product import Product


class StockTransferService:
    """Service for managing inter-site stock transfers."""
    
    def __init__(self, session: Session):
        """
        Initialize the stock transfer service.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
    
    def create_transfer(
        self,
        number: str,
        source_site_id: int,
        destination_site_id: int,
        created_by: int,
        requested_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        lines: Optional[List[Dict[str, Any]]] = None
    ) -> StockTransfer:
        """
        Create a new stock transfer.
        
        Args:
            number: Unique transfer number
            source_site_id: Source site ID
            destination_site_id: Destination site ID
            created_by: User ID who creates the transfer
            requested_date: Optional requested date
            notes: Optional notes
            lines: Optional list of transfer lines with keys: product_id, variant_id, quantity, notes
            
        Returns:
            Created StockTransfer instance
            
        Raises:
            ValueError: If validation fails
        """
        # Validate sites exist
        source_site = self.session.get(Site, source_site_id)
        if not source_site:
            raise ValueError(f"Source site with ID {source_site_id} not found.")
        
        if source_site.status != 'active':
            raise ValueError(f"Source site '{source_site.code}' is not active.")
        
        destination_site = self.session.get(Site, destination_site_id)
        if not destination_site:
            raise ValueError(f"Destination site with ID {destination_site_id} not found.")
        
        if destination_site.status != 'active':
            raise ValueError(f"Destination site '{destination_site.code}' is not active.")
        
        # Check if number already exists
        existing = self.session.query(StockTransfer).filter(StockTransfer.number == number).first()
        if existing:
            raise ValueError(f"Transfer with number '{number}' already exists.")
        
        # Create transfer
        transfer = StockTransfer.create(
            number=number,
            source_site_id=source_site_id,
            destination_site_id=destination_site_id,
            created_by=created_by,
            requested_date=requested_date,
            notes=notes
        )
        
        self.session.add(transfer)
        self.session.flush()  # Get transfer.id
        
        # Add lines if provided
        if lines:
            for idx, line_data in enumerate(lines):
                product_id = line_data.get('product_id')
                variant_id = line_data.get('variant_id')
                quantity = Decimal(str(line_data.get('quantity', 0)))
                notes = line_data.get('notes')
                
                if not product_id:
                    raise ValueError("Product ID is required for transfer line.")
                
                if quantity <= 0:
                    raise ValueError("Transfer quantity must be positive.")
                
                # Validate product exists
                product = self.session.get(Product, product_id)
                if not product:
                    raise ValueError(f"Product with ID {product_id} not found.")
                
                # Validate variant if provided
                if variant_id:
                    from app.domain.models.product import ProductVariant
                    variant = self.session.get(ProductVariant, variant_id)
                    if not variant or variant.product_id != product_id:
                        raise ValueError(f"Variant with ID {variant_id} not found or does not belong to product {product_id}.")
                
                line = StockTransferLine.create(
                    transfer_id=transfer.id,
                    product_id=product_id,
                    quantity=quantity,
                    variant_id=variant_id,
                    sequence=idx,
                    notes=notes
                )
                
                self.session.add(line)
        
        self.session.flush()
        
        return transfer
    
    def ship_transfer(
        self,
        transfer_id: int,
        shipped_by: int,
        shipped_date: Optional[datetime] = None
    ) -> StockTransfer:
        """
        Mark a transfer as shipped and create exit stock movements.
        
        Args:
            transfer_id: Transfer ID
            shipped_by: User ID who ships the transfer
            shipped_date: Optional shipping date
            
        Returns:
            Updated StockTransfer instance
            
        Raises:
            ValueError: If validation fails
        """
        transfer = self.session.get(StockTransfer, transfer_id)
        if not transfer:
            raise ValueError(f"Transfer with ID {transfer_id} not found.")
        
        # Ship the transfer (validates status and lines)
        transfer.ship(shipped_by=shipped_by, shipped_date=shipped_date)
        
        # Create exit stock movements for each line
        for line in transfer.lines:
            # Find stock item at source site
            stock_item = self._find_or_create_stock_item(
                product_id=line.product_id,
                variant_id=line.variant_id,
                site_id=transfer.source_site_id,
                location_id=None  # Will use default location for site
            )
            
            # Validate sufficient stock
            if stock_item.physical_quantity < line.quantity:
                raise ValueError(
                    f"Insufficient stock for product {line.product_id} at source site. "
                    f"Available: {stock_item.physical_quantity}, Required: {line.quantity}"
                )
            
            # Create exit movement
            movement = StockMovement.create(
                stock_item_id=stock_item.id,
                product_id=line.product_id,
                quantity=-line.quantity,  # Negative for exit
                movement_type='exit',
                user_id=shipped_by,
                location_from_id=stock_item.location_id,
                variant_id=line.variant_id,
                reason=f"Stock transfer {transfer.number}",
                related_document_type='stock_transfer',
                related_document_id=transfer.id
            )
            
            self.session.add(movement)
            
            # Update stock item
            stock_item.adjust(quantity=-line.quantity, reason=f"Shipped via transfer {transfer.number}")
        
        self.session.flush()
        
        return transfer
    
    def receive_transfer(
        self,
        transfer_id: int,
        received_by: int,
        received_date: Optional[datetime] = None,
        received_quantities: Optional[Dict[int, Decimal]] = None
    ) -> StockTransfer:
        """
        Mark a transfer as received and create entry stock movements.
        
        Args:
            transfer_id: Transfer ID
            received_by: User ID who receives the transfer
            received_date: Optional receiving date
            received_quantities: Optional dict mapping line_id to received quantity (for partial receipts)
            
        Returns:
            Updated StockTransfer instance
            
        Raises:
            ValueError: If validation fails
        """
        transfer = self.session.get(StockTransfer, transfer_id)
        if not transfer:
            raise ValueError(f"Transfer with ID {transfer_id} not found.")
        
        # Receive the transfer (validates status)
        transfer.receive(received_by=received_by, received_date=received_date)
        
        # Create entry stock movements for each line
        for line in transfer.lines:
            # Determine quantity received (use provided or full quantity)
            quantity_received = received_quantities.get(line.id, line.quantity) if received_quantities else line.quantity
            
            if quantity_received <= 0:
                continue  # Skip if nothing received
            
            if quantity_received > line.quantity:
                raise ValueError(
                    f"Received quantity {quantity_received} exceeds transfer quantity {line.quantity} for line {line.id}"
                )
            
            # Update line received quantity
            line.quantity_received = quantity_received
            
            # Find or create stock item at destination site
            stock_item = self._find_or_create_stock_item(
                product_id=line.product_id,
                variant_id=line.variant_id,
                site_id=transfer.destination_site_id,
                location_id=None  # Will use default location for site
            )
            
            # Create entry movement
            movement = StockMovement.create(
                stock_item_id=stock_item.id,
                product_id=line.product_id,
                quantity=quantity_received,  # Positive for entry
                movement_type='entry',
                user_id=received_by,
                location_to_id=stock_item.location_id,
                variant_id=line.variant_id,
                reason=f"Stock transfer {transfer.number} received",
                related_document_type='stock_transfer',
                related_document_id=transfer.id
            )
            
            self.session.add(movement)
            
            # Update stock item
            stock_item.adjust(quantity=quantity_received, reason=f"Received via transfer {transfer.number}")
        
        self.session.flush()
        
        return transfer
    
    def _find_or_create_stock_item(
        self,
        product_id: int,
        variant_id: Optional[int],
        site_id: int,
        location_id: Optional[int] = None
    ) -> StockItem:
        """
        Find or create a stock item for a product at a site.
        
        Args:
            product_id: Product ID
            variant_id: Optional variant ID
            site_id: Site ID
            location_id: Optional specific location ID (uses default location if None)
            
        Returns:
            StockItem instance
        """
        # If location_id not provided, find default location for site
        if not location_id:
            location = self.session.query(Location).filter(
                and_(
                    Location.site_id == site_id,
                    Location.type == 'warehouse',
                    Location.is_active == True
                )
            ).first()
            
            if not location:
                # Create default warehouse location for site
                site = self.session.get(Site, site_id)
                location = Location.create(
                    code=f"{site.code}-WH-01",
                    name=f"{site.name} - Warehouse",
                    type='warehouse',
                    site_id=site_id
                )
                self.session.add(location)
                self.session.flush()
            
            location_id = location.id
        
        # Find existing stock item
        stock_item = self.session.query(StockItem).filter(
            and_(
                StockItem.product_id == product_id,
                StockItem.variant_id == variant_id,
                StockItem.location_id == location_id
            )
        ).first()
        
        if not stock_item:
            # Create new stock item
            stock_item = StockItem.create(
                product_id=product_id,
                location_id=location_id,
                variant_id=variant_id,
                site_id=site_id,
                physical_quantity=Decimal('0')
            )
            self.session.add(stock_item)
            self.session.flush()
        
        return stock_item


