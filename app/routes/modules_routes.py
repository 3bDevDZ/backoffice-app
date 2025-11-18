"""Frontend route handlers for modular navigation."""
from flask import Blueprint, render_template, request
from flask_babel import get_locale, gettext as _
from app.security.session_auth import require_roles_or_redirect

modules_routes = Blueprint('modules', __name__)


@modules_routes.route('/modules')
@require_roles_or_redirect('admin', 'commercial', 'direction', 'warehouse')
def home():
    """Render the modules home page."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    return render_template(
        'modules/home.html',
        locale=locale,
        direction=direction
    )


@modules_routes.route('/modules/sales')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def sales_menu():
    """Render the Sales module menu."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    from flask import url_for
    
    menu_items = [
        {
            'title': _('Customers'),
            'description': _('Manage customer database and information'),
            'icon': 'fas fa-users',
            'color': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'url': url_for('customers_frontend.list')
        },
        {
            'title': _('Quotes'),
            'description': _('Create and manage sales quotes'),
            'icon': 'fas fa-file-invoice',
            'color': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'url': url_for('sales.quotes_list')
        },
        {
            'title': _('Orders'),
            'description': _('Manage sales orders and fulfillment'),
            'icon': 'fas fa-shopping-cart',
            'color': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'url': url_for('sales.orders_list')
        },
        {
            'title': _('Promotions'),
            'description': _('Manage promotional campaigns and discounts'),
            'icon': 'fas fa-percent',
            'color': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            'url': url_for('promotions.list')
        },
        {
            'title': _('Invoices'),
            'description': _('Generate and manage customer invoices'),
            'icon': 'fas fa-file-invoice-dollar',
            'color': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'url': url_for('billing.invoices_list')
        },
        {
            'title': _('Payments'),
            'description': _('Record payments and manage collections'),
            'icon': 'fas fa-money-check-alt',
            'color': 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
            'url': url_for('billing.payments_list')
        },
        {
            'title': _('Payments Dashboard'),
            'description': _('View payment KPIs and aging reports'),
            'icon': 'fas fa-chart-bar',
            'color': 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            'url': url_for('billing.payments_dashboard')
        }
    ]
    
    return render_template(
        'modules/menu.html',
        module_name=_('Sales'),
        module_description=_('Manage your sales process from quotes to payments'),
        module_icon='fas fa-shopping-cart',
        module_color='linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        menu_items=menu_items,
        locale=locale,
        direction=direction
    )


@modules_routes.route('/modules/purchases')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def purchases_menu():
    """Render the Purchases module menu."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    from flask import url_for
    
    menu_items = [
        {
            'title': _('Suppliers'),
            'description': _('Manage supplier database and information'),
            'icon': 'fas fa-truck',
            'color': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'url': url_for('purchases_frontend.list_suppliers')
        },
        {
            'title': _('Purchase Requests'),
            'description': _('Create and manage purchase requests'),
            'icon': 'fas fa-clipboard-list',
            'color': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'url': url_for('purchases_frontend.list_purchase_requests')
        },
        {
            'title': _('Purchase Orders'),
            'description': _('Manage purchase orders from suppliers'),
            'icon': 'fas fa-shopping-bag',
            'color': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'url': url_for('purchases_frontend.list_purchase_orders')
        },
        {
            'title': _('Purchase Receipts'),
            'description': _('Record goods received from suppliers'),
            'icon': 'fas fa-clipboard-check',
            'color': 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
            'url': url_for('purchases_frontend.list_purchase_receipts')
        },
        {
            'title': _('Supplier Invoices'),
            'description': _('Process and match supplier invoices'),
            'icon': 'fas fa-file-invoice-dollar',
            'color': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'url': url_for('purchases_frontend.list_supplier_invoices')
        }
    ]
    
    return render_template(
        'modules/menu.html',
        module_name=_('Purchases'),
        module_description=_('Manage your complete purchase cycle from requests to invoices'),
        module_icon='fas fa-shopping-bag',
        module_color='linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        menu_items=menu_items,
        locale=locale,
        direction=direction
    )


@modules_routes.route('/modules/inventory')
@require_roles_or_redirect('admin', 'warehouse', 'direction')
def inventory_menu():
    """Render the Inventory module menu."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    from flask import url_for
    
    menu_items = [
        {
            'title': _('Stock Overview'),
            'description': _('View current stock levels and availability'),
            'icon': 'fas fa-boxes',
            'color': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'url': url_for('stock.index')
        },
        {
            'title': _('Warehouses'),
            'description': _('Manage warehouse locations and sites'),
            'icon': 'fas fa-warehouse',
            'color': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'url': url_for('stock.locations')
        },
        {
            'title': _('Stock Movements'),
            'description': _('View and track stock movements history'),
            'icon': 'fas fa-exchange-alt',
            'color': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            'url': url_for('stock.movements')
        },
        {
            'title': _('Stock Alerts'),
            'description': _('Monitor low stock and reorder alerts'),
            'icon': 'fas fa-exclamation-triangle',
            'color': 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            'url': url_for('stock.alerts')
        }
    ]
    
    return render_template(
        'modules/menu.html',
        module_name=_('Inventory'),
        module_description=_('Manage stock levels, locations, and movements'),
        module_icon='fas fa-boxes',
        module_color='linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        menu_items=menu_items,
        locale=locale,
        direction=direction
    )


@modules_routes.route('/modules/catalog')
@require_roles_or_redirect('admin', 'commercial', 'direction')
def catalog_menu():
    """Render the Catalog module menu."""
    locale = get_locale()
    direction = 'rtl' if locale == 'ar' else 'ltr'
    
    from flask import url_for
    
    menu_items = [
        {
            'title': _('Products'),
            'description': _('Manage product catalog and variants'),
            'icon': 'fas fa-box',
            'color': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'url': url_for('products_frontend.list')
        },
        {
            'title': _('Price Lists'),
            'description': _('Create and manage pricing lists'),
            'icon': 'fas fa-tags',
            'color': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            'url': url_for('products_frontend.list_price_lists')
        }
    ]
    
    return render_template(
        'modules/menu.html',
        module_name=_('Catalog'),
        module_description=_('Manage your product catalog and pricing'),
        module_icon='fas fa-box',
        module_color='linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
        menu_items=menu_items,
        locale=locale,
        direction=direction
    )

