"""Query handlers for purchase request management."""
from app.application.common.cqrs import QueryHandler
from app.domain.models.purchase import PurchaseRequest, PurchaseRequestLine
from app.infrastructure.db import get_session
from .queries import ListPurchaseRequestsQuery, GetPurchaseRequestByIdQuery
from .request_dto import PurchaseRequestDTO, PurchaseRequestLineDTO


class ListPurchaseRequestsHandler(QueryHandler):
    """Handler for listing purchase requests."""
    
    def handle(self, query: ListPurchaseRequestsQuery) -> list[PurchaseRequestDTO]:
        """
        List purchase requests with optional filters.
        
        Args:
            query: ListPurchaseRequestsQuery with filters
            
        Returns:
            List of PurchaseRequestDTO
        """
        with get_session() as session:
            # Build query
            q = session.query(PurchaseRequest)
            
            # Apply filters
            if query.status:
                q = q.filter(PurchaseRequest.status == query.status)
            
            if query.requested_by:
                q = q.filter(PurchaseRequest.requested_by == query.requested_by)
            
            if query.date_from:
                q = q.filter(PurchaseRequest.requested_date >= query.date_from)
            
            if query.date_to:
                q = q.filter(PurchaseRequest.requested_date <= query.date_to)
            
            # Order by requested date descending
            q = q.order_by(PurchaseRequest.requested_date.desc(), PurchaseRequest.number.desc())
            
            # Pagination
            offset = (query.page - 1) * query.per_page
            requests = q.offset(offset).limit(query.per_page).all()
            
            # Convert to DTOs
            result = []
            for request in requests:
                # Load relationships
                session.refresh(request, ['requester', 'approver', 'converted_to_po', 'lines'])
                
                # Get requester name
                requester_name = None
                if request.requester:
                    requester_name = getattr(request.requester, 'name', None) or \
                                    getattr(request.requester, 'username', None)
                
                # Get approver name
                approver_name = None
                if request.approver:
                    approver_name = getattr(request.approver, 'name', None) or \
                                   getattr(request.approver, 'username', None)
                
                # Get converted PO number
                po_number = None
                if request.converted_to_po:
                    po_number = request.converted_to_po.number
                
                # Convert lines
                lines_dto = []
                if request.lines:
                    for line in request.lines:
                        session.refresh(line, ['product'])
                        
                        product_code = None
                        product_name = None
                        if line.product:
                            product_code = getattr(line.product, 'code', None)
                            product_name = getattr(line.product, 'name', None)
                        
                        lines_dto.append(PurchaseRequestLineDTO(
                            id=line.id,
                            product_id=line.product_id,
                            product_code=product_code,
                            product_name=product_name,
                            quantity=line.quantity,
                            unit_price_estimate=line.unit_price_estimate,
                            notes=line.notes,
                            sequence=line.sequence
                        ))
                
                result.append(PurchaseRequestDTO(
                    id=request.id,
                    number=request.number,
                    requested_by=request.requested_by,
                    requested_by_name=requester_name,
                    requested_date=request.requested_date,
                    required_date=request.required_date,
                    status=request.status,
                    approved_by=request.approved_by,
                    approved_by_name=approver_name,
                    approved_at=request.approved_at,
                    rejection_reason=request.rejection_reason,
                    converted_to_po_id=request.converted_to_po_id,
                    converted_to_po_number=po_number,
                    converted_at=request.converted_at,
                    notes=request.notes,
                    internal_notes=request.internal_notes,
                    lines=lines_dto,
                    created_at=request.created_at,
                    updated_at=request.updated_at
                ))
            
            return result


class GetPurchaseRequestByIdHandler(QueryHandler):
    """Handler for getting a purchase request by ID."""
    
    def handle(self, query: GetPurchaseRequestByIdQuery) -> PurchaseRequestDTO:
        """
        Get a purchase request by ID.
        
        Args:
            query: GetPurchaseRequestByIdQuery with request ID
            
        Returns:
            PurchaseRequestDTO or None if not found
        """
        with get_session() as session:
            request = session.get(PurchaseRequest, query.id)
            if not request:
                return None
            
            # Load relationships
            session.refresh(request, ['requester', 'approver', 'converted_to_po', 'lines'])
            
            # Get requester name
            requester_name = None
            if request.requester:
                requester_name = getattr(request.requester, 'name', None) or \
                                getattr(request.requester, 'username', None)
            
            # Get approver name
            approver_name = None
            if request.approver:
                approver_name = getattr(request.approver, 'name', None) or \
                               getattr(request.approver, 'username', None)
            
            # Get converted PO number
            po_number = None
            if request.converted_to_po:
                po_number = request.converted_to_po.number
            
            # Convert lines
            lines_dto = []
            if request.lines:
                for line in request.lines:
                    session.refresh(line, ['product'])
                    
                    product_code = None
                    product_name = None
                    if line.product:
                        product_code = getattr(line.product, 'code', None)
                        product_name = getattr(line.product, 'name', None)
                    
                    lines_dto.append(PurchaseRequestLineDTO(
                        id=line.id,
                        product_id=line.product_id,
                        product_code=product_code,
                        product_name=product_name,
                        quantity=line.quantity,
                        unit_price_estimate=line.unit_price_estimate,
                        notes=line.notes,
                        sequence=line.sequence
                    ))
            
            return PurchaseRequestDTO(
                id=request.id,
                number=request.number,
                requested_by=request.requested_by,
                requested_by_name=requester_name,
                requested_date=request.requested_date,
                required_date=request.required_date,
                status=request.status,
                approved_by=request.approved_by,
                approved_by_name=approver_name,
                approved_at=request.approved_at,
                rejection_reason=request.rejection_reason,
                converted_to_po_id=request.converted_to_po_id,
                converted_to_po_number=po_number,
                converted_at=request.converted_at,
                notes=request.notes,
                internal_notes=request.internal_notes,
                lines=lines_dto,
                created_at=request.created_at,
                updated_at=request.updated_at
            )




