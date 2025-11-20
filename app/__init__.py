from flask import Flask, request, g
from flask_babel import Babel, gettext as _
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables from .env file
load_dotenv()

def create_app() -> Flask:
    app = Flask(__name__)

    from .config import Config

    app.config.from_object(Config)
    
    # Configure logging
    if not app.debug:
        # In production, log to file
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/gmflow.log', maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('GMFlow startup')
    
    # Always log to console as well
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s'
    ))
    console_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG)
    
    # Configure session
    from datetime import timedelta
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    
    # Initialize JWT early (before blueprints) - for API endpoints only
    from .security.auth import init_jwt
    init_jwt(app)
    
    # Configure Flask-Babel
    app.config['BABEL_DEFAULT_LOCALE'] = 'fr'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'fr', 'ar']
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    
    # Initialize Babel
    babel = Babel()
    babel.init_app(app)
    
    def get_locale():
        from flask import session
        # 1. Check URL parameter (highest priority - save to session if present)
        locale = request.args.get('locale')
        if locale in ['en', 'fr', 'ar']:
            # Save to session for persistence
            session['locale'] = locale
            session.permanent = True
            # Force session to be saved
            session.modified = True
            return locale
        # 2. Check user preference from session (if logged in)
        if 'locale' in session:
            saved_locale = session['locale']
            if saved_locale in ['en', 'fr', 'ar']:
                return saved_locale
        # 3. Check user object in g (if available and expunged)
        if hasattr(g, 'user') and g.user:
            # User object is expunged, so we can safely access locale
            try:
                user_locale = getattr(g.user, 'locale', None)
                if user_locale in ['en', 'fr', 'ar']:
                    # Save to session for consistency
                    session['locale'] = user_locale
                    session.permanent = True
                    session.modified = True
                    return user_locale
            except:
                pass
        # 4. Check application default language from settings
        try:
            from app.utils.settings_helper import get_default_language
            default_lang = get_default_language()
            if default_lang in ['en', 'fr', 'ar']:
                # Save to session for consistency
                session['locale'] = default_lang
                session.permanent = True
                session.modified = True
                return default_lang
        except Exception:
            # If settings not available, continue to next fallback
            pass
        # 5. Check Accept-Language header
        browser_locale = request.accept_languages.best_match(['en', 'fr', 'ar'], 'fr')
        # Save to session for consistency
        session['locale'] = browser_locale
        session.permanent = True
        session.modified = True
        return browser_locale
    
    # Set locale selector for Flask-Babel 4.0
    app.config['BABEL_LOCALE_SELECTOR'] = get_locale
    
    # Ensure locale is set in session before each request
    @app.before_request
    def ensure_locale_in_session():
        """Ensure locale is set in session before processing request."""
        from flask import session
        # This will call get_locale() which saves to session if needed
        get_locale()
        # Force session to be saved
        if session.modified:
            session.permanent = True
    
    @app.context_processor
    def inject_locale():
        """Inject locale and stock management mode into all templates."""
        from app.utils.settings_helper import get_stock_management_mode
        from datetime import date, datetime
        locale = get_locale()
        
        # Determine current module based on endpoint
        current_module = None
        if hasattr(request, 'endpoint') and request.endpoint:
            endpoint = request.endpoint
            # Check purchases FIRST (before sales) to avoid conflicts with 'orders'
            if 'purchases_frontend' in endpoint or 'purchase_orders' in endpoint or 'purchase_requests' in endpoint or 'purchase_receipts' in endpoint or 'supplier_invoices' in endpoint or 'suppliers' in endpoint:
                current_module = 'purchases'
            elif 'customers' in endpoint or 'sales' in endpoint or 'quotes' in endpoint or ('orders' in endpoint and 'purchase' not in endpoint) or 'promotions' in endpoint or 'billing' in endpoint or 'invoices' in endpoint or ('payments' in endpoint and 'supplier' not in endpoint):
                current_module = 'sales'
            elif 'stock' in endpoint or 'inventory' in endpoint:
                current_module = 'inventory'
            elif 'products' in endpoint or 'price' in endpoint:
                current_module = 'catalog'
            elif 'dashboard' in endpoint:
                current_module = 'dashboard'
        
        # Get stock management mode
        try:
            stock_management_mode = get_stock_management_mode()
        except Exception:
            stock_management_mode = 'simple'  # Default to simple if error
        
        # Get default currency
        try:
            from app.utils.settings_helper import get_default_currency
            default_currency = get_default_currency()
        except Exception:
            default_currency = 'EUR'  # Default to EUR if error
        
        return {
            'locale': locale,
            'direction': 'rtl' if locale == 'ar' else 'ltr',
            '_': _,
            'date': date,
            'datetime': datetime,
            'current_module': current_module,
            'stock_management_mode': stock_management_mode,
            'default_currency': default_currency
        }
    
    # Register custom Jinja2 filters
    @app.template_filter('nl2br')
    def nl2br_filter(value):
        """Convert newlines to <br> tags."""
        if value is None:
            return ''
        return value.replace('\n', '<br>')
    
    @app.template_filter('currency')
    def currency_filter(value, currency=None, locale_code=None):
        """
        Format a number as currency according to locale and currency settings.
        
        Args:
            value: Numeric value to format
            currency: Currency code (defaults to app default currency)
            locale_code: Locale code (defaults to current locale)
        
        Returns:
            Formatted currency string
        """
        if value is None:
            return ''
        
        try:
            from decimal import Decimal
            # Convert to float for formatting
            if isinstance(value, Decimal):
                num_value = float(value)
            else:
                num_value = float(value)
        except (ValueError, TypeError):
            return str(value)
        
        # Get currency from parameter or default
        if currency is None:
            try:
                from app.utils.settings_helper import get_default_currency
                currency = get_default_currency()
            except Exception:
                currency = 'EUR'
        
        # Get locale from parameter or current locale
        if locale_code is None:
            locale_code = get_locale()
        
        # Map locale codes to proper Intl locale format
        locale_map = {
            'en': 'en-US',
            'fr': 'fr-FR',
            'ar': 'ar-DZ'  # Arabic locale for Algeria (can be adjusted)
        }
        intl_locale = locale_map.get(locale_code, locale_code)
        
        try:
            import babel.numbers
            return babel.numbers.format_currency(
                num_value,
                currency,
                locale=intl_locale.replace('-', '_')
            )
        except Exception:
            # Fallback to basic formatting if babel is not available
            try:
                # Use Python's locale module as fallback
                import locale as py_locale
                # Map locale codes
                py_locale_map = {
                    'en': 'en_US.UTF-8',
                    'fr': 'fr_FR.UTF-8',
                    'ar': 'ar_DZ.UTF-8'
                }
                py_locale.setlocale(py_locale.LC_ALL, py_locale_map.get(locale_code, 'en_US.UTF-8'))
                return py_locale.currency(num_value, grouping=True, symbol=True)
            except Exception:
                # Final fallback: simple format
                currency_symbols = {
                    'EUR': '€',
                    'USD': '$',
                    'GBP': '£',
                    'MAD': 'د.م.',
                    'DZD': 'د.ج',
                    'TND': 'د.ت'
                }
                symbol = currency_symbols.get(currency, currency)
                return f"{num_value:,.2f} {symbol}"
    
    @app.template_filter('from_json')
    def from_json_filter(value):
        """Parse JSON string to Python dict."""
        if not value:
            return {}
        try:
            import json
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    @app.template_filter('to_float')
    def to_float_filter(value):
        """Convert Decimal or numeric value to float."""
        if value is None:
            return 0.0
        try:
            from decimal import Decimal
            if isinstance(value, Decimal):
                return float(value)
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    # Initialize DB
    from .infrastructure.db import init_db

    init_db(app.config["SQLALCHEMY_DATABASE_URI"])
    
    # Import all domain models to ensure SQLAlchemy can resolve relationships
    # This must be done after DB initialization but before any queries
    from .domain.models.payment import Payment, PaymentAllocation, PaymentReminder  # noqa: F401

    # Register CQRS handlers
    from .application.common.mediator import mediator
    
    # Product Commands
    from .application.products.commands.commands import (
        CreateProductCommand, UpdateProductCommand, ArchiveProductCommand, DeleteProductCommand,
        ActivateProductCommand, DeactivateProductCommand
    )
    from .application.products.commands.handlers import (
        CreateProductHandler, UpdateProductHandler, ArchiveProductHandler, DeleteProductHandler,
        ActivateProductHandler, DeactivateProductHandler
    )
    
    # Product Queries
    from .application.products.queries.queries import (
        GetProductByIdQuery, ListProductsQuery, SearchProductsQuery, GetPriceHistoryQuery, GetCostHistoryQuery
    )
    from .application.products.queries.handlers import (
        GetProductByIdHandler, ListProductsHandler, SearchProductsHandler, GetPriceHistoryHandler, GetCostHistoryHandler
    )
    
    # Category Commands
    from .application.products.commands.commands import (
        CreateCategoryCommand, UpdateCategoryCommand, DeleteCategoryCommand
    )
    from .application.products.commands.handlers import (
        CreateCategoryHandler, UpdateCategoryHandler, DeleteCategoryHandler
    )
    
    # Category Queries
    from .application.products.queries.queries import (
        GetCategoryByIdQuery, ListCategoriesQuery
    )
    from .application.products.queries.handlers import (
        GetCategoryByIdHandler, ListCategoriesHandler
    )
    
    # Customer Commands/Queries
    from .application.customers.commands.commands import (
        CreateCustomerCommand, UpdateCustomerCommand, ArchiveCustomerCommand,
        ActivateCustomerCommand, DeactivateCustomerCommand,
        CreateAddressCommand, UpdateAddressCommand, DeleteAddressCommand,
        CreateContactCommand, UpdateContactCommand, DeleteContactCommand
    )
    from .application.customers.commands.handlers import (
        CreateCustomerHandler, UpdateCustomerHandler, ArchiveCustomerHandler,
        ActivateCustomerHandler, DeactivateCustomerHandler,
        CreateAddressHandler, UpdateAddressHandler, DeleteAddressHandler,
        CreateContactHandler, UpdateContactHandler, DeleteContactHandler
    )
    from .application.customers.queries.queries import (
        GetCustomerByIdQuery, ListCustomersQuery, SearchCustomersQuery, GetCustomerHistoryQuery
    )
    from .application.customers.queries.handlers import (
        GetCustomerByIdHandler, ListCustomersHandler, SearchCustomersHandler, GetCustomerHistoryHandler
    )
    
    # User Commands (existing)
    from .application.users.commands.commands import LoginCommand
    from .application.users.commands.handlers import LoginCommandHandler

    # Register Product Commands
    mediator.register_command(CreateProductCommand, CreateProductHandler())
    mediator.register_command(UpdateProductCommand, UpdateProductHandler())
    mediator.register_command(ArchiveProductCommand, ArchiveProductHandler())
    mediator.register_command(DeleteProductCommand, DeleteProductHandler())
    mediator.register_command(ActivateProductCommand, ActivateProductHandler())
    mediator.register_command(DeactivateProductCommand, DeactivateProductHandler())
    
    # Register Product Queries
    mediator.register_query(GetProductByIdQuery, GetProductByIdHandler())
    mediator.register_query(ListProductsQuery, ListProductsHandler())
    mediator.register_query(SearchProductsQuery, SearchProductsHandler())
    mediator.register_query(GetPriceHistoryQuery, GetPriceHistoryHandler())
    mediator.register_query(GetCostHistoryQuery, GetCostHistoryHandler())
    
    # Register Category Commands
    mediator.register_command(CreateCategoryCommand, CreateCategoryHandler())
    mediator.register_command(UpdateCategoryCommand, UpdateCategoryHandler())
    mediator.register_command(DeleteCategoryCommand, DeleteCategoryHandler())
    
    # Register Category Queries
    mediator.register_query(GetCategoryByIdQuery, GetCategoryByIdHandler())
    mediator.register_query(ListCategoriesQuery, ListCategoriesHandler())
    
    # Product Variant Commands
    from .application.products.variants.commands.commands import (
        CreateVariantCommand, UpdateVariantCommand, ArchiveVariantCommand,
        ActivateVariantCommand, DeleteVariantCommand
    )
    from .application.products.variants.commands.handlers import (
        CreateVariantHandler, UpdateVariantHandler, ArchiveVariantHandler,
        ActivateVariantHandler, DeleteVariantHandler
    )
    
    # Product Variant Queries
    from .application.products.variants.queries.queries import (
        GetVariantByIdQuery, GetVariantsByProductQuery, ListVariantsQuery
    )
    from .application.products.variants.queries.handlers import (
        GetVariantByIdHandler, GetVariantsByProductHandler, ListVariantsHandler
    )
    
    mediator.register_command(CreateVariantCommand, CreateVariantHandler())
    mediator.register_command(UpdateVariantCommand, UpdateVariantHandler())
    mediator.register_command(ArchiveVariantCommand, ArchiveVariantHandler())
    mediator.register_command(ActivateVariantCommand, ActivateVariantHandler())
    mediator.register_command(DeleteVariantCommand, DeleteVariantHandler())
    
    mediator.register_query(GetVariantByIdQuery, GetVariantByIdHandler())
    mediator.register_query(GetVariantsByProductQuery, GetVariantsByProductHandler())
    mediator.register_query(ListVariantsQuery, ListVariantsHandler())
    
    # Price List Commands (updated to include Volume Pricing and Promotional Pricing commands)
    from .application.products.pricing.commands.commands import (
        CreatePriceListCommand, UpdatePriceListCommand, DeletePriceListCommand,
        AddProductToPriceListCommand, UpdateProductPriceInListCommand, RemoveProductFromPriceListCommand,
        CreateVolumePricingCommand, UpdateVolumePricingCommand, DeleteVolumePricingCommand,
        CreatePromotionalPriceCommand, UpdatePromotionalPriceCommand, DeletePromotionalPriceCommand
    )
    from .application.products.pricing.commands.handlers import (
        CreatePriceListHandler, UpdatePriceListHandler, DeletePriceListHandler,
        AddProductToPriceListHandler, UpdateProductPriceInListHandler, RemoveProductFromPriceListHandler,
        CreateVolumePricingHandler, UpdateVolumePricingHandler, DeleteVolumePricingHandler,
        CreatePromotionalPriceHandler, UpdatePromotionalPriceHandler, DeletePromotionalPriceHandler
    )
    
    # Price List Queries (updated to include Volume Pricing and Promotional Pricing queries)
    from .application.products.pricing.queries.queries import (
        ListPriceListsQuery, GetPriceListByIdQuery, GetProductsInPriceListQuery,
        GetVolumePricingQuery,
        GetActivePromotionalPricesQuery, GetPromotionalPricesByProductQuery
    )
    from .application.products.pricing.queries.handlers import (
        ListPriceListsHandler, GetPriceListByIdHandler, GetProductsInPriceListHandler,
        GetVolumePricingHandler,
        GetActivePromotionalPricesHandler, GetPromotionalPricesByProductHandler
    )
    
    mediator.register_command(CreatePriceListCommand, CreatePriceListHandler())
    mediator.register_command(UpdatePriceListCommand, UpdatePriceListHandler())
    mediator.register_command(DeletePriceListCommand, DeletePriceListHandler())
    mediator.register_command(AddProductToPriceListCommand, AddProductToPriceListHandler())
    mediator.register_command(UpdateProductPriceInListCommand, UpdateProductPriceInListHandler())
    mediator.register_command(RemoveProductFromPriceListCommand, RemoveProductFromPriceListHandler())
    
    mediator.register_command(CreateVolumePricingCommand, CreateVolumePricingHandler())
    mediator.register_command(UpdateVolumePricingCommand, UpdateVolumePricingHandler())
    mediator.register_command(DeleteVolumePricingCommand, DeleteVolumePricingHandler())
    
    mediator.register_query(ListPriceListsQuery, ListPriceListsHandler())
    mediator.register_query(GetPriceListByIdQuery, GetPriceListByIdHandler())
    mediator.register_query(GetProductsInPriceListQuery, GetProductsInPriceListHandler())
    mediator.register_query(GetVolumePricingQuery, GetVolumePricingHandler())
    
    # Promotional Pricing Commands and Queries
    mediator.register_command(CreatePromotionalPriceCommand, CreatePromotionalPriceHandler())
    mediator.register_command(UpdatePromotionalPriceCommand, UpdatePromotionalPriceHandler())
    mediator.register_command(DeletePromotionalPriceCommand, DeletePromotionalPriceHandler())
    
    mediator.register_query(GetActivePromotionalPricesQuery, GetActivePromotionalPricesHandler())
    mediator.register_query(GetPromotionalPricesByProductQuery, GetPromotionalPricesByProductHandler())
    
    # Register Domain Event Handlers
    from .application.common.domain_event_dispatcher import domain_event_dispatcher
    from .domain.models.product import (
        ProductCreatedDomainEvent, ProductUpdatedDomainEvent, ProductArchivedDomainEvent
    )
    from .domain.models.category import CategoryCreatedDomainEvent
    from .domain.models.purchase import (
        PurchaseOrderReceivedDomainEvent,
        PurchaseOrderLineReceivedDomainEvent,
        PurchaseReceiptValidatedDomainEvent
    )
    from .application.products.events.product_created_handler import ProductCreatedDomainEventHandler
    from .application.products.events.product_updated_handler import ProductUpdatedDomainEventHandler
    from .application.products.events.product_archived_handler import ProductArchivedDomainEventHandler
    from .application.purchases.events.purchase_order_received_handler import PurchaseOrderReceivedDomainEventHandler
    from .application.purchases.events.purchase_order_line_received_handler import PurchaseOrderLineReceivedDomainEventHandler
    from .application.purchases.receipts.events.purchase_receipt_validated_handler import PurchaseReceiptValidatedDomainEventHandler
    
    # Register product domain event handlers
    domain_event_dispatcher.register_handler(
        ProductCreatedDomainEvent,
        ProductCreatedDomainEventHandler().handle
    )
    domain_event_dispatcher.register_handler(
        ProductUpdatedDomainEvent,
        ProductUpdatedDomainEventHandler().handle
    )
    domain_event_dispatcher.register_handler(
        ProductArchivedDomainEvent,
        ProductArchivedDomainEventHandler().handle
    )
    
    # Register purchase domain event handlers
    domain_event_dispatcher.register_handler(
        PurchaseOrderLineReceivedDomainEvent,
        PurchaseOrderLineReceivedDomainEventHandler().handle
    )
    domain_event_dispatcher.register_handler(
        PurchaseOrderReceivedDomainEvent,
        PurchaseOrderReceivedDomainEventHandler().handle
    )
    domain_event_dispatcher.register_handler(
        PurchaseReceiptValidatedDomainEvent,
        PurchaseReceiptValidatedDomainEventHandler().handle
    )
    
    # Register order domain event handlers
    from .domain.models.order import (
        OrderConfirmedDomainEvent,
        OrderCanceledDomainEvent,
        OrderReadyDomainEvent,
        OrderShippedDomainEvent
    )
    from .application.sales.orders.events.order_confirmed_handler import OrderConfirmedDomainEventHandler
    from .application.sales.orders.events.order_canceled_handler import OrderCanceledDomainEventHandler
    from .application.sales.orders.events.order_ready_handler import OrderReadyDomainEventHandler
    from .application.sales.orders.events.order_shipped_handler import OrderShippedDomainEventHandler
    
    domain_event_dispatcher.register_handler(
        OrderConfirmedDomainEvent,
        OrderConfirmedDomainEventHandler().handle
    )
    domain_event_dispatcher.register_handler(
        OrderCanceledDomainEvent,
        OrderCanceledDomainEventHandler().handle
    )
    domain_event_dispatcher.register_handler(
        OrderReadyDomainEvent,
        OrderReadyDomainEventHandler().handle
    )
    domain_event_dispatcher.register_handler(
        OrderShippedDomainEvent,
        OrderShippedDomainEventHandler().handle
    )
    # TODO: Register handlers for CategoryCreatedDomainEvent, etc.

    # Register Customer Commands
    mediator.register_command(CreateCustomerCommand, CreateCustomerHandler())
    mediator.register_command(UpdateCustomerCommand, UpdateCustomerHandler())
    mediator.register_command(ArchiveCustomerCommand, ArchiveCustomerHandler())
    mediator.register_command(ActivateCustomerCommand, ActivateCustomerHandler())
    mediator.register_command(DeactivateCustomerCommand, DeactivateCustomerHandler())
    mediator.register_command(CreateAddressCommand, CreateAddressHandler())
    mediator.register_command(UpdateAddressCommand, UpdateAddressHandler())
    mediator.register_command(DeleteAddressCommand, DeleteAddressHandler())
    mediator.register_command(CreateContactCommand, CreateContactHandler())
    mediator.register_command(UpdateContactCommand, UpdateContactHandler())
    mediator.register_command(DeleteContactCommand, DeleteContactHandler())
    
    # Register Customer Queries
    mediator.register_query(GetCustomerByIdQuery, GetCustomerByIdHandler())
    mediator.register_query(ListCustomersQuery, ListCustomersHandler())
    mediator.register_query(SearchCustomersQuery, SearchCustomersHandler())
    mediator.register_query(GetCustomerHistoryQuery, GetCustomerHistoryHandler())
    
    # Purchase Commands/Queries
    from .application.purchases.commands.commands import (
        CreateSupplierCommand, UpdateSupplierCommand, ArchiveSupplierCommand,
        ActivateSupplierCommand, DeactivateSupplierCommand,
        CreateSupplierAddressCommand, UpdateSupplierAddressCommand, DeleteSupplierAddressCommand,
        CreateSupplierContactCommand, UpdateSupplierContactCommand, DeleteSupplierContactCommand,
        CreatePurchaseOrderCommand, UpdatePurchaseOrderCommand, ConfirmPurchaseOrderCommand,
        CancelPurchaseOrderCommand, AddPurchaseOrderLineCommand, UpdatePurchaseOrderLineCommand,
        RemovePurchaseOrderLineCommand, ReceivePurchaseOrderLineCommand
    )
    from .application.purchases.commands.handlers import (
        CreateSupplierHandler, UpdateSupplierHandler, ArchiveSupplierHandler,
        ActivateSupplierHandler, DeactivateSupplierHandler,
        CreateSupplierAddressHandler, UpdateSupplierAddressHandler, DeleteSupplierAddressHandler,
        CreateSupplierContactHandler, UpdateSupplierContactHandler, DeleteSupplierContactHandler,
        CreatePurchaseOrderHandler, UpdatePurchaseOrderHandler, ConfirmPurchaseOrderHandler,
        CancelPurchaseOrderHandler, AddPurchaseOrderLineHandler, UpdatePurchaseOrderLineHandler,
        RemovePurchaseOrderLineHandler, ReceivePurchaseOrderLineHandler
    )
    from .application.purchases.queries.queries import (
        GetSupplierByIdQuery, ListSuppliersQuery, SearchSuppliersQuery,
        GetPurchaseOrderByIdQuery, ListPurchaseOrdersQuery
    )
    from .application.purchases.queries.handlers import (
        GetSupplierByIdHandler, ListSuppliersHandler, SearchSuppliersHandler,
        GetPurchaseOrderByIdHandler, ListPurchaseOrdersHandler
    )
    
    # Register Purchase Commands
    mediator.register_command(CreateSupplierCommand, CreateSupplierHandler())
    mediator.register_command(UpdateSupplierCommand, UpdateSupplierHandler())
    mediator.register_command(ArchiveSupplierCommand, ArchiveSupplierHandler())
    mediator.register_command(ActivateSupplierCommand, ActivateSupplierHandler())
    mediator.register_command(DeactivateSupplierCommand, DeactivateSupplierHandler())
    mediator.register_command(CreateSupplierAddressCommand, CreateSupplierAddressHandler())
    mediator.register_command(UpdateSupplierAddressCommand, UpdateSupplierAddressHandler())
    mediator.register_command(DeleteSupplierAddressCommand, DeleteSupplierAddressHandler())
    mediator.register_command(CreateSupplierContactCommand, CreateSupplierContactHandler())
    mediator.register_command(UpdateSupplierContactCommand, UpdateSupplierContactHandler())
    mediator.register_command(DeleteSupplierContactCommand, DeleteSupplierContactHandler())
    mediator.register_command(CreatePurchaseOrderCommand, CreatePurchaseOrderHandler())
    mediator.register_command(UpdatePurchaseOrderCommand, UpdatePurchaseOrderHandler())
    mediator.register_command(ConfirmPurchaseOrderCommand, ConfirmPurchaseOrderHandler())
    mediator.register_command(CancelPurchaseOrderCommand, CancelPurchaseOrderHandler())
    mediator.register_command(AddPurchaseOrderLineCommand, AddPurchaseOrderLineHandler())
    mediator.register_command(UpdatePurchaseOrderLineCommand, UpdatePurchaseOrderLineHandler())
    mediator.register_command(RemovePurchaseOrderLineCommand, RemovePurchaseOrderLineHandler())
    mediator.register_command(ReceivePurchaseOrderLineCommand, ReceivePurchaseOrderLineHandler())
    
    # User Story 9: Purchase Request Commands
    from .application.purchases.requests.commands.commands import (
        CreatePurchaseRequestCommand,
        SubmitPurchaseRequestCommand,
        ApprovePurchaseRequestCommand,
        RejectPurchaseRequestCommand,
        ConvertPurchaseRequestCommand
    )
    from .application.purchases.requests.commands.handlers import (
        CreatePurchaseRequestHandler,
        SubmitPurchaseRequestHandler,
        ApprovePurchaseRequestHandler,
        RejectPurchaseRequestHandler,
        ConvertPurchaseRequestHandler
    )
    
    mediator.register_command(CreatePurchaseRequestCommand, CreatePurchaseRequestHandler())
    mediator.register_command(SubmitPurchaseRequestCommand, SubmitPurchaseRequestHandler())
    mediator.register_command(ApprovePurchaseRequestCommand, ApprovePurchaseRequestHandler())
    mediator.register_command(RejectPurchaseRequestCommand, RejectPurchaseRequestHandler())
    mediator.register_command(ConvertPurchaseRequestCommand, ConvertPurchaseRequestHandler())
    
    # User Story 9: Purchase Receipt Commands
    from .application.purchases.receipts.commands.commands import (
        CreatePurchaseReceiptCommand,
        ValidatePurchaseReceiptCommand
    )
    from .application.purchases.receipts.commands.handlers import (
        CreatePurchaseReceiptHandler,
        ValidatePurchaseReceiptHandler
    )
    
    mediator.register_command(CreatePurchaseReceiptCommand, CreatePurchaseReceiptHandler())
    mediator.register_command(ValidatePurchaseReceiptCommand, ValidatePurchaseReceiptHandler())
    
    # User Story 9: Supplier Invoice Commands
    from .application.purchases.invoices.commands.commands import (
        CreateSupplierInvoiceCommand,
        MatchSupplierInvoiceCommand
    )
    from .application.purchases.invoices.commands.handlers import (
        CreateSupplierInvoiceHandler,
        MatchSupplierInvoiceHandler
    )
    
    mediator.register_command(CreateSupplierInvoiceCommand, CreateSupplierInvoiceHandler())
    mediator.register_command(MatchSupplierInvoiceCommand, MatchSupplierInvoiceHandler())
    
    # Register Purchase Queries
    mediator.register_query(GetSupplierByIdQuery, GetSupplierByIdHandler())
    mediator.register_query(ListSuppliersQuery, ListSuppliersHandler())
    mediator.register_query(SearchSuppliersQuery, SearchSuppliersHandler())
    mediator.register_query(GetPurchaseOrderByIdQuery, GetPurchaseOrderByIdHandler())
    mediator.register_query(ListPurchaseOrdersQuery, ListPurchaseOrdersHandler())
    
    # User Story 9: Purchase Receipt Queries
    from .application.purchases.receipts.queries.queries import (
        ListPurchaseReceiptsQuery,
        GetPurchaseReceiptByIdQuery
    )
    from .application.purchases.receipts.queries.handlers import (
        ListPurchaseReceiptsHandler,
        GetPurchaseReceiptByIdHandler
    )
    
    mediator.register_query(ListPurchaseReceiptsQuery, ListPurchaseReceiptsHandler())
    mediator.register_query(GetPurchaseReceiptByIdQuery, GetPurchaseReceiptByIdHandler())
    
    # User Story 9: Purchase Request Queries
    from .application.purchases.requests.queries.queries import (
        ListPurchaseRequestsQuery,
        GetPurchaseRequestByIdQuery
    )
    from .application.purchases.requests.queries.handlers import (
        ListPurchaseRequestsHandler,
        GetPurchaseRequestByIdHandler
    )
    
    mediator.register_query(ListPurchaseRequestsQuery, ListPurchaseRequestsHandler())
    mediator.register_query(GetPurchaseRequestByIdQuery, GetPurchaseRequestByIdHandler())
    
    # User Story 9: Supplier Invoice Queries
    from .application.purchases.invoices.queries.queries import (
        ListSupplierInvoicesQuery,
        GetSupplierInvoiceByIdQuery
    )
    from .application.purchases.invoices.queries.handlers import (
        ListSupplierInvoicesHandler,
        GetSupplierInvoiceByIdHandler
    )
    
    mediator.register_query(ListSupplierInvoicesQuery, ListSupplierInvoicesHandler())
    mediator.register_query(GetSupplierInvoiceByIdQuery, GetSupplierInvoiceByIdHandler())
    
    # Stock Commands/Queries
    from .application.stock.commands.commands import (
        CreateLocationCommand, UpdateLocationCommand,
        CreateStockItemCommand, UpdateStockItemCommand,
        CreateStockMovementCommand,
        ReserveStockCommand, ReleaseStockCommand, AdjustStockCommand
    )
    from .application.stock.commands.handlers import (
        CreateLocationHandler, UpdateLocationHandler,
        CreateStockItemHandler, UpdateStockItemHandler,
        CreateStockMovementHandler,
        ReserveStockHandler, ReleaseStockHandler, AdjustStockHandler
    )
    from .application.stock.queries.queries import (
        GetStockLevelsQuery, GetStockAlertsQuery, GetStockMovementsQuery,
        GetLocationHierarchyQuery, GetStockItemByIdQuery, GetLocationByIdQuery,
        GlobalStockQuery
    )
    from .application.stock.queries.handlers import (
        GetStockLevelsHandler, GetStockAlertsHandler, GetStockMovementsHandler,
        GetLocationHierarchyHandler, GetStockItemByIdHandler, GetLocationByIdHandler,
        GlobalStockHandler
    )
    
    # Register Stock Commands
    mediator.register_command(CreateLocationCommand, CreateLocationHandler())
    mediator.register_command(UpdateLocationCommand, UpdateLocationHandler())
    mediator.register_command(CreateStockItemCommand, CreateStockItemHandler())
    mediator.register_command(UpdateStockItemCommand, UpdateStockItemHandler())
    mediator.register_command(CreateStockMovementCommand, CreateStockMovementHandler())
    mediator.register_command(ReserveStockCommand, ReserveStockHandler())
    mediator.register_command(ReleaseStockCommand, ReleaseStockHandler())
    mediator.register_command(AdjustStockCommand, AdjustStockHandler())
    
    # Register Stock Queries
    mediator.register_query(GetStockLevelsQuery, GetStockLevelsHandler())
    mediator.register_query(GetStockAlertsQuery, GetStockAlertsHandler())
    mediator.register_query(GetStockMovementsQuery, GetStockMovementsHandler())
    mediator.register_query(GetLocationHierarchyQuery, GetLocationHierarchyHandler())
    mediator.register_query(GlobalStockQuery, GlobalStockHandler())
    
    # Site Commands/Queries (User Story 10)
    from .application.stock.sites.commands import (
        CreateSiteCommand, UpdateSiteCommand, DeactivateSiteCommand,
        CreateSiteHandler, UpdateSiteHandler, DeactivateSiteHandler
    )
    from .application.stock.sites.queries import (
        ListSitesQuery, GetSiteByIdQuery, GetSiteStockQuery,
        ListSitesHandler, GetSiteByIdHandler, GetSiteStockHandler
    )
    
    mediator.register_command(CreateSiteCommand, CreateSiteHandler())
    mediator.register_command(UpdateSiteCommand, UpdateSiteHandler())
    mediator.register_command(DeactivateSiteCommand, DeactivateSiteHandler())
    
    mediator.register_query(ListSitesQuery, ListSitesHandler())
    mediator.register_query(GetSiteByIdQuery, GetSiteByIdHandler())
    mediator.register_query(GetSiteStockQuery, GetSiteStockHandler())
    
    # Stock Transfer Commands/Queries (User Story 10)
    from .application.stock.transfers.commands import (
        CreateStockTransferCommand, ShipStockTransferCommand,
        ReceiveStockTransferCommand, CancelStockTransferCommand,
        CreateStockTransferHandler, ShipStockTransferHandler,
        ReceiveStockTransferHandler, CancelStockTransferHandler
    )
    from .application.stock.transfers.queries import (
        ListStockTransfersQuery, GetStockTransferByIdQuery,
        ListStockTransfersHandler, GetStockTransferByIdHandler
    )
    
    mediator.register_command(CreateStockTransferCommand, CreateStockTransferHandler())
    mediator.register_command(ShipStockTransferCommand, ShipStockTransferHandler())
    mediator.register_command(ReceiveStockTransferCommand, ReceiveStockTransferHandler())
    mediator.register_command(CancelStockTransferCommand, CancelStockTransferHandler())
    
    mediator.register_query(ListStockTransfersQuery, ListStockTransfersHandler())
    mediator.register_query(GetStockTransferByIdQuery, GetStockTransferByIdHandler())
    mediator.register_query(GetStockItemByIdQuery, GetStockItemByIdHandler())
    mediator.register_query(GetLocationByIdQuery, GetLocationByIdHandler())
    
    # Quote Commands/Queries
    from .application.sales.quotes.commands.commands import (
        CreateQuoteCommand, UpdateQuoteCommand, AddQuoteLineCommand,
        UpdateQuoteLineCommand, RemoveQuoteLineCommand,
        SendQuoteCommand, AcceptQuoteCommand, RejectQuoteCommand,
        CancelQuoteCommand, DeleteQuoteCommand, ConvertQuoteToOrderCommand
    )
    from .application.sales.quotes.commands.handlers import (
        CreateQuoteHandler, UpdateQuoteHandler, AddQuoteLineHandler,
        UpdateQuoteLineHandler, RemoveQuoteLineHandler,
        SendQuoteHandler, AcceptQuoteHandler, RejectQuoteHandler,
        CancelQuoteHandler, DeleteQuoteHandler, ConvertQuoteToOrderHandler
    )
    from .application.sales.quotes.queries.queries import (
        ListQuotesQuery, GetQuoteByIdQuery, GetQuoteHistoryQuery
    )
    from .application.sales.quotes.queries.handlers import (
        ListQuotesHandler, GetQuoteByIdHandler, GetQuoteHistoryHandler
    )
    
    # Register Quote Commands
    mediator.register_command(CreateQuoteCommand, CreateQuoteHandler())
    mediator.register_command(UpdateQuoteCommand, UpdateQuoteHandler())
    mediator.register_command(AddQuoteLineCommand, AddQuoteLineHandler())
    mediator.register_command(UpdateQuoteLineCommand, UpdateQuoteLineHandler())
    mediator.register_command(RemoveQuoteLineCommand, RemoveQuoteLineHandler())
    mediator.register_command(SendQuoteCommand, SendQuoteHandler())
    mediator.register_command(AcceptQuoteCommand, AcceptQuoteHandler())
    mediator.register_command(RejectQuoteCommand, RejectQuoteHandler())
    mediator.register_command(CancelQuoteCommand, CancelQuoteHandler())
    mediator.register_command(DeleteQuoteCommand, DeleteQuoteHandler())
    mediator.register_command(ConvertQuoteToOrderCommand, ConvertQuoteToOrderHandler())
    
    # Register Order Commands
    from .application.sales.orders.commands import (
        CreateOrderCommand, UpdateOrderCommand, ConfirmOrderCommand,
        CancelOrderCommand, UpdateOrderStatusCommand,
        AddOrderLineCommand, UpdateOrderLineCommand, RemoveOrderLineCommand,
        CreateOrderHandler, UpdateOrderHandler, ConfirmOrderHandler,
        CancelOrderHandler, UpdateOrderStatusHandler,
        AddOrderLineHandler, UpdateOrderLineHandler, RemoveOrderLineHandler
    )
    
    mediator.register_command(CreateOrderCommand, CreateOrderHandler())
    mediator.register_command(UpdateOrderCommand, UpdateOrderHandler())
    mediator.register_command(ConfirmOrderCommand, ConfirmOrderHandler())
    mediator.register_command(CancelOrderCommand, CancelOrderHandler())
    mediator.register_command(UpdateOrderStatusCommand, UpdateOrderStatusHandler())
    mediator.register_command(AddOrderLineCommand, AddOrderLineHandler())
    mediator.register_command(UpdateOrderLineCommand, UpdateOrderLineHandler())
    mediator.register_command(RemoveOrderLineCommand, RemoveOrderLineHandler())
    
    # Register Quote Queries
    mediator.register_query(ListQuotesQuery, ListQuotesHandler())
    mediator.register_query(GetQuoteByIdQuery, GetQuoteByIdHandler())
    mediator.register_query(GetQuoteHistoryQuery, GetQuoteHistoryHandler())
    
    # Register Order Queries
    from .application.sales.orders.queries import (
        ListOrdersQuery, GetOrderByIdQuery, GetOrderHistoryQuery,
        ListOrdersHandler, GetOrderByIdHandler, GetOrderHistoryHandler
    )
    
    mediator.register_query(ListOrdersQuery, ListOrdersHandler())
    mediator.register_query(GetOrderByIdQuery, GetOrderByIdHandler())
    mediator.register_query(GetOrderHistoryQuery, GetOrderHistoryHandler())
    
    # Invoice Commands/Queries
    from .application.billing.invoices.commands.commands import (
        CreateInvoiceCommand, ValidateInvoiceCommand, SendInvoiceCommand, CreateCreditNoteCommand
    )
    from .application.billing.invoices.commands.handlers import (
        CreateInvoiceHandler, ValidateInvoiceHandler, SendInvoiceHandler, CreateCreditNoteHandler
    )
    from .application.billing.invoices.queries.queries import (
        ListInvoicesQuery, GetInvoiceByIdQuery, GetInvoiceHistoryQuery
    )
    from .application.billing.invoices.queries.handlers import (
        ListInvoicesHandler, GetInvoiceByIdHandler, GetInvoiceHistoryHandler
    )
    
    # Register Invoice Commands
    mediator.register_command(CreateInvoiceCommand, CreateInvoiceHandler())
    mediator.register_command(ValidateInvoiceCommand, ValidateInvoiceHandler())
    mediator.register_command(SendInvoiceCommand, SendInvoiceHandler())
    mediator.register_command(CreateCreditNoteCommand, CreateCreditNoteHandler())
    
    # Register Invoice Queries
    mediator.register_query(ListInvoicesQuery, ListInvoicesHandler())
    mediator.register_query(GetInvoiceByIdQuery, GetInvoiceByIdHandler())
    mediator.register_query(GetInvoiceHistoryQuery, GetInvoiceHistoryHandler())
    
    # Payment Commands/Queries
    from .application.billing.payments.commands.commands import (
        CreatePaymentCommand, AllocatePaymentCommand, ReconcilePaymentCommand, ImportBankStatementCommand,
        ConfirmPaymentCommand
    )
    from .application.billing.payments.commands.handlers import (
        CreatePaymentHandler, AllocatePaymentHandler, ReconcilePaymentHandler, ImportBankStatementHandler,
        ConfirmPaymentHandler
    )
    from .application.billing.payments.queries.queries import (
        ListPaymentsQuery, GetPaymentByIdQuery, GetOverdueInvoicesQuery, GetAgingReportQuery
    )
    from .application.billing.payments.queries.handlers import (
        ListPaymentsHandler, GetPaymentByIdHandler, GetOverdueInvoicesHandler, GetAgingReportHandler
    )
    
    # Register Payment Commands
    mediator.register_command(CreatePaymentCommand, CreatePaymentHandler())
    mediator.register_command(AllocatePaymentCommand, AllocatePaymentHandler())
    mediator.register_command(ReconcilePaymentCommand, ReconcilePaymentHandler())
    mediator.register_command(ImportBankStatementCommand, ImportBankStatementHandler())
    mediator.register_command(ConfirmPaymentCommand, ConfirmPaymentHandler())
    
    # Register Payment Queries
    mediator.register_query(ListPaymentsQuery, ListPaymentsHandler())
    mediator.register_query(GetPaymentByIdQuery, GetPaymentByIdHandler())
    mediator.register_query(GetOverdueInvoicesQuery, GetOverdueInvoicesHandler())
    mediator.register_query(GetAgingReportQuery, GetAgingReportHandler())
    
    # Register Dashboard Queries
    from .application.dashboard.queries import (
        GetKPIsQuery, GetRevenueQuery, GetStockAlertsQuery, GetActiveOrdersQuery,
        GetKPIsHandler, GetRevenueHandler, GetStockAlertsHandler, GetActiveOrdersHandler
    )
    
    mediator.register_query(GetKPIsQuery, GetKPIsHandler())
    mediator.register_query(GetRevenueQuery, GetRevenueHandler())
    mediator.register_query(GetStockAlertsQuery, GetStockAlertsHandler())
    mediator.register_query(GetActiveOrdersQuery, GetActiveOrdersHandler())
    
    # Settings Commands/Queries
    from .application.settings.commands import (
        UpdateCompanySettingsCommand, UpdateAppSettingsCommand,
        UpdateCompanySettingsHandler, UpdateAppSettingsHandler
    )
    from .application.settings.queries import (
        GetCompanySettingsQuery, GetAppSettingsQuery,
        GetCompanySettingsHandler, GetAppSettingsHandler
    )
    
    mediator.register_command(UpdateCompanySettingsCommand, UpdateCompanySettingsHandler())
    mediator.register_command(UpdateAppSettingsCommand, UpdateAppSettingsHandler())
    mediator.register_query(GetCompanySettingsQuery, GetCompanySettingsHandler())
    mediator.register_query(GetAppSettingsQuery, GetAppSettingsHandler())
    
    mediator.register_command(LoginCommand, LoginCommandHandler())

    # Register API blueprints
    try:
        from .api.auth import auth_bp
        from .api.products import products_bp
        from .api.customers import customers_bp
        from .api.purchases import purchases_bp
        from .api.stock import stock_bp
        from .api.sales import sales_bp
        from .api.dashboard import dashboard_bp
        from .api.i18n import i18n_bp

        app.register_blueprint(auth_bp, url_prefix="/api/auth")
        app.register_blueprint(products_bp, url_prefix="/api/products")
        app.register_blueprint(customers_bp, url_prefix="/api/customers")
        app.register_blueprint(purchases_bp, url_prefix="/api")
        app.register_blueprint(stock_bp, url_prefix="/api/stock", name="stock_api")
        app.register_blueprint(sales_bp, url_prefix="/api/sales", name="sales_api")
        app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard", name="dashboard_api")
        app.register_blueprint(i18n_bp, url_prefix="/api/i18n", name="i18n_api")
        print(f"[OK] Registered API blueprints: purchases, products, customers, auth, stock, sales, dashboard, i18n")
    except Exception as e:
        import traceback
        print(f"[ERROR] Error registering API blueprints: {e}")
        traceback.print_exc()
    
    # Register frontend route blueprints
    try:
        from .routes.auth_routes import auth_routes
        from .routes.dashboard_routes import dashboard_routes
        from .routes.products_routes import products_routes
        from .routes.customers_routes import customers_routes
        from .routes.purchases_routes import purchases_routes
        from .routes.stock_routes import stock_routes
        from .routes.sales_routes import sales_routes
        from .routes.promotions_routes import promotions_routes
        from .routes.modules_routes import modules_routes
        
        app.register_blueprint(auth_routes)
        app.register_blueprint(dashboard_routes)
        app.register_blueprint(products_routes)
        app.register_blueprint(customers_routes)
        app.register_blueprint(purchases_routes)
        app.register_blueprint(stock_routes)
        app.register_blueprint(sales_routes)
        app.register_blueprint(promotions_routes)
        from .routes.billing_routes import billing_routes
        from .routes.settings_routes import settings_routes
        app.register_blueprint(billing_routes)
        app.register_blueprint(modules_routes)
        app.register_blueprint(settings_routes)
        
        print(f"[OK] Registered frontend blueprints: {list(app.blueprints.keys())}")
    except Exception as e:
        import traceback
        print(f"[ERROR] Error registering frontend routes: {e}")
        traceback.print_exc()
        pass

    return app