"""BDD step definitions for stock alimentation."""
from behave import given, when, then
from decimal import Decimal
from app.application.common.mediator import mediator
from app.application.common.domain_event_dispatcher import domain_event_dispatcher
from app.application.purchases.commands.commands import (
    CreateSupplierCommand,
    CreatePurchaseOrderCommand,
    AddPurchaseOrderLineCommand,
    ReceivePurchaseOrderLineCommand
)
from app.domain.models.supplier import Supplier
from app.domain.models.product import Product
from app.domain.models.category import Category
from app.domain.models.user import User
from app.domain.models.purchase import PurchaseOrder, PurchaseOrderLine
from app.domain.models.stock import Location, StockItem, StockMovement
from datetime import date


def ensure_db_session(context):
    """Ensure db_session is initialized."""
    # db_session should already be initialized in before_scenario
    # Just verify it exists
    if not hasattr(context, 'db_session'):
        raise RuntimeError("db_session not initialized. This should be set in before_scenario.")


@given('the system has a warehouse location "{location_name}" with code "{location_code}"')
def step_impl(context, location_name, location_code):
    """Create a warehouse location in the system."""
    ensure_db_session(context)
    session = context.db_session
    location = Location.create(
        code=location_code,
        name=location_name,
        type='warehouse',
        is_active=True
    )
    session.add(location)
    session.commit()
    session.refresh(location)
    context.location_id = location.id
    context.location_code = location_code


@given('the system has a supplier "{supplier_name}" with email "{email}"')
def step_impl(context, supplier_name, email):
    """Create a supplier in the system."""
    ensure_db_session(context)
    session = context.db_session
    supplier = Supplier.create(
        name=supplier_name,
        email=email,
        code=f"SUP-{supplier_name[:3].upper()}"
    )
    session.add(supplier)
    session.commit()
    session.refresh(supplier)
    context.supplier_id = supplier.id
    context.supplier_name = supplier_name


@given('the system has a product "{product_code}" with name "{name}" and price "{price}"')
def step_impl(context, product_code, name, price):
    """Create a product in the system."""
    ensure_db_session(context)
    session = context.db_session
    # Ensure category exists
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
    
    # Store product IDs by code
    if not hasattr(context, 'product_ids'):
        context.product_ids = {}
    context.product_ids[product_code] = product.id


@given('the system has a user "{username}" with role "{role}"')
def step_impl(context, username, role):
    """Create a user in the system."""
    ensure_db_session(context)
    session = context.db_session
    user = User(username=username, role=role)
    user.set_password("testpass")
    session.add(user)
    session.commit()
    session.refresh(user)
    context.user_id = user.id


@given('a purchase order "{order_number}" exists for supplier "{supplier_name}" with status "{status}"')
def step_impl(context, order_number, supplier_name, status):
    """Create a purchase order in the system."""
    ensure_db_session(context)
    session = context.db_session
    
    # Get supplier ID
    supplier = session.query(Supplier).filter(Supplier.name == supplier_name).first()
    if not supplier:
        raise ValueError(f"Supplier '{supplier_name}' not found")
    
    # Get user ID
    user_id = getattr(context, 'user_id', 1)
    
    # Create purchase order directly in session (simpler for tests)
    # Always create in 'draft' status first - confirmation will happen after lines are added
    # Create directly without using PurchaseOrder.create() to avoid domain events that might interfere
    from datetime import datetime
    order = PurchaseOrder(
        number=order_number,
        supplier_id=supplier.id,
        created_by=user_id,
        order_date=date.today(),
        expected_delivery_date=date.today(),
        status='draft'  # Explicitly set to draft
    )
    session.add(order)
    session.flush()  # Get ID
    session.commit()
    
    # Store order IDs by number
    if not hasattr(context, 'purchase_order_ids'):
        context.purchase_order_ids = {}
    context.purchase_order_ids[order_number] = order.id
    
    # Store desired status for later confirmation
    if not hasattr(context, 'purchase_order_desired_status'):
        context.purchase_order_desired_status = {}
    context.purchase_order_desired_status[order_number] = status
    
    context.purchase_order_id = order.id
    context.purchase_order_number = order_number


@given('the purchase order "{order_number}" has a line with product "{product_code}" and quantity "{quantity}"')
def step_impl(context, order_number, product_code, quantity):
    """Add a line to the purchase order."""
    ensure_db_session(context)
    order_id = context.purchase_order_ids.get(order_number)
    if not order_id:
        raise ValueError(f"Purchase order '{order_number}' not found in context")
    
    product_id = context.product_ids.get(product_code)
    if not product_id:
        raise ValueError(f"Product '{product_code}' not found in context")
    
    # Check order status before adding line (must be draft)
    # Refresh session to ensure we see the latest state from database
    import app.infrastructure.db as db_module
    context.db_session.close()
    context.db_session = db_module.SessionLocal()
    session = context.db_session
    
    order_before = session.get(PurchaseOrder, order_id)
    if not order_before:
        raise ValueError(f"Purchase order '{order_number}' (ID: {order_id}) not found in database")
    
    # Force status to 'draft' if it's not already (in case something modified it)
    if order_before.status != 'draft':
        order_before.status = 'draft'
        session.commit()
        session.refresh(order_before)
    
    command = AddPurchaseOrderLineCommand(
        purchase_order_id=order_id,
        product_id=product_id,
        quantity=Decimal(quantity),
        unit_price=Decimal("50.00"),
        discount_percent=Decimal("0"),
        tax_rate=Decimal("20.0")
    )
    mediator.dispatch(command)
    
    # The handler uses a different session, so we need to refresh our session
    # to see the changes committed by the handler
    # Close and recreate the session to ensure we see the latest data
    context.db_session.close()
    context.db_session = db_module.SessionLocal()
    session = context.db_session
    
    # Query the line directly from the database
    line = session.query(PurchaseOrderLine).filter(
        PurchaseOrderLine.purchase_order_id == order_id,
        PurchaseOrderLine.product_id == product_id
    ).order_by(PurchaseOrderLine.id.desc()).first()
    
    if not line:
        # Debug: check all lines for this order
        all_lines = session.query(PurchaseOrderLine).filter(
            PurchaseOrderLine.purchase_order_id == order_id
        ).all()
        debug_info = f"Order {order_number} (ID: {order_id}) has {len(all_lines)} lines. "
        debug_info += f"Looking for product_id={product_id}. "
        if all_lines:
            debug_info += f"Found lines with product_ids: {[l.product_id for l in all_lines]}"
        raise ValueError(f"Line not found for product '{product_code}' in purchase order '{order_number}'. {debug_info}")
    
    # Store line IDs
    if not hasattr(context, 'purchase_order_lines'):
        context.purchase_order_lines = {}
    context.purchase_order_lines[f"{order_number}-{product_code}"] = line.id
    
    # If the order should be confirmed, confirm it now (after line is added)
    desired_status = getattr(context, 'purchase_order_desired_status', {}).get(order_number, 'draft')
    if desired_status == 'confirmed':
        # Retrieve the order from the new session with lines loaded
        from sqlalchemy.orm import joinedload
        order = session.query(PurchaseOrder).options(
            joinedload(PurchaseOrder.lines)
        ).filter(PurchaseOrder.id == order_id).first()
        if order and order.status == 'draft' and order.lines:
            user_id = getattr(context, 'user_id', 1)
            order.confirm(user_id)
            session.commit()
            session.refresh(order)


@given('no stock item exists for product "{product_code}" at location "{location_code}"')
def step_impl(context, product_code, location_code):
    """Verify no stock item exists."""
    session = context.db_session
    product_id = context.product_ids.get(product_code)
    location_id = context.location_id
    
    stock_item = session.query(StockItem).filter(
        StockItem.product_id == product_id,
        StockItem.location_id == location_id
    ).first()
    
    if stock_item:
        # Remove it for test
        session.delete(stock_item)
        session.commit()


@given('a stock item exists for product "{product_code}" at location "{location_code}" with physical_quantity "{quantity}"')
def step_impl(context, product_code, location_code, quantity):
    """Create a stock item with specific quantity."""
    session = context.db_session
    product_id = context.product_ids.get(product_code)
    location_id = context.location_id
    
    stock_item = StockItem.create(
        product_id=product_id,
        location_id=location_id,
        physical_quantity=Decimal(quantity)
    )
    session.add(stock_item)
    session.commit()
    session.refresh(stock_item)
    
    if not hasattr(context, 'stock_item_ids'):
        context.stock_item_ids = {}
    context.stock_item_ids[f"{product_code}-{location_code}"] = stock_item.id


@when('I mark the purchase order line as received with quantity "{quantity}"')
def step_impl(context, quantity):
    """Mark a purchase order line as received."""
    ensure_db_session(context)
    order_id = context.purchase_order_id
    session = context.db_session
    
    # Get the order with lines
    from sqlalchemy.orm import joinedload
    order = session.query(PurchaseOrder).options(
        joinedload(PurchaseOrder.lines)
    ).filter(PurchaseOrder.id == order_id).first()
    
    if not order or not order.lines:
        raise ValueError("Purchase order or line not found")
    
    # Find the line: use the one stored in context if available, otherwise use the last line (highest ID)
    # which should be the one we just added
    line = None
    if hasattr(context, 'purchase_order_lines') and context.purchase_order_lines:
        # Get the most recent line ID from context
        line_ids = list(context.purchase_order_lines.values())
        if line_ids:
            latest_line_id = max(line_ids)
            line = next((l for l in order.lines if l.id == latest_line_id), None)
    
    # If not found, use the line with the highest ID (most recently created)
    if not line:
        line = max(order.lines, key=lambda l: l.id)
    
    command = ReceivePurchaseOrderLineCommand(
        purchase_order_id=order_id,
        line_id=line.id,
        quantity_received=Decimal(quantity)
    )
    
    try:
        context.received_line = mediator.dispatch(command)
        context.last_error = None
        
        # Refresh the session to see changes made by the handler
        import app.infrastructure.db as db_module
        context.db_session.close()
        context.db_session = db_module.SessionLocal()
    except Exception as e:
        context.last_error = str(e)
        context.received_line = None


@when('I mark all purchase order lines as received')
def step_impl(context):
    """Mark all purchase order lines as received."""
    ensure_db_session(context)
    order_id = context.purchase_order_id
    session = context.db_session
    
    order = session.get(PurchaseOrder, order_id)
    if not order:
        raise ValueError("Purchase order not found")
    
    for line in order.lines:
        command = ReceivePurchaseOrderLineCommand(
            purchase_order_id=order_id,
            line_id=line.id,
            quantity_received=line.quantity  # Receive full quantity
        )
        mediator.dispatch(command)
    
    # Refresh the session to see changes made by the handlers
    import app.infrastructure.db as db_module
    context.db_session.close()
    context.db_session = db_module.SessionLocal()


@then('the purchase order status should be "{status}"')
def step_impl(context, status):
    """Verify purchase order status."""
    # Refresh session to ensure we see latest changes
    import app.infrastructure.db as db_module
    context.db_session.close()
    context.db_session = db_module.SessionLocal()
    session = context.db_session
    
    order = session.get(PurchaseOrder, context.purchase_order_id)
    assert order is not None, "Purchase order not found"
    assert order.status == status, f"Expected status '{status}', got '{order.status}'"


@then('a stock item should exist for product "{product_code}" at location "{location_code}"')
def step_impl(context, product_code, location_code):
    """Verify stock item exists."""
    session = context.db_session
    product_id = context.product_ids.get(product_code)
    location_id = context.location_id
    
    stock_item = session.query(StockItem).filter(
        StockItem.product_id == product_id,
        StockItem.location_id == location_id
    ).first()
    
    assert stock_item is not None, f"Stock item not found for product {product_code} at location {location_code}"


@then('the stock item should have physical_quantity "{quantity}"')
def step_impl(context, quantity):
    """Verify stock item physical quantity."""
    session = context.db_session
    order_id = context.purchase_order_id
    order = session.get(PurchaseOrder, order_id)
    
    # Get the first line's product
    product_id = order.lines[0].product_id
    location_id = context.location_id
    
    stock_item = session.query(StockItem).filter(
        StockItem.product_id == product_id,
        StockItem.location_id == location_id
    ).first()
    
    assert stock_item is not None, "Stock item not found"
    assert stock_item.physical_quantity == Decimal(quantity), \
        f"Expected physical_quantity {quantity}, got {stock_item.physical_quantity}"


@then('a stock movement of type "{movement_type}" should exist for product "{product_code}" with quantity "{quantity}"')
def step_impl(context, movement_type, product_code, quantity):
    """Verify stock movement exists."""
    session = context.db_session
    product_id = context.product_ids.get(product_code)
    
    movement = session.query(StockMovement).filter(
        StockMovement.product_id == product_id,
        StockMovement.type == movement_type,
        StockMovement.quantity == Decimal(quantity)
    ).first()
    
    assert movement is not None, \
        f"Stock movement not found: type={movement_type}, product={product_code}, quantity={quantity}"


@then('the stock movement should be linked to purchase order "{order_number}"')
def step_impl(context, order_number):
    """Verify stock movement is linked to purchase order."""
    session = context.db_session
    order_id = context.purchase_order_ids.get(order_number)
    
    movement = session.query(StockMovement).filter(
        StockMovement.related_document_type == 'purchase_order',
        StockMovement.related_document_id == order_id
    ).first()
    
    assert movement is not None, f"Stock movement not linked to purchase order {order_number}"
    assert movement.related_document_id == order_id


@then('no stock movement should be created yet')
def step_impl(context):
    """Verify no stock movement exists."""
    session = context.db_session
    movements = session.query(StockMovement).all()
    assert len(movements) == 0, f"Expected no stock movements, but found {len(movements)}"


@then('a stock movement should exist for product "{product_code}" with quantity "{quantity}"')
def step_impl(context, product_code, quantity):
    """Verify stock movement exists for product."""
    session = context.db_session
    product_id = context.product_ids.get(product_code)
    
    movement = session.query(StockMovement).filter(
        StockMovement.product_id == product_id,
        StockMovement.quantity == Decimal(quantity)
    ).first()
    
    assert movement is not None, \
        f"Stock movement not found for product {product_code} with quantity {quantity}"


@then('the stock item for product "{product_code}" should have physical_quantity "{quantity}"')
def step_impl(context, product_code, quantity):
    """Verify stock item quantity for specific product."""
    session = context.db_session
    product_id = context.product_ids.get(product_code)
    location_id = context.location_id
    
    stock_item = session.query(StockItem).filter(
        StockItem.product_id == product_id,
        StockItem.location_id == location_id
    ).first()
    
    assert stock_item is not None, f"Stock item not found for product {product_code}"
    assert stock_item.physical_quantity == Decimal(quantity), \
        f"Expected physical_quantity {quantity}, got {stock_item.physical_quantity}"


@then('a stock item should be created for product "{product_code}" at location "{location_code}"')
def step_impl(context, product_code, location_code):
    """Verify stock item was created."""
    session = context.db_session
    product_id = context.product_ids.get(product_code)
    location_id = context.location_id
    
    stock_item = session.query(StockItem).filter(
        StockItem.product_id == product_id,
        StockItem.location_id == location_id
    ).first()
    
    assert stock_item is not None, \
        f"Stock item was not created for product {product_code} at location {location_code}"

