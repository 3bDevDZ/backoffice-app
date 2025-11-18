"""Query handlers for purchase receipt management."""
from app.application.common.cqrs import QueryHandler
from app.domain.models.purchase import PurchaseReceipt, PurchaseReceiptLine
from app.infrastructure.db import get_session
from .queries import ListPurchaseReceiptsQuery, GetPurchaseReceiptByIdQuery
from .receipt_dto import PurchaseReceiptDTO, PurchaseReceiptLineDTO


class ListPurchaseReceiptsHandler(QueryHandler):
    """Handler for listing purchase receipts."""
    
    def handle(self, query: ListPurchaseReceiptsQuery) -> list[PurchaseReceiptDTO]:
        """
        List purchase receipts with optional filters.
        
        Args:
            query: ListPurchaseReceiptsQuery with filters
            
        Returns:
            List of PurchaseReceiptDTO
        """
        with get_session() as session:
            # Build query
            q = session.query(PurchaseReceipt)
            
            # Apply filters
            if query.purchase_order_id:
                q = q.filter(PurchaseReceipt.purchase_order_id == query.purchase_order_id)
            
            if query.status:
                q = q.filter(PurchaseReceipt.status == query.status)
            
            if query.date_from:
                q = q.filter(PurchaseReceipt.receipt_date >= query.date_from)
            
            if query.date_to:
                q = q.filter(PurchaseReceipt.receipt_date <= query.date_to)
            
            # Order by receipt date descending
            q = q.order_by(PurchaseReceipt.receipt_date.desc(), PurchaseReceipt.number.desc())
            
            # Pagination
            offset = (query.page - 1) * query.per_page
            receipts = q.offset(offset).limit(query.per_page).all()
            
            # Convert to DTOs
            result = []
            for receipt in receipts:
                # Load relationships
                session.refresh(receipt, ['purchase_order', 'receiver', 'validator', 'lines'])
                
                # Get purchase order number
                po_number = None
                if receipt.purchase_order:
                    po_number = receipt.purchase_order.number
                
                # Get receiver name
                receiver_name = None
                if receipt.receiver:
                    receiver_name = getattr(receipt.receiver, 'name', None) or \
                                   getattr(receipt.receiver, 'username', None)
                
                # Get validator name
                validator_name = None
                if receipt.validator:
                    validator_name = getattr(receipt.validator, 'name', None) or \
                                    getattr(receipt.validator, 'username', None)
                
                # Convert lines
                lines_dto = []
                if receipt.lines:
                    for line in receipt.lines:
                        session.refresh(line, ['product', 'location', 'purchase_order_line'])
                        
                        product_code = None
                        product_name = None
                        if line.product:
                            product_code = getattr(line.product, 'code', None)
                            product_name = getattr(line.product, 'name', None)
                        
                        location_code = None
                        if line.location:
                            location_code = getattr(line.location, 'code', None)
                        
                        lines_dto.append(PurchaseReceiptLineDTO(
                            id=line.id,
                            purchase_order_line_id=line.purchase_order_line_id,
                            product_id=line.product_id,
                            product_code=product_code,
                            product_name=product_name,
                            quantity_ordered=line.quantity_ordered,
                            quantity_received=line.quantity_received,
                            quantity_discrepancy=line.quantity_discrepancy,
                            discrepancy_reason=line.discrepancy_reason,
                            quality_notes=line.quality_notes,
                            location_id=line.location_id,
                            location_code=location_code,
                            sequence=line.sequence
                        ))
                
                result.append(PurchaseReceiptDTO(
                    id=receipt.id,
                    number=receipt.number,
                    purchase_order_id=receipt.purchase_order_id,
                    purchase_order_number=po_number,
                    receipt_date=receipt.receipt_date,
                    received_by=receipt.received_by,
                    received_by_name=receiver_name,
                    status=receipt.status,
                    validated_by=receipt.validated_by,
                    validated_by_name=validator_name,
                    validated_at=receipt.validated_at,
                    notes=receipt.notes,
                    internal_notes=receipt.internal_notes,
                    lines=lines_dto,
                    created_at=receipt.created_at,
                    updated_at=receipt.updated_at
                ))
            
            return result


class GetPurchaseReceiptByIdHandler(QueryHandler):
    """Handler for getting a purchase receipt by ID."""
    
    def handle(self, query: GetPurchaseReceiptByIdQuery) -> PurchaseReceiptDTO:
        """
        Get a purchase receipt by ID.
        
        Args:
            query: GetPurchaseReceiptByIdQuery with receipt ID
            
        Returns:
            PurchaseReceiptDTO or None if not found
        """
        with get_session() as session:
            receipt = session.get(PurchaseReceipt, query.id)
            if not receipt:
                return None
            
            # Load relationships
            session.refresh(receipt, ['purchase_order', 'receiver', 'validator', 'lines'])
            
            # Get purchase order number
            po_number = None
            if receipt.purchase_order:
                po_number = receipt.purchase_order.number
            
            # Get receiver name
            receiver_name = None
            if receipt.receiver:
                receiver_name = getattr(receipt.receiver, 'name', None) or \
                               getattr(receipt.receiver, 'username', None)
            
            # Get validator name
            validator_name = None
            if receipt.validator:
                validator_name = getattr(receipt.validator, 'name', None) or \
                                getattr(receipt.validator, 'username', None)
            
            # Convert lines
            lines_dto = []
            if receipt.lines:
                for line in receipt.lines:
                    session.refresh(line, ['product', 'location', 'purchase_order_line'])
                    
                    product_code = None
                    product_name = None
                    if line.product:
                        product_code = getattr(line.product, 'code', None)
                        product_name = getattr(line.product, 'name', None)
                    
                    location_code = None
                    if line.location:
                        location_code = getattr(line.location, 'code', None)
                    
                    lines_dto.append(PurchaseReceiptLineDTO(
                        id=line.id,
                        purchase_order_line_id=line.purchase_order_line_id,
                        product_id=line.product_id,
                        product_code=product_code,
                        product_name=product_name,
                        quantity_ordered=line.quantity_ordered,
                        quantity_received=line.quantity_received,
                        quantity_discrepancy=line.quantity_discrepancy,
                        discrepancy_reason=line.discrepancy_reason,
                        quality_notes=line.quality_notes,
                        location_id=line.location_id,
                        location_code=location_code,
                        sequence=line.sequence
                    ))
            
            return PurchaseReceiptDTO(
                id=receipt.id,
                number=receipt.number,
                purchase_order_id=receipt.purchase_order_id,
                purchase_order_number=po_number,
                receipt_date=receipt.receipt_date,
                received_by=receipt.received_by,
                received_by_name=receiver_name,
                status=receipt.status,
                validated_by=receipt.validated_by,
                validated_by_name=validator_name,
                validated_at=receipt.validated_at,
                notes=receipt.notes,
                internal_notes=receipt.internal_notes,
                lines=lines_dto,
                created_at=receipt.created_at,
                updated_at=receipt.updated_at
            )




