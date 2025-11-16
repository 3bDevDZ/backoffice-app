# Tasks: Commercial Management MVP System

**Input**: Design documents from `/specs/001-commercial-management-mvp/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `app/` at repository root
- Paths shown below assume Flask application structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create Flask-Babel configuration file `babel.cfg` in project root
- [X] T002 [P] Add Flask-Babel dependency to `requirements.txt` (flask-babel>=4.0.0)
- [X] T003 [P] Create translation directory structure `app/translations/fr/LC_MESSAGES/` and `app/translations/ar/LC_MESSAGES/`
- [X] T004 [P] Create static files directory structure `app/static/css/`, `app/static/js/`, `app/static/images/`
- [X] T005 [P] Create templates directory structure `app/templates/` with subdirectories `auth/`, `dashboard/`, `products/`, `customers/`, `stock/`, `sales/`
- [X] T006 [P] Create routes directory `app/routes/` with `__init__.py`
- [X] T007 [P] Create services directory `app/services/` with `__init__.py`
- [X] T008 [P] Create utils directory `app/utils/` with `__init__.py`
- [X] T009 [P] Create pdf_templates directory `app/pdf_templates/` for PDF generation templates
- [X] T010 Initialize Flask-Babel in `app/__init__.py` with locale selector function

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T011 Create Alembic migration for User model locale field in `migrations/versions/`
- [X] T012 [P] Create base template `app/templates/base.html` with sidebar, navigation, and RTL support
- [X] T013 [P] Create locale detection middleware in `app/utils/locale.py` (URL param, user preference, Accept-Language header)
- [X] T014 [P] Create RTL CSS utilities in `app/static/css/rtl.css` for Arabic text direction
- [X] T015 [P] Create language switcher JavaScript in `app/static/js/i18n.js` for frontend language switching
- [X] T016 [P] Create main JavaScript file `app/static/js/main.js` for common frontend functionality
- [X] T017 [P] Create API client utilities in `app/static/js/api.js` for AJAX requests
- [X] T018 Extend User model in `app/domain/models/user.py` with locale field (String(5), default='fr')
- [X] T019 Create Flask-Babel locale selector function in `app/__init__.py` supporting fr/ar locales
- [X] T020 Create translation context processor in `app/__init__.py` to inject locale and direction into template context
- [~] T021 Create database migration for all new entities (Category, Address, Contact, CommercialConditions, Location, StockItem, StockMovement, Quote, QuoteLine, Order, OrderLine, StockReservation) in `migrations/versions/` (Partially done: Category and Product columns added. Remaining: Address, Contact, CommercialConditions, Location, StockItem, StockMovement, Quote, QuoteLine, Order, OrderLine, StockReservation)
- [X] T022 Create API response wrapper in `app/utils/response.py` to include meta.locale and meta.direction in JSON responses
- [X] T023 Register frontend routes blueprint in `app/__init__.py` for template rendering
- [X] T024 Register API blueprints in `app/__init__.py` for REST endpoints

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Manage Product Catalog (Priority: P1) 🎯 MVP

**Goal**: Enable users to create and maintain a complete product catalog with categories, pricing, and variants. Products are the foundation of all commercial operations.

**Independent Test**: Create products with various attributes, categorize them, set prices, and search/filter the catalog. Verify products can be created, updated, searched, and filtered independently of other modules.

### Implementation for User Story 1

- [X] T025 [P] [US1] Create Category domain model in `app/domain/models/category.py` with hierarchical structure
- [X] T026 [P] [US1] Create ProductCategory junction table model in `app/domain/models/product.py` for many-to-many relationship
- [X] T027 [P] [US1] Create ProductVariant domain model in `app/domain/models/product.py` for product variants
- [X] T028 [US1] Extend existing Product model in `app/domain/models/product.py` with category relationships, variant support, and business logic methods (can_delete, archive, activate)
- [X] T029 [US1] Create Category commands (CreateCategoryCommand, UpdateCategoryCommand, DeleteCategoryCommand) in `app/application/products/commands/commands.py`
- [X] T030 [US1] Create Category command handlers in `app/application/products/commands/handlers.py`
- [X] T031 [US1] Create Product commands (CreateProductCommand, UpdateProductCommand, ArchiveProductCommand, DeleteProductCommand) in `app/application/products/commands/commands.py` (extend existing)
- [X] T032 [US1] Extend Product command handlers in `app/application/products/commands/handlers.py` to support categories, variants, and validation
- [X] T033 [US1] Create Product queries (ListProductsQuery, GetProductByIdQuery, SearchProductsQuery) in `app/application/products/queries/queries.py` (extend existing)
- [X] T034 [US1] Extend Product query handlers in `app/application/products/queries/handlers.py` to support filtering by category, search, and pagination
- [X] T035 [US1] Create Product DTO in `app/application/products/queries/product_dto.py` for API responses
- [X] T036 [US1] Create Product API endpoints (GET /api/products, POST /api/products, GET /api/products/{id}, PUT /api/products/{id}, DELETE /api/products/{id}) in `app/api/products.py` (extend existing)
- [X] T037 [US1] Create Category API endpoints (GET /api/categories, POST /api/categories, PUT /api/categories/{id}, DELETE /api/categories/{id}) in `app/api/products.py`
- [X] T038 [US1] Create frontend route handler for products list in `app/routes/products_routes.py` (GET /products)
- [X] T039 [US1] Create frontend route handler for product form (new/edit) in `app/routes/products_routes.py` (GET /products/new, GET /products/{id}/edit, POST /products)
- [X] T040 [US1] Convert design file `design/03-products-list.html` to Jinja2 template `app/templates/products/list.html` with i18n and RTL support
- [X] T041 [US1] Convert design file `design/04-product-form.html` to Jinja2 template `app/templates/products/form.html` with i18n and RTL support
- [X] T042 [US1] Create Product import/export service in `app/services/import_export.py` for Excel/CSV import/export
- [X] T043 [US1] Create Product import API endpoint (POST /api/products/import) in `app/api/products.py`
- [X] T044 [US1] Create Product export API endpoint (GET /api/products/export) in `app/api/products.py`
- [X] T045 [US1] Add locale parameter support to Product API endpoints in `app/api/products.py`
- [X] T046 [US1] Add translated error messages and validation messages to Product API responses in `app/api/products.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can create, update, search, filter, import, and export products.

---

## Phase 4: User Story 2 - Manage Customer Information (Priority: P1)

**Goal**: Enable users to create and maintain customer records for both B2B and B2C customers, including addresses, contacts, and commercial conditions.

**Independent Test**: Create B2B and B2C customers, add multiple addresses and contacts, set commercial conditions, and view customer history. Verify customers can be created, updated, and managed independently of other modules.

### Implementation for User Story 2

- [X] T047 [P] [US2] Create Address domain model in `app/domain/models/customer.py` with type (billing/delivery) and default flags
- [X] T048 [P] [US2] Create Contact domain model in `app/domain/models/customer.py` with role and permission flags
- [X] T049 [P] [US2] Create CommercialConditions domain model in `app/domain/models/customer.py` with payment terms, credit limit, and price list
- [X] T050 [US2] Extend existing Customer model in `app/domain/models/customer.py` with B2B/B2C fields, addresses, contacts, and commercial conditions relationships
- [X] T051 [US2] Create Customer commands (CreateCustomerCommand, UpdateCustomerCommand, ArchiveCustomerCommand) in `app/application/customers/commands/commands.py` (extend existing)
- [X] T052 [US2] Extend Customer command handlers in `app/application/customers/commands/handlers.py` to support B2B/B2C validation, addresses, contacts, and commercial conditions
- [X] T053 [US2] Create Address commands (CreateAddressCommand, UpdateAddressCommand, DeleteAddressCommand) in `app/application/customers/commands/commands.py`
- [X] T054 [US2] Create Address command handlers in `app/application/customers/commands/handlers.py`
- [X] T055 [US2] Create Contact commands (CreateContactCommand, UpdateContactCommand, DeleteContactCommand) in `app/application/customers/commands/commands.py`
- [X] T056 [US2] Create Contact command handlers in `app/application/customers/commands/handlers.py`
- [X] T057 [US2] Create Customer queries (ListCustomersQuery, GetCustomerByIdQuery, SearchCustomersQuery, GetCustomerHistoryQuery) in `app/application/customers/queries/queries.py` (extend existing)
- [X] T058 [US2] Extend Customer query handlers in `app/application/customers/queries/handlers.py` to support filtering by type, search, and customer history
- [X] T059 [US2] Create Customer DTO in `app/application/customers/queries/customer_dto.py` for API responses
- [X] T060 [US2] Create Customer API endpoints (GET /api/customers, POST /api/customers, GET /api/customers/{id}, PUT /api/customers/{id}) in `app/api/customers.py` (extend existing)
- [X] T061 [US2] Create Address API endpoints (GET /api/customers/{id}/addresses, POST /api/customers/{id}/addresses, PUT /api/customers/{id}/addresses/{address_id}, DELETE /api/customers/{id}/addresses/{address_id}) in `app/api/customers.py`
- [X] T062 [US2] Create Contact API endpoints (GET /api/customers/{id}/contacts, POST /api/customers/{id}/contacts, PUT /api/customers/{id}/contacts/{contact_id}, DELETE /api/customers/{id}/contacts/{contact_id}) in `app/api/customers.py`
- [X] T063 [US2] Create frontend route handler for customers list in `app/routes/customers_routes.py` (GET /customers)
- [X] T064 [US2] Create frontend route handler for customer form (new/edit) in `app/routes/customers_routes.py` (GET /customers/new, GET /customers/{id}/edit, POST /customers)
- [X] T065 [US2] Convert design file `design/05-customers-list.html` to Jinja2 template `app/templates/customers/list.html` with i18n and RTL support
- [X] T066 [US2] Convert design file `design/06-customer-form.html` to Jinja2 template `app/templates/customers/form.html` with i18n and RTL support
- [~] T067 [US2] Create Customer import/export service methods in `app/services/import_export.py` for Excel/CSV import/export (API endpoints created, service methods TODO)
- [X] T068 [US2] Create Customer import API endpoint (POST /api/customers/import) in `app/api/customers.py`
- [X] T069 [US2] Create Customer export API endpoint (GET /api/customers/export) in `app/api/customers.py`
- [X] T070 [US2] Add locale parameter support to Customer API endpoints in `app/api/customers.py`
- [X] T071 [US2] Add translated error messages and validation messages to Customer API responses in `app/api/customers.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can manage products and customers.

---

## Phase 5: User Story 3 - Track Inventory in Real-Time (Priority: P1)

**Goal**: Enable warehouse users to view current stock levels, record stock movements, and receive alerts when stock falls below minimum levels.

**Independent Test**: View stock levels, record manual stock movements, transfer stock between locations, and verify that stock reservations are reflected in available quantities. Verify stock tracking works independently of sales modules.

### Implementation for User Story 3

- [ ] T072 [P] [US3] Create Location domain model in `app/domain/models/stock.py` with hierarchical structure (warehouse, zone, aisle, shelf, level)
- [ ] T073 [P] [US3] Create StockItem domain model in `app/domain/models/stock.py` with physical_quantity, reserved_quantity, available_quantity, and business logic methods (reserve, release, adjust, is_below_minimum)
- [ ] T074 [P] [US3] Create StockMovement domain model in `app/domain/models/stock.py` with types (entry, exit, transfer, adjustment) and validation
- [ ] T075 [US3] Create Stock commands (CreateStockMovementCommand, CreateLocationCommand, UpdateLocationCommand) in `app/application/stock/commands/commands.py`
- [ ] T076 [US3] Create Stock command handlers in `app/application/stock/commands/handlers.py` with transaction management and row-level locking for stock operations
- [ ] T077 [US3] Create Stock queries (GetStockLevelsQuery, GetStockAlertsQuery, GetStockMovementsQuery, GetLocationHierarchyQuery) in `app/application/stock/queries/queries.py`
- [ ] T078 [US3] Create Stock query handlers in `app/application/stock/queries/handlers.py`
- [ ] T079 [US3] Create Stock DTO in `app/application/stock/queries/stock_dto.py` for API responses
- [ ] T080 [US3] Create Stock service in `app/services/stock_service.py` for stock reservation, movement validation, and stock level calculations
- [ ] T081 [US3] Create Stock API endpoints (GET /api/stock, GET /api/stock/alerts, POST /api/stock/movements, GET /api/stock/movements) in `app/api/stock.py`
- [ ] T082 [US3] Create Location API endpoints (GET /api/locations, POST /api/locations, PUT /api/locations/{id}) in `app/api/stock.py`
- [ ] T083 [US3] Create frontend route handler for stock management in `app/routes/stock_routes.py` (GET /stock)
- [ ] T084 [US3] Convert design file `design/07-stock.html` to Jinja2 template `app/templates/stock/index.html` with i18n and RTL support
- [ ] T085 [US3] Add real-time stock level updates via AJAX in `app/static/js/main.js` for stock dashboard
- [ ] T086 [US3] Add locale parameter support to Stock API endpoints in `app/api/stock.py`
- [ ] T087 [US3] Add translated error messages and validation messages to Stock API responses in `app/api/stock.py`

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Users can manage products, customers, and track inventory.

---

## Phase 6: User Story 4 - Create and Manage Quotes (Priority: P2)

**Goal**: Enable commercial users to create professional quotes for customers, send them via email, track their status, and convert accepted quotes into orders.

**Independent Test**: Create a quote with products, calculate totals automatically, generate a PDF, send it to a customer, track status changes, and convert an accepted quote to an order. Verify quotes can be created and managed independently.

### Implementation for User Story 4

- [x] T088 [P] [US4] Create Quote domain model in `app/domain/models/quote.py` with status workflow (draft, sent, accepted, rejected, expired, canceled) and business logic methods (calculate_totals, send, accept, reject, expire, create_version, can_convert_to_order)
- [x] T089 [P] [US4] Create QuoteLine domain model in `app/domain/models/quote.py` with quantity, unit_price, discounts, and calculated totals
- [x] T090 [P] [US4] Create QuoteVersion domain model in `app/domain/models/quote.py` for version history
- [x] T091 [US4] Create Quote commands (CreateQuoteCommand, UpdateQuoteCommand, SendQuoteCommand, AcceptQuoteCommand, RejectQuoteCommand, ConvertQuoteToOrderCommand) in `app/application/sales/quotes/commands/commands.py`
- [x] T092 [US4] Create Quote command handlers in `app/application/sales/quotes/commands/handlers.py` with validation and state transitions
- [x] T093 [US4] Create Quote queries (ListQuotesQuery, GetQuoteByIdQuery, GetQuoteHistoryQuery) in `app/application/sales/quotes/queries/queries.py`
- [x] T094 [US4] Create Quote query handlers in `app/application/sales/quotes/queries/handlers.py`
- [x] T095 [US4] Create Quote DTO in `app/application/sales/quotes/queries/quote_dto.py` for API responses
- [x] T096 [US4] Create Pricing service in `app/services/pricing_service.py` for price calculation and discount application
- [x] T097 [US4] Create PDF service in `app/services/pdf_service.py` for generating quote PDFs using ReportLab (migrated from WeasyPrint for Windows compatibility)
- [x] T098 [US4] Create Quote PDF template in `app/pdf_templates/quote.html` with Jinja2 for quote document generation (Note: ReportLab uses programmatic generation, template kept for reference)
- [x] T099 [US4] Create Celery task for sending quote emails in `app/tasks/email_tasks.py`
- [x] T100 [US4] Create Quote API endpoints (GET /api/sales/quotes, POST /api/sales/quotes, GET /api/sales/quotes/{id}, PUT /api/sales/quotes/{id}, POST /api/sales/quotes/{id}/send, POST /api/sales/quotes/{id}/convert-to-order, GET /api/sales/quotes/{id}/history) in `app/api/sales.py`
- [x] T101 [US4] Create frontend route handler for quotes list in `app/routes/sales_routes.py` (GET /quotes)
- [x] T102 [US4] Create frontend route handler for quote form (new/edit) in `app/routes/sales_routes.py` (GET /quotes/new, GET /quotes/{id}/edit, POST /quotes)
- [x] T103 [US4] Add quote list and form templates to `app/templates/sales/` (quotes_list.html, quote_form.html, quote_view.html) with i18n and RTL support
- [x] T104 [US4] Add automatic quote expiration background task in `app/tasks/email_tasks.py` using Celery (expire_quotes_task)
- [x] T105 [US4] Add locale parameter support to Quote API endpoints in `app/api/sales.py`
- [x] T106 [US4] Add translated error messages and validation messages to Quote API responses in `app/api/sales.py`

**Checkpoint**: At this point, User Stories 1-4 should all work independently. Users can manage products, customers, track inventory, and create quotes.

---

## Phase 7: User Story 5 - Create and Fulfill Orders (Priority: P2)

**Goal**: Enable commercial users to create orders (from quotes or manually), validate stock availability and customer credit, reserve stock automatically, and track order fulfillment through various statuses.

**Independent Test**: Create an order, verify stock availability and credit limits, confirm the order (which reserves stock), update order status through fulfillment stages, and cancel an order (which releases reserved stock). Verify orders can be created and managed independently.

### Implementation for User Story 5

- [ ] T107 [P] [US5] Create Order domain model in `app/domain/models/order.py` with status workflow (draft, confirmed, in_preparation, ready, shipped, delivered, invoiced, canceled) and business logic methods (calculate_totals, validate_stock, validate_credit, confirm, cancel, ship, deliver)
- [ ] T108 [P] [US5] Create OrderLine domain model in `app/domain/models/order.py` with quantity, unit_price, discounts, and partial delivery/invoicing support
- [ ] T109 [P] [US5] Create StockReservation domain model in `app/domain/models/order.py` for tracking reserved stock per order line
- [ ] T110 [US5] Create Order commands (CreateOrderCommand, UpdateOrderCommand, ConfirmOrderCommand, CancelOrderCommand, UpdateOrderStatusCommand) in `app/application/sales/orders/commands/commands.py`
- [ ] T111 [US5] Create Order command handlers in `app/application/sales/orders/commands/handlers.py` with stock validation, credit validation, stock reservation/release, and state transitions
- [ ] T112 [US5] Create Order queries (ListOrdersQuery, GetOrderByIdQuery, GetOrderHistoryQuery) in `app/application/sales/orders/queries/queries.py`
- [ ] T113 [US5] Create Order query handlers in `app/application/sales/orders/queries/handlers.py`
- [ ] T114 [US5] Create Order DTO in `app/application/sales/orders/queries/order_dto.py` for API responses
- [ ] T115 [US5] Extend Stock service in `app/services/stock_service.py` with order stock reservation and release methods
- [ ] T116 [US5] Create Credit validation service in `app/services/credit_service.py` for customer credit limit checking
- [ ] T117 [US5] Create Order PDF template in `app/pdf_templates/order.html` with Jinja2 for order document generation
- [ ] T118 [US5] Extend PDF service in `app/services/pdf_service.py` for generating order PDFs
- [ ] T119 [US5] Create Order API endpoints (GET /api/sales/orders, POST /api/sales/orders, GET /api/sales/orders/{id}, PUT /api/sales/orders/{id}, POST /api/sales/orders/{id}/confirm, POST /api/sales/orders/{id}/cancel, GET /api/sales/orders/{id}/pdf) in `app/api/sales.py`
- [ ] T120 [US5] Create frontend route handler for orders list in `app/routes/sales_routes.py` (GET /orders)
- [ ] T121 [US5] Create frontend route handler for order form (new/edit) in `app/routes/sales_routes.py` (GET /orders/new, GET /orders/{id}/edit, POST /orders)
- [ ] T122 [US5] Convert design file `design/08-orders-list.html` to Jinja2 template `app/templates/sales/orders_list.html` with i18n and RTL support
- [ ] T123 [US5] Convert design file `design/09-order-form.html` to Jinja2 template `app/templates/sales/order_form.html` with i18n and RTL support
- [ ] T124 [US5] Add locale parameter support to Order API endpoints in `app/api/sales.py`
- [ ] T125 [US5] Add translated error messages and validation messages to Order API responses in `app/api/sales.py`

**Checkpoint**: At this point, User Stories 1-5 should all work independently. Users can manage products, customers, track inventory, create quotes, and create orders.

---

## Phase 8: User Story 6 - View Business Dashboard with KPIs (Priority: P2)

**Goal**: Enable managers to view key business metrics and KPIs on a dashboard to monitor sales performance, stock status, and operational health in real-time.

**Independent Test**: View the dashboard and verify that KPIs (revenue, stock alerts, active orders) are displayed correctly, update in real-time, and can be filtered by time periods. Verify dashboard works independently and aggregates data from other modules.

### Implementation for User Story 6

- [ ] T126 [US6] Create Dashboard queries (GetKPIsQuery, GetRevenueQuery, GetStockAlertsQuery, GetActiveOrdersQuery) in `app/application/dashboard/queries/queries.py`
- [ ] T127 [US6] Create Dashboard query handlers in `app/application/dashboard/queries/handlers.py` with aggregation logic for revenue, stock alerts, and order counts
- [ ] T128 [US6] Create Dashboard DTO in `app/application/dashboard/queries/dashboard_dto.py` for API responses
- [ ] T129 [US6] Create Dashboard API endpoints (GET /api/dashboard/kpi) in `app/api/dashboard.py` with time period filtering
- [ ] T130 [US6] Create frontend route handler for dashboard in `app/routes/dashboard_routes.py` (GET /dashboard)
- [ ] T131 [US6] Convert design file `design/02-dashboard.html` to Jinja2 template `app/templates/dashboard/index.html` with i18n and RTL support
- [ ] T132 [US6] Add real-time dashboard updates via AJAX in `app/static/js/main.js` for KPI refresh
- [ ] T133 [US6] Add locale parameter support to Dashboard API endpoints in `app/api/dashboard.py`
- [ ] T134 [US6] Add translated labels and messages to Dashboard API responses in `app/api/dashboard.py`

**Checkpoint**: At this point, all User Stories 1-6 should be complete and functional. The MVP is ready for validation.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T135 [P] Create login page template `app/templates/auth/login.html` converted from `design/01-login.html` with i18n and RTL support
- [ ] T136 [P] Create frontend route handler for login in `app/routes/auth_routes.py` (GET /login, POST /login)
- [ ] T137 [P] Create index page route handler in `app/routes/__init__.py` (GET /) that redirects to dashboard or login
- [ ] T138 [P] Extract and translate all template strings using Flask-Babel extract command
- [ ] T139 [P] Translate French messages in `app/translations/fr/LC_MESSAGES/messages.po`
- [ ] T140 [P] Translate Arabic messages in `app/translations/ar/LC_MESSAGES/messages.po`
- [ ] T141 [P] Compile translations using Flask-Babel compile command
- [ ] T142 [P] Add error handling middleware in `app/utils/errors.py` for consistent error responses
- [ ] T143 [P] Add request logging middleware in `app/utils/logging.py` for audit trail
- [ ] T144 [P] Add API documentation comments to all API endpoints following OpenAPI spec
- [ ] T145 [P] Create API documentation endpoint (GET /api/docs) using Flask-Swagger or similar
- [ ] T146 [P] Add input validation decorators in `app/utils/validators.py` for common validations
- [ ] T147 [P] Add pagination utilities in `app/utils/pagination.py` for consistent pagination across endpoints
- [ ] T148 [P] Add search utilities in `app/utils/search.py` for consistent search functionality
- [ ] T149 [P] Create database indexes as specified in data-model.md for performance optimization
- [ ] T150 [P] Add database connection pooling configuration in `app/config.py`
- [ ] T151 [P] Add Celery task monitoring and error handling in `app/tasks/__init__.py`
- [ ] T152 [P] Add comprehensive logging configuration in `app/config.py` for production readiness
- [ ] T153 [P] Create deployment documentation in `docs/deployment.md`
- [ ] T154 [P] Run quickstart.md validation to ensure all setup steps work correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Depends on User Story 1 (products exist for stock tracking)
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Depends on User Stories 1 and 2 (products and customers needed for quotes)
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - Depends on User Stories 1, 2, and 3 (products, customers, and stock needed for orders)
- **User Story 6 (P2)**: Can start after Foundational (Phase 2) - Depends on User Stories 1-5 (aggregates data from all modules)

### Within Each User Story

- Models before services
- Services before endpoints
- Domain models before application layer
- Application layer before API/routes
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, User Stories 1 and 2 can start in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members (with coordination)
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task: "Create Category domain model in app/domain/models/category.py"
Task: "Create ProductCategory junction table model in app/domain/models/product.py"
Task: "Create ProductVariant domain model in app/domain/models/product.py"

# Launch all API endpoints together (after models and handlers are done):
Task: "Create Product API endpoints in app/api/products.py"
Task: "Create Category API endpoints in app/api/products.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Manage Product Catalog)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Add User Story 6 → Test independently → Deploy/Demo
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Products)
   - Developer B: User Story 2 (Customers)
   - Developer C: User Story 3 (Stock) - after US1 complete
3. After US1-3 complete:
   - Developer A: User Story 4 (Quotes)
   - Developer B: User Story 5 (Orders)
   - Developer C: User Story 6 (Dashboard)
4. Stories complete and integrate independently

---

## Task Summary

- **Total Tasks**: 154
- **Setup Tasks**: 10 (Phase 1)
- **Foundational Tasks**: 14 (Phase 2)
- **User Story 1 Tasks**: 22 (Phase 3)
- **User Story 2 Tasks**: 25 (Phase 4)
- **User Story 3 Tasks**: 16 (Phase 5)
- **User Story 4 Tasks**: 19 (Phase 6)
- **User Story 5 Tasks**: 19 (Phase 7)
- **User Story 6 Tasks**: 9 (Phase 8)
- **Polish Tasks**: 20 (Phase 9)

### Parallel Opportunities Identified

- **Phase 1**: 9 parallel tasks
- **Phase 2**: 13 parallel tasks
- **Phase 3**: Multiple model creation tasks can run in parallel
- **Phase 4**: Multiple model creation tasks can run in parallel
- **Phase 5**: Multiple model creation tasks can run in parallel
- **Phase 6**: Multiple model creation tasks can run in parallel
- **Phase 7**: Multiple model creation tasks can run in parallel
- **Phase 9**: 20 parallel tasks

### Independent Test Criteria

- **User Story 1**: Create products, categorize, search, filter, import/export - all without other modules
- **User Story 2**: Create B2B/B2C customers, add addresses/contacts, set conditions - all without other modules
- **User Story 3**: View stock, record movements, transfer stock - requires products but independent of sales
- **User Story 4**: Create quotes, send, track status, convert to order - requires products and customers
- **User Story 5**: Create orders, validate stock/credit, reserve stock, track fulfillment - requires products, customers, and stock
- **User Story 6**: View dashboard KPIs - aggregates data from all modules but can work with mock data

### Suggested MVP Scope

**Minimum Viable Product**: User Story 1 (Manage Product Catalog) only
- Enables product data management
- Provides immediate value
- Can be extended incrementally

**Extended MVP**: User Stories 1, 2, and 3
- Products + Customers + Stock
- Enables complete inventory management
- Foundation for sales operations

**Full MVP**: All User Stories 1-6
- Complete commercial management system
- All core functionality
- Ready for production use

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (if tests are included)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All file paths are relative to repository root
- Follow existing CQRS pattern and code structure
- Maintain consistency with existing Product and Customer implementations
- Ensure all templates support i18n (French/Arabic) and RTL for Arabic
- All API endpoints must support locale parameter and return meta.locale/meta.direction

