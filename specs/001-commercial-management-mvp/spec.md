# Feature Specification: Commercial Management MVP System

**Feature Branch**: `001-commercial-management-mvp`  
**Created**: 2025-01-27  
**Status**: Draft  
**Input**: User description: "Develop a Commercial Management MVP system with product management, customer management, inventory tracking, sales workflow (quotes and orders), and dashboard with KPIs. The system should support B2B and B2C operations, real-time stock tracking, quote-to-order conversion, and provide essential business metrics."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Manage Product Catalog (Priority: P1)

A commercial user needs to create and maintain a complete product catalog with all necessary information to support sales operations. This includes product details, pricing, categories, and variants.

**Why this priority**: Products are the foundation of all commercial operations. Without a product catalog, no sales can be processed. This is the first building block that enables all other functionality.

**Independent Test**: Can be fully tested by creating products with various attributes, categorizing them, setting prices, and searching/filtering the catalog. Delivers immediate value by enabling product data management and visibility.

**Acceptance Scenarios**:

1. **Given** a user with product management permissions, **When** they create a new product with code, name, category, price, and stock information, **Then** the product is saved and appears in the product list
2. **Given** a product exists in the system, **When** a user searches for it by name or code, **Then** the product is found and displayed
3. **Given** a product with multiple categories, **When** a user filters products by category, **Then** only products in that category are displayed
4. **Given** a product is used in a quote or order, **When** a user attempts to delete it, **Then** the system prevents deletion and shows an error message
5. **Given** a user wants to import products, **When** they upload a properly formatted Excel/CSV file, **Then** products are created or updated and a report shows success/error details

---

### User Story 2 - Manage Customer Information (Priority: P1)

A commercial user needs to create and maintain customer records for both B2B (business) and B2C (individual) customers, including contact information, addresses, commercial conditions, and credit management.

**Why this priority**: Customers are essential for sales operations. Without customer data, quotes and orders cannot be created. This enables the sales workflow and customer relationship management.

**Independent Test**: Can be fully tested by creating B2B and B2C customers, adding multiple addresses and contacts, setting commercial conditions, and viewing customer history. Delivers value by centralizing customer data and enabling sales operations.

**Acceptance Scenarios**:

1. **Given** a user with customer management permissions, **When** they create a new B2B customer with company name, SIRET, email, and billing address, **Then** the customer is saved with an auto-generated code and appears in the customer list
2. **Given** a user creates a B2C customer, **When** they provide name, email, and address, **Then** the customer is saved and can be used in sales documents
3. **Given** a customer exists, **When** a user adds multiple delivery addresses, **Then** all addresses are saved and can be selected during order creation
4. **Given** a customer has a credit limit set, **When** their unpaid invoices exceed the limit, **Then** new orders are blocked (if configured) and an alert is shown
5. **Given** a user views a customer profile, **When** they access the history tab, **Then** they see a chronological timeline of all quotes, orders, invoices, and interactions

---

### User Story 3 - Track Inventory in Real-Time (Priority: P1)

A warehouse user needs to view current stock levels, record stock movements (entries, exits, transfers), and receive alerts when stock falls below minimum levels.

**Why this priority**: Inventory tracking is critical for order fulfillment. Without accurate stock information, the system cannot validate orders or reserve stock. This ensures data integrity and operational efficiency.

**Independent Test**: Can be fully tested by viewing stock levels, recording manual stock movements, transferring stock between locations, and verifying that stock reservations are reflected in available quantities. Delivers value by providing real-time visibility into inventory status.

**Acceptance Scenarios**:

1. **Given** products exist with stock quantities, **When** a user views the stock dashboard, **Then** they see current stock levels with color coding (green/orange/red) based on stock status
2. **Given** stock is received from a supplier, **When** a user records a stock entry movement, **Then** the product stock quantity increases and the movement is logged with user, timestamp, and reason
3. **Given** stock needs to be transferred between locations, **When** a user creates a transfer movement, **Then** stock decreases at source location and increases at destination location
4. **Given** a product's stock falls below the minimum threshold, **When** a user views the stock dashboard, **Then** an alert is displayed indicating low stock
5. **Given** stock is reserved for an order, **When** a user views available stock, **Then** they see physical stock, reserved stock, and available stock (physical minus reserved)

---

### User Story 4 - Create and Manage Quotes (Priority: P2)

A commercial user needs to create professional quotes for customers, send them via email, track their status, and convert accepted quotes into orders.

**Why this priority**: Quotes are the first step in the sales process. They enable commercial users to propose products and prices to customers. This workflow is essential for B2B operations and provides a foundation for order management.

**Independent Test**: Can be fully tested by creating a quote with products, calculating totals automatically, generating a PDF, sending it to a customer, tracking status changes, and converting an accepted quote to an order. Delivers value by streamlining the quotation process and improving customer communication.

**Acceptance Scenarios**:

1. **Given** a customer and products exist, **When** a user creates a new quote and adds product lines with quantities and prices, **Then** the quote is saved as draft with automatic calculation of subtotals, taxes, and total
2. **Given** a quote is in draft status, **When** a user finalizes and sends it to the customer, **Then** the quote status changes to "Sent", a PDF is generated and emailed, and the quote gets a version number
3. **Given** a quote has been sent, **When** the customer accepts it, **Then** the quote status changes to "Accepted" and it becomes eligible for conversion to an order
4. **Given** a quote's validity period expires, **When** a user views expired quotes, **Then** the quote status automatically changes to "Expired"
5. **Given** a quote needs modification after being sent, **When** a user edits it, **Then** a new version is created while preserving the original version history

---

### User Story 5 - Create and Fulfill Orders (Priority: P2)

A commercial user needs to create orders (from quotes or manually), validate stock availability and customer credit, reserve stock automatically, and track order fulfillment through various statuses.

**Why this priority**: Orders are the core of commercial operations. They represent committed sales and trigger stock reservations. This enables order fulfillment and provides visibility into sales pipeline.

**Independent Test**: Can be fully tested by creating an order, verifying stock availability and credit limits, confirming the order (which reserves stock), updating order status through fulfillment stages, and canceling an order (which releases reserved stock). Delivers value by managing the complete order lifecycle.

**Acceptance Scenarios**:

1. **Given** an accepted quote exists, **When** a user converts it to an order, **Then** an order is created with all quote lines, stock availability is checked, stock is automatically reserved, and order status is set to "Confirmed"
2. **Given** a user creates an order manually, **When** they add products and confirm, **Then** the system validates stock availability, checks customer credit limit, reserves stock if available, and creates the order
3. **Given** an order is confirmed, **When** stock is insufficient for one or more lines, **Then** the system shows an alert but allows order creation with partial stock reservation
4. **Given** an order is in "Confirmed" status, **When** warehouse staff updates status to "In Preparation", **Then** the status changes and the order appears in preparation queue
5. **Given** an order needs to be canceled, **When** a user cancels it, **Then** all reserved stock is automatically released and becomes available again

---

### User Story 6 - View Business Dashboard with KPIs (Priority: P2)

A manager needs to view key business metrics and KPIs on a dashboard to monitor sales performance, stock status, and operational health in real-time.

**Why this priority**: The dashboard provides visibility into business performance and helps decision-making. While not required for core operations, it delivers significant value by enabling management oversight and identifying issues quickly.

**Independent Test**: Can be fully tested by viewing the dashboard and verifying that KPIs (revenue, stock alerts, active orders) are displayed correctly, update in real-time, and can be filtered by time periods. Delivers value by providing at-a-glance business intelligence.

**Acceptance Scenarios**:

1. **Given** a user with dashboard access, **When** they view the dashboard, **Then** they see key metrics including daily/monthly/annual revenue, number of low stock alerts, and count of orders in progress
2. **Given** sales transactions occur, **When** a user refreshes the dashboard, **Then** revenue metrics update to reflect the latest transactions
3. **Given** stock levels change, **When** a user views the dashboard, **Then** the low stock alerts section updates to show current products below minimum thresholds
4. **Given** orders are created or status changes, **When** a user views the dashboard, **Then** the orders in progress count reflects current active orders
5. **Given** a user wants to see historical trends, **When** they select a different time period (week/month/year), **Then** all dashboard metrics update to show data for the selected period

---

### Edge Cases

- What happens when a user tries to create an order for a product that has zero stock?
- How does the system handle concurrent stock reservations for the same product?
- What happens when a quote is converted to an order but stock has been depleted since the quote was created?
- How does the system handle a customer whose credit limit is exceeded during order creation?
- What happens when a product is deleted but is referenced in existing quotes or orders?
- How does the system handle quote expiration when converting to an order?
- What happens when stock movements are recorded for products that don't exist?
- How does the system handle invalid email addresses when sending quotes?
- What happens when multiple users modify the same customer record simultaneously?
- How does the system handle products with negative stock (if allowed by configuration)?

## Requirements *(mandatory)*

### Functional Requirements

#### Product Management

- **FR-001**: System MUST allow users to create products with unique code, name, description, category, price, cost, unit of measure, and status
- **FR-002**: System MUST automatically generate unique product codes when not provided by user
- **FR-003**: System MUST enforce that product codes are unique and maximum 50 characters
- **FR-004**: System MUST allow products to be assigned to one or more categories
- **FR-005**: System MUST prevent deletion of products that are referenced in quotes or orders
- **FR-006**: System MUST allow users to search products by name, code, or description
- **FR-007**: System MUST allow users to filter products by category, price range, stock status, and active/inactive status
- **FR-008**: System MUST support product variants (parent product with multiple variants like size, color)
- **FR-009**: System MUST allow import of products from Excel/CSV files with validation and error reporting
- **FR-010**: System MUST allow export of product catalog to Excel/CSV format
- **FR-011**: System MUST maintain price history when product prices are updated
- **FR-012**: System MUST support multiple price lists per product
- **FR-013**: System MUST validate that product prices and costs are non-negative numbers

#### Customer Management

- **FR-014**: System MUST allow users to create customers of type B2B (business) or B2C (individual)
- **FR-015**: System MUST automatically generate unique customer codes in format CLI-XXXXXX
- **FR-016**: System MUST require unique and valid email addresses for all customers
- **FR-017**: System MUST require company name (reason sociale) for B2B customers
- **FR-018**: System MUST require at least one billing address for each customer
- **FR-019**: System MUST allow multiple delivery addresses per customer
- **FR-020**: System MUST allow multiple contacts per customer with roles and permissions
- **FR-021**: System MUST allow setting commercial conditions per customer (payment terms, price list, default discount, credit limit)
- **FR-022**: System MUST track and display customer credit used (unpaid invoices) and available credit
- **FR-023**: System MUST allow blocking new orders when customer credit limit is exceeded (configurable per customer)
- **FR-024**: System MUST display customer history including all quotes, orders, invoices, and interactions in chronological timeline
- **FR-025**: System MUST calculate and display customer statistics (total revenue, current year revenue, average order value, purchase frequency)
- **FR-026**: System MUST allow import of customers from Excel/CSV files
- **FR-027**: System MUST validate SIRET numbers for French B2B customers (14 digits)
- **FR-028**: System MUST allow deactivating or archiving customers without deleting them

#### Inventory Management

- **FR-029**: System MUST display real-time stock levels per product showing physical stock, reserved stock, and available stock
- **FR-030**: System MUST allow recording stock movements of types: entry, exit, transfer, and adjustment
- **FR-031**: System MUST track who, when, and why for each stock movement
- **FR-032**: System MUST support hierarchical location structure (warehouse, zone, aisle, shelf, level)
- **FR-033**: System MUST automatically reserve stock when an order is confirmed
- **FR-034**: System MUST automatically release reserved stock when an order is canceled
- **FR-035**: System MUST prevent stock from going negative unless explicitly authorized
- **FR-036**: System MUST ensure reserved stock does not exceed physical stock
- **FR-037**: System MUST allow setting minimum stock, maximum stock, and reorder point per product
- **FR-038**: System MUST generate alerts when stock falls below minimum threshold
- **FR-039**: System MUST support inventory counts (full or partial) with comparison to system stock and generation of adjustment movements
- **FR-040**: System MUST support stock valuation methods: Standard (fixed), AVCO (weighted average), and FIFO (first in, first out)
- **FR-041**: System MUST block stock movements for products that are being inventoried
- **FR-042**: System MUST validate that transfer movements have sufficient stock at source location

#### Sales Management - Quotes

- **FR-043**: System MUST allow creating quotes with customer, products, quantities, prices, and discounts
- **FR-044**: System MUST automatically calculate quote totals (subtotal, taxes, total) based on line items
- **FR-045**: System MUST automatically generate quote numbers in format DEV-YYYY-XXXXX
- **FR-046**: System MUST require at least one product line in a quote
- **FR-047**: System MUST support line-level and document-level discounts
- **FR-048**: System MUST support quote statuses: Draft, Sent, Accepted, Rejected, Expired, Canceled
- **FR-049**: System MUST automatically set quote expiration date (default 30 days from creation, configurable)
- **FR-050**: System MUST automatically change quote status to "Expired" when validity period passes
- **FR-051**: System MUST create new version when editing a quote that has been sent
- **FR-052**: System MUST maintain version history for quotes
- **FR-053**: System MUST generate professional PDF documents for quotes
- **FR-054**: System MUST allow sending quote PDFs via email to customers
- **FR-055**: System MUST validate that discount percentages do not exceed 100%
- **FR-056**: System MUST validate that quote expiration date is after quote creation date

#### Sales Management - Orders

- **FR-057**: System MUST allow creating orders from accepted quotes or manually
- **FR-058**: System MUST automatically generate order numbers in format CMD-YYYY-XXXXX
- **FR-059**: System MUST validate stock availability before confirming an order
- **FR-060**: System MUST validate customer credit limit before confirming an order (if credit checking is enabled)
- **FR-061**: System MUST automatically reserve stock when an order is confirmed
- **FR-062**: System MUST support order statuses: Draft, Confirmed, In Preparation, Ready, Shipped, Delivered, Invoiced, Canceled
- **FR-063**: System MUST allow partial deliveries and partial invoicing
- **FR-064**: System MUST track delivery dates (requested, promised, actual)
- **FR-065**: System MUST allow selecting delivery address from customer's address list
- **FR-066**: System MUST generate delivery notes (bon de livraison) as PDF documents
- **FR-067**: System MUST automatically release reserved stock when an order is canceled
- **FR-068**: System MUST show alerts when creating orders with insufficient stock
- **FR-069**: System MUST show alerts when customer credit limit would be exceeded
- **FR-070**: System MUST only allow converting quotes to orders if quote status is "Accepted"
- **FR-071**: System MUST require validation for discounts exceeding 15% (configurable threshold)

#### Dashboard

- **FR-072**: System MUST display daily revenue on the dashboard
- **FR-073**: System MUST display monthly revenue on the dashboard
- **FR-074**: System MUST display annual revenue on the dashboard
- **FR-075**: System MUST display count of products with stock below minimum threshold
- **FR-076**: System MUST display count of orders currently in progress (not completed or canceled)
- **FR-077**: System MUST update dashboard metrics in real-time as transactions occur
- **FR-078**: System MUST allow filtering dashboard metrics by time period (day, week, month, year, custom range)

### Key Entities *(include if feature involves data)*

- **Product**: Represents a sellable item with code, name, description, categories, prices, cost, stock information, images, and status. Can have variants (size, color, etc.). Related to categories, stock movements, and order/quote lines.

- **Customer**: Represents a buyer (B2B business or B2C individual) with contact information, addresses, commercial conditions (payment terms, credit limit, price list, discounts), and relationship history. Related to quotes, orders, invoices, and addresses/contacts.

- **Category**: Represents product classification in hierarchical structure. Related to products.

- **Address**: Represents a physical location for billing or delivery. Belongs to a customer and can be used in quotes and orders.

- **Contact**: Represents a person associated with a customer (for B2B). Has role, email, phone, and permissions. Belongs to a customer.

- **Quote**: Represents a sales proposal with customer, quote lines (products, quantities, prices), totals, status, validity period, and version history. Can be converted to an order.

- **Order**: Represents a confirmed sale with customer, order lines (products, quantities, prices), delivery information, status, and stock reservations. Created from quotes or manually.

- **Stock Movement**: Represents a change in inventory (entry, exit, transfer, adjustment) with product, quantity, location, user, timestamp, reason, and related document reference.

- **Location**: Represents a physical storage location in hierarchical structure (warehouse → zone → aisle → shelf → level). Related to stock movements and inventory.

- **Stock Level**: Represents current inventory status per product per location with physical quantity, reserved quantity, and available quantity (calculated).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a complete product record (with all required fields) in under 2 minutes
- **SC-002**: Users can create a customer record (B2B or B2C) with addresses and contacts in under 3 minutes
- **SC-003**: Stock levels update and reflect reservations within 5 seconds of order confirmation
- **SC-004**: Users can create a quote with 10 product lines and generate PDF in under 5 minutes
- **SC-005**: Quote-to-order conversion completes successfully in under 30 seconds including stock validation and reservation
- **SC-006**: Dashboard displays current metrics and updates within 10 seconds of page load
- **SC-007**: Product search returns results for 10,000 products in under 1 second
- **SC-008**: System supports 50 concurrent users performing typical operations without performance degradation
- **SC-009**: 95% of quote PDFs generate successfully on first attempt
- **SC-010**: Stock movement recording completes in under 2 seconds including validation and stock level updates
- **SC-011**: Customer credit limit validation occurs in real-time (under 1 second) during order creation
- **SC-012**: 90% of users successfully complete their primary task (create quote, create order, view stock) on first attempt without training
- **SC-013**: System maintains data integrity with zero stock discrepancies between reserved and available quantities
- **SC-014**: Import of 1,000 products from Excel file completes with validation and error reporting in under 2 minutes
