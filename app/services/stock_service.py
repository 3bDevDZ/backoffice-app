"""Stock service for complex stock management operations."""
from typing import List, Optional, Dict, Any
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.domain.models.stock import StockItem, StockMovement, Location
from app.domain.models.product import Product


@dataclass
class AvailabilitySummary:
    """Summary of stock availability across locations."""
    product_id: int
    variant_id: Optional[int]
    total_physical: Decimal
    total_reserved: Decimal
    total_available: Decimal
    by_location: List[Dict[str, Any]]


@dataclass
class ReservationResult:
    """Result of a stock reservation operation."""
    stock_item_id: int
    location_id: int
    quantity_reserved: Decimal
    success: bool
    message: Optional[str] = None


@dataclass
class TransferResult:
    """Result of a stock transfer operation."""
    from_stock_item_id: int
    to_stock_item_id: int
    quantity: Decimal
    exit_movement_id: int
    entry_movement_id: int
    success: bool
    message: Optional[str] = None


@dataclass
class ReorderNeed:
    """Represents a reorder need for a product."""
    stock_item_id: int
    product_id: int
    product_code: str
    product_name: str
    location_id: int
    location_code: str
    current_quantity: Decimal
    min_stock: Decimal
    reorder_point: Decimal
    suggested_quantity: Decimal
    urgency: str  # 'critical', 'high', 'medium', 'low'


class StockService:
    """
    Service for complex stock management operations.
    Contains business logic that spans multiple aggregates.
    """
    
    def __init__(self, session: Session):
        """
        Initialize the stock service.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
    
    # ==================== Validation Methods ====================
    
    def validate_stock_rules(self, stock_item: StockItem, operation: str) -> None:
        """
        Validate stock business rules (RG-STOCK-001 to RG-STOCK-007).
        
        Args:
            stock_item: The stock item to validate
            operation: Operation being performed ('reserve', 'release', 'adjust', 'transfer')
            
        Raises:
            ValueError: If any rule is violated
        """
        # RG-STOCK-001 : Stock physique ≥ 0 (sauf autorisation)
        if stock_item.physical_quantity < 0:
            raise ValueError(
                f"RG-STOCK-001: Stock physique ne peut pas être négatif. "
                f"Current: {stock_item.physical_quantity}"
            )
        
        # RG-STOCK-002 : Stock réservé ≤ stock physique
        if stock_item.reserved_quantity > stock_item.physical_quantity:
            raise ValueError(
                f"RG-STOCK-002: Stock réservé ({stock_item.reserved_quantity}) ne peut pas "
                f"dépasser le stock physique ({stock_item.physical_quantity})"
            )
        
        # RG-STOCK-005 : Inventaire bloque mouvements sur produits concernés
        if self.is_inventory_in_progress(stock_item.product_id):
            raise ValueError(
                f"RG-STOCK-005: Un inventaire est en cours pour le produit {stock_item.product_id}. "
                f"Les mouvements sont bloqués."
            )
    
    def validate_movement(self, movement_data: Dict[str, Any]) -> None:
        """
        Validate a stock movement according to business rules.
        
        Args:
            movement_data: Dictionary containing movement data:
                - type: Movement type ('entry', 'exit', 'transfer', 'adjustment')
                - quantity: Movement quantity
                - location_from_id: Source location (optional)
                - location_to_id: Destination location (optional)
                - product_id: Product ID
                - stock_item_id: Stock item ID (optional)
                
        Raises:
            ValueError: If validation fails
        """
        movement_type = movement_data.get('type')
        quantity = movement_data.get('quantity', Decimal('0'))
        location_from_id = movement_data.get('location_from_id')
        location_to_id = movement_data.get('location_to_id')
        product_id = movement_data.get('product_id')
        
        # RG-STOCK-003 : Mouvement nécessite emplacement source ET/OU destination
        if movement_type == 'transfer':
            if not location_from_id or not location_to_id:
                raise ValueError(
                    "RG-STOCK-003: Un transfert nécessite un emplacement source ET destination"
                )
            if location_from_id == location_to_id:
                raise ValueError(
                    "RG-STOCK-003: L'emplacement source et destination doivent être différents"
                )
        elif movement_type == 'entry':
            if not location_to_id:
                raise ValueError(
                    "RG-STOCK-003: Une entrée nécessite un emplacement destination"
                )
        elif movement_type == 'exit':
            if not location_from_id:
                raise ValueError(
                    "RG-STOCK-003: Une sortie nécessite un emplacement source"
                )
        
        # RG-STOCK-006 : Transfert : stock source ≥ quantité transférée
        if movement_type == 'transfer' and location_from_id:
            stock_item = self.session.query(StockItem).filter(
                StockItem.product_id == product_id,
                StockItem.location_id == location_from_id
            ).first()
            
            if stock_item:
                available = stock_item.available_quantity
                if available < abs(quantity):
                    raise ValueError(
                        f"RG-STOCK-006: Stock disponible insuffisant pour le transfert. "
                        f"Disponible: {available}, Requis: {abs(quantity)}"
                    )
        
        # RG-STOCK-004 : Lot/Série obligatoire si produit tracé
        # TODO: Implement when product tracking (lot/serial) is added
        # if product.requires_tracking and not lot_serial:
        #     raise ValueError("RG-STOCK-004: Lot/Série obligatoire pour ce produit")
    
    def is_inventory_in_progress(self, product_id: int) -> bool:
        """
        Check if an inventory is in progress for a product.
        
        Args:
            product_id: Product ID to check
            
        Returns:
            True if inventory is in progress, False otherwise
        """
        # TODO: Implement when Inventory model is created
        # For now, return False (no inventory blocking)
        # In the future, query Inventory table for open inventories
        return False
    
    # ==================== Availability Methods ====================
    
    def get_global_availability(
        self, 
        product_id: int, 
        variant_id: Optional[int] = None
    ) -> AvailabilitySummary:
        """
        Calculate global availability of a product across all locations.
        
        Args:
            product_id: Product ID
            variant_id: Optional variant ID
            
        Returns:
            AvailabilitySummary with totals and breakdown by location
        """
        # Query all stock items for this product
        query = self.session.query(StockItem).filter(
            StockItem.product_id == product_id
        )
        
        if variant_id is None:
            query = query.filter(StockItem.variant_id.is_(None))
        else:
            query = query.filter(StockItem.variant_id == variant_id)
        
        stock_items = query.all()
        
        total_physical = Decimal('0')
        total_reserved = Decimal('0')
        by_location = []
        
        for item in stock_items:
            total_physical += item.physical_quantity
            total_reserved += item.reserved_quantity
            
            by_location.append({
                'location_id': item.location_id,
                'location_code': item.location.code if item.location else None,
                'location_name': item.location.name if item.location else None,
                'physical_quantity': item.physical_quantity,
                'reserved_quantity': item.reserved_quantity,
                'available_quantity': item.available_quantity,
                'min_stock': item.min_stock,
                'max_stock': item.max_stock
            })
        
        total_available = total_physical - total_reserved
        
        return AvailabilitySummary(
            product_id=product_id,
            variant_id=variant_id,
            total_physical=total_physical,
            total_reserved=total_reserved,
            total_available=total_available,
            by_location=by_location
        )
    
    def check_availability(
        self, 
        product_id: int, 
        quantity: Decimal, 
        location_id: Optional[int] = None,
        variant_id: Optional[int] = None
    ) -> bool:
        """
        Check if a quantity is available for a product.
        
        Args:
            product_id: Product ID
            quantity: Required quantity
            location_id: Optional specific location (if None, checks all locations)
            variant_id: Optional variant ID
            
        Returns:
            True if available, False otherwise
        """
        if location_id:
            # Check specific location
            query = self.session.query(StockItem).filter(
                StockItem.product_id == product_id,
                StockItem.location_id == location_id
            )
            if variant_id is None:
                query = query.filter(StockItem.variant_id.is_(None))
            else:
                query = query.filter(StockItem.variant_id == variant_id)
            
            stock_item = query.first()
            if stock_item:
                return stock_item.available_quantity >= quantity
            return False
        else:
            # Check all locations
            availability = self.get_global_availability(product_id, variant_id)
            return availability.total_available >= quantity
    
    # ==================== Reservation Methods ====================
    
    def reserve_stock_for_order(
        self, 
        order_id: int, 
        order_lines: List[Dict[str, Any]]
    ) -> List[ReservationResult]:
        """
        Reserve stock for an order, searching across multiple locations if needed.
        
        Args:
            order_id: Order ID
            order_lines: List of order line dictionaries with:
                - product_id: Product ID
                - quantity: Quantity to reserve
                - variant_id: Optional variant ID
                - preferred_location_id: Optional preferred location
                
        Returns:
            List of ReservationResult objects
        """
        results = []
        
        for line in order_lines:
            product_id = line.get('product_id')
            quantity = Decimal(str(line.get('quantity', 0)))
            variant_id = line.get('variant_id')
            preferred_location_id = line.get('preferred_location_id')
            
            if quantity <= 0:
                continue
            
            # Try preferred location first
            if preferred_location_id:
                result = self._reserve_at_location(
                    product_id, quantity, preferred_location_id, variant_id, order_id
                )
                if result.success:
                    results.append(result)
                    continue
            
            # If preferred location doesn't have enough, search other locations
            result = None
            remaining = quantity
            if preferred_location_id:
                result = self._reserve_at_location(
                    product_id, quantity, preferred_location_id, variant_id, order_id
                )
                if result.success:
                    results.append(result)
                    remaining = quantity - result.quantity_reserved
                else:
                    remaining = quantity
            
            if remaining > 0:
                # Find locations with available stock
                # Note: available_quantity is a property, so we use physical_quantity - reserved_quantity
                query = self.session.query(StockItem).filter(
                    StockItem.product_id == product_id,
                    (StockItem.physical_quantity - StockItem.reserved_quantity) > 0
                )
                if variant_id is None:
                    query = query.filter(StockItem.variant_id.is_(None))
                else:
                    query = query.filter(StockItem.variant_id == variant_id)
                
                if preferred_location_id:
                    query = query.filter(StockItem.location_id != preferred_location_id)
                
                # Order by available quantity descending (physical - reserved)
                stock_items = query.order_by((StockItem.physical_quantity - StockItem.reserved_quantity).desc()).all()
                
                for stock_item in stock_items:
                    if remaining <= 0:
                        break
                    
                    available = stock_item.available_quantity
                    to_reserve = min(remaining, available)
                    
                    try:
                        stock_item.reserve(to_reserve)
                        self.validate_stock_rules(stock_item, 'reserve')
                        
                        results.append(ReservationResult(
                            stock_item_id=stock_item.id,
                            location_id=stock_item.location_id,
                            quantity_reserved=to_reserve,
                            success=True,
                            message=f"Réservé {to_reserve} à l'emplacement {stock_item.location.code}"
                        ))
                        
                        remaining -= to_reserve
                    except ValueError as e:
                        results.append(ReservationResult(
                            stock_item_id=stock_item.id,
                            location_id=stock_item.location_id,
                            quantity_reserved=Decimal('0'),
                            success=False,
                            message=str(e)
                        ))
                
                if remaining > 0:
                    results.append(ReservationResult(
                        stock_item_id=0,
                        location_id=0,
                        quantity_reserved=Decimal('0'),
                        success=False,
                        message=f"Stock insuffisant: {remaining} unités manquantes"
                    ))
        
        return results
    
    def _reserve_at_location(
        self,
        product_id: int,
        quantity: Decimal,
        location_id: int,
        variant_id: Optional[int],
        order_id: int
    ) -> ReservationResult:
        """Reserve stock at a specific location."""
        query = self.session.query(StockItem).filter(
            StockItem.product_id == product_id,
            StockItem.location_id == location_id
        )
        if variant_id is None:
            query = query.filter(StockItem.variant_id.is_(None))
        else:
            query = query.filter(StockItem.variant_id == variant_id)
        
        stock_item = query.with_for_update().first()
        
        if not stock_item:
            return ReservationResult(
                stock_item_id=0,
                location_id=location_id,
                quantity_reserved=Decimal('0'),
                success=False,
                message="Stock item not found"
            )
        
        if stock_item.available_quantity < quantity:
            return ReservationResult(
                stock_item_id=stock_item.id,
                location_id=location_id,
                quantity_reserved=Decimal('0'),
                success=False,
                message=f"Stock insuffisant. Disponible: {stock_item.available_quantity}, Requis: {quantity}"
            )
        
        try:
            stock_item.reserve(quantity)
            self.validate_stock_rules(stock_item, 'reserve')
            
            return ReservationResult(
                stock_item_id=stock_item.id,
                location_id=location_id,
                quantity_reserved=quantity,
                success=True,
                message="Réservation réussie"
            )
        except ValueError as e:
            return ReservationResult(
                stock_item_id=stock_item.id,
                location_id=location_id,
                quantity_reserved=Decimal('0'),
                success=False,
                message=str(e)
            )
    
    def release_stock_for_order(self, order_id: int) -> None:
        """
        Release all stock reservations for an order.
        
        Args:
            order_id: Order ID
        """
        # TODO: Implement when order-stock reservation link is added
        # For now, this is a placeholder
        # In the future, query reservations linked to order_id and release them
        pass
    
    # ==================== Transfer Methods ====================
    
    def transfer_stock(
        self,
        from_location_id: int,
        to_location_id: int,
        product_id: int,
        quantity: Decimal,
        user_id: int,
        reason: Optional[str] = None,
        variant_id: Optional[int] = None
    ) -> TransferResult:
        """
        Transfer stock between locations with full validation.
        
        Args:
            from_location_id: Source location ID
            to_location_id: Destination location ID
            product_id: Product ID
            quantity: Quantity to transfer
            user_id: User performing the transfer
            reason: Optional reason for transfer
            variant_id: Optional variant ID
            
        Returns:
            TransferResult with details of the transfer
        """
        # Validate movement data
        self.validate_movement({
            'type': 'transfer',
            'quantity': -quantity,  # Negative for exit
            'location_from_id': from_location_id,
            'location_to_id': to_location_id,
            'product_id': product_id
        })
        
        # Get source stock item with lock
        source_query = self.session.query(StockItem).filter(
            StockItem.product_id == product_id,
            StockItem.location_id == from_location_id
        )
        if variant_id is None:
            source_query = source_query.filter(StockItem.variant_id.is_(None))
        else:
            source_query = source_query.filter(StockItem.variant_id == variant_id)
        
        source_item = source_query.with_for_update().first()
        
        if not source_item:
            return TransferResult(
                from_stock_item_id=0,
                to_stock_item_id=0,
                quantity=quantity,
                exit_movement_id=0,
                entry_movement_id=0,
                success=False,
                message="Stock item source non trouvé"
            )
        
        # Validate source has enough stock
        if source_item.available_quantity < quantity:
            return TransferResult(
                from_stock_item_id=source_item.id,
                to_stock_item_id=0,
                quantity=quantity,
                exit_movement_id=0,
                entry_movement_id=0,
                success=False,
                message=f"Stock insuffisant. Disponible: {source_item.available_quantity}, Requis: {quantity}"
            )
        
        # Get or create destination stock item
        dest_query = self.session.query(StockItem).filter(
            StockItem.product_id == product_id,
            StockItem.location_id == to_location_id
        )
        if variant_id is None:
            dest_query = dest_query.filter(StockItem.variant_id.is_(None))
        else:
            dest_query = dest_query.filter(StockItem.variant_id == variant_id)
        
        dest_item = dest_query.first()
        
        if not dest_item:
            # Create destination stock item
            dest_item = StockItem.create(
                product_id=product_id,
                location_id=to_location_id,
                physical_quantity=Decimal('0'),
                variant_id=variant_id
            )
            self.session.add(dest_item)
            self.session.flush()
        
        # Create exit movement
        exit_movement = StockMovement.create(
            stock_item_id=source_item.id,
            product_id=product_id,
            quantity=-quantity,  # Negative for exit
            movement_type='exit',
            user_id=user_id,
            location_from_id=from_location_id,
            variant_id=variant_id,
            reason=reason or f"Transfert vers {to_location_id}"
        )
        self.session.add(exit_movement)
        self.session.flush()
        
        # Create entry movement
        entry_movement = StockMovement.create(
            stock_item_id=dest_item.id,
            product_id=product_id,
            quantity=quantity,  # Positive for entry
            movement_type='entry',
            user_id=user_id,
            location_to_id=to_location_id,
            variant_id=variant_id,
            reason=reason or f"Transfert depuis {from_location_id}"
        )
        self.session.add(entry_movement)
        self.session.flush()
        
        # Update stock items
        source_item.physical_quantity -= quantity
        source_item.last_movement_at = exit_movement.created_at
        
        dest_item.physical_quantity += quantity
        dest_item.last_movement_at = entry_movement.created_at
        
        # Validate rules
        self.validate_stock_rules(source_item, 'transfer')
        self.validate_stock_rules(dest_item, 'transfer')
        
        return TransferResult(
            from_stock_item_id=source_item.id,
            to_stock_item_id=dest_item.id,
            quantity=quantity,
            exit_movement_id=exit_movement.id,
            entry_movement_id=entry_movement.id,
            success=True,
            message="Transfert réussi"
        )
    
    # ==================== Valuation Methods ====================
    
    def calculate_stock_value(
        self, 
        stock_item: StockItem, 
        method: str = 'standard'
    ) -> Decimal:
        """
        Calculate stock value according to valuation method.
        
        Args:
            stock_item: Stock item to value
            method: Valuation method ('standard', 'fifo', 'avco')
            
        Returns:
            Stock value in Decimal
        """
        if method == 'standard':
            # Use product cost
            product = self.session.query(Product).get(stock_item.product_id)
            if product and product.cost:
                return stock_item.physical_quantity * product.cost
            return Decimal('0')
        
        elif method == 'fifo':
            # First In, First Out - use earliest entry movements
            # TODO: Implement FIFO calculation based on entry movements
            # For now, use standard method
            return self.calculate_stock_value(stock_item, 'standard')
        
        elif method == 'avco':
            # Average Cost - weighted average of entry movements
            # TODO: Implement AVCO calculation
            # For now, use standard method
            return self.calculate_stock_value(stock_item, 'standard')
        
        else:
            raise ValueError(f"Méthode de valorisation inconnue: {method}")
    
    # ==================== Reorder Methods ====================
    
    def calculate_reorder_needs(
        self, 
        location_id: Optional[int] = None
    ) -> List[ReorderNeed]:
        """
        Calculate reorder needs based on reorder points and minimum stock.
        
        Args:
            location_id: Optional location ID to filter (None = all locations)
            
        Returns:
            List of ReorderNeed objects sorted by urgency
        """
        query = self.session.query(StockItem).join(Product).join(Location)
        
        if location_id:
            query = query.filter(StockItem.location_id == location_id)
        
        # Filter items that need reordering
        stock_items = query.filter(
            or_(
                and_(
                    StockItem.reorder_point.isnot(None),
                    StockItem.physical_quantity <= StockItem.reorder_point
                ),
                and_(
                    StockItem.min_stock.isnot(None),
                    StockItem.physical_quantity < StockItem.min_stock
                )
            )
        ).all()
        
        reorder_needs = []
        
        for item in stock_items:
            # Determine urgency
            if item.min_stock and item.physical_quantity <= 0:
                urgency = 'critical'
            elif item.min_stock and item.physical_quantity < item.min_stock:
                urgency = 'high'
            elif item.reorder_point and item.physical_quantity <= item.reorder_point:
                urgency = 'medium'
            else:
                urgency = 'low'
            
            # Calculate suggested quantity
            if item.reorder_quantity:
                suggested = item.reorder_quantity
            elif item.max_stock:
                suggested = item.max_stock - item.physical_quantity
            else:
                suggested = item.min_stock - item.physical_quantity if item.min_stock else Decimal('0')
            
            reorder_needs.append(ReorderNeed(
                stock_item_id=item.id,
                product_id=item.product_id,
                product_code=item.product.code if item.product else '',
                product_name=item.product.name if item.product else '',
                location_id=item.location_id,
                location_code=item.location.code if item.location else '',
                current_quantity=item.physical_quantity,
                min_stock=item.min_stock or Decimal('0'),
                reorder_point=item.reorder_point or Decimal('0'),
                suggested_quantity=max(suggested, Decimal('0')),
                urgency=urgency
            ))
        
        # Sort by urgency (critical > high > medium > low)
        urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        reorder_needs.sort(key=lambda x: urgency_order.get(x.urgency, 99))
        
        return reorder_needs

