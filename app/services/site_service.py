"""Service for site management operations."""
from typing import List, Optional, Tuple
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.domain.models.stock import Site, Location, StockItem
from app.domain.models.user import User


class SiteService:
    """Service for managing sites and site-related operations."""
    
    def __init__(self, session: Session):
        """
        Initialize the site service.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
    
    def create_site(
        self,
        code: str,
        name: str,
        address: Optional[str] = None,
        manager_id: Optional[int] = None,
        status: str = 'active'
    ) -> Site:
        """
        Create a new site.
        
        Args:
            code: Unique site code
            name: Site name
            address: Optional site address
            manager_id: Optional site manager user ID
            status: Site status ('active', 'inactive', 'archived')
            
        Returns:
            Created Site instance
            
        Raises:
            ValueError: If validation fails
        """
        # Check if code already exists
        existing = self.session.query(Site).filter(Site.code == code).first()
        if existing:
            raise ValueError(f"Site with code '{code}' already exists.")
        
        # Validate manager if provided
        if manager_id:
            manager = self.session.get(User, manager_id)
            if not manager:
                raise ValueError(f"User with ID {manager_id} not found.")
        
        site = Site.create(
            code=code,
            name=name,
            address=address,
            manager_id=manager_id,
            status=status
        )
        
        self.session.add(site)
        self.session.flush()
        
        return site
    
    def update_site(
        self,
        site_id: int,
        name: Optional[str] = None,
        address: Optional[str] = None,
        manager_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> Site:
        """
        Update an existing site.
        
        Args:
            site_id: Site ID
            name: Optional new name
            address: Optional new address
            manager_id: Optional new manager ID
            status: Optional new status
            
        Returns:
            Updated Site instance
            
        Raises:
            ValueError: If site not found or validation fails
        """
        site = self.session.get(Site, site_id)
        if not site:
            raise ValueError(f"Site with ID {site_id} not found.")
        
        if name is not None:
            if not name.strip():
                raise ValueError("Site name cannot be empty.")
            site.name = name.strip()
        
        if address is not None:
            site.address = address.strip() if address else None
        
        if manager_id is not None:
            if manager_id:
                manager = self.session.get(User, manager_id)
                if not manager:
                    raise ValueError(f"User with ID {manager_id} not found.")
            site.manager_id = manager_id
        
        if status is not None:
            if status == 'inactive':
                site.deactivate()
            elif status == 'active':
                site.activate()
            elif status == 'archived':
                site.archive()
            else:
                raise ValueError(f"Invalid status: {status}")
        
        site.updated_at = datetime.utcnow()
        self.session.flush()
        
        return site
    
    def get_site_stock(
        self,
        site_id: int,
        product_id: Optional[int] = None,
        variant_id: Optional[int] = None
    ) -> List[StockItem]:
        """
        Get stock items for a specific site.
        
        Args:
            site_id: Site ID
            product_id: Optional product ID filter
            variant_id: Optional variant ID filter
            
        Returns:
            List of StockItem instances for the site
        """
        query = self.session.query(StockItem).filter(StockItem.site_id == site_id)
        
        if product_id:
            query = query.filter(StockItem.product_id == product_id)
        
        if variant_id:
            query = query.filter(StockItem.variant_id == variant_id)
        
        return query.all()
    
    def get_site_locations(self, site_id: int) -> List[Location]:
        """
        Get all locations for a specific site.
        
        Args:
            site_id: Site ID
            
        Returns:
            List of Location instances for the site
        """
        return self.session.query(Location).filter(Location.site_id == site_id).all()
    
    def can_deactivate_site(self, site_id: int) -> Tuple[bool, Optional[str]]:
        """
        Check if a site can be deactivated.
        
        Args:
            site_id: Site ID
            
        Returns:
            Tuple of (can_deactivate, reason_if_not)
        """
        site = self.session.get(Site, site_id)
        if not site:
            return False, "Site not found."
        
        # Check if site has active stock
        stock_count = self.session.query(StockItem).filter(
            and_(
                StockItem.site_id == site_id,
                StockItem.physical_quantity > 0
            )
        ).count()
        
        if stock_count > 0:
            return False, f"Site has {stock_count} stock items with physical quantity > 0. Cannot deactivate."
        
        # Check if site has active transfers
        from app.domain.models.stock import StockTransfer
        active_transfers = self.session.query(StockTransfer).filter(
            and_(
                or_(
                    StockTransfer.source_site_id == site_id,
                    StockTransfer.destination_site_id == site_id
                ),
                StockTransfer.status.in_(['created', 'in_transit'])
            )
        ).count()
        
        if active_transfers > 0:
            return False, f"Site has {active_transfers} active transfers. Cannot deactivate."
        
        return True, None

