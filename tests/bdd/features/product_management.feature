Feature: Product Management
  As a commercial user
  I want to manage products in the catalog
  So that I can track and sell products

  Background:
    Given the system has a category "Electronics" with code "ELEC-001"

  Scenario: Create a new product successfully
    Given I am logged in as a commercial user
    When I create a product with:
      | code      | name           | price | category_ids |
      | PROD-001  | Laptop Dell    | 999.99| [1]          |
    Then the product should be created successfully
    And the product should have status "active"
    And a domain event "ProductCreatedDomainEvent" should be raised
    And an integration event should be saved to outbox

  Scenario: Create product without category fails
    Given I am logged in as a commercial user
    When I create a product with:
      | code      | name           | price | category_ids |
      | PROD-002  | Laptop Dell    | 999.99| []            |
    Then the creation should fail with error "Product must have at least one category"

  Scenario: Update product details
    Given I am logged in as a commercial user
    And a product "PROD-001" exists with name "Laptop Dell" and price "999.99"
    When I update product "PROD-001" with:
      | name           | price  |
      | Laptop Dell XPS| 1299.99|
    Then the product should be updated successfully
    And the product name should be "Laptop Dell XPS"
    And the product price should be "1299.99"
    And a domain event "ProductUpdatedDomainEvent" should be raised

  Scenario: Archive a product
    Given I am logged in as a commercial user
    And a product "PROD-001" exists with status "active"
    When I archive product "PROD-001"
    Then the product status should be "archived"
    And a domain event "ProductArchivedDomainEvent" should be raised

  Scenario: Delete a product
    Given I am logged in as a commercial user
    And a product "PROD-001" exists
    When I delete product "PROD-001"
    Then the product should be deleted from the system

