# Data Model: Commercial Management MVP

**Date**: 2025-01-27  
**Feature**: Commercial Management MVP System

## Overview

This document defines the data model for the Commercial Management MVP, extending existing Product and Customer models and adding Stock, Sales (Quotes/Orders), and supporting entities.

## Entity Relationships

```
Product ──┬── ProductCategory (many-to-many)
          ├── ProductVariant (one-to-many)
          ├── QuoteLine (one-to-many)
          ├── OrderLine (one-to-many)
          └── StockItem (one-to-many)

Category ──┬── ProductCategory (many-to-many)
           └── Category (self-referential for hierarchy)

Customer ──┬── Address (one-to-many)
           ├── Contact (one-to-many)
           ├── CommercialConditions (one-to-one)
           ├── Quote (one-to-many)
           └── Order (one-to-many)

StockItem ──┬── StockMovement (one-to-many)
            └── Location (many-to-one)

Quote ──┬── QuoteLine (one-to-many)
        └── QuoteVersion (one-to-many)

Order ──┬── OrderLine (one-to-many)
        └── StockReservation (one-to-many)

Location ──┬── StockItem (one-to-many)
           └── Location (self-referential for hierarchy)

User ──┬── StockMovement (one-to-many)
       ├── Quote (one-to-many)
       ├── Order (one-to-many)
       └── AuditLog (one-to-many)
```

## Core Entities

### Product (Extended)

**Table**: `products`  
**Existing**: Yes, extends existing model

**Fields**:
- `id` (Integer, PK)
- `code` (String(50), unique, not null) - Auto-generated if not provided
- `name` (String(200), not null)
- `description` (Text, nullable)
- `price` (Numeric(12,2), not null, default=0) - Selling price
- `cost` (Numeric(12,2), nullable) - Cost price for margin calculation
- `unit_of_measure` (String(20), nullable) - e.g., "piece", "kg", "L"
- `barcode` (String(50), unique, nullable)
- `status` (String(20), not null, default='active') - 'active', 'inactive', 'archived'
- `created_at` (DateTime, not null)
- `updated_at` (DateTime, not null)

**Business Rules**:
- Code must be unique and max 50 characters (FR-003)
- Price and cost must be ≥ 0 (FR-013)
- At least one category required (FR-004)
- Cannot delete if referenced in quotes/orders (FR-005)
- Barcode must be unique if provided (RG-PROD-005)

**Methods** (Domain Logic):
- `create(code, name, description, price, cost, ...)` - Factory method with validation
- `update_details(name, description, price, cost, ...)` - Update with validation
- `archive()` - Set status to 'archived'
- `activate()` - Set status to 'active'
- `can_delete()` - Check if safe to delete (no references)

### Category

**Table**: `categories`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `name` (String(100), not null)
- `code` (String(50), unique, nullable) - Optional category code
- `parent_id` (Integer, FK to categories.id, nullable) - For hierarchical structure
- `description` (Text, nullable)
- `created_at` (DateTime, not null)

**Business Rules**:
- Name required
- Code must be unique if provided
- Parent category must exist if parent_id provided
- Cannot delete if has products assigned

**Relationships**:
- Self-referential: `parent_id` → `categories.id` (hierarchy)
- Many-to-many with Product via `product_categories` junction table

### ProductCategory (Junction Table)

**Table**: `product_categories`  
**Existing**: No, new entity

**Fields**:
- `product_id` (Integer, FK to products.id, PK)
- `category_id` (Integer, FK to categories.id, PK)

**Business Rules**:
- Product must have at least one category (FR-004)

### ProductVariant

**Table**: `product_variants`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `product_id` (Integer, FK to products.id, not null) - Parent product
- `code` (String(50), unique, not null) - Variant code (e.g., "PROD-001-RED-L")
- `name` (String(200), not null) - Variant name (e.g., "Red - Large")
- `attributes` (JSON, nullable) - Variant attributes (color, size, etc.)
- `price` (Numeric(12,2), nullable) - Override price if different from parent
- `cost` (Numeric(12,2), nullable) - Override cost if different from parent
- `barcode` (String(50), unique, nullable)
- `status` (String(20), not null, default='active')
- `created_at` (DateTime, not null)

**Business Rules**:
- Code must be unique
- Parent product must exist
- Price/cost ≥ 0 if provided

### Customer (Extended)

**Table**: `customers`  
**Existing**: Yes, extends existing model

**Fields**:
- `id` (Integer, PK)
- `code` (String(50), unique, not null) - Auto-generated format: CLI-XXXXXX (FR-015)
- `type` (String(20), not null) - 'B2B' or 'B2C' (FR-014)
- `name` (String(200), not null) - Company name (B2B) or Full name (B2C)
- `email` (String(200), unique, not null) - Must be valid email (FR-016)
- `phone` (String(20), nullable)
- `mobile` (String(20), nullable)
- `category` (String(50), nullable) - e.g., 'VIP', 'Standard'
- `status` (String(20), not null, default='active') - 'active', 'inactive', 'archived', 'blocked'
- `notes` (Text, nullable) - Internal notes
- `created_at` (DateTime, not null)
- `updated_at` (DateTime, not null)

**B2B-Specific Fields** (when type='B2B'):
- `company_name` (String(200), not null) - Raison sociale (FR-017)
- `siret` (String(14), unique, nullable) - 14 digits for France (FR-027)
- `vat_number` (String(50), nullable) - TVA intracommunautaire
- `rcs` (String(50), nullable) - RCS number
- `legal_form` (String(50), nullable) - Forme juridique

**B2C-Specific Fields** (when type='B2C'):
- `first_name` (String(100), not null)
- `last_name` (String(100), not null)
- `birth_date` (Date, nullable)

**Business Rules**:
- Email must be unique and valid (FR-016, RG-CLI-001)
- Code auto-generated if not provided (FR-015)
- B2B: company_name required (FR-017, RG-CLI-003)
- B2C: first_name and last_name required
- SIRET must be 14 digits if provided (FR-027, RG-CLI-008)
- At least one billing address required (FR-018, RG-CLI-004)

**Methods**:
- `create(type, name, email, ...)` - Factory method with validation
- `update_details(...)` - Update with validation
- `archive()` - Set status to 'archived'
- `block()` - Set status to 'blocked' (credit limit exceeded)
- `unblock()` - Set status to 'active'

### Address

**Table**: `addresses`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `customer_id` (Integer, FK to customers.id, not null)
- `type` (String(20), not null) - 'billing', 'delivery', 'both'
- `is_default_billing` (Boolean, default=False)
- `is_default_delivery` (Boolean, default=False)
- `street` (String(200), not null)
- `city` (String(100), not null)
- `postal_code` (String(20), not null)
- `country` (String(100), not null, default='France')
- `state` (String(100), nullable)
- `created_at` (DateTime, not null)

**Business Rules**:
- Customer must have at least one billing address (FR-018)
- Only one default billing address per customer
- Only one default delivery address per customer

### Contact

**Table**: `contacts`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `customer_id` (Integer, FK to customers.id, not null)
- `first_name` (String(100), not null)
- `last_name` (String(100), not null)
- `function` (String(100), nullable) - Job title
- `email` (String(200), nullable)
- `phone` (String(20), nullable)
- `mobile` (String(20), nullable)
- `is_primary` (Boolean, default=False)
- `receives_quotes` (Boolean, default=True)
- `receives_invoices` (Boolean, default=False)
- `receives_orders` (Boolean, default=False)
- `created_at` (DateTime, not null)

**Business Rules**:
- At least one contact for B2B customers (recommended)
- Only one primary contact per customer

### CommercialConditions

**Table**: `commercial_conditions`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `customer_id` (Integer, FK to customers.id, unique, not null) - One-to-one
- `payment_terms_days` (Integer, default=30) - 30/60/90 days (FR-021)
- `price_list_id` (Integer, FK to price_lists.id, nullable)
- `default_discount_percent` (Numeric(5,2), default=0) - 0-100% (FR-021, RG-CLI-006)
- `credit_limit` (Numeric(12,2), default=0) - ≥ 0 (FR-021, RG-CLI-005)
- `block_on_credit_exceeded` (Boolean, default=True) - Block orders if limit exceeded (FR-023)
- `created_at` (DateTime, not null)
- `updated_at` (DateTime, not null)

**Business Rules**:
- Credit limit ≥ 0 (RG-CLI-005)
- Default discount 0-100% (RG-CLI-006)
- Payment terms typically 30, 60, or 90 days

**Methods**:
- `check_credit_available()` - Calculate available credit (limit - used)
- `is_credit_exceeded()` - Check if credit limit exceeded

### Location

**Table**: `locations`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `code` (String(50), unique, not null)
- `name` (String(200), not null)
- `type` (String(20), not null) - 'warehouse', 'zone', 'aisle', 'shelf', 'level', 'virtual'
- `parent_id` (Integer, FK to locations.id, nullable) - For hierarchy
- `capacity` (Numeric(12,2), nullable) - Optional capacity limit
- `is_active` (Boolean, default=True)
- `created_at` (DateTime, not null)

**Business Rules**:
- Code must be unique
- Hierarchical structure: warehouse → zone → aisle → shelf → level
- Virtual locations for suppliers/clients

### StockItem

**Table**: `stock_items`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `product_id` (Integer, FK to products.id, not null)
- `variant_id` (Integer, FK to product_variants.id, nullable) - If variant exists
- `location_id` (Integer, FK to locations.id, not null)
- `physical_quantity` (Numeric(12,3), not null, default=0) - Physical stock
- `reserved_quantity` (Numeric(12,3), not null, default=0) - Reserved for orders
- `available_quantity` (Numeric(12,3), computed) - physical - reserved
- `min_stock` (Numeric(12,3), nullable) - Minimum stock threshold (FR-037)
- `max_stock` (Numeric(12,3), nullable) - Maximum stock level
- `reorder_point` (Numeric(12,3), nullable) - Point of reorder
- `reorder_quantity` (Numeric(12,3), nullable) - Quantity to order
- `valuation_method` (String(20), default='standard') - 'standard', 'fifo', 'avco' (FR-040)
- `last_movement_at` (DateTime, nullable)
- `created_at` (DateTime, not null)
- `updated_at` (DateTime, not null)

**Business Rules**:
- Physical quantity ≥ 0 (unless authorized) (RG-STOCK-001)
- Reserved quantity ≤ physical quantity (RG-STOCK-002)
- Available quantity = physical - reserved (calculated)
- Unique constraint: (product_id, variant_id, location_id)

**Methods**:
- `reserve(quantity)` - Reserve stock (with lock)
- `release(quantity)` - Release reserved stock
- `adjust(quantity, reason)` - Adjust physical stock
- `is_below_minimum()` - Check if below min_stock threshold

### StockMovement

**Table**: `stock_movements`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `product_id` (Integer, FK to products.id, not null)
- `variant_id` (Integer, FK to product_variants.id, nullable)
- `location_from_id` (Integer, FK to locations.id, nullable) - For transfers
- `location_to_id` (Integer, FK to locations.id, nullable) - For entries/transfers
- `quantity` (Numeric(12,3), not null) - Positive for entry, negative for exit
- `type` (String(20), not null) - 'entry', 'exit', 'transfer', 'adjustment'
- `reason` (String(200), nullable) - Why movement occurred
- `user_id` (Integer, FK to users.id, not null) - Who performed movement (FR-031)
- `related_document_type` (String(50), nullable) - 'order', 'inventory', 'purchase_order'
- `related_document_id` (Integer, nullable) - Reference to related document
- `created_at` (DateTime, not null)

**Business Rules**:
- Movement requires source OR destination location (RG-STOCK-003)
- Transfer requires both source and destination
- Quantity must match movement type (positive for entry, negative for exit)
- User must exist

### Inventory

**Table**: `inventories`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `code` (String(50), unique, not null) - Inventory reference
- `type` (String(20), not null) - 'full', 'partial'
- `status` (String(20), not null, default='open') - 'open', 'closed'
- `location_id` (Integer, FK to locations.id, nullable) - If partial by location
- `category_id` (Integer, FK to categories.id, nullable) - If partial by category
- `started_by` (Integer, FK to users.id, not null)
- `started_at` (DateTime, not null)
- `closed_by` (Integer, FK to users.id, nullable)
- `closed_at` (DateTime, nullable)
- `notes` (Text, nullable)
- `created_at` (DateTime, not null)

**Business Rules**:
- Cannot close if has open counts
- Products under inventory cannot have movements (RG-STOCK-005)

### InventoryCount

**Table**: `inventory_counts`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `inventory_id` (Integer, FK to inventories.id, not null)
- `product_id` (Integer, FK to products.id, not null)
- `variant_id` (Integer, FK to product_variants.id, nullable)
- `location_id` (Integer, FK to locations.id, not null)
- `system_quantity` (Numeric(12,3), not null) - System stock at count time
- `counted_quantity` (Numeric(12,3), nullable) - Physical count
- `difference` (Numeric(12,3), computed) - counted - system
- `counted_by` (Integer, FK to users.id, nullable)
- `counted_at` (DateTime, nullable)
- `created_at` (DateTime, not null)

**Business Rules**:
- Counted quantity can be null until counted
- Difference calculated when counted
- Adjustment movement generated on inventory close if difference exists

### Quote

**Table**: `quotes`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `number` (String(50), unique, not null) - Format: DEV-YYYY-XXXXX (FR-045)
- `version` (Integer, not null, default=1) - Current version number
- `customer_id` (Integer, FK to customers.id, not null)
- `status` (String(20), not null, default='draft') - 'draft', 'sent', 'accepted', 'rejected', 'expired', 'canceled' (FR-048)
- `valid_until` (Date, not null) - Expiration date (default: created_at + 30 days) (FR-049)
- `subtotal` (Numeric(12,2), not null, default=0) - Subtotal HT
- `tax_amount` (Numeric(12,2), not null, default=0) - Total TVA
- `total` (Numeric(12,2), not null, default=0) - Total TTC
- `discount_percent` (Numeric(5,2), default=0) - Document-level discount
- `discount_amount` (Numeric(12,2), default=0) - Document-level discount amount
- `notes` (Text, nullable) - Customer-facing notes
- `internal_notes` (Text, nullable) - Internal notes
- `sent_at` (DateTime, nullable) - When quote was sent
- `sent_by` (Integer, FK to users.id, nullable) - Who sent quote
- `accepted_at` (DateTime, nullable)
- `created_by` (Integer, FK to users.id, not null)
- `created_at` (DateTime, not null)
- `updated_at` (DateTime, not null)

**Business Rules**:
- Number auto-generated if not provided (FR-045)
- At least one quote line required (FR-046, RG-VENTE-001)
- Valid until must be after creation date (FR-056, RG-VENTE-005)
- Status 'expired' set automatically when valid_until passes (FR-050)
- New version created when editing sent quote (FR-051)
- Can only convert to order if status is 'accepted' (FR-070)

**Methods**:
- `calculate_totals()` - Recalculate subtotal, tax, total
- `send(user_id)` - Change status to 'sent', set sent_at, sent_by
- `accept()` - Change status to 'accepted', set accepted_at
- `reject()` - Change status to 'rejected'
- `expire()` - Change status to 'expired' (automatic)
- `create_version()` - Create new version, increment version number
- `can_convert_to_order()` - Check if status is 'accepted'

### QuoteLine

**Table**: `quote_lines`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `quote_id` (Integer, FK to quotes.id, not null)
- `product_id` (Integer, FK to products.id, not null)
- `variant_id` (Integer, FK to product_variants.id, nullable)
- `quantity` (Numeric(12,3), not null) - Must be > 0 (RG-VENTE-002)
- `unit_price` (Numeric(12,2), not null) - Price per unit (FR-043)
- `discount_percent` (Numeric(5,2), default=0) - Line-level discount (FR-047)
- `discount_amount` (Numeric(12,2), default=0) - Line-level discount amount
- `tax_rate` (Numeric(5,2), default=20.0) - TVA rate (%)
- `line_total_ht` (Numeric(12,2), computed) - (quantity * unit_price) - discount
- `line_total_ttc` (Numeric(12,2), computed) - line_total_ht * (1 + tax_rate/100)
- `sequence` (Integer, not null) - Line order
- `created_at` (DateTime, not null)

**Business Rules**:
- Quantity > 0 (RG-VENTE-002)
- Unit price ≥ 0 (RG-VENTE-003)
- Discount percent ≤ 100% (RG-VENTE-004)
- Line total calculated automatically

### QuoteVersion

**Table**: `quote_versions`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `quote_id` (Integer, FK to quotes.id, not null)
- `version_number` (Integer, not null)
- `data` (JSON, not null) - Snapshot of quote and lines data
- `created_by` (Integer, FK to users.id, not null)
- `created_at` (DateTime, not null)

**Business Rules**:
- Version number must be unique per quote
- Data stored as JSON snapshot for historical reference

### Order

**Table**: `orders`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `number` (String(50), unique, not null) - Format: CMD-YYYY-XXXXX (FR-058)
- `quote_id` (Integer, FK to quotes.id, nullable) - If created from quote
- `customer_id` (Integer, FK to customers.id, not null)
- `status` (String(20), not null, default='draft') - 'draft', 'confirmed', 'in_preparation', 'ready', 'shipped', 'delivered', 'invoiced', 'canceled' (FR-062)
- `delivery_address_id` (Integer, FK to addresses.id, nullable)
- `delivery_date_requested` (Date, nullable) - Requested delivery date (FR-064)
- `delivery_date_promised` (Date, nullable) - Promised delivery date
- `delivery_date_actual` (Date, nullable) - Actual delivery date
- `delivery_instructions` (Text, nullable)
- `subtotal` (Numeric(12,2), not null, default=0)
- `tax_amount` (Numeric(12,2), not null, default=0)
- `total` (Numeric(12,2), not null, default=0)
- `discount_percent` (Numeric(5,2), default=0)
- `discount_amount` (Numeric(12,2), default=0)
- `notes` (Text, nullable)
- `confirmed_at` (DateTime, nullable)
- `confirmed_by` (Integer, FK to users.id, nullable)
- `created_by` (Integer, FK to users.id, not null)
- `created_at` (DateTime, not null)
- `updated_at` (DateTime, not null)

**Business Rules**:
- Number auto-generated if not provided (FR-058)
- At least one order line required
- Stock availability validated before confirmation (FR-059)
- Customer credit limit validated before confirmation (FR-060)
- Stock automatically reserved on confirmation (FR-061)
- Stock automatically released on cancellation (FR-067)
- Can only convert from quote if quote status is 'accepted' (FR-070)
- Discount > 15% requires validation (FR-071, RG-VENTE-010)

**Methods**:
- `calculate_totals()` - Recalculate subtotals and totals
- `validate_stock()` - Check stock availability for all lines
- `validate_credit()` - Check customer credit limit
- `confirm(user_id)` - Change status to 'confirmed', reserve stock, set confirmed_at
- `cancel()` - Change status to 'canceled', release reserved stock
- `ship()` - Change status to 'shipped'
- `deliver()` - Change status to 'delivered', set delivery_date_actual

### OrderLine

**Table**: `order_lines`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `order_id` (Integer, FK to orders.id, not null)
- `product_id` (Integer, FK to products.id, not null)
- `variant_id` (Integer, FK to product_variants.id, nullable)
- `quantity` (Numeric(12,3), not null) - Must be > 0
- `unit_price` (Numeric(12,2), not null)
- `discount_percent` (Numeric(5,2), default=0)
- `discount_amount` (Numeric(12,2), default=0)
- `tax_rate` (Numeric(5,2), default=20.0)
- `line_total_ht` (Numeric(12,2), computed)
- `line_total_ttc` (Numeric(12,2), computed)
- `quantity_delivered` (Numeric(12,3), default=0) - For partial deliveries (FR-063)
- `quantity_invoiced` (Numeric(12,3), default=0) - For partial invoicing (FR-063)
- `sequence` (Integer, not null)
- `created_at` (DateTime, not null)

**Business Rules**:
- Quantity > 0
- Unit price ≥ 0
- Quantity delivered ≤ quantity ordered
- Quantity invoiced ≤ quantity delivered

### StockReservation

**Table**: `stock_reservations`  
**Existing**: No, new entity

**Fields**:
- `id` (Integer, PK)
- `order_id` (Integer, FK to orders.id, not null)
- `order_line_id` (Integer, FK to order_lines.id, not null)
- `stock_item_id` (Integer, FK to stock_items.id, not null)
- `quantity` (Numeric(12,3), not null) - Reserved quantity
- `status` (String(20), not null, default='reserved') - 'reserved', 'fulfilled', 'released'
- `reserved_at` (DateTime, not null)
- `released_at` (DateTime, nullable)
- `created_at` (DateTime, not null)

**Business Rules**:
- Quantity must be ≤ available stock at reservation time
- Reservation created on order confirmation
- Reservation released on order cancellation
- Status 'fulfilled' when stock actually moved

### User (Extended)

**Table**: `users`  
**Existing**: Yes, existing entity (extend)

**Fields**:
- `id` (Integer, PK)
- `email` (String, unique, not null)
- `password_hash` (String, not null)
- `first_name` (String(100), nullable)
- `last_name` (String(100), nullable)
- `role` (String(20), not null) - 'admin', 'direction', 'commercial', 'magasinier'
- `locale` (String(5), default='fr') - User's preferred language: 'fr' or 'ar' (NEW for i18n)
- `is_active` (Boolean, default=True)
- `last_login` (DateTime, nullable)
- `created_at` (DateTime, not null)
- `updated_at` (DateTime, not null)

**Business Rules**:
- Email must be unique and valid
- Locale must be 'fr' or 'ar' (default: 'fr')
- Role must be one of: admin, direction, commercial, magasinier

**Methods**:
- `update_locale(locale)` - Update user's preferred language
- `has_permission(permission)` - Check if user has specific permission

## Validation Rules Summary

### Product Validation
- Code: unique, max 50 chars, required
- Price/Cost: ≥ 0
- At least one category required
- Cannot delete if referenced

### Customer Validation
- Email: unique, valid format, required
- Code: auto-generated CLI-XXXXXX format
- B2B: company_name required
- B2C: first_name, last_name required
- At least one billing address required
- SIRET: 14 digits if provided

### Stock Validation
- Physical quantity ≥ 0
- Reserved ≤ physical
- Available = physical - reserved
- Movement requires source or destination location
- Transfer requires both locations

### Quote Validation
- At least one line required
- Valid until > creation date
- Discount ≤ 100%
- Status transitions validated

### Order Validation
- At least one line required
- Stock availability checked
- Credit limit checked (if enabled)
- Discount > 15% requires validation
- Status transitions validated

## Indexes

**Performance Optimization**:
- `products.code` (unique index)
- `products.name` (for search)
- `customers.email` (unique index)
- `customers.code` (unique index)
- `stock_items(product_id, location_id)` (composite index)
- `quotes.number` (unique index)
- `quotes.customer_id, created_at` (composite index for customer history)
- `orders.number` (unique index)
- `orders.customer_id, created_at` (composite index for customer history)
- `orders.status, created_at` (composite index for dashboard)
- `stock_movements(product_id, created_at)` (for stock history)

## State Machines

### Quote Status Flow
```
draft → sent → accepted → (convert to order)
                ↓
              rejected
                ↓
              expired (automatic)
                ↓
              canceled
```

### Order Status Flow
```
draft → confirmed → in_preparation → ready → shipped → delivered → invoiced
         ↓
       canceled (releases stock)
```

### Stock Movement Types
- **entry**: quantity > 0, location_to required
- **exit**: quantity < 0, location_from required
- **transfer**: location_from and location_to required, quantity absolute value
- **adjustment**: location_to required, quantity can be positive or negative

