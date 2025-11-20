"""Commands for site management."""
from dataclasses import dataclass
from typing import Optional

from app.application.common.cqrs import Command


@dataclass
class CreateSiteCommand(Command):
    """Command to create a new site."""
    code: str
    name: str
    address: Optional[str] = None
    manager_id: Optional[int] = None
    status: str = 'active'


@dataclass
class UpdateSiteCommand(Command):
    """Command to update an existing site."""
    id: int
    name: Optional[str] = None
    address: Optional[str] = None
    manager_id: Optional[int] = None
    status: Optional[str] = None


@dataclass
class DeactivateSiteCommand(Command):
    """Command to deactivate a site."""
    id: int


