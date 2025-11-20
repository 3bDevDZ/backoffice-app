"""Query handlers for site management."""
from typing import List
from app.application.common.cqrs import QueryHandler
from app.domain.models.stock import Site, StockItem
from app.infrastructure.db import get_session
from app.services.site_service import SiteService
from .queries import ListSitesQuery, GetSiteByIdQuery, GetSiteStockQuery
from .site_dto import SiteDTO, SiteStockItemDTO


class ListSitesHandler(QueryHandler):
    """Handler for listing sites."""
    
    def handle(self, query: ListSitesQuery) -> List[SiteDTO]:
        """
        List sites with optional filters.
        
        Args:
            query: ListSitesQuery with filters
            
        Returns:
            List of SiteDTO
        """
        with get_session() as session:
            # Build query
            q = session.query(Site)
            
            # Apply filters
            if query.status:
                q = q.filter(Site.status == query.status)
            
            if query.search:
                search_term = f"%{query.search}%"
                q = q.filter(
                    (Site.code.ilike(search_term)) |
                    (Site.name.ilike(search_term))
                )
            
            # Order by name
            q = q.order_by(Site.name)
            
            # Pagination
            offset = (query.page - 1) * query.per_page
            sites = q.offset(offset).limit(query.per_page).all()
            
            # Convert to DTOs
            result = []
            for site in sites:
                # Get manager name
                manager_name = None
                if site.manager:
                    manager_name = getattr(site.manager, 'name', None) or \
                                 getattr(site.manager, 'username', None)
                
                result.append(SiteDTO(
                    id=site.id,
                    code=site.code,
                    name=site.name,
                    address=site.address,
                    manager_id=site.manager_id,
                    manager_name=manager_name,
                    status=site.status,
                    created_at=site.created_at,
                    updated_at=site.updated_at
                ))
            
            return result


class GetSiteByIdHandler(QueryHandler):
    """Handler for getting a site by ID."""
    
    def handle(self, query: GetSiteByIdQuery) -> SiteDTO:
        """
        Get a site by ID.
        
        Args:
            query: GetSiteByIdQuery with site ID
            
        Returns:
            SiteDTO or None if not found
        """
        with get_session() as session:
            site = session.get(Site, query.id)
            if not site:
                return None
            
            # Get manager name
            manager_name = None
            if site.manager:
                manager_name = getattr(site.manager, 'name', None) or \
                             getattr(site.manager, 'username', None)
            
            return SiteDTO(
                id=site.id,
                code=site.code,
                name=site.name,
                address=site.address,
                manager_id=site.manager_id,
                manager_name=manager_name,
                status=site.status,
                created_at=site.created_at,
                updated_at=site.updated_at
            )


class GetSiteStockHandler(QueryHandler):
    """Handler for getting stock for a site."""
    
    def handle(self, query: GetSiteStockQuery) -> List[SiteStockItemDTO]:
        """
        Get stock items for a specific site.
        
        Args:
            query: GetSiteStockQuery with site ID and filters
            
        Returns:
            List of SiteStockItemDTO
        """
        with get_session() as session:
            site_service = SiteService(session)
            stock_items = site_service.get_site_stock(
                site_id=query.site_id,
                product_id=query.product_id,
                variant_id=query.variant_id
            )
            
            # Convert to DTOs
            result = []
            for item in stock_items:
                product_code = None
                product_name = None
                if item.product:
                    product_code = getattr(item.product, 'code', None)
                    product_name = getattr(item.product, 'name', None)
                
                location_code = None
                location_name = None
                if item.location:
                    location_code = getattr(item.location, 'code', None)
                    location_name = getattr(item.location, 'name', None)
                
                result.append(SiteStockItemDTO(
                    id=item.id,
                    product_id=item.product_id,
                    product_code=product_code,
                    product_name=product_name,
                    variant_id=item.variant_id,
                    location_id=item.location_id,
                    location_code=location_code,
                    location_name=location_name,
                    physical_quantity=item.physical_quantity,
                    reserved_quantity=item.reserved_quantity,
                    available_quantity=item.available_quantity
                ))
            
            return result


