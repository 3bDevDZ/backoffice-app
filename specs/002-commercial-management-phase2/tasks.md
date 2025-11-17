# Tasks: Commercial Management Phase 2 System

**Input**: Design documents from `/specs/002-commercial-management-phase2/`  
**Prerequisites**: Phase 1 (MVP) must be complete - all User Stories 1-6 implemented  
**Dependencies**: Orders must support "Delivered" status, Stock module must be functional

**Tests**: Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US7, US8, US9, US10, US11)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `app/` at repository root
- Paths shown below assume Flask application structure per plan.md

---

## Phase 0: User Story 12 - Advanced Product Management (Priority: P1) 🔴 CRITICAL

**Goal**: Complete product management functionality by adding variant UI, price history, price lists, volume pricing, promotional pricing, and automatic cost updates after purchase receipts.

**Independent Test**: Create product variants via UI, view price history, create price lists, set volume discounts, create promotional prices, receive purchase orders (verify cost updates), and use variants in quotes/orders. Verify all features work independently and integrate with existing product management.

### Implementation for User Story 12

#### Product Variants UI and Validation

- [x] T334 [P] [US12] Create ProductVariant commands (CreateVariantCommand, UpdateVariantCommand, ArchiveVariantCommand) in `app/application/products/variants/commands/commands.py`
- [x] T335 [P] [US12] Create ProductVariant command handlers in `app/application/products/variants/commands/handlers.py` with validation
- [x] T336 [P] [US12] Create ProductVariant queries (ListVariantsQuery, GetVariantByIdQuery, GetVariantsByProductQuery) in `app/application/products/variants/queries/queries.py`
- [x] T337 [P] [US12] Create ProductVariant query handlers in `app/application/products/variants/queries/handlers.py`
- [x] T338 [P] [US12] Create ProductVariant DTO in `app/application/products/variants/queries/variant_dto.py` for API responses
- [x] T339 [US12] Create ProductVariant API endpoints (GET /api/products/{id}/variants, POST /api/products/{id}/variants, GET /api/variants/{id}, PUT /api/variants/{id}, DELETE /api/variants/{id}) in `app/api/products.py`
- [x] T340 [US12] Create frontend route handler for variants list in `app/routes/products_routes.py` (GET /products/{id}/variants)
- [x] T341 [US12] Create frontend route handler for variant form in `app/routes/products_routes.py` (GET /products/{id}/variants/new, GET /variants/{id}/edit, POST /variants)
- [x] T342 [US12] Convert design file to Jinja2 template `app/templates/products/variants_list.html` with i18n and RTL support
- [x] T343 [US12] Convert design file to Jinja2 template `app/templates/products/variant_form.html` with i18n and RTL support
- [x] T344 [US12] Add "Variants" tab to product view page (`app/templates/products/view.html`) with list and add button
- [x] T345 [US12] Add variant selection dropdown in quote form (`app/templates/sales/quote_form.html`) after product selection
- [x] T346 [US12] Add variant selection dropdown in order form (`app/templates/sales/order_form.html`) after product selection
- [x] T347 [US12] Add JavaScript function to load variants when product is selected in quote/order forms
- [x] T348 [US12] Add validation in AddQuoteLineHandler to verify variant belongs to product
- [x] T349 [US12] Add validation in AddOrderLineHandler to verify variant belongs to product
- [x] T350 [US12] Modify AddQuoteLineHandler to use variant price if variant has price override
- [x] T351 [US12] Modify AddOrderLineHandler to use variant price if variant has price override
- [x] T352 [US12] Remove "For future use" comments from StockItem.variant_id and StockMovement.variant_id
- [x] T353 [US12] Update stock queries to support filtering by variant_id
- [x] T354 [US12] Update stock dashboard to display stock by variant

#### Price History

- [x] T355 [P] [US12] Create ProductPriceHistory domain model in `app/domain/models/product.py` with product_id, old_price, new_price, changed_by, changed_at, reason
- [x] T356 [US12] Modify ProductUpdatedDomainEventHandler in `app/application/products/events/product_updated_handler.py` to persist price changes to ProductPriceHistory
- [x] T357 [US12] Create ProductPriceHistory queries (GetPriceHistoryQuery) in `app/application/products/queries/queries.py`
- [x] T358 [US12] Create ProductPriceHistory query handler in `app/application/products/queries/handlers.py`
- [x] T359 [US12] Create ProductPriceHistory DTO in `app/application/products/queries/product_dto.py` for API responses
- [x] T360 [US12] Create ProductPriceHistory API endpoint (GET /api/products/{id}/price-history) in `app/api/products.py`
- [x] T361 [US12] Add "Price History" tab to product view page (`app/templates/products/view.html`) with chronological list

#### Price Lists

- [x] T362 [P] [US12] Create PriceList domain model in `app/domain/models/product.py` with name, description, is_active
- [x] T363 [P] [US12] Create ProductPriceList domain model in `app/domain/models/product.py` with price_list_id, product_id, price
- [x] T364 [US12] Create PriceList commands (CreatePriceListCommand, UpdatePriceListCommand, DeletePriceListCommand) in `app/application/products/pricing/commands/commands.py`
- [x] T365 [US12] Create PriceList command handlers in `app/application/products/pricing/commands/handlers.py`
- [x] T366 [US12] Create ProductPriceList commands (AddProductToPriceListCommand, UpdateProductPriceInListCommand, RemoveProductFromPriceListCommand) in `app/application/products/pricing/commands/commands.py`
- [x] T367 [US12] Create ProductPriceList command handlers in `app/application/products/pricing/commands/handlers.py`
- [x] T368 [US12] Create PriceList queries (ListPriceListsQuery, GetPriceListByIdQuery) in `app/application/products/pricing/queries/queries.py`
- [x] T369 [US12] Create PriceList query handlers in `app/application/products/pricing/queries/handlers.py`
- [x] T370 [US12] Create PriceList DTO in `app/application/products/pricing/queries/pricing_dto.py` for API responses
- [x] T371 [US12] Modify PricingService.get_price_for_customer() to check customer's price_list_id and use ProductPriceList price if exists
- [x] T372 [US12] Create PriceList API endpoints (GET /api/price-lists, POST /api/price-lists, GET /api/price-lists/{id}, PUT /api/price-lists/{id}, DELETE /api/price-lists/{id}) in `app/api/products.py`
- [x] T373 [US12] Create ProductPriceList API endpoints (GET /api/price-lists/{id}/products, POST /api/price-lists/{id}/products, PUT /api/price-lists/{id}/products/{product_id}, DELETE /api/price-lists/{id}/products/{product_id}) in `app/api/products.py`
- [x] T374 [US12] Create frontend route handler for price lists list in `app/routes/products_routes.py` (GET /price-lists)
- [x] T375 [US12] Create frontend route handler for price list form in `app/routes/products_routes.py` (GET /price-lists/new, GET /price-lists/{id}/edit, POST /price-lists)
- [x] T376 [US12] Convert design file to Jinja2 template `app/templates/products/price_lists_list.html` with i18n and RTL support
- [x] T377 [US12] Convert design file to Jinja2 template `app/templates/products/price_list_form.html` with i18n and RTL support
- [x] T378 [US12] Add price list selection in customer form (`app/templates/customers/form.html`) in CommercialConditions section

#### Volume Pricing

- [x] T379 [P] [US12] Create ProductVolumePricing domain model in `app/domain/models/product.py` with product_id, min_quantity, max_quantity, price
- [x] T380 [US12] Create ProductVolumePricing commands (CreateVolumePricingCommand, UpdateVolumePricingCommand, DeleteVolumePricingCommand) in `app/application/products/pricing/commands/commands.py`
- [x] T381 [US12] Create ProductVolumePricing command handlers in `app/application/products/pricing/commands/handlers.py`
- [x] T382 [US12] Create ProductVolumePricing queries (GetVolumePricingQuery) in `app/application/products/pricing/queries/queries.py`
- [x] T383 [US12] Create ProductVolumePricing query handler in `app/application/products/pricing/queries/handlers.py`
- [x] T384 [US12] Modify PricingService.get_price_for_customer() to check volume pricing tiers and apply appropriate price based on quantity
- [x] T385 [US12] Create ProductVolumePricing API endpoints (GET /api/products/{id}/volume-pricing, POST /api/products/{id}/volume-pricing, PUT /api/volume-pricing/{id}, DELETE /api/volume-pricing/{id}) in `app/api/products.py`
- [x] T386 [US12] Add "Volume Pricing" section to product form (`app/templates/products/form.html`) with table for quantity tiers

#### Promotional Pricing

- [x] T387 [P] [US12] Create ProductPromotionalPrice domain model in `app/domain/models/product.py` with product_id, price, start_date, end_date, description
- [x] T388 [US12] Create ProductPromotionalPrice commands (CreatePromotionalPriceCommand, UpdatePromotionalPriceCommand, DeletePromotionalPriceCommand) in `app/application/products/pricing/commands/commands.py`
- [x] T389 [US12] Create ProductPromotionalPrice command handlers in `app/application/products/pricing/commands/handlers.py` with date validation
- [x] T390 [US12] Create ProductPromotionalPrice queries (GetActivePromotionalPricesQuery, GetPromotionalPricesByProductQuery) in `app/application/products/pricing/queries/queries.py`
- [x] T391 [US12] Create ProductPromotionalPrice query handler in `app/application/products/pricing/queries/handlers.py`
- [x] T392 [US12] Modify PricingService.get_price_for_customer() to check active promotional prices first (highest priority)
- [x] T393 [US12] Create Celery task to expire promotional prices automatically when end_date passes
- [x] T394 [US12] Create ProductPromotionalPrice API endpoints (GET /api/products/{id}/promotional-prices, POST /api/products/{id}/promotional-prices, PUT /api/promotional-prices/{id}, DELETE /api/promotional-prices/{id}) in `app/api/products.py`
- [x] T395 [US12] Add "Promotional Prices" section to product form (`app/templates/products/form.html`) with table for active/past promotions

#### Automatic Cost Update (CRITICAL)

- [x] T396 [US12] Create ProductCostHistory domain model in `app/domain/models/product.py` with product_id, old_cost, new_cost, changed_by, changed_at, reason, purchase_order_id
- [x] T397 [US12] Modify PurchaseOrderLineReceivedDomainEventHandler in `app/application/purchases/events/purchase_order_line_received_handler.py` to calculate and update product cost using AVCO method
- [x] T398 [US12] Add AVCO calculation logic: `new_cost = (old_cost * old_stock + purchase_price * quantity_received) / new_stock` with edge case handling (old_stock = 0)
- [x] T399 [US12] Persist cost change to ProductCostHistory when cost is updated
- [x] T400 [US12] Create ProductCostHistory queries (GetCostHistoryQuery) in `app/application/products/queries/queries.py`
- [x] T401 [US12] Create ProductCostHistory query handler in `app/application/products/queries/handlers.py`
- [x] T402 [US12] Create ProductCostHistory DTO in `app/application/products/queries/product_dto.py` for API responses
- [x] T403 [US12] Create ProductCostHistory API endpoint (GET /api/products/{id}/cost-history) in `app/api/products.py`
- [x] T404 [US12] Add "Cost History" tab to product view page (`app/templates/products/view.html`) with chronological list

**Checkpoint**: At this point, User Story 12 should be fully functional. Product variants are usable via UI, price history is tracked, price lists work, volume and promotional pricing are applied automatically, and product costs are updated after purchase receipts.

---

## Phase 1: User Story 7 - Generate Legal-Compliant Invoices (Priority: P1)

**Goal**: Enable accountants to generate invoices from delivered orders that comply with French tax legislation, with sequential numbering, credit notes, and automatic email sending.

**Independent Test**: Create invoices from delivered orders, verify sequential numbering without gaps, generate credit notes, send invoices via email, and export FEC files. Verify invoicing works independently and integrates with orders.

### Implementation for User Story 7

- [x] T200 [P] [US7] Create Invoice domain model in `app/domain/models/invoice.py` with status workflow (draft, validated, sent, partially_paid, paid, overdue, canceled) and business logic methods (calculate_totals, validate, send, mark_paid)
- [x] T201 [P] [US7] Create InvoiceLine domain model in `app/domain/models/invoice.py` with quantity, unit_price, tax_rate, discounts, and link to order line
- [x] T202 [P] [US7] Create CreditNote domain model in `app/domain/models/invoice.py` with link to original invoice, reason, and sequential numbering (AV-YYYY-XXXXX)
- [x] T203 [US7] Create InvoiceNumberingService in `app/services/invoice_numbering_service.py` for sequential numbering without gaps (FA-YYYY-XXXXX)
- [x] T204 [US7] Create Invoice commands (CreateInvoiceCommand, ValidateInvoiceCommand, SendInvoiceCommand, CreateCreditNoteCommand) in `app/application/billing/invoices/commands/commands.py`
- [x] T205 [US7] Create Invoice command handlers in `app/application/billing/invoices/commands/handlers.py` with sequential numbering, validation, and state transitions
- [x] T206 [US7] Create Invoice queries (ListInvoicesQuery, GetInvoiceByIdQuery, GetInvoiceHistoryQuery) in `app/application/billing/invoices/queries/queries.py`
- [x] T207 [US7] Create Invoice query handlers in `app/application/billing/invoices/queries/handlers.py`
- [x] T208 [US7] Create Invoice DTO in `app/application/billing/invoices/queries/invoice_dto.py` for API responses
- [x] T209 [US7] Create InvoicePDFService in `app/services/invoice_pdf_service.py` for generating legal-compliant PDF invoices (Article 289 CGI)
- [x] T210 [US7] Create InvoiceEmailService in `app/services/invoice_email_service.py` for sending invoice PDFs via email
- [x] T211 [US7] Create FECExportService in `app/services/fec_export_service.py` for exporting Fichier des Écritures Comptables
- [x] T212 [US7] Create Invoice PDF template in `app/pdf_templates/invoice.html` with Jinja2 for invoice document generation (legal compliance) - Note: Using ReportLab directly instead
- [x] T213 [US7] Create Invoice API endpoints (GET /api/invoices, POST /api/invoices, GET /api/invoices/{id}, POST /api/invoices/{id}/validate, POST /api/invoices/{id}/send, POST /api/invoices/{id}/credit-note, GET /api/invoices/{id}/pdf, GET /api/invoices/fec) in `app/api/billing.py` - Note: Implemented as frontend routes in `app/routes/billing_routes.py` instead
- [x] T214 [US7] Create frontend route handler for invoices list in `app/routes/billing_routes.py` (GET /invoices)
- [x] T215 [US7] Create frontend route handler for invoice view in `app/routes/billing_routes.py` (GET /invoices/{id})
- [x] T216 [US7] Create frontend route handler for invoice actions (validate, send, create credit note) in `app/routes/billing_routes.py` (POST /invoices/{id}/validate, POST /invoices/{id}/send, POST /invoices/{id}/credit-note)
- [x] T217 [US7] Convert design file to Jinja2 template `app/templates/billing/invoices_list.html` with i18n and RTL support
- [x] T218 [US7] Convert design file to Jinja2 template `app/templates/billing/invoice_view.html` with i18n and RTL support
- [x] T219 [US7] Add "Invoice Order" button to order view page (`app/templates/sales/order_view.html`) for delivered orders
- [x] T220 [US7] Add locale parameter support to Invoice API endpoints in `app/api/billing.py` - Note: Implemented in frontend routes with i18n support
- [x] T221 [US7] Add translated error messages and validation messages to Invoice API responses in `app/api/billing.py` - Note: Implemented in frontend routes with Flask-Babel

**Checkpoint**: At this point, User Story 7 should be fully functional. Accountants can create invoices from delivered orders, validate them, send them, create credit notes, and export FEC files.

---

## Phase 2: User Story 8 - Manage Payments and Collections (Priority: P1)

**Goal**: Enable accountants to record customer payments, reconcile bank statements, send automatic payment reminders, and track overdue invoices.

**Independent Test**: Record payments, import bank statements, reconcile payments with invoices, send reminders, and view overdue reports. Verify payment management works independently and integrates with invoices.

### Implementation for User Story 8

- [x] T222 [P] [US8] Create Payment domain model in `app/domain/models/payment.py` with payment_method, amount, date, value_date, and business logic methods
- [x] T223 [P] [US8] Create PaymentAllocation domain model in `app/domain/models/payment.py` for linking payments to invoices (many-to-many with amounts)
- [x] T224 [P] [US8] Create PaymentReminder domain model in `app/domain/models/payment.py` for tracking reminder history
- [x] T225 [US8] Create Payment commands (CreatePaymentCommand, AllocatePaymentCommand, ImportBankStatementCommand, ReconcilePaymentCommand, ConfirmPaymentCommand) in `app/application/billing/payments/commands/commands.py`
- [x] T226 [US8] Create Payment command handlers in `app/application/billing/payments/commands/handlers.py` with allocation logic and credit release
- [x] T227 [US8] Create Payment queries (ListPaymentsQuery, GetPaymentByIdQuery, GetOverdueInvoicesQuery, GetAgingReportQuery) in `app/application/billing/payments/queries/queries.py`
- [x] T228 [US8] Create Payment query handlers in `app/application/billing/payments/queries/handlers.py` with aging calculation
- [x] T229 [US8] Create Payment DTO in `app/application/billing/payments/queries/payment_dto.py` for API responses
- [x] T230 [US8] Create BankReconciliationService in `app/services/bank_reconciliation_service.py` for automatic payment matching
- [x] T231 [US8] Create PaymentReminderService in `app/services/payment_reminder_service.py` for automatic reminder sending
- [x] T232 [US8] Create Celery task for automatic payment reminders in `app/tasks/payment_reminders.py` (J+7, J+15, J+30)
- [x] T233 [US8] Create PaymentReminderEmailService in `app/services/payment_reminder_email_service.py` for sending reminder emails
- [x] T234 [US8] Create PaymentReminderPDFService in `app/services/payment_reminder_pdf_service.py` for generating reminder letters
- [x] T235 [US8] Create Payment API endpoints (GET /api/payments, POST /api/payments, POST /api/payments/import, POST /api/payments/reconcile, GET /api/payments/overdue, GET /api/payments/aging, POST /api/payments/{id}/remind) in `app/api/billing.py` - Note: Implemented as frontend routes instead of API endpoints
- [x] T236 [US8] Create frontend route handler for payments list in `app/routes/billing_routes.py` (GET /payments)
- [x] T237 [US8] Create frontend route handler for payment form in `app/routes/billing_routes.py` (GET /payments/new, POST /payments)
- [x] T238 [US8] Create frontend route handler for bank reconciliation in `app/routes/billing_routes.py` (GET /payments/reconcile, POST /payments/reconcile)
- [x] T239 [US8] Create frontend route handler for overdue invoices in `app/routes/billing_routes.py` (GET /payments/overdue)
- [x] T240 [US8] Convert design file to Jinja2 template `app/templates/billing/payments_list.html` with i18n and RTL support
- [x] T241 [US8] Convert design file to Jinja2 template `app/templates/billing/payment_form.html` with i18n and RTL support
- [x] T242 [US8] Convert design file to Jinja2 template `app/templates/billing/reconciliation.html` with i18n and RTL support
- [x] T243 [US8] Convert design file to Jinja2 template `app/templates/billing/overdue_invoices.html` with i18n and RTL support
- [x] T244 [US8] Add locale parameter support to Payment API endpoints in `app/api/billing.py` - Note: Implemented in frontend routes with Flask-Babel i18n support
- [x] T245 [US8] Add translated error messages and validation messages to Payment API responses in `app/api/billing.py` - Note: Implemented in frontend routes with Flask-Babel
- [x] T245.1 [US8] Create PaymentAutoAllocationService in `app/services/payment_auto_allocation_service.py` with FIFO and proportional allocation strategies
- [x] T245.2 [US8] Add auto_allocation_strategy field to CreatePaymentCommand (None, 'fifo', 'proportional')
- [x] T245.3 [US8] Update CreatePaymentHandler to support automatic allocation when strategy is provided
- [x] T245.4 [US8] Add auto-allocation option checkbox and strategy selector to payment form (`app/templates/billing/payment_form.html`)
- [x] T245.5 [US8] Update payment form route to handle auto_allocation_strategy parameter
- [x] T245.6 [US8] Create payments dashboard route and template (`app/routes/billing_routes.py` GET /payments/dashboard, `app/templates/billing/payments_dashboard.html`) with KPIs and charts
- [x] T245.7 [US8] Fix GetAgingReportHandler and GetOverdueInvoicesHandler to include invoices with status "validated"
- [x] T245.8 [US8] Fix Invoice.mark_paid() to update status to "partially_paid" for both "sent" and "validated" invoices
- [x] T245.9 [US8] Add to_float Jinja2 template filter for Decimal to float conversion in dashboard templates
- [x] T245.10 [US8] Fix JavaScript error in order form (appendChild on null) by removing obsolete product-select code

**Checkpoint**: At this point, User Stories 7 AND 8 should both work independently. Accountants can manage invoices and payments.

---

## Phase 3: User Story 9 - Complete Purchase Cycle Management (Priority: P2)

**Goal**: Enable purchasing managers to manage the complete purchase cycle: create purchase requests (manual or automatic from low stock), convert to purchase orders, receive goods, and process supplier invoices.

**Independent Test**: Create purchase requests, convert to purchase orders, receive goods, process supplier invoices, and verify 3-way matching. Verify purchasing works independently and integrates with stock.

### Implementation for User Story 9

- [ ] T246 [P] [US9] Create PurchaseRequest domain model in `app/domain/models/purchase.py` with status workflow (draft, pending_approval, approved, rejected, converted) and business logic methods
- [ ] T247 [P] [US9] Create PurchaseRequestLine domain model in `app/domain/models/purchase.py` for purchase request line items
- [ ] T248 [P] [US9] Create PurchaseReceipt domain model in `app/domain/models/purchase.py` for tracking goods received
- [ ] T249 [P] [US9] Create PurchaseReceiptLine domain model in `app/domain/models/purchase.py` for receipt line items with quantity discrepancies
- [ ] T250 [P] [US9] Create SupplierInvoice domain model in `app/domain/models/purchase.py` for supplier invoice processing
- [ ] T251 [US9] Extend existing PurchaseOrder model in `app/domain/models/purchase.py` with receipt and invoice relationships
- [ ] T252 [US9] Create PurchaseRequestService in `app/services/purchase_request_service.py` for automatic generation from low stock
- [ ] T253 [US9] Create PurchaseRequest commands (CreatePurchaseRequestCommand, ApprovePurchaseRequestCommand, ConvertPurchaseRequestCommand) in `app/application/purchases/requests/commands/commands.py`
- [ ] T254 [US9] Create PurchaseRequest command handlers in `app/application/purchases/requests/commands/handlers.py` with approval workflow
- [ ] T255 [US9] Create PurchaseReceipt commands (CreatePurchaseReceiptCommand, ValidateReceiptCommand) in `app/application/purchases/receipts/commands/commands.py`
- [ ] T256 [US9] Create PurchaseReceipt command handlers in `app/application/purchases/receipts/commands/handlers.py` with stock movement creation and quantity validation
- [ ] T257 [US9] Create SupplierInvoice commands (CreateSupplierInvoiceCommand, MatchSupplierInvoiceCommand) in `app/application/purchases/invoices/commands/commands.py`
- [ ] T258 [US9] Create SupplierInvoice command handlers in `app/application/purchases/invoices/commands/handlers.py` with 3-way matching logic
- [ ] T259 [US9] Create ThreeWayMatchingService in `app/services/three_way_matching_service.py` for matching PO/Receipt/Invoice
- [ ] T260 [US9] Create PurchaseReceipt queries (ListPurchaseReceiptsQuery, GetPurchaseReceiptByIdQuery) in `app/application/purchases/receipts/queries/queries.py`
- [ ] T261 [US9] Create PurchaseReceipt query handlers in `app/application/purchases/receipts/queries/handlers.py`
- [ ] T262 [US9] Create PurchaseReceipt DTO in `app/application/purchases/receipts/queries/receipt_dto.py` for API responses
- [ ] T263 [US9] Create PurchaseReceiptPDFService in `app/services/purchase_receipt_pdf_service.py` for generating receipt documents
- [ ] T264 [US9] Create PurchaseRequest API endpoints (GET /api/purchase-requests, POST /api/purchase-requests, POST /api/purchase-requests/{id}/approve, POST /api/purchase-requests/{id}/convert) in `app/api/purchases.py`
- [ ] T265 [US9] Create PurchaseReceipt API endpoints (GET /api/purchase-receipts, POST /api/purchase-receipts, POST /api/purchase-receipts/{id}/validate) in `app/api/purchases.py`
- [ ] T266 [US9] Create SupplierInvoice API endpoints (GET /api/supplier-invoices, POST /api/supplier-invoices, POST /api/supplier-invoices/{id}/match) in `app/api/purchases.py`
- [ ] T267 [US9] Create frontend route handler for purchase requests list in `app/routes/purchases_routes.py` (GET /purchase-requests)
- [ ] T268 [US9] Create frontend route handler for purchase request form in `app/routes/purchases_routes.py` (GET /purchase-requests/new, POST /purchase-requests)
- [ ] T269 [US9] Create frontend route handler for purchase receipts in `app/routes/purchases_routes.py` (GET /purchase-receipts, POST /purchase-receipts)
- [ ] T270 [US9] Create frontend route handler for supplier invoices in `app/routes/purchases_routes.py` (GET /supplier-invoices, POST /supplier-invoices)
- [ ] T271 [US9] Convert design file to Jinja2 template `app/templates/purchases/requests_list.html` with i18n and RTL support
- [ ] T272 [US9] Convert design file to Jinja2 template `app/templates/purchases/request_form.html` with i18n and RTL support
- [ ] T273 [US9] Convert design file to Jinja2 template `app/templates/purchases/receipts_list.html` with i18n and RTL support
- [ ] T274 [US9] Convert design file to Jinja2 template `app/templates/purchases/receipt_form.html` with i18n and RTL support
- [ ] T275 [US9] Convert design file to Jinja2 template `app/templates/purchases/supplier_invoices_list.html` with i18n and RTL support
- [ ] T276 [US9] Convert design file to Jinja2 template `app/templates/purchases/supplier_invoice_form.html` with i18n and RTL support
- [ ] T277 [US9] Add "Receive" button to purchase order view page (`app/templates/purchases/orders/view.html`) for confirmed orders
- [ ] T278 [US9] Add locale parameter support to Purchase API endpoints in `app/api/purchases.py`
- [ ] T279 [US9] Add translated error messages and validation messages to Purchase API responses in `app/api/purchases.py`

**Checkpoint**: At this point, User Stories 7-9 should all work independently. Accountants can manage invoices and payments, and purchasing managers can manage the complete purchase cycle.

---

## Phase 4: User Story 10 - Multi-Location Stock Management (Priority: P2)

**Goal**: Enable warehouse managers to manage stock across multiple warehouses/sites, transfer stock between sites, and view consolidated or site-specific stock levels.

**Independent Test**: Create multiple sites, view stock by site, create inter-site transfers, receive transfers, and view consolidated stock. Verify multi-location works independently and integrates with stock.

### Implementation for User Story 10

- [ ] T280 [P] [US10] Create Site domain model in `app/domain/models/stock.py` with name, address, manager, status, and business logic methods
- [ ] T281 [P] [US10] Create StockTransfer domain model in `app/domain/models/stock.py` with source_site, destination_site, status (created, in_transit, received), and business logic methods
- [ ] T282 [P] [US10] Create StockTransferLine domain model in `app/domain/models/stock.py` for transfer line items
- [ ] T283 [US10] Extend existing Location model in `app/domain/models/stock.py` with site_id foreign key
- [ ] T284 [US10] Extend existing StockItem model in `app/domain/models/stock.py` with site_id (if not already present)
- [ ] T285 [US10] Create SiteService in `app/services/site_service.py` for site management
- [ ] T286 [US10] Create StockTransferService in `app/services/stock_transfer_service.py` for transfer creation and processing
- [ ] T287 [US10] Create Site commands (CreateSiteCommand, UpdateSiteCommand, DeactivateSiteCommand) in `app/application/stock/sites/commands/commands.py`
- [ ] T288 [US10] Create Site command handlers in `app/application/stock/sites/commands/handlers.py`
- [ ] T289 [US10] Create StockTransfer commands (CreateStockTransferCommand, ReceiveStockTransferCommand) in `app/application/stock/transfers/commands/commands.py`
- [ ] T290 [US10] Create StockTransfer command handlers in `app/application/stock/transfers/commands/handlers.py` with stock movement creation
- [ ] T291 [US10] Create Site queries (ListSitesQuery, GetSiteByIdQuery, GetSiteStockQuery) in `app/application/stock/sites/queries/queries.py`
- [ ] T292 [US10] Create Site query handlers in `app/application/stock/sites/queries/handlers.py`
- [ ] T293 [US10] Create StockTransfer queries (ListStockTransfersQuery, GetStockTransferByIdQuery) in `app/application/stock/transfers/queries/queries.py`
- [ ] T294 [US10] Create StockTransfer query handlers in `app/application/stock/transfers/queries/handlers.py`
- [ ] T295 [US10] Create GlobalStockQuery in `app/application/stock/queries/queries.py` for consolidated stock view
- [ ] T296 [US10] Create GlobalStock query handler in `app/application/stock/queries/handlers.py` with multi-site aggregation
- [ ] T297 [US10] Create Site DTO in `app/application/stock/sites/queries/site_dto.py` for API responses
- [ ] T298 [US10] Create StockTransfer DTO in `app/application/stock/transfers/queries/transfer_dto.py` for API responses
- [ ] T299 [US10] Create Site API endpoints (GET /api/sites, POST /api/sites, GET /api/sites/{id}, PUT /api/sites/{id}) in `app/api/stock.py`
- [ ] T300 [US10] Create StockTransfer API endpoints (GET /api/stock-transfers, POST /api/stock-transfers, POST /api/stock-transfers/{id}/receive, GET /api/stock-transfers/{id}) in `app/api/stock.py`
- [ ] T301 [US10] Create GlobalStock API endpoint (GET /api/stock/global) in `app/api/stock.py` for consolidated view
- [ ] T302 [US10] Create frontend route handler for sites list in `app/routes/stock_routes.py` (GET /sites)
- [ ] T303 [US10] Create frontend route handler for site form in `app/routes/stock_routes.py` (GET /sites/new, GET /sites/{id}/edit, POST /sites)
- [ ] T304 [US10] Create frontend route handler for stock transfers in `app/routes/stock_routes.py` (GET /stock-transfers, POST /stock-transfers, POST /stock-transfers/{id}/receive)
- [ ] T305 [US10] Convert design file to Jinja2 template `app/templates/stock/sites_list.html` with i18n and RTL support
- [ ] T306 [US10] Convert design file to Jinja2 template `app/templates/stock/site_form.html` with i18n and RTL support
- [ ] T307 [US10] Convert design file to Jinja2 template `app/templates/stock/transfers_list.html` with i18n and RTL support
- [ ] T308 [US10] Convert design file to Jinja2 template `app/templates/stock/transfer_form.html` with i18n and RTL support
- [ ] T309 [US10] Extend stock dashboard (`app/templates/stock/index.html`) with site filter and multi-site view toggle
- [ ] T310 [US10] Add locale parameter support to Site and StockTransfer API endpoints in `app/api/stock.py`
- [ ] T311 [US10] Add translated error messages and validation messages to Site and StockTransfer API responses in `app/api/stock.py`

**Checkpoint**: At this point, User Stories 7-10 should all work independently. Multi-location stock management is functional.

---

## Phase 5: User Story 11 - Advanced Reporting and Analytics (Priority: P2)

**Goal**: Enable managers to generate customizable reports, analyze sales and margins, and view forecasts to make informed business decisions.

**Independent Test**: Create custom reports, view standard reports (sales, margins, stock, customers, purchases), export to Excel/PDF, and view forecasts. Verify reporting works independently and aggregates data from all modules.

### Implementation for User Story 11

- [ ] T312 [P] [US11] Create ReportTemplate domain model in `app/domain/models/report.py` for saving custom report configurations
- [ ] T313 [US11] Create ReportService in `app/services/report_service.py` for generating standard and custom reports
- [ ] T314 [US11] Create AnalyticsService in `app/services/analytics_service.py` for calculating sales, margins, and trends
- [ ] T315 [US11] Create ForecastService in `app/services/forecast_service.py` for generating sales and stock forecasts
- [ ] T316 [US11] Create ReportBuilderService in `app/services/report_builder_service.py` for building custom reports with column selection, filters, and calculated fields
- [ ] T317 [US11] Create ReportExportService in `app/services/report_export_service.py` for exporting reports to Excel, PDF, and CSV
- [ ] T318 [US11] Create Report queries (GetSalesReportQuery, GetMarginReportQuery, GetStockReportQuery, GetCustomerReportQuery, GetPurchaseReportQuery, GetCustomReportQuery) in `app/application/reports/queries/queries.py`
- [ ] T319 [US11] Create Report query handlers in `app/application/reports/queries/handlers.py` with aggregation logic
- [ ] T320 [US11] Create Report DTO in `app/application/reports/queries/report_dto.py` for API responses
- [ ] T321 [US11] Create Report API endpoints (GET /api/reports/sales, GET /api/reports/margins, GET /api/reports/stock, GET /api/reports/customers, GET /api/reports/purchases, GET /api/reports/custom, POST /api/reports/export) in `app/api/reports.py`
- [ ] T322 [US11] Create Forecast API endpoints (GET /api/reports/forecast/sales, GET /api/reports/forecast/stock) in `app/api/reports.py`
- [ ] T323 [US11] Create frontend route handler for reports list in `app/routes/reports_routes.py` (GET /reports)
- [ ] T324 [US11] Create frontend route handler for report builder in `app/routes/reports_routes.py` (GET /reports/builder, POST /reports/builder)
- [ ] T325 [US11] Create frontend route handler for report view in `app/routes/reports_routes.py` (GET /reports/{type}, GET /reports/custom/{id})
- [ ] T326 [US11] Convert design file to Jinja2 template `app/templates/reports/list.html` with i18n and RTL support
- [ ] T327 [US11] Convert design file to Jinja2 template `app/templates/reports/builder.html` with i18n and RTL support
- [ ] T328 [US11] Convert design file to Jinja2 template `app/templates/reports/sales.html` with i18n and RTL support
- [ ] T329 [US11] Convert design file to Jinja2 template `app/templates/reports/margins.html` with i18n and RTL support
- [ ] T330 [US11] Convert design file to Jinja2 template `app/templates/reports/forecast.html` with i18n and RTL support
- [ ] T331 [US11] Add charting library integration (Chart.js or similar) in `app/static/js/reports.js` for visualizations
- [ ] T332 [US11] Add locale parameter support to Report API endpoints in `app/api/reports.py`
- [ ] T333 [US11] Add translated labels and messages to Report API responses in `app/api/reports.py`

**Checkpoint**: At this point, all User Stories 7-11 should be complete and functional. Phase 2 is ready for validation.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (US7 - Invoicing)**: Depends on Phase 1 MVP - Orders must support "Delivered" status
- **Phase 2 (US8 - Payments)**: Depends on Phase 1 (US7) - Requires invoices
- **Phase 3 (US9 - Purchasing)**: Depends on Phase 1 MVP - Requires Stock module and Suppliers
- **Phase 4 (US10 - Multi-Locations)**: Depends on Phase 1 MVP - Requires Stock module
- **Phase 5 (US11 - Reporting)**: Depends on all previous phases - Aggregates data from all modules

### User Story Dependencies

- **User Story 12 (P1)**: Can start immediately - Depends on Phase 1 MVP Products module - **MUST BE DONE FIRST** (blocks proper purchasing)
- **User Story 7 (P1)**: Can start after Phase 1 MVP - Depends on Orders with "Delivered" status
- **User Story 8 (P1)**: Can start after User Story 7 - Depends on Invoices
- **User Story 9 (P2)**: Can start after Phase 1 MVP - Depends on Stock and Suppliers - **BENEFITS FROM US12** (cost updates)
- **User Story 10 (P2)**: Can start after Phase 1 MVP - Depends on Stock
- **User Story 11 (P2)**: Can start after User Stories 7-10 - Depends on all data sources

### Within Each User Story

- Domain models can be created in parallel (marked [P])
- Commands and queries can be created in parallel (marked [P])
- Command handlers depend on domain models
- Query handlers depend on domain models
- API endpoints depend on command/query handlers
- Frontend routes depend on API endpoints
- Templates depend on frontend routes

---

## Summary

**Total Tasks**: 205 tasks (T200-T404)

**By User Story**:
- User Story 12 (Advanced Product Management): 71 tasks (T334-T404) 🔴 CRITICAL
- User Story 7 (Invoicing): 22 tasks (T200-T221)
- User Story 8 (Payments): 24 tasks (T222-T245)
- User Story 9 (Purchasing): 34 tasks (T246-T279)
- User Story 10 (Multi-Locations): 32 tasks (T280-T311)
- User Story 11 (Reporting): 22 tasks (T312-T333)

**Estimated Duration**: 18 weeks (4.5 months) - Extended due to critical product management enhancements

**Priority Order**:
1. **User Story 12 (P1) - Advanced Product Management (3 weeks)** 🔴 CRITICAL - Must be done first
   - Variants UI: 1 week
   - Price History: 0.5 weeks
   - Price Lists: 0.5 weeks
   - Volume/Promotional Pricing: 0.5 weeks
   - Automatic Cost Update: 0.5 weeks
2. User Story 7 (P1) - Invoicing (4 weeks)
3. User Story 8 (P1) - Payments (3 weeks)
4. User Story 9 (P2) - Purchasing (3 weeks)
5. User Story 10 (P2) - Multi-Locations (2 weeks)
6. User Story 11 (P2) - Reporting (3 weeks)
7. Testing & Polish (1 week)

