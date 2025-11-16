"""Commands for Price List management."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from app.application.common.cqrs import Command


# PriceList Commands
@dataclass
class CreatePriceListCommand(Command):
    """Command to create a new price list."""
    name: str
    description: Optional[str] = None
    is_active: bool = True


@dataclass
class UpdatePriceListCommand(Command):
    """Command to update an existing price list."""
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


@dataclass
class DeletePriceListCommand(Command):
    """Command to delete a price list."""
    id: int


# ProductPriceList Commands
@dataclass
class AddProductToPriceListCommand(Command):
    """Command to add a product to a price list with a specific price."""
    price_list_id: int
    product_id: int
    price: Decimal


@dataclass
class UpdateProductPriceInListCommand(Command):
    """Command to update a product's price in a price list."""
    price_list_id: int
    product_id: int
    price: Decimal


@dataclass
class RemoveProductFromPriceListCommand(Command):
    """Command to remove a product from a price list."""
    price_list_id: int
    product_id: int


# ProductVolumePricing Commands
@dataclass
class CreateVolumePricingCommand(Command):
    """Command to create a volume pricing tier for a product."""
    product_id: int
    min_quantity: Decimal
    price: Decimal
    max_quantity: Optional[Decimal] = None  # None = unlimited


@dataclass
class UpdateVolumePricingCommand(Command):
    """Command to update a volume pricing tier."""
    id: int
    min_quantity: Optional[Decimal] = None
    max_quantity: Optional[Decimal] = None
    price: Optional[Decimal] = None


@dataclass
class DeleteVolumePricingCommand(Command):
    """Command to delete a volume pricing tier."""
    id: int


# ProductPromotionalPrice Commands
@dataclass
class CreatePromotionalPriceCommand(Command):
    """Command to create a promotional price for a product."""
    product_id: int
    price: Decimal
    start_date: str  # ISO format datetime string
    end_date: str  # ISO format datetime string
    description: Optional[str] = None
    created_by: Optional[int] = None


@dataclass
class UpdatePromotionalPriceCommand(Command):
    """Command to update a promotional price."""
    id: int
    price: Optional[Decimal] = None
    start_date: Optional[str] = None  # ISO format datetime string
    end_date: Optional[str] = None  # ISO format datetime string
    description: Optional[str] = None
    is_active: Optional[bool] = None


@dataclass
class DeletePromotionalPriceCommand(Command):
    """Command to delete a promotional price."""
    id: int

