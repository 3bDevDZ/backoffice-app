"""BDD step definitions for product management."""
from behave import given, when, then
from decimal import Decimal
from app.application.products.commands.commands import (
    CreateProductCommand,
    UpdateProductCommand,
    ArchiveProductCommand,
    DeleteProductCommand
)
from app.application.products.commands.handlers import (
    CreateProductHandler,
    UpdateProductHandler,
    ArchiveProductHandler,
    DeleteProductHandler
)
from app.domain.models.product import Product
from app.domain.models.category import Category
# Use context.db_session instead of get_session()


@given('the system has a category "{category_name}" with code "{category_code}"')
def step_impl(context, category_name, category_code):
    """Create a category in the system."""
    session = context.db_session
    category = Category.create(
        name=category_name,
        code=category_code
    )
    session.add(category)
    session.commit()
    session.refresh(category)
    context.category_id = category.id


@given('I am logged in as a commercial user')
def step_impl(context):
    """Set up user context (simplified for BDD tests)."""
    context.user_role = "commercial"
    # In real implementation, you would set up authentication context


@given('a product "{product_code}" exists with name "{name}" and price "{price}"')
def step_impl(context, product_code, name, price):
    """Create a product in the system."""
    session = context.db_session
    category = session.query(Category).first()
    if not category:
        category = Category.create(name="Default Category", code="DEFAULT")
        session.add(category)
        session.commit()
        session.refresh(category)
    
    product = Product.create(
        code=product_code,
        name=name,
        price=Decimal(price),
        category_ids=[category.id]
    )
    product.categories = [category]
    session.add(product)
    session.flush()
    
    # Update domain event with product ID
    events = product.get_domain_events()
    for event in events:
        if hasattr(event, 'product_id') and event.product_id == 0:
            event.product_id = product.id
    
    session.commit()
    session.refresh(product)
    context.product_id = product.id
    context.product_code = product_code


@given('a product "{product_code}" exists with status "{status}"')
def step_impl(context, product_code, status):
    """Create a product with specific status."""
    session = context.db_session
    # Use context session
    with session.begin():
        category = session.query(Category).first()
        if not category:
            category = Category.create(name="Default Category", code="DEFAULT")
            session.add(category)
            session.commit()
            session.refresh(category)
        
        product = Product.create(
            code=product_code,
            name="Test Product",
            price=Decimal("100.00"),
            category_ids=[category.id]
        )
        product.categories = [category]
        product.status = status
        session.add(product)
        session.flush()
        
        events = product.get_domain_events()
        for event in events:
            if hasattr(event, 'product_id') and event.product_id == 0:
                event.product_id = product.id
        
        session.commit()
        session.refresh(product)
        context.product_id = product.id
        context.product_code = product_code


@given('a product "{product_code}" exists')
def step_impl(context, product_code):
    """Create a product in the system."""
    session = context.db_session
    # Use context session
    with session.begin():
        category = session.query(Category).first()
        if not category:
            category = Category.create(name="Default Category", code="DEFAULT")
            session.add(category)
            session.commit()
            session.refresh(category)
        
        product = Product.create(
            code=product_code,
            name="Test Product",
            price=Decimal("100.00"),
            category_ids=[category.id]
        )
        product.categories = [category]
        session.add(product)
        session.flush()
        
        events = product.get_domain_events()
        for event in events:
            if hasattr(event, 'product_id') and event.product_id == 0:
                event.product_id = product.id
        
        session.commit()
        session.refresh(product)
        context.product_id = product.id
        context.product_code = product_code


@when('I create a product with:')
def step_impl(context):
    """Create a product using the provided data."""
    row = context.table[0]
    handler = CreateProductHandler()
    
    category_ids = eval(row['category_ids']) if row.get('category_ids') else []
    
    command = CreateProductCommand(
        code=row['code'],
        name=row['name'],
        price=Decimal(row['price']),
        category_ids=category_ids
    )
    
    try:
        context.product = handler.handle(command)
        context.last_error = None
    except Exception as e:
        context.last_error = str(e)
        context.product = None


@when('I update product "{product_code}" with:')
def step_impl(context, product_code):
    """Update a product using the provided data."""
    row = context.table[0]
    handler = UpdateProductHandler()
    
    session = context.db_session
    product = session.query(Product).filter(Product.code == product_code).first()
    if not product:
        context.last_error = "Product not found"
        return
    
    command = UpdateProductCommand(
        id=product.id,
        name=row.get('name'),
        price=Decimal(row['price']) if row.get('price') else None
    )
    
    try:
        context.product = handler.handle(command)
        context.last_error = None
    except Exception as e:
        context.last_error = str(e)
        context.product = None


@when('I archive product "{product_code}"')
def step_impl(context, product_code):
    """Archive a product."""
    handler = ArchiveProductHandler()
    
    session = context.db_session
    product = session.query(Product).filter(Product.code == product_code).first()
    if not product:
        context.last_error = "Product not found"
        return
    
    command = ArchiveProductCommand(id=product.id)
    
    try:
        context.product = handler.handle(command)
        context.last_error = None
    except Exception as e:
        context.last_error = str(e)
        context.product = None


@when('I delete product "{product_code}"')
def step_impl(context, product_code):
    """Delete a product."""
    handler = DeleteProductHandler()
    
    session = context.db_session
    product = session.query(Product).filter(Product.code == product_code).first()
    if not product:
        context.last_error = "Product not found"
        return
    
    command = DeleteProductCommand(id=product.id)
    
    try:
        handler.handle(command)
        context.last_error = None
    except Exception as e:
        context.last_error = str(e)


@then('the product should be created successfully')
def step_impl(context):
    """Verify product was created successfully."""
    assert context.product is not None, f"Product creation failed: {context.last_error}"
    assert context.product.id is not None


@then('the product should have status "{status}"')
def step_impl(context, status):
    """Verify product status."""
    assert context.product.status == status


@then('a domain event "{event_type}" should be raised')
def step_impl(context, event_type):
    """Verify domain event was raised."""
    events = context.product.get_domain_events()
    event_types = [type(e).__name__ for e in events]
    assert event_type in event_types, f"Expected {event_type}, got {event_types}"


@then('an integration event should be saved to outbox')
def step_impl(context):
    """Verify integration event was saved to outbox."""
    # This would check the outbox table in a real implementation
    # For now, we verify the domain event handler was called
    # In a full implementation, you would query the OutboxEvent table
    pass  # Placeholder - would query outbox_events table


@then('the creation should fail with error "{error_message}"')
def step_impl(context, error_message):
    """Verify creation failed with specific error."""
    assert context.last_error is not None, "Expected error but creation succeeded"
    assert error_message in context.last_error, f"Expected '{error_message}' in '{context.last_error}'"


@then('the product should be updated successfully')
def step_impl(context):
    """Verify product was updated successfully."""
    assert context.product is not None, f"Product update failed: {context.last_error}"


@then('the product name should be "{name}"')
def step_impl(context, name):
    """Verify product name."""
    assert context.product.name == name


@then('the product price should be "{price}"')
def step_impl(context, price):
    """Verify product price."""
    assert context.product.price == Decimal(price)


@then('the product status should be "{status}"')
def step_impl(context, status):
    """Verify product status."""
    assert context.product.status == status


@then('the product should be deleted from the system')
def step_impl(context):
    """Verify product was deleted."""
    assert context.last_error is None, f"Product deletion failed: {context.last_error}"
    
    session = context.db_session
    session.expire_all()
    product = session.query(Product).filter(Product.code == context.product_code).first()
    assert product is None, "Product still exists after deletion"

