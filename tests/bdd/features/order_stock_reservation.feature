# Order Stock Reservation and Delivery Notes - BDD Tests

Feature: Order Stock Reservation and Release
  As a commercial user
  I want to create and manage orders
  So that stock is automatically reserved and released when orders are confirmed or canceled

  Background:
    Given the database is clean
    And a user "admin" exists with role "admin"
    And a customer "CUST-001" exists with name "Test Customer" and type "B2B"
    And a product "PROD-001" exists with name "Test Product" and code "PROD-001"
    And a location "WH-001" exists with code "WH-001" and type "warehouse"
    And a stock item exists for product "PROD-001" at location "WH-001" with physical quantity "100"

  Scenario: Confirm order reserves stock automatically
    Given an order "CMD-2025-00001" exists for customer "CUST-001" with status "draft"
    And the order "CMD-2025-00001" has a line with product "PROD-001" and quantity "50"
    When I confirm the order "CMD-2025-00001"
    Then the order "CMD-2025-00001" status should be "confirmed"
    And the stock item for product "PROD-001" at location "WH-001" should have reserved quantity "50"
    And the stock item for product "PROD-001" at location "WH-001" should have available quantity "50"
    And a stock reservation should exist for order "CMD-2025-00001" with quantity "50"

  Scenario: Cancel order releases reserved stock automatically
    Given an order "CMD-2025-00001" exists for customer "CUST-001" with status "confirmed"
    And the order "CMD-2025-00001" has a line with product "PROD-001" and quantity "50"
    And the order "CMD-2025-00001" has stock reserved
    When I cancel the order "CMD-2025-00001"
    Then the order "CMD-2025-00001" status should be "canceled"
    And the stock item for product "PROD-001" at location "WH-001" should have reserved quantity "0"
    And the stock item for product "PROD-001" at location "WH-001" should have available quantity "100"
    And all stock reservations for order "CMD-2025-00001" should have status "released"

  Scenario: Reserve stock from multiple locations when first location is insufficient
    Given a location "WH-002" exists with code "WH-002" and type "warehouse"
    # Set WH-001 to have only 50 available (to force reservation from multiple locations)
    And a stock item exists for product "PROD-001" at location "WH-001" with physical quantity "50"
    And a stock item exists for product "PROD-001" at location "WH-002" with physical quantity "30"
    And an order "CMD-2025-00001" exists for customer "CUST-001" with status "draft"
    And the order "CMD-2025-00001" has a line with product "PROD-001" and quantity "80"
    When I confirm the order "CMD-2025-00001"
    Then the order "CMD-2025-00001" status should be "confirmed"
    And stock reservations should exist for order "CMD-2025-00001" with total quantity "80"
    # Handler reserves from largest available stock first, so WH-001 (50 available) gets 50, WH-002 (30 available) gets 30
    And the stock item for product "PROD-001" at location "WH-001" should have reserved quantity "50"
    And the stock item for product "PROD-001" at location "WH-002" should have reserved quantity "30"

  Scenario: Cannot confirm order with insufficient stock
    Given an order "CMD-2025-00001" exists for customer "CUST-001" with status "draft"
    And the order "CMD-2025-00001" has a line with product "PROD-001" and quantity "150"
    When I try to confirm the order "CMD-2025-00001"
    Then the order confirmation should fail with stock validation error
    And the order "CMD-2025-00001" status should remain "draft"
    And no stock reservations should exist for order "CMD-2025-00001"

  Scenario: Create order from accepted quote
    Given a quote "DEV-2025-00001" exists for customer "CUST-001" with status "accepted"
    And the quote "DEV-2025-00001" has a line with product "PROD-001" and quantity "30"
    When I create an order from quote "DEV-2025-00001"
    Then an order should be created with quote "DEV-2025-00001"
    And the order should have the same lines as the quote
    And the order status should be "draft"

  Scenario: Order ready triggers delivery note generation event
    Given an order "CMD-2025-00001" exists for customer "CUST-001" with status "in_preparation"
    When I mark the order "CMD-2025-00001" as ready
    Then the order "CMD-2025-00001" status should be "ready"
    And an OrderReadyDomainEvent should be raised

