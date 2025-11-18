"""Script to create all database tables."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.infrastructure.db import Base, engine
from app.infrastructure.migrate import create_all

# Import all models to ensure they are registered with Base
from app.domain.models.user import User
from app.domain.models.product import Product, ProductVariant, ProductPriceHistory, ProductCostHistory, PriceList, ProductPriceList, ProductVolumePricing, ProductPromotionalPrice
from app.domain.models.category import Category
from app.domain.models.customer import Customer, Address, Contact, CommercialConditions
from app.domain.models.supplier import Supplier, SupplierAddress, SupplierContact, SupplierConditions
from app.domain.models.purchase import PurchaseOrder, PurchaseOrderLine, PurchaseRequest, PurchaseRequestLine, PurchaseReceipt, PurchaseReceiptLine, SupplierInvoice
from app.domain.models.stock import StockItem, StockMovement, Location
from app.domain.models.quote import Quote, QuoteLine, QuoteVersion
from app.domain.models.order import Order, OrderLine, StockReservation
from app.domain.models.invoice import Invoice, InvoiceLine, CreditNote
from app.domain.models.payment import Payment, PaymentAllocation, PaymentReminder
from app.infrastructure.outbox.outbox_event import OutboxEvent


def main():
    """Create all database tables."""
    print("Creating Flask app...")
    app = create_app()
    
    print("Creating all database tables...")
    with app.app_context():
        # Import engine after app is created (it's initialized in create_app)
        from app.infrastructure.db import engine
        if engine is None:
            raise RuntimeError("Database engine not initialized. Check database configuration.")
        
        Base.metadata.create_all(bind=engine)
    
    print("OK: All tables created successfully!")
    print("\nTables created:")
    for table_name in sorted(Base.metadata.tables.keys()):
        print(f"  - {table_name}")


if __name__ == "__main__":
    main()

