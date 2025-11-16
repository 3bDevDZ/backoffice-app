# Implementation Plan: Commercial Management MVP System

**Branch**: `001-commercial-management-mvp` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-commercial-management-mvp/spec.md`

## Summary

Implement a Commercial Management MVP system using Flask with CQRS architecture. The system will manage products, customers, inventory, sales (quotes and orders), and provide a dashboard with KPIs. The implementation builds on existing Flask codebase with CQRS pattern, extending Product and Customer modules, and adding Stock, Sales, and Dashboard modules.

**Frontend & Backend**: Flask will serve both frontend (HTML templates) and backend (REST API). The design files in `/design` folder will be converted to Jinja2 templates served by Flask. The application will be a full-stack Flask application with server-side rendering and API endpoints. Multi-language (Arabic and French) with RTL support for Arabic will be implemented for both templates and API responses.

**Technical Approach**: Full-stack Flask application with:
- Server-side rendering: Convert design HTML files to Jinja2 templates
- REST API endpoints: For AJAX/fetch requests from frontend
- CQRS pattern: Commands/Queries/Handlers for business logic
- SQLAlchemy domain models
- Internationalization (i18n): Flask-Babel for templates and API responses
- Maintain consistency with existing code structure

## Technical Context

**Language/Version**: Python 3.10+ (as per pyproject.toml target-version)  
**Primary Dependencies**: Flask 3.0+, SQLAlchemy 2.0+, Alembic, Marshmallow, Flask-JWT-Extended, Celery, WeasyPrint, Flask-Babel (i18n), Jinja2 (templates)  
**Storage**: PostgreSQL (via SQLAlchemy ORM with existing Base declarative model)  
**Testing**: pytest, pytest-cov, factory_boy (for test data factories)  
**Target Platform**: Linux server (full-stack web application)  
**Project Type**: Full-stack web application (Flask serves both frontend templates and REST API)  
**Frontend**: Jinja2 templates converted from `/design` HTML files, served by Flask with server-side rendering  
**Internationalization**: Multi-language support (Arabic/AR, French/FR) with RTL support for Arabic in both templates and API  
**Performance Goals**: 
- Page responses < 2 seconds (95th percentile)
- Product search returns results for 10,000 products in < 1 second
- Stock level updates reflect within 5 seconds of order confirmation
- Support 50 concurrent users without performance degradation
**Constraints**: 
- Must maintain data integrity for stock reservations (no negative stock, reserved ≤ physical)
- Real-time stock updates required
- PDF generation for quotes/orders must complete in < 5 seconds
- Import/export operations must handle 1,000+ records
**Scale/Scope**: 
- 100-10,000 product references
- 50-5,000 active customers
- 100,000+ documents per year
- 5-50 users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: Constitution file (`.specify/memory/constitution.md`) appears to be a template and does not contain project-specific principles. No specific gates defined. Proceeding with standard development practices:
- Follow existing CQRS architecture pattern
- Maintain separation of concerns (Domain, Application, Infrastructure, API layers)
- Use existing mediator pattern for command/query dispatch
- Follow existing code style and structure

## Project Structure

### Documentation (this feature)

```
specs/001-commercial-management-mvp/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

**Structure Decision**: Extend existing Flask application structure. The codebase already follows a clean architecture with Domain, Application (CQRS), Infrastructure, and API layers. We will extend this pattern for new modules.

```
app/
├── __init__.py                    # Flask app factory (existing)
├── config.py                      # Configuration (existing)
├── api/                           # REST API blueprints (existing - extend)
│   ├── auth.py                   # Authentication API endpoints (existing)
│   ├── products.py               # Product API endpoints (existing - extend)
│   ├── customers.py               # Customer API endpoints (existing - extend)
│   ├── stock.py                   # NEW: Stock API endpoints
│   ├── sales.py                   # NEW: Quotes and Orders API endpoints
│   └── dashboard.py               # NEW: Dashboard KPI API endpoints
├── routes/                        # NEW: Frontend route handlers (template rendering)
│   ├── __init__.py
│   ├── auth_routes.py            # Login, logout pages
│   ├── dashboard_routes.py       # Dashboard page
│   ├── products_routes.py         # Products list and form pages
│   ├── customers_routes.py        # Customers list and form pages
│   ├── stock_routes.py            # Stock management page
│   └── sales_routes.py            # Orders/quotes list and form pages
├── templates/                     # NEW: Jinja2 templates (converted from /design)
│   ├── base.html                  # Base template with sidebar, navigation
│   ├── auth/
│   │   └── login.html             # Converted from 01-login.html
│   ├── dashboard/
│   │   └── index.html             # Converted from 02-dashboard.html
│   ├── products/
│   │   ├── list.html              # Converted from 03-products-list.html
│   │   └── form.html              # Converted from 04-product-form.html
│   ├── customers/
│   │   ├── list.html              # Converted from 05-customers-list.html
│   │   └── form.html              # Converted from 06-customer-form.html
│   ├── stock/
│   │   └── index.html             # Converted from 07-stock.html
│   └── sales/
│       ├── orders_list.html       # Converted from 08-orders-list.html
│       └── order_form.html        # Converted from 09-order-form.html
├── static/                        # NEW: Static files (CSS, JS, images)
│   ├── css/
│   │   └── custom.css             # Custom styles (if needed beyond Tailwind)
│   ├── js/
│   │   ├── main.js                # Main JavaScript for frontend
│   │   ├── api.js                 # API client utilities
│   │   └── i18n.js                # Language switching, RTL handling
│   └── images/
│       └── logo.png               # Application logo
├── application/                   # CQRS application layer (existing)
│   ├── common/
│   │   ├── cqrs.py               # Command/Query base classes (existing)
│   │   └── mediator.py           # Mediator pattern (existing)
│   ├── products/                  # Product commands/queries (existing - extend)
│   │   ├── commands/
│   │   │   ├── commands.py
│   │   │   └── handlers.py
│   │   └── queries/
│   │       ├── queries.py
│   │       ├── handlers.py
│   │       └── product_dto.py
│   ├── customers/                # Customer commands/queries (existing - extend)
│   │   ├── commands/
│   │   └── queries/
│   ├── stock/                     # NEW: Stock commands/queries
│   │   ├── commands/
│   │   │   ├── commands.py       # CreateMovementCommand, CreateInventoryCommand, etc.
│   │   │   └── handlers.py
│   │   └── queries/
│   │       ├── queries.py         # GetStockLevelsQuery, GetStockAlertsQuery, etc.
│   │       ├── handlers.py
│   │       └── stock_dto.py
│   ├── sales/                      # NEW: Sales commands/queries
│   │   ├── quotes/
│   │   │   ├── commands/
│   │   │   │   ├── commands.py    # CreateQuoteCommand, SendQuoteCommand, ConvertQuoteToOrderCommand
│   │   │   │   └── handlers.py
│   │   │   └── queries/
│   │   │       ├── queries.py
│   │   │       └── handlers.py
│   │   └── orders/
│   │       ├── commands/
│   │       │   ├── commands.py    # CreateOrderCommand, ConfirmOrderCommand, CancelOrderCommand
│   │       │   └── handlers.py
│   │       └── queries/
│   │           ├── queries.py
│   │           └── handlers.py
│   └── dashboard/                  # NEW: Dashboard queries
│       └── queries/
│           ├── queries.py          # GetKPIsQuery
│           └── handlers.py
├── domain/                         # Domain models (existing - extend)
│   └── models/
│       ├── product.py              # Product model (existing - extend for categories, variants)
│       ├── customer.py             # Customer model (existing - extend for B2B/B2C, addresses, contacts)
│       ├── user.py                 # User model (existing)
│       ├── category.py             # NEW: Category model
│       ├── stock.py                # NEW: StockItem, StockMovement, Location models
│       ├── inventory.py            # NEW: Inventory, InventoryCount models
│       ├── quote.py                # NEW: Quote, QuoteLine models
│       └── order.py                # NEW: Order, OrderLine models
├── infrastructure/
│   ├── db.py                       # SQLAlchemy Base and session management (existing)
│   └── migrate.py                  # Alembic migration helpers (existing)
├── security/
│   ├── auth.py                     # Authentication (existing)
│   └── rbac.py                     # Role-based access control (existing)
├── services/                       # NEW: Domain services
│   ├── stock_service.py            # Stock reservation, movement validation
│   ├── pricing_service.py          # Price calculation, discount application
│   └── pdf_service.py              # PDF generation for quotes/orders
├── pdf_templates/                  # NEW: Jinja2 templates for PDFs
│   ├── quote.html
│   └── order.html
└── utils/                          # NEW: Common utilities
    ├── validators.py               # Business rule validators
    └── import_export.py            # CSV/Excel import/export helpers

migrations/                          # Alembic migrations (existing)
├── versions/
└── env.py

tests/                               # Test suites
├── unit/
│   ├── domain/
│   ├── application/
│   └── services/
├── integration/
│   ├── api/
│   └── workflows/
└── fixtures/                        # Test data factories

uploads/                             # Product images storage
instance/                            # Instance config, .env loading
```

## Full-Stack Flask Implementation

### Frontend: Server-Side Rendering with Jinja2

The design files in `/design` folder will be converted to Jinja2 templates served by Flask:

**Template Structure**:
- **Base Template** (`templates/base.html`): Common layout with sidebar, navigation, user profile
- **Page Templates**: Converted from design HTML files
- **Partials**: Reusable components (cards, tables, forms, modals)

**Design Characteristics** (from `/design` folder):
- **UI Framework**: Tailwind CSS (via CDN or bundled)
- **Layout**: Sidebar navigation (64px width), main content area, top bar with user info
- **Color Scheme**: Indigo primary color (#4F46E5), gray backgrounds, white cards
- **Icons**: Font Awesome 6.4.0
- **Components**: Cards, tables, forms, modals, filters, search bars

**Template Conversion**:
- Convert static HTML to Jinja2 templates
- Replace hardcoded data with template variables
- Add template inheritance (extend base.html)
- Add template includes for reusable components
- Integrate with Flask-Babel for translations

### Backend: REST API Endpoints

Flask will also provide REST API endpoints for:
- AJAX/fetch requests from frontend
- Future mobile app integration
- Third-party integrations

**API Endpoints**:
- Same endpoints as documented in `contracts/openapi.yaml`
- Support locale parameter for translations
- Return JSON responses with locale metadata

### Hybrid Approach

**Server-Side Rendering (SSR)**:
- Initial page load: Flask renders HTML with data
- Better SEO, faster initial load
- Works without JavaScript

**Client-Side Enhancement (AJAX)**:
- Dynamic updates: Frontend JavaScript calls API endpoints
- Form submissions via AJAX
- Real-time updates (stock levels, dashboard KPIs)
- Search/filter without page reload

### Multi-Language Support (Templates + API)

**Templates**:
- Flask-Babel translates template strings
- Locale detection from URL, session, or user preference
- Template context includes `current_locale` and `direction` (ltr/rtl)
- RTL CSS classes applied based on locale

**API**:
- Same locale detection as templates
- JSON responses include translated messages
- Meta includes locale and direction

**Implementation**:
```python
# In route handler
@products_routes.route('/products')
@require_roles('admin', 'commercial')
def products_list():
    locale = get_locale()  # From Flask-Babel
    products = mediator.dispatch(ListProductsQuery())
    return render_template('products/list.html', 
                          products=products, 
                          locale=locale,
                          direction='rtl' if locale == 'ar' else 'ltr')

# In template
{% extends "base.html" %}
{% block content %}
  <h1>{{ _('Products') }}</h1>  {# Translated via Flask-Babel #}
  <div class="{% if direction == 'rtl' %}rtl{% endif %}">
    {# RTL-aware content #}
  </div>
{% endblock %}
```

### Internationalization (i18n) Implementation

**Flask-Babel Setup** (for templates and API):

1. **Flask-Babel Integration**:
   ```python
   from flask_babel import Babel, gettext as _, format_date, format_number
   
   babel = Babel(app)
   
   @babel.localeselector
   def get_locale():
       # 1. Check URL parameter
       locale = request.args.get('locale')
       if locale in ['fr', 'ar']:
           return locale
       # 2. Check user preference
       if current_user and current_user.locale:
           return current_user.locale
       # 3. Check Accept-Language header
       return request.accept_languages.best_match(['fr', 'ar'], 'fr')
   ```

2. **Translation Files Structure**:
   ```
   app/
   └── translations/
       ├── fr/
       │   └── LC_MESSAGES/
       │       ├── messages.po
       │       └── messages.mo
       └── ar/
           └── LC_MESSAGES/
               ├── messages.po
               └── messages.mo
   ```

3. **Locale Detection** (for both templates and API):
   - URL parameter: `/products?locale=ar`
   - User session preference
   - User database preference (default: fr)
   - Accept-Language header
   - Fallback to French if locale not supported

4. **Translation Coverage**:
   - **Templates**: All text in HTML templates
   - **API**: Error messages, status labels, field names, success messages
   - **Documents**: PDF templates (quotes, orders)
   - **Emails**: Email templates

5. **Template Context**:
   ```python
   # In route handlers
   return render_template('page.html',
                         locale=get_locale(),
                         direction='rtl' if get_locale() == 'ar' else 'ltr',
                         ...)
   ```

6. **API Response Format**:
   ```json
   {
     "data": {...},
     "meta": {
       "locale": "fr",
       "direction": "ltr"
     }
   }
   ```

### Route Structure

**Frontend Routes** (Server-Side Rendering):
- `GET /` - Redirect to dashboard or login
- `GET /login` - Login page (renders `templates/auth/login.html`)
- `GET /dashboard` - Dashboard page (renders `templates/dashboard/index.html`)
- `GET /products` - Products list (renders `templates/products/list.html`)
- `GET /products/new` - New product form (renders `templates/products/form.html`)
- `GET /products/<id>/edit` - Edit product form
- `GET /customers` - Customers list (renders `templates/customers/list.html`)
- `GET /customers/new` - New customer form (renders `templates/customers/form.html`)
- `GET /stock` - Stock management (renders `templates/stock/index.html`)
- `GET /orders` - Orders list (renders `templates/sales/orders_list.html`)
- `GET /orders/new` - New order form (renders `templates/sales/order_form.html`)

**API Routes** (REST API for AJAX):
- `GET /api/products` - Products list (JSON)
- `POST /api/products` - Create product (JSON)
- `GET /api/dashboard/stats` - Dashboard statistics (JSON)
- `GET /api/products/search?q=...` - Product search/autocomplete (JSON)
- All other API endpoints as documented in `contracts/openapi.yaml`

**Hybrid Approach**:
- Initial page load: Server-side rendered HTML (fast, SEO-friendly)
- Dynamic updates: AJAX calls to API endpoints (no page reload)
- Form submissions: Can use either POST to route (redirect) or AJAX to API (JSON response)

## Complexity Tracking

*No violations identified. The structure extends existing patterns consistently.*
