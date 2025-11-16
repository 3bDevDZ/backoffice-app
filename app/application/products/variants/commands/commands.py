"""Commands for Product Variant management."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from app.application.common.cqrs import Command


@dataclass
class CreateVariantCommand(Command):
    """Command to create a new product variant."""
    product_id: int
    code: str
    name: str
    attributes: Optional[str] = None  # JSON string for variant attributes
    price: Optional[Decimal] = None  # Override price if different from parent
    cost: Optional[Decimal] = None  # Override cost if different from parent
    barcode: Optional[str] = None


@dataclass
class UpdateVariantCommand(Command):
    """Command to update an existing product variant."""
    id: int
    name: Optional[str] = None
    attributes: Optional[str] = None
    price: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    barcode: Optional[str] = None


@dataclass
class ArchiveVariantCommand(Command):
    """Command to archive a product variant."""
    id: int


@dataclass
class ActivateVariantCommand(Command):
    """Command to activate an archived product variant."""
    id: int


@dataclass
class DeleteVariantCommand(Command):
    """Command to delete a product variant (only if not referenced)."""
    id: int

