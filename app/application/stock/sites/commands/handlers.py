"""Command handlers for site management."""
from app.application.common.cqrs import CommandHandler
from app.domain.models.stock import Site
from app.infrastructure.db import get_session
from app.services.site_service import SiteService
from .commands import (
    CreateSiteCommand,
    UpdateSiteCommand,
    DeactivateSiteCommand
)


class CreateSiteHandler(CommandHandler):
    """Handler for creating a new site."""
    
    def handle(self, command: CreateSiteCommand) -> int:
        """
        Create a new site.
        
        Args:
            command: CreateSiteCommand with site details
            
        Returns:
            Site ID (int)
        """
        with get_session() as session:
            site_service = SiteService(session)
            site = site_service.create_site(
                code=command.code,
                name=command.name,
                address=command.address,
                manager_id=command.manager_id,
                status=command.status
            )
            
            site_id = site.id
            session.commit()
            
            return site_id


class UpdateSiteHandler(CommandHandler):
    """Handler for updating an existing site."""
    
    def handle(self, command: UpdateSiteCommand) -> int:
        """
        Update an existing site.
        
        Args:
            command: UpdateSiteCommand with site updates
            
        Returns:
            Site ID (int)
        """
        with get_session() as session:
            site_service = SiteService(session)
            site = site_service.update_site(
                site_id=command.id,
                name=command.name,
                address=command.address,
                manager_id=command.manager_id,
                status=command.status
            )
            
            site_id = site.id
            session.commit()
            
            return site_id


class DeactivateSiteHandler(CommandHandler):
    """Handler for deactivating a site."""
    
    def handle(self, command: DeactivateSiteCommand) -> int:
        """
        Deactivate a site.
        
        Args:
            command: DeactivateSiteCommand with site ID
            
        Returns:
            Site ID (int)
        """
        with get_session() as session:
            site_service = SiteService(session)
            
            # Check if site can be deactivated
            can_deactivate, reason = site_service.can_deactivate_site(command.id)
            if not can_deactivate:
                raise ValueError(reason or "Cannot deactivate site.")
            
            site = site_service.update_site(
                site_id=command.id,
                status='inactive'
            )
            
            site_id = site.id
            session.commit()
            
            return site_id


