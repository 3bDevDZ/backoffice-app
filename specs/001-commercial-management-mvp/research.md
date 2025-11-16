# Research & Technical Decisions: Commercial Management MVP

**Date**: 2025-01-27  
**Feature**: Commercial Management MVP System

## Overview

This document consolidates technical research and decisions for implementing the Commercial Management MVP using Flask. The implementation builds on existing codebase patterns and extends them for new modules.

## Technical Stack Decisions

### Decision: Flask with CQRS Architecture

**Rationale**: 
- Existing codebase already uses Flask with CQRS pattern (Commands/Queries/Handlers)
- Mediator pattern is already implemented for dispatching
- Domain models follow SQLAlchemy declarative base pattern
- Consistency with existing code structure reduces learning curve and maintenance

**Alternatives Considered**:
- FastAPI: Rejected - would require rewriting existing code
- Django: Rejected - different ORM and patterns, would require significant refactoring
- Pure Flask without CQRS: Rejected - existing codebase already uses CQRS, maintaining consistency is important

### Decision: PostgreSQL Database

**Rationale**:
- Already configured in existing codebase (config.py references PostgreSQL)
- Supports ACID transactions required for stock reservations
- Row-level locking available for concurrent stock operations
- Good performance for complex queries (dashboard KPIs, stock reports)

**Alternatives Considered**:
- SQLite: Rejected - insufficient for concurrent operations and production scale
- MySQL: Rejected - PostgreSQL already configured and provides better JSON support

### Decision: SQLAlchemy 2.0 with Declarative Base

**Rationale**:
- Already in use in existing codebase (requirements.txt specifies SQLAlchemy>=2.0.0)
- Domain models already extend Base declarative model
- Alembic migrations already configured
- Maintains consistency with existing Product and Customer models

**Alternatives Considered**: None - already established in codebase

### Decision: Marshmallow for Validation

**Rationale**:
- Already used in existing API schemas (product_schema.py, customer_schema.py)
- Provides serialization/deserialization for API layer
- Validation rules can be defined declaratively
- Consistent with existing patterns

**Alternatives Considered**: 
- Pydantic: Rejected - would require changing existing schemas
- Manual validation: Rejected - Marshmallow provides better structure and reusability

### Decision: Flask-JWT-Extended for Authentication

**Rationale**:
- Already configured in requirements.txt
- JWT tokens suitable for REST API
- Session expiration configurable (30 min default per spec)
- RBAC already implemented in security/rbac.py

**Alternatives Considered**: None - already established

### Decision: WeasyPrint for PDF Generation

**Rationale**:
- Already in requirements.txt
- Converts HTML (Jinja2 templates) to PDF
- Good for professional documents (quotes, orders)
- Supports custom styling and layouts

**Alternatives Considered**:
- ReportLab: Rejected - WeasyPrint already in dependencies, HTML templates are easier to maintain
- PDFKit: Rejected - requires external dependencies (wkhtmltopdf)

### Decision: Celery for Background Tasks

**Rationale**:
- Already in requirements.txt
- Needed for async email sending (quote emails, reminders)
- Scheduled tasks for quote expiration and relances
- Redis/RabbitMQ broker already configured in config.py

**Alternatives Considered**:
- Flask-APScheduler: Rejected - Celery already configured, more robust for production
- Threading: Rejected - Celery provides better task management and monitoring

## Architecture Decisions

### Decision: Extend Existing CQRS Pattern

**Rationale**:
- Existing codebase uses Commands/Queries/Handlers pattern
- Mediator pattern already implemented
- Clear separation of concerns (Domain, Application, Infrastructure, API)
- Maintains consistency across codebase

**Implementation**:
- New modules (Stock, Sales, Dashboard) follow same pattern
- Commands for write operations (create, update, delete)
- Queries for read operations (list, get by id, search)
- Handlers contain business logic and coordinate with domain models

### Decision: Domain Models with Business Logic

**Rationale**:
- Existing Product and Customer models contain business logic (create, update, archive methods)
- Domain-driven design principles
- Business rules enforced at domain level
- Models are self-contained and testable

**Implementation**:
- Stock models: StockItem, StockMovement with validation methods
- Sales models: Quote, Order with state transition methods
- Business rules (e.g., stock reservations, quote expiration) in domain models

### Decision: Row-Level Locking for Stock Operations

**Rationale**:
- Prevents race conditions in concurrent stock reservations
- SQLAlchemy supports `with_for_update()` for pessimistic locking
- Required for data integrity (FR-013: zero stock discrepancies)
- Standard pattern for inventory management systems

**Implementation**:
- Use `session.query(StockItem).with_for_update()` when reserving stock
- Lock held during transaction, released on commit/rollback
- Prevents concurrent modifications to same stock item

### Decision: Transaction Management for Stock Movements

**Rationale**:
- Stock movements must be atomic (entry/exit/transfer)
- Stock level updates must be consistent
- Rollback on errors prevents data corruption
- Existing `get_session()` context manager provides transaction support

**Implementation**:
- All stock movements within single transaction
- Stock level updates in same transaction
- Automatic rollback on exceptions

## Data Model Decisions

### Decision: Separate StockItem Table (Product + Location)

**Rationale**:
- Stock levels tracked per product per location
- Supports multi-location inventory (future requirement)
- Efficient queries for stock by location
- Clear separation of product catalog from inventory

**Alternatives Considered**:
- Stock quantity in Product table: Rejected - doesn't support multi-location, mixes concerns

### Decision: Stock Movement History Table

**Rationale**:
- Complete audit trail of all stock changes
- Required for traceability (FR-031: track who, when, why)
- Supports inventory reconciliation
- Enables stock valuation calculations (FIFO, AVCO)

**Implementation**:
- StockMovement table with: product_id, location_id, quantity, type (entry/exit/transfer/adjustment), user_id, timestamp, reason, related_document_id

### Decision: Quote Versioning via Separate Versions Table

**Rationale**:
- FR-051: Create new version when editing sent quote
- FR-052: Maintain version history
- Preserves original quote for audit
- Allows comparison between versions

**Implementation**:
- Quote table: current version data
- QuoteVersion table: historical versions with version number, created_at, created_by
- QuoteLineVersion for line-level history

### Decision: Order Status as Enum/State Machine

**Rationale**:
- FR-062: Support multiple order statuses (Draft, Confirmed, In Preparation, etc.)
- State transitions must be validated
- Status determines available actions
- Clear workflow definition

**Implementation**:
- OrderStatus enum in domain model
- State transition methods (confirm(), cancel(), ship(), etc.)
- Validation in domain model prevents invalid transitions

## API Design Decisions

### Decision: RESTful API with Flask Blueprints

**Rationale**:
- Existing codebase uses Flask blueprints (products.py, customers.py)
- RESTful conventions (GET, POST, PUT, DELETE)
- Clear resource-based URLs
- Consistent with existing API structure

**Implementation**:
- `/api/stock` - Stock endpoints
- `/api/sales/quotes` - Quote endpoints
- `/api/sales/orders` - Order endpoints
- `/api/dashboard` - Dashboard endpoints

### Decision: Pagination for List Endpoints

**Rationale**:
- Performance requirement: handle 10,000 products
- Existing products endpoint already uses pagination
- Consistent API pattern
- Prevents large response payloads

**Implementation**:
- Query parameters: `?page=1&page_size=20`
- Default page_size: 20, max: 100
- Response includes pagination metadata (total, page, page_size)

### Decision: Standardized Error Responses

**Rationale**:
- Consistent error handling across API
- Better client error handling
- Aligns with REST best practices
- Existing code may need extension for new error types

**Implementation**:
- JSON format: `{"code": "ERROR_CODE", "message": "Human readable", "details": {}}`
- HTTP status codes: 400 (validation), 404 (not found), 403 (forbidden), 500 (server error)

## Security Decisions

### Decision: RBAC with Role-Based Endpoint Protection

**Rationale**:
- Already implemented in security/rbac.py
- Decorator pattern: `@require_roles("admin", "commercial")`
- Fine-grained permissions per module
- Consistent with existing security model

**Implementation**:
- Stock endpoints: require "admin" or "magasinier" roles
- Sales endpoints: require "admin" or "commercial" roles
- Dashboard: require "admin" or "direction" roles
- Extend existing @require_roles decorator

### Decision: Audit Logging for Critical Operations

**Rationale**:
- FR-031: Track who, when, why for stock movements
- Business requirement: complete traceability
- Compliance and debugging
- Non-repudiation for financial operations

**Implementation**:
- AuditLog table: user_id, action, resource_type, resource_id, before_state, after_state, timestamp
- Log stock movements, order confirmations, quote sends
- Queryable for customer history timeline

## Performance Decisions

### Decision: Database Indexes for Common Queries

**Rationale**:
- Performance requirement: product search < 1 second for 10,000 products
- Stock queries need fast lookups
- Dashboard KPIs require efficient aggregations

**Implementation**:
- Index on Product.code, Product.name (for search)
- Index on StockItem(product_id, location_id) composite
- Index on Order.created_at (for dashboard date filtering)
- Index on Customer.email (unique constraint)

### Decision: Query Optimization for Dashboard

**Rationale**:
- FR-077: Dashboard updates within 10 seconds
- Aggregations (revenue, counts) can be slow on large datasets
- Real-time requirement

**Implementation**:
- Use database aggregations (SUM, COUNT) rather than application-level
- Date range filtering at database level
- Consider materialized views for complex KPIs (future optimization)

## Integration Decisions

### Decision: CSV/Excel Import with Validation

**Rationale**:
- FR-009, FR-026: Import products and customers
- Error reporting required
- Large file handling (1,000+ records)

**Implementation**:
- Use pandas or openpyxl for Excel parsing
- csv module for CSV files
- Stream processing for large files
- Validation report: row number, field, error message
- Return validation errors before committing any data

### Decision: Email Sending via Celery Tasks

**Rationale**:
- FR-054: Send quote PDFs via email
- Async operation prevents blocking API response
- Retry capability for failed sends
- Celery already configured

**Implementation**:
- Celery task: `send_quote_email(quote_id, recipient_email)`
- SMTP configuration via environment variables
- Template-based email content
- Track email send status in database

## Testing Decisions

### Decision: pytest with Factory Pattern

**Rationale**:
- Standard Python testing framework
- factory_boy for test data creation
- Fixtures for database setup/teardown
- Consistent with Python ecosystem

**Implementation**:
- Unit tests: domain models, services, handlers
- Integration tests: API endpoints, workflows
- Test factories: ProductFactory, CustomerFactory, etc.
- Database fixtures: test database with migrations

## Deployment Decisions

### Decision: Environment-Based Configuration

**Rationale**:
- Already using python-dotenv in config.py
- Separate dev/test/prod settings
- Security: secrets via environment variables
- Flexible deployment

**Implementation**:
- .env files for local development
- Environment variables in production
- Config classes: DevelopmentConfig, ProductionConfig, TestConfig

## Open Questions Resolved

### Q: How to handle concurrent stock reservations?

**A**: Use database row-level locking (`with_for_update()`) within transactions. This ensures atomic stock reservation and prevents race conditions.

### Q: How to implement quote versioning?

**A**: Create QuoteVersion table to store historical versions. When editing a sent quote, create new version while preserving original.

### Q: How to calculate dashboard KPIs efficiently?

**A**: Use database aggregations with proper indexes. For MVP, calculate on-demand. Future optimization: materialized views or caching.

### Q: How to handle large file imports?

**A**: Stream processing with chunked reading. Validate all rows before committing. Return detailed error report.

## Frontend Design & Internationalization Decisions

### Decision: Full-Stack Flask Application

**Rationale**:
- User requirement: Use Flask for both frontend and backend
- Design files in `/design` folder provide complete UI/UX specifications
- Server-side rendering provides better SEO and initial load performance
- Can still provide REST API for AJAX/fetch requests
- Single codebase, single deployment

**Implementation**:
- Convert design HTML files to Jinja2 templates
- Flask serves templates via route handlers
- Templates use Flask-Babel for translations
- REST API endpoints available for AJAX requests
- Hybrid approach: SSR for initial load, AJAX for dynamic updates

**Template Conversion**:
- `01-login.html` → `templates/auth/login.html`
- `02-dashboard.html` → `templates/dashboard/index.html`
- `03-products-list.html` → `templates/products/list.html`
- `04-product-form.html` → `templates/products/form.html`
- `05-customers-list.html` → `templates/customers/list.html`
- `06-customer-form.html` → `templates/customers/form.html`
- `07-stock.html` → `templates/stock/index.html`
- `08-orders-list.html` → `templates/sales/orders_list.html`
- `09-order-form.html` → `templates/sales/order_form.html`

**Base Template**:
- Extract common layout (sidebar, navigation, top bar) to `templates/base.html`
- All page templates extend base template
- Sidebar navigation, user profile, language switcher in base template

### Decision: Multi-Language Support (Arabic & French)

**Rationale**:
- Business requirement: Support Arabic and French languages
- Arabic requires RTL (right-to-left) text direction
- User experience: Users should see interface in their preferred language
- Compliance: May be required for certain markets

**Implementation**:
- Flask-Babel for translation management (templates and API)
- Translation files for French (fr) and Arabic (ar)
- Locale detection: URL parameter → User preference → Accept-Language header → Default (fr)
- User preference stored in database
- Templates translated via `{{ _('text') }}` syntax
- API responses include locale metadata and translated messages

**Translation Coverage**:
- **Templates**: All UI text (buttons, labels, headings, messages)
- **API**: Error messages, status labels, field names, success messages
- **Documents**: PDF templates (quotes, orders) - language-specific templates
- **Emails**: Email templates (quotes, orders, notifications)

**Template Translation Example**:
```jinja2
{# In template #}
<h1>{{ _('Products') }}</h1>
<button>{{ _('Create Product') }}</button>
<div class="{% if direction == 'rtl' %}rtl text-right{% else %}ltr text-left{% endif %}">
  {{ _('Product Name') }}
</div>
```

### Decision: RTL Support for Arabic

**Rationale**:
- Arabic is written right-to-left
- UI must support RTL layout for Arabic users
- Backend provides direction metadata in API responses

**Implementation**:
- API responses include `direction: "rtl"` when locale=ar
- Frontend uses this metadata to apply RTL CSS classes
- Date/number formatting can use Arabic-Indic numerals (optional)
- Text alignment handled by frontend based on direction

**Alternatives Considered**:
- Separate Arabic API endpoints: Rejected - unnecessary complexity
- Frontend-only translation: Rejected - backend error messages need translation

### Decision: Locale Storage in User Profile

**Rationale**:
- User preference should persist across sessions
- Default locale per user improves UX
- Can be changed in user settings

**Implementation**:
- Add `locale` field to User model (default: 'fr')
- API uses user's preferred locale if not specified in request
- Override with query parameter or Accept-Language header
- User can change locale in profile settings

## References

- Existing codebase: `app/` directory structure
- Flask documentation: https://flask.palletsprojects.com/
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/en/20/
- CQRS pattern: Existing implementation in `app/application/common/`
- Requirements document: `cahier-des-charges-systeme-gestion-commerciale.md`
- Frontend design: `/design` folder with Tailwind CSS wireframes
- Flask-Babel: https://flask-babel.tkte.ch/

