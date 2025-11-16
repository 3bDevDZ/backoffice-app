from app.application.common.cqrs import CommandHandler
from app.domain.models.product import Product
from app.domain.models.category import Category
from app.infrastructure.db import get_session
from .commands import (
    CreateProductCommand,
    UpdateProductCommand,
    ArchiveProductCommand,
    DeleteProductCommand,
    ActivateProductCommand,
    DeactivateProductCommand,
    CreateCategoryCommand,
    UpdateCategoryCommand,
    DeleteCategoryCommand
)


# Product Handlers
class CreateProductHandler(CommandHandler):
    def handle(self, command: CreateProductCommand) -> Product:
        with get_session() as session:
            # Validate categories exist if provided
            if command.category_ids:
                categories = session.query(Category).filter(
                    Category.id.in_(command.category_ids)
                ).all()
                if len(categories) != len(command.category_ids):
                    raise ValueError("One or more categories not found")
            elif command.category_ids is None or len(command.category_ids) == 0:
                raise ValueError("Product must have at least one category")
            
            # Create product using domain factory method
            product = Product.create(
                code=command.code,
                name=command.name,
                description=command.description,
                price=command.price,
                cost=command.cost,
                unit_of_measure=command.unit_of_measure,
                barcode=command.barcode
            )
            
            # Add categories via relationship
            if command.category_ids:
                product.categories = categories
            
            session.add(product)
            session.flush()  # Flush to get ID for domain event
            
            # Update domain event with product ID
            events = product.get_domain_events()
            for event in events:
                if hasattr(event, 'product_id') and event.product_id == 0:
                    event.product_id = product.id
            
            session.commit()  # Commit will trigger domain event dispatch
            return product


class UpdateProductHandler(CommandHandler):
    def handle(self, command: UpdateProductCommand) -> Product:
        with get_session() as session:
            product = session.get(Product, command.id)
            if not product:
                raise ValueError("Product not found")
            
            # Update product details using domain method
            product.update_details(
                name=command.name,
                description=command.description,
                price=command.price,
                cost=command.cost,
                unit_of_measure=command.unit_of_measure,
                barcode=command.barcode
            )
            
            # Update categories if provided
            if command.category_ids is not None:
                categories = session.query(Category).filter(
                    Category.id.in_(command.category_ids)
                ).all()
                if len(categories) != len(command.category_ids):
                    raise ValueError("One or more categories not found")
                if len(categories) == 0:
                    raise ValueError("Product must have at least one category")
                product.categories = categories
            
            session.commit()
            return product


class ArchiveProductHandler(CommandHandler):
    def handle(self, command: ArchiveProductCommand) -> Product:
        with get_session() as session:
            product = session.get(Product, command.id)
            if not product:
                raise ValueError("Product not found")
            
            # Use domain method for business logic
            product.archive()
            session.commit()
            return product


class DeleteProductHandler(CommandHandler):
    def handle(self, command: DeleteProductCommand):
        with get_session() as session:
            product = session.get(Product, command.id)
            if not product:
                raise ValueError("Product not found")
            
            # Check if product can be deleted using domain method
            if not product.can_delete():
                raise ValueError("Product cannot be deleted because it is referenced in quotes or orders")
            
            session.delete(product)
            session.commit()


class ActivateProductHandler(CommandHandler):
    def handle(self, command: ActivateProductCommand) -> Product:
        with get_session() as session:
            product = session.get(Product, command.id)
            if not product:
                raise ValueError("Product not found")
            
            # Use domain method for business logic
            product.activate()
            session.commit()
            return product


class DeactivateProductHandler(CommandHandler):
    def handle(self, command: DeactivateProductCommand) -> Product:
        with get_session() as session:
            product = session.get(Product, command.id)
            if not product:
                raise ValueError("Product not found")
            
            # Set status to inactive
            product.status = 'inactive'
            session.commit()
            return product


# Category Handlers
class CreateCategoryHandler(CommandHandler):
    def handle(self, command: CreateCategoryCommand) -> Category:
        with get_session() as session:
            # Validate parent exists if provided
            if command.parent_id:
                parent = session.query(Category).get(command.parent_id)
                if not parent:
                    raise ValueError("Parent category not found")
            
            # Create category using domain factory method
            category = Category.create(
                name=command.name,
                code=command.code,
                parent_id=command.parent_id,
                description=command.description
            )
            
            session.add(category)
            session.commit()
            return category


class UpdateCategoryHandler(CommandHandler):
    def handle(self, command: UpdateCategoryCommand) -> Category:
        with get_session() as session:
            category = session.get(Category, command.id)
            if not category:
                raise ValueError("Category not found")
            
            # Update category details using domain method
            category.update_details(
                name=command.name,
                code=command.code,
                description=command.description
            )
            
            session.commit()
            return category


class DeleteCategoryHandler(CommandHandler):
    def handle(self, command: DeleteCategoryCommand):
        with get_session() as session:
            category = session.get(Category, command.id)
            if not category:
                raise ValueError("Category not found")
            
            # Check if category can be deleted using domain method
            if not category.can_delete():
                raise ValueError("Category cannot be deleted because it has products assigned or has children")
            
            session.delete(category)
            session.commit()