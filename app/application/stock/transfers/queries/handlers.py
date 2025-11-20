"""Query handlers for stock transfer management."""
from typing import List
from app.application.common.cqrs import QueryHandler
from app.domain.models.stock import StockTransfer, StockTransferLine
from app.infrastructure.db import get_session
from .queries import ListStockTransfersQuery, GetStockTransferByIdQuery
from .transfer_dto import StockTransferDTO, StockTransferLineDTO


class ListStockTransfersHandler(QueryHandler):
    """Handler for listing stock transfers."""
    
    def handle(self, query: ListStockTransfersQuery) -> List[StockTransferDTO]:
        """
        List stock transfers with optional filters.
        
        Args:
            query: ListStockTransfersQuery with filters
            
        Returns:
            List of StockTransferDTO
        """
        with get_session() as session:
            # Build query
            q = session.query(StockTransfer)
            
            # Apply filters
            if query.source_site_id:
                q = q.filter(StockTransfer.source_site_id == query.source_site_id)
            
            if query.destination_site_id:
                q = q.filter(StockTransfer.destination_site_id == query.destination_site_id)
            
            if query.status:
                q = q.filter(StockTransfer.status == query.status)
            
            if query.date_from:
                q = q.filter(StockTransfer.created_at >= query.date_from)
            
            if query.date_to:
                q = q.filter(StockTransfer.created_at <= query.date_to)
            
            # Order by created date descending
            q = q.order_by(StockTransfer.created_at.desc())
            
            # Pagination
            offset = (query.page - 1) * query.per_page
            transfers = q.offset(offset).limit(query.per_page).all()
            
            # Convert to DTOs
            result = []
            for transfer in transfers:
                # Load relationships
                session.refresh(transfer, ['source_site', 'destination_site', 'shipper', 'receiver', 'creator', 'lines'])
                
                # Get site codes and names
                source_site_code = None
                source_site_name = None
                if transfer.source_site:
                    source_site_code = getattr(transfer.source_site, 'code', None)
                    source_site_name = getattr(transfer.source_site, 'name', None)
                
                destination_site_code = None
                destination_site_name = None
                if transfer.destination_site:
                    destination_site_code = getattr(transfer.destination_site, 'code', None)
                    destination_site_name = getattr(transfer.destination_site, 'name', None)
                
                # Get user names
                shipped_by_name = None
                if transfer.shipper:
                    shipped_by_name = getattr(transfer.shipper, 'name', None) or \
                                    getattr(transfer.shipper, 'username', None)
                
                received_by_name = None
                if transfer.receiver:
                    received_by_name = getattr(transfer.receiver, 'name', None) or \
                                     getattr(transfer.receiver, 'username', None)
                
                created_by_name = None
                if transfer.creator:
                    created_by_name = getattr(transfer.creator, 'name', None) or \
                                    getattr(transfer.creator, 'username', None)
                
                # Convert lines
                lines_dto = []
                if transfer.lines:
                    for line in transfer.lines:
                        session.refresh(line, ['product'])
                        
                        product_code = None
                        product_name = None
                        if line.product:
                            product_code = getattr(line.product, 'code', None)
                            product_name = getattr(line.product, 'name', None)
                        
                        lines_dto.append(StockTransferLineDTO(
                            id=line.id,
                            product_id=line.product_id,
                            product_code=product_code,
                            product_name=product_name,
                            variant_id=line.variant_id,
                            quantity=line.quantity,
                            quantity_received=line.quantity_received,
                            sequence=line.sequence,
                            notes=line.notes
                        ))
                
                result.append(StockTransferDTO(
                    id=transfer.id,
                    number=transfer.number,
                    source_site_id=transfer.source_site_id,
                    source_site_code=source_site_code,
                    source_site_name=source_site_name,
                    destination_site_id=transfer.destination_site_id,
                    destination_site_code=destination_site_code,
                    destination_site_name=destination_site_name,
                    status=transfer.status,
                    requested_date=transfer.requested_date,
                    shipped_date=transfer.shipped_date,
                    received_date=transfer.received_date,
                    shipped_by=transfer.shipped_by,
                    shipped_by_name=shipped_by_name,
                    received_by=transfer.received_by,
                    received_by_name=received_by_name,
                    notes=transfer.notes,
                    created_by=transfer.created_by,
                    created_by_name=created_by_name,
                    lines=lines_dto,
                    created_at=transfer.created_at,
                    updated_at=transfer.updated_at
                ))
            
            return result


class GetStockTransferByIdHandler(QueryHandler):
    """Handler for getting a stock transfer by ID."""
    
    def handle(self, query: GetStockTransferByIdQuery) -> StockTransferDTO:
        """
        Get a stock transfer by ID.
        
        Args:
            query: GetStockTransferByIdQuery with transfer ID
            
        Returns:
            StockTransferDTO or None if not found
        """
        with get_session() as session:
            transfer = session.get(StockTransfer, query.id)
            if not transfer:
                return None
            
            # Load relationships
            session.refresh(transfer, ['source_site', 'destination_site', 'shipper', 'receiver', 'creator', 'lines'])
            
            # Get site codes and names
            source_site_code = None
            source_site_name = None
            if transfer.source_site:
                source_site_code = getattr(transfer.source_site, 'code', None)
                source_site_name = getattr(transfer.source_site, 'name', None)
            
            destination_site_code = None
            destination_site_name = None
            if transfer.destination_site:
                destination_site_code = getattr(transfer.destination_site, 'code', None)
                destination_site_name = getattr(transfer.destination_site, 'name', None)
            
            # Get user names
            shipped_by_name = None
            if transfer.shipper:
                shipped_by_name = getattr(transfer.shipper, 'name', None) or \
                                getattr(transfer.shipper, 'username', None)
            
            received_by_name = None
            if transfer.receiver:
                received_by_name = getattr(transfer.receiver, 'name', None) or \
                                 getattr(transfer.receiver, 'username', None)
            
            created_by_name = None
            if transfer.creator:
                created_by_name = getattr(transfer.creator, 'name', None) or \
                                getattr(transfer.creator, 'username', None)
            
            # Convert lines
            lines_dto = []
            if transfer.lines:
                for line in transfer.lines:
                    session.refresh(line, ['product'])
                    
                    product_code = None
                    product_name = None
                    if line.product:
                        product_code = getattr(line.product, 'code', None)
                        product_name = getattr(line.product, 'name', None)
                    
                    lines_dto.append(StockTransferLineDTO(
                        id=line.id,
                        product_id=line.product_id,
                        product_code=product_code,
                        product_name=product_name,
                        variant_id=line.variant_id,
                        quantity=line.quantity,
                        quantity_received=line.quantity_received,
                        sequence=line.sequence,
                        notes=line.notes
                    ))
            
            return StockTransferDTO(
                id=transfer.id,
                number=transfer.number,
                source_site_id=transfer.source_site_id,
                source_site_code=source_site_code,
                source_site_name=source_site_name,
                destination_site_id=transfer.destination_site_id,
                destination_site_code=destination_site_code,
                destination_site_name=destination_site_name,
                status=transfer.status,
                requested_date=transfer.requested_date,
                shipped_date=transfer.shipped_date,
                received_date=transfer.received_date,
                shipped_by=transfer.shipped_by,
                shipped_by_name=shipped_by_name,
                received_by=transfer.received_by,
                received_by_name=received_by_name,
                notes=transfer.notes,
                created_by=transfer.created_by,
                created_by_name=created_by_name,
                lines=lines_dto,
                created_at=transfer.created_at,
                updated_at=transfer.updated_at
            )


