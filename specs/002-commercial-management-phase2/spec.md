# Feature Specification: Commercial Management Phase 2 System

**Feature Branch**: `002-commercial-management-phase2`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: Cahier des Charges - Phase 2 (Mois 5-8)  
**Prerequisites**: Phase 1 (MVP) must be complete

## Overview

Phase 2 extends the MVP with 5 essential modules for complete commercial management:
1. **Module 6: Invoicing** - Legal-compliant invoice generation
2. **Module 7: Payments** - Payment recording, bank reconciliation, automatic reminders
3. **Module 8: Purchasing** - Complete purchase cycle (requests, orders, receipts, supplier invoices)
4. **Module 9: Multi-Locations** - Multiple warehouses/sites with inter-site transfers
5. **Module 10: Advanced Reporting** - Customizable reports, analytics, and forecasting

**Additionally, Phase 2 includes critical product management enhancements** (identified gaps from Phase 1):
6. **Module 11: Advanced Product Management** - Price history, price lists, volume pricing, promotional pricing, product variants UI, and automatic cost updates

**Duration**: 16 weeks (4 months)  
**Priority**: SHOULD HAVE (after MVP)  
**Module 11 Priority**: P1 (CRITICAL - blocks proper purchasing and pricing)

---

## User Scenarios & Testing *(mandatory)*

### User Story 12 - Advanced Product Management (Priority: P1) 🔴 CRITICAL

A product manager needs to manage product variants with a user interface, track price history, configure multiple price lists, set volume discounts, create promotional prices, and ensure product costs are automatically updated after purchase receipts.

**Why this priority**: These features are critical gaps from Phase 1 that block proper purchasing operations (cost updates) and pricing management (price lists, history). Without these, the system cannot properly track product costs, manage complex pricing, or use product variants effectively.

**Independent Test**: Can be fully tested by creating product variants via UI, viewing price history, creating price lists, setting volume discounts, creating promotional prices, receiving purchase orders (which should update product costs), and using variants in quotes/orders. Delivers immediate value by completing product management functionality and enabling accurate cost tracking.

**Acceptance Scenarios**:

1. **Given** a product exists, **When** a product manager creates a variant via the UI, **Then** the variant is created with code, name, attributes, optional price/cost override, and appears in the variant list
2. **Given** a product has variants, **When** a user creates a quote/order and selects the product, **Then** they can select a variant from a dropdown, the variant name is displayed in the line, and the variant price (if set) is used automatically
3. **Given** a product price is updated, **When** the system processes the update, **Then** the old price is saved to price history with timestamp, user, and reason
4. **Given** a product manager views a product, **When** they access the price history tab, **Then** they see a chronological list of all price changes with old/new values, dates, and reasons
5. **Given** a product manager creates a price list, **When** they assign prices to products in the list, **Then** customers assigned to that price list see those prices instead of standard prices
6. **Given** a product has volume pricing configured, **When** a user adds the product to a quote with quantity 50, **Then** the system automatically applies the price tier for 50 units (e.g., 95€ instead of 100€)
7. **Given** a product has a promotional price valid from 01/01/2025 to 31/01/2025, **When** a user creates a quote on 15/01/2025, **Then** the promotional price is automatically applied
8. **Given** goods are received from a purchase order, **When** the system processes the receipt, **Then** the product cost is automatically updated using AVCO (Average Cost) method: `new_cost = (old_cost * old_stock + purchase_price * quantity_received) / new_stock`
9. **Given** a user selects a variant in a quote/order, **When** the system validates the line, **Then** it verifies that the variant belongs to the selected product and shows an error if not
10. **Given** a product has stock tracked by variant, **When** a user views stock levels, **Then** they see separate stock quantities for each variant at each location

---

### User Story 7 - Generate Legal-Compliant Invoices (Priority: P1)

An accountant needs to generate invoices from delivered orders that comply with French tax legislation (Article 289 CGI), with sequential numbering, credit notes, and automatic email sending.

**Why this priority**: Invoicing is legally required for all sales transactions. Without invoicing, the business cannot operate legally. This enables revenue recognition and payment collection.

**Independent Test**: Can be fully tested by creating invoices from delivered orders, verifying sequential numbering without gaps, generating credit notes, sending invoices via email, and exporting FEC files. Delivers immediate value by enabling legal compliance and payment collection.

**Acceptance Scenarios**:

1. **Given** an order is in "Delivered" status, **When** an accountant creates an invoice from the order, **Then** an invoice is generated with sequential number (FA-YYYY-XXXXX), all order lines are included, and totals are calculated automatically
2. **Given** an invoice is created, **When** an accountant validates it, **Then** the invoice status changes to "Validated", becomes non-modifiable, and a PDF is generated
3. **Given** an invoice needs correction, **When** an accountant creates a credit note (avoir), **Then** a credit note is created with link to original invoice, sequential number (AV-YYYY-XXXXX), and the invoice status changes to "Canceled"
4. **Given** an invoice is validated, **When** the system sends it to the customer, **Then** the invoice PDF is emailed automatically, status changes to "Sent", and the email is logged
5. **Given** invoices exist in the system, **When** an accountant exports FEC (Fichier des Écritures Comptables), **Then** a compliant FEC file is generated with all invoice data for tax authorities

---

### User Story 8 - Manage Payments and Collections (Priority: P1)

An accountant needs to record customer payments, reconcile bank statements, send automatic payment reminders, and track overdue invoices.

**Why this priority**: Payment collection is essential for cash flow. Without payment management, the business cannot track receivables or collect payments efficiently. This enables financial control and reduces bad debt.

**Independent Test**: Can be fully tested by recording payments, importing bank statements, reconciling payments with invoices, sending reminders, and viewing overdue reports. Delivers value by automating payment collection and improving cash flow.

**Acceptance Scenarios**:

1. **Given** an invoice exists with outstanding balance, **When** an accountant records a payment, **Then** the payment is allocated to the invoice, invoice status updates (partially paid/paid), and customer credit is released
2. **Given** a bank statement is available, **When** an accountant imports it, **Then** payments are automatically matched with invoices by amount and reference, and unmatched items are flagged for manual reconciliation
3. **Given** an invoice is overdue (past due date), **When** the system runs the reminder job, **Then** a reminder email is sent (J+7, J+15, J+30), the reminder is logged, and the invoice is marked as "Overdue"
4. **Given** multiple overdue invoices exist, **When** an accountant views the overdue report, **Then** invoices are grouped by aging (0-30, 30-60, 60-90, >90 days) with totals and customer information
5. **Given** a payment is recorded, **When** an accountant views the payment allocation, **Then** they see which invoices were paid, payment method, date, and remaining balance

---

### User Story 9 - Complete Purchase Cycle Management (Priority: P2)

A purchasing manager needs to manage the complete purchase cycle: create purchase requests (manual or automatic from low stock), convert to purchase orders, receive goods, and process supplier invoices.

**Why this priority**: Purchasing is essential for inventory replenishment. Without purchase management, stock cannot be replenished efficiently. This enables cost control and supplier relationship management.

**Independent Test**: Can be fully tested by creating purchase requests, converting to purchase orders, receiving goods, processing supplier invoices, and verifying 3-way matching. Delivers value by streamlining procurement and ensuring cost accuracy.

**Acceptance Scenarios**:

1. **Given** stock falls below minimum threshold, **When** the system generates automatic purchase requests, **Then** purchase requests are created with products, quantities, and suggested suppliers
2. **Given** a purchase request is approved, **When** a purchasing manager converts it to a purchase order, **Then** a purchase order is created with supplier, products, prices, and sent to supplier via email
3. **Given** goods are received from a supplier, **When** warehouse staff records the reception, **Then** stock movements are created automatically, purchase order status updates, and a receipt document is generated
4. **Given** a supplier invoice is received, **When** an accountant processes it, **Then** the system performs 3-way matching (PO/Receipt/Invoice), validates amounts, and creates supplier invoice record
5. **Given** a purchase order has quantity discrepancies, **When** warehouse staff records reception with different quantities, **Then** if discrepancy >10%, validation is required, and adjustments are logged

---

### User Story 10 - Multi-Location Stock Management (Priority: P2)

A warehouse manager needs to manage stock across multiple warehouses/sites, transfer stock between sites, and view consolidated or site-specific stock levels.

**Why this priority**: Multi-location support is essential for businesses with multiple warehouses. Without this, stock cannot be managed across sites, and transfers must be done manually. This enables efficient inventory distribution.

**Independent Test**: Can be fully tested by creating multiple sites, viewing stock by site, creating inter-site transfers, receiving transfers, and viewing consolidated stock. Delivers value by enabling multi-site operations and optimizing inventory distribution.

**Acceptance Scenarios**:

1. **Given** multiple warehouses exist, **When** a warehouse manager views stock for a product, **Then** they see stock levels per site, consolidated total, and can filter by specific site
2. **Given** stock needs to be transferred between sites, **When** a warehouse manager creates a transfer, **Then** stock is reserved at source site, transfer order is created, and status is "In Transit"
3. **Given** a transfer is in transit, **When** destination site receives the transfer, **Then** stock is released at source, added at destination, and transfer status changes to "Received"
4. **Given** a product has stock at multiple sites, **When** a warehouse manager views the global stock dashboard, **Then** they see consolidated quantities, site breakdown, and alerts per site
5. **Given** a transfer is created, **When** source site has insufficient stock, **Then** the system prevents transfer creation and shows an error message

---

### User Story 11 - Advanced Reporting and Analytics (Priority: P2)

A manager needs to generate customizable reports, analyze sales and margins, and view forecasts to make informed business decisions.

**Why this priority**: Advanced reporting provides business intelligence for decision-making. Without analytics, managers cannot identify trends, optimize operations, or forecast future needs. This enables data-driven management.

**Independent Test**: Can be fully tested by creating custom reports, viewing standard reports (sales, margins, stock, customers, purchases), exporting to Excel/PDF, and viewing forecasts. Delivers value by providing actionable insights and business intelligence.

**Acceptance Scenarios**:

1. **Given** a manager wants to analyze sales, **When** they generate a sales report, **Then** they see revenue by period, top products, top customers, and revenue trends with charts
2. **Given** a manager wants to analyze profitability, **When** they generate a margin report, **Then** they see margins by product, by customer, overall margin, and margin trends
3. **Given** a manager wants a custom report, **When** they use the report builder, **Then** they can select columns, apply filters, add calculated fields, save as template, and export to Excel/PDF
4. **Given** historical sales data exists, **When** a manager views sales forecast, **Then** they see predicted sales based on historical trends, confidence intervals, and alerts for deviations
5. **Given** a manager wants to export a report, **When** they select export format (Excel/PDF/CSV), **Then** the report is generated with proper formatting, charts (if applicable), and downloaded

---

## Requirements *(mandatory)*

### Functional Requirements

#### Invoicing

- **FR-079**: System MUST allow creating invoices from delivered orders with automatic line inclusion
- **FR-080**: System MUST generate sequential invoice numbers in format FA-YYYY-XXXXX without gaps (legal requirement)
- **FR-081**: System MUST prevent modification of validated invoices (create credit note for corrections)
- **FR-082**: System MUST support partial invoicing (select specific order lines to invoice)
- **FR-083**: System MUST automatically calculate invoice totals (subtotal, tax, total) from line items
- **FR-084**: System MUST include all legally required information: invoice number, date, due date, seller info (company name, SIRET, VAT, address), buyer info, line details (quantity, unit price, tax), totals, payment terms, late payment penalties, legal mentions
- **FR-085**: System MUST support invoice statuses: Draft, Validated, Sent, Partially Paid, Paid, Overdue, Canceled
- **FR-086**: System MUST allow creating credit notes (avoir) linked to original invoices with sequential numbering (AV-YYYY-XXXXX)
- **FR-087**: System MUST require reason for credit note creation
- **FR-088**: System MUST generate PDF invoices compliant with legal requirements (Article 289 CGI)
- **FR-089**: System MUST automatically send invoice PDFs via email to customers
- **FR-090**: System MUST export FEC (Fichier des Écritures Comptables) for tax authorities
- **FR-091**: System MUST archive invoices for minimum 10 years (legal requirement)
- **FR-092**: System MUST calculate invoice due date based on customer payment terms
- **FR-093**: System MUST validate that invoice date is not in the future
- **FR-094**: System MUST validate that invoiced quantities do not exceed delivered quantities

#### Payments

- **FR-095**: System MUST allow recording payments with payment method (cash, check, wire transfer, credit card, direct debit)
- **FR-096**: System MUST allow allocating payments to one or more invoices (partial payment support)
- **FR-097**: System MUST validate that payment amount does not exceed outstanding invoice balance
- **FR-098**: System MUST validate that payment date is not before invoice date
- **FR-099**: System MUST support payment value date (different from payment date)
- **FR-100**: System MUST allow importing bank statements (CSV, OFX, QIF formats)
- **FR-101**: System MUST automatically match imported payments with invoices by amount and reference
- **FR-102**: System MUST allow manual reconciliation of unmatched payments
- **FR-103**: System MUST support automatic payment reminders at J+7, J+15, J+30 after due date
- **FR-104**: System MUST send reminder emails with customizable templates
- **FR-105**: System MUST generate reminder letters as PDF documents
- **FR-106**: System MUST log all reminder activities (who, when, type)
- **FR-107**: System MUST track overdue invoices grouped by aging: 0-30 days, 30-60 days, 60-90 days, >90 days
- **FR-108**: System MUST display overdue amounts per aging bucket
- **FR-109**: System MUST provide dashboard showing overdue invoices summary
- **FR-110**: System MUST automatically release customer credit when invoice is paid
- **FR-111**: System MUST prevent modification of fully paid invoices

#### Purchasing

- **FR-112**: System MUST allow creating purchase requests manually
- **FR-113**: System MUST automatically generate purchase requests when stock falls below minimum threshold
- **FR-114**: System MUST require approval workflow for purchase requests before conversion to purchase orders
- **FR-115**: System MUST allow converting approved purchase requests to purchase orders
- **FR-116**: System MUST generate purchase order numbers in format BCA-YYYY-XXXXX
- **FR-117**: System MUST allow creating purchase orders directly (without purchase request)
- **FR-118**: System MUST automatically send purchase orders to suppliers via email
- **FR-119**: System MUST support purchase order statuses: Draft, Sent, Confirmed, Partially Received, Received, Invoiced
- **FR-120**: System MUST allow recording partial receipts from purchase orders
- **FR-121**: System MUST validate received quantities against ordered quantities
- **FR-122**: System MUST require validation if receipt quantity discrepancy >10%
- **FR-123**: System MUST automatically create stock entry movements when goods are received
- **FR-124**: System MUST generate receipt documents (bon de réception) as PDF
- **FR-125**: System MUST allow recording supplier invoices
- **FR-126**: System MUST perform 3-way matching: Purchase Order, Receipt, Supplier Invoice
- **FR-127**: System MUST validate that supplier invoice amount does not exceed purchase order amount
- **FR-128**: System MUST update product cost after receipt (if configured)
- **FR-129**: System MUST track supplier payment terms and due dates

#### Multi-Locations

- **FR-130**: System MUST support multiple warehouse/site locations
- **FR-131**: System MUST maintain hierarchical location structure per site: Site → Warehouse → Zone → Aisle → Shelf → Level
- **FR-132**: System MUST store site information (name, address, manager, status)
- **FR-133**: System MUST allow viewing stock consolidated across all sites
- **FR-134**: System MUST allow viewing stock per specific site
- **FR-135**: System MUST allow creating stock transfers between sites
- **FR-136**: System MUST validate that source site has sufficient stock for transfer
- **FR-137**: System MUST reserve stock at source site when transfer is created
- **FR-138**: System MUST create stock exit movement at source and entry movement at destination when transfer is received
- **FR-139**: System MUST support transfer statuses: Created, In Transit, Received
- **FR-140**: System MUST generate transfer orders as documents
- **FR-141**: System MUST provide multi-site stock dashboard showing consolidated and per-site views
- **FR-142**: System MUST generate stock alerts per site

#### Advanced Reporting

- **FR-143**: System MUST provide customizable report builder with column selection, filters, sorting, and grouping
- **FR-144**: System MUST allow saving custom report templates for reuse
- **FR-145**: System MUST support calculated fields in custom reports
- **FR-146**: System MUST export reports to Excel, PDF, and CSV formats
- **FR-147**: System MUST include charts/graphs in exported reports (where applicable)
- **FR-148**: System MUST provide standard sales report with revenue by period, top products, top customers, revenue trends
- **FR-149**: System MUST provide standard margin report with margins by product, by customer, overall margin, margin trends
- **FR-150**: System MUST provide standard stock report with stock value, turnover, slow/fast moving products
- **FR-151**: System MUST provide standard customer report with revenue by customer, purchase frequency, average order value, payment delays
- **FR-152**: System MUST provide standard purchase report with purchases by supplier, price evolution, delivery delays
- **FR-153**: System MUST generate sales forecasts based on historical data
- **FR-154**: System MUST generate stock forecasts (future needs) based on sales trends
- **FR-155**: System MUST display forecast confidence intervals
- **FR-156**: System MUST provide forecast alerts for significant deviations
- **FR-157**: System MUST ensure report generation completes within 5 seconds for standard reports
- **FR-158**: System MUST support report scheduling (future enhancement)

#### Advanced Product Management (US12 - CRITICAL)

- **FR-159**: System MUST allow creating product variants via user interface with code, name, attributes (JSON), optional price/cost override, and barcode
- **FR-160**: System MUST allow editing and archiving product variants via user interface
- **FR-161**: System MUST display product variants in a list view with parent product information
- **FR-162**: System MUST allow selecting product variants in quote/order forms via dropdown after product selection
- **FR-163**: System MUST validate that selected variant belongs to the selected product (variant.product_id == product_id)
- **FR-164**: System MUST automatically use variant price if variant has price override, otherwise use parent product price
- **FR-165**: System MUST display variant name in quote/order lines when variant is selected
- **FR-166**: System MUST track stock separately by variant (StockItem with variant_id)
- **FR-167**: System MUST reserve stock by variant when order is confirmed (StockReservation with variant_id)
- **FR-168**: System MUST persist price history when product price is updated (ProductPriceHistory table)
- **FR-169**: System MUST store price history with old price, new price, changed_by, changed_at, and optional reason
- **FR-170**: System MUST display price history in chronological order with all details
- **FR-171**: System MUST allow creating price lists with name, description, and active status
- **FR-172**: System MUST allow assigning products to price lists with specific prices per product
- **FR-173**: System MUST allow assigning price lists to customers via CommercialConditions
- **FR-174**: System MUST use price list price when customer has price list assigned, otherwise use standard price
- **FR-175**: System MUST allow configuring volume pricing (quantity tiers) per product with price per tier
- **FR-176**: System MUST automatically apply volume pricing based on quantity in quote/order lines
- **FR-177**: System MUST allow creating promotional prices with start date, end date, and price
- **FR-178**: System MUST automatically apply promotional price if current date is within promotion period
- **FR-179**: System MUST prioritize promotional price over volume pricing and price lists
- **FR-180**: System MUST automatically update product cost after purchase order receipt using AVCO (Average Cost) method
- **FR-181**: System MUST calculate AVCO as: `new_cost = (old_cost * old_stock + purchase_price * quantity_received) / new_stock`
- **FR-182**: System MUST handle AVCO calculation when old_stock is zero (use purchase_price directly)
- **FR-183**: System MUST update product cost in PurchaseOrderLineReceivedDomainEventHandler
- **FR-184**: System MUST track cost history when product cost is updated (ProductCostHistory table)
- **FR-185**: System MUST display cost history alongside price history in product view

### Non-Functional Requirements

- **NFR-015**: Invoice generation MUST complete within 2 seconds
- **NFR-016**: Payment reconciliation MUST handle 1000+ transactions per import
- **NFR-017**: Report generation MUST complete within 5 seconds for 12 months of data
- **NFR-018**: System MUST support 10+ warehouse sites simultaneously
- **NFR-019**: Invoice PDFs MUST be compliant with Article 289 CGI (French tax law)
- **NFR-020**: Invoice numbering MUST be sequential without gaps (legal requirement)
- **NFR-021**: Invoices MUST be archived for minimum 10 years
- **NFR-022**: Payment reminders MUST run automatically via background jobs (Celery)
- **NFR-023**: Multi-site stock queries MUST complete within 1 second
- **NFR-024**: Custom reports MUST support up to 50 columns and 20 filters
- **NFR-025**: Price history queries MUST complete within 1 second for products with 1000+ price changes
- **NFR-026**: Cost update after purchase receipt MUST complete within 500ms

### Security Requirements

- **SEC-007**: Only users with "accountant" or "admin" roles can create/validate invoices
- **SEC-008**: Only users with "accountant" or "admin" roles can record payments
- **SEC-009**: Only users with "purchasing" or "admin" roles can create purchase orders
- **SEC-010**: Invoice PDFs MUST be accessible only to authorized users
- **SEC-011**: Payment data MUST be encrypted at rest
- **SEC-012**: All invoice and payment operations MUST be logged for audit
- **SEC-013**: Only users with "admin" or "commercial" roles can create/modify price lists
- **SEC-014**: Only users with "admin" or "commercial" roles can create/modify promotional prices
- **SEC-015**: Price history MUST be read-only (cannot be modified or deleted)

---

## Edge Cases

- What happens when an invoice is created but the order is later canceled?
- How does the system handle invoice numbering if an invoice is deleted?
- What happens when a payment is recorded but the invoice is later canceled?
- How does the system handle bank statement imports with duplicate transactions?
- What happens when a purchase order is received but quantities differ significantly (>10%)?
- How does the system handle stock transfers when source site stock becomes insufficient?
- What happens when a custom report includes calculated fields with division by zero?
- How does the system handle forecast generation with insufficient historical data?
- What happens when multiple users try to validate the same invoice simultaneously?
- How does the system handle invoice creation when customer payment terms are missing?
- What happens when a variant is selected but doesn't belong to the selected product?
- How does the system handle price list conflicts (customer has price list but product not in list)?
- What happens when multiple promotional prices overlap for the same product?
- How does the system handle AVCO calculation when purchase price is zero or negative?
- What happens when a variant is deleted but is referenced in quotes/orders?

---

## Dependencies

### Phase 1 (MVP) Dependencies
- ✅ Module Products (US1)
- ✅ Module Customers (US2)
- ✅ Module Stock (US3)
- ✅ Module Sales - Orders (US5) - Must support "Delivered" status
- ✅ Dashboard (US6)

### External Dependencies
- Email service for invoice/payment reminder sending
- PDF generation library (ReportLab or similar)
- Background job processor (Celery) for automatic reminders
- Excel/CSV export library (openpyxl, pandas)

---

## Success Criteria

- ✅ 100% of Phase 2 functional requirements implemented
- ✅ All invoices comply with Article 289 CGI
- ✅ Invoice numbering is sequential without gaps
- ✅ Payment reconciliation handles 1000+ transactions
- ✅ Reports generate within 5 seconds
- ✅ Multi-site stock queries complete within 1 second
- ✅ Unit test coverage >80%
- ✅ Integration tests pass for all user stories
- ✅ User acceptance tests pass
- ✅ Performance requirements met
- ✅ Security requirements validated

