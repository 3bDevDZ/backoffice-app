"""Query handlers for quote management."""
from app.application.common.cqrs import QueryHandler
from app.domain.models.quote import Quote, QuoteLine, QuoteVersion
from app.domain.models.customer import Customer
from app.domain.models.product import Product
from app.domain.models.user import User
from app.infrastructure.db import get_session
from .queries import (
    ListQuotesQuery,
    GetQuoteByIdQuery,
    GetQuoteHistoryQuery
)
from .quote_dto import (
    QuoteDTO, QuoteLineDTO, QuoteVersionDTO
)
from typing import List
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload


class ListQuotesHandler(QueryHandler):
    def handle(self, query: ListQuotesQuery) -> dict:
        """List quotes with pagination and filtering."""
        with get_session() as session:
            # Build query
            q = session.query(Quote).join(Customer)
            
            # Apply filters
            if query.status:
                q = q.filter(Quote.status == query.status)
            
            if query.customer_id:
                q = q.filter(Quote.customer_id == query.customer_id)
            
            if query.search:
                search_term = f"%{query.search}%"
                q = q.filter(
                    or_(
                        Quote.number.ilike(search_term),
                        Customer.name.ilike(search_term),
                        Customer.code.ilike(search_term)
                    )
                )
            
            # Get total count
            total = q.count()
            
            # Apply pagination
            offset = (query.page - 1) * query.per_page
            quotes = q.order_by(Quote.created_at.desc()).offset(offset).limit(query.per_page).all()
            
            # Convert to DTOs
            quote_dtos = []
            for quote in quotes:
                quote_dto = QuoteDTO(
                    id=quote.id,
                    number=quote.number,
                    version=quote.version,
                    customer_id=quote.customer_id,
                    customer_code=quote.customer.code if quote.customer else None,
                    customer_name=quote.customer.name if quote.customer else None,
                    status=quote.status,
                    valid_until=quote.valid_until,
                    subtotal=quote.subtotal,
                    tax_amount=quote.tax_amount,
                    total=quote.total,
                    discount_percent=quote.discount_percent,
                    discount_amount=quote.discount_amount,
                    notes=quote.notes,
                    internal_notes=quote.internal_notes,
                    sent_at=quote.sent_at,
                    sent_by=quote.sent_by,
                    sent_by_username=quote.sender.username if quote.sender else None,
                    accepted_at=quote.accepted_at,
                    created_by=quote.created_by,
                    created_by_username=quote.creator.username if quote.creator else None,
                    created_at=quote.created_at,
                    updated_at=quote.updated_at,
                    lines=None,  # Not included in list view
                    versions=None
                )
                quote_dtos.append(quote_dto)
            
            return {
                'items': quote_dtos,
                'total': total,
                'page': query.page,
                'per_page': query.per_page,
                'pages': (total + query.per_page - 1) // query.per_page
            }


class GetQuoteByIdHandler(QueryHandler):
    def handle(self, query: GetQuoteByIdQuery) -> QuoteDTO:
        """Get a quote by ID with optional relationships."""
        with get_session() as session:
            # Build query with eager loading
            q = session.query(Quote).join(Customer)
            
            if query.include_lines:
                q = q.options(joinedload(Quote.lines).joinedload(QuoteLine.product))
            
            if query.include_versions:
                q = q.options(joinedload(Quote.versions).joinedload(QuoteVersion.creator))
            
            quote = q.filter(Quote.id == query.id).first()
            
            if not quote:
                raise ValueError(f"Quote with ID {query.id} not found.")
            
            # Convert lines to DTOs
            lines_dto = None
            if query.include_lines and quote.lines:
                lines_dto = [
                    QuoteLineDTO(
                        id=line.id,
                        quote_id=line.quote_id,
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
                        sequence=line.sequence
                    )
                    for line in quote.lines
                ]
            
            # Convert versions to DTOs
            versions_dto = None
            if query.include_versions and quote.versions:
                versions_dto = [
                    QuoteVersionDTO(
                        id=version.id,
                        quote_id=version.quote_id,
                        version_number=version.version_number,
                        created_by=version.created_by,
                        created_by_username=version.creator.username if version.creator else None,
                        created_at=version.created_at,
                        data=version.data
                    )
                    for version in quote.versions
                ]
            
            return QuoteDTO(
                id=quote.id,
                number=quote.number,
                version=quote.version,
                customer_id=quote.customer_id,
                customer_code=quote.customer.code if quote.customer else None,
                customer_name=quote.customer.name if quote.customer else None,
                status=quote.status,
                valid_until=quote.valid_until,
                subtotal=quote.subtotal,
                tax_amount=quote.tax_amount,
                total=quote.total,
                discount_percent=quote.discount_percent,
                discount_amount=quote.discount_amount,
                notes=quote.notes,
                internal_notes=quote.internal_notes,
                sent_at=quote.sent_at,
                sent_by=quote.sent_by,
                sent_by_username=quote.sender.username if quote.sender else None,
                accepted_at=quote.accepted_at,
                created_by=quote.created_by,
                created_by_username=quote.creator.username if quote.creator else None,
                created_at=quote.created_at,
                updated_at=quote.updated_at,
                lines=lines_dto,
                versions=versions_dto
            )


class GetQuoteHistoryHandler(QueryHandler):
    def handle(self, query: GetQuoteHistoryQuery) -> dict:
        """Get quote version history with pagination."""
        with get_session() as session:
            # Verify quote exists
            quote = session.get(Quote, query.quote_id)
            if not quote:
                raise ValueError(f"Quote with ID {query.quote_id} not found.")
            
            # Get versions
            q = session.query(QuoteVersion).filter(
                QuoteVersion.quote_id == query.quote_id
            ).join(User, QuoteVersion.created_by == User.id)
            
            # Get total count
            total = q.count()
            
            # Apply pagination
            offset = (query.page - 1) * query.per_page
            versions = q.order_by(QuoteVersion.version_number.desc()).offset(offset).limit(query.per_page).all()
            
            # Convert to DTOs
            version_dtos = [
                QuoteVersionDTO(
                    id=version.id,
                    quote_id=version.quote_id,
                    version_number=version.version_number,
                    created_by=version.created_by,
                    created_by_username=version.creator.username if version.creator else None,
                    created_at=version.created_at,
                    data=version.data
                )
                for version in versions
            ]
            
            return {
                'items': version_dtos,
                'total': total,
                'page': query.page,
                'per_page': query.per_page,
                'pages': (total + query.per_page - 1) // query.per_page
            }

