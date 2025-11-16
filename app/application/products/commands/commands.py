from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from app.application.common.cqrs import Command


# Product Commands
@dataclass
class CreateProductCommand(Command):
    code: str
    name: str
    description: str = None
    price: Decimal = Decimal(0)
    cost: Decimal = None
    unit_of_measure: str = None
    barcode: str = None
    category_ids: List[int] = None


@dataclass
class UpdateProductCommand(Command):
    id: int
    name: str = None
    description: str = None
    price: Decimal = None
    cost: Decimal = None
    unit_of_measure: str = None
    barcode: str = None
    category_ids: List[int] = None


@dataclass
class ArchiveProductCommand(Command):
    id: int


@dataclass
class DeleteProductCommand(Command):
    id: int


@dataclass
class ActivateProductCommand(Command):
    id: int


@dataclass
class DeactivateProductCommand(Command):
    id: int


# Category Commands
@dataclass
class CreateCategoryCommand(Command):
    name: str
    code: str = None
    parent_id: int = None
    description: str = None


@dataclass
class UpdateCategoryCommand(Command):
    id: int
    name: str = None
    code: str = None
    description: str = None


@dataclass
class DeleteCategoryCommand(Command):
    id: int