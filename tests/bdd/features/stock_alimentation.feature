Feature: Alimentation Automatique du Stock
  As a warehouse user
  I want the stock to be automatically updated when purchase orders are received
  So that inventory levels are always accurate without manual intervention

  Background:
    Given the system has a warehouse location "Entrepôt Principal" with code "WH-001"
    And the system has a supplier "Fournisseur Test" with email "test@supplier.fr"
    And the system has a product "PROD-001" with name "Produit Test" and price "100.00"
    And the system has a user "admin" with role "admin"

  Scenario: Alimentation automatique du stock lors de la réception complète d'une commande
    Given a purchase order "PO-001" exists for supplier "Fournisseur Test" with status "confirmed"
    And the purchase order "PO-001" has a line with product "PROD-001" and quantity "100"
    When I mark the purchase order line as received with quantity "100"
    Then the purchase order status should be "received"
    And a stock item should exist for product "PROD-001" at location "WH-001"
    And the stock item should have physical_quantity "100"
    And a stock movement of type "entry" should exist for product "PROD-001" with quantity "100"
    And the stock movement should be linked to purchase order "PO-001"

  Scenario: Alimentation partielle du stock (réception partielle)
    Given a purchase order "PO-002" exists for supplier "Fournisseur Test" with status "confirmed"
    And the purchase order "PO-002" has a line with product "PROD-001" and quantity "100"
    When I mark the purchase order line as received with quantity "50"
    Then the purchase order status should be "partially_received"
    And no stock movement should be created yet
    When I mark the purchase order line as received with quantity "100"
    Then the purchase order status should be "received"
    And a stock movement of type "entry" should exist for product "PROD-001" with quantity "100"
    And the stock item should have physical_quantity "100"

  Scenario: Alimentation du stock avec plusieurs lignes
    Given a purchase order "PO-003" exists for supplier "Fournisseur Test" with status "confirmed"
    And the purchase order "PO-003" has a line with product "PROD-001" and quantity "50"
    And the system has a product "PROD-002" with name "Produit Test 2" and price "200.00"
    And the purchase order "PO-003" has a line with product "PROD-002" and quantity "30"
    When I mark all purchase order lines as received
    Then the purchase order status should be "received"
    And a stock movement should exist for product "PROD-001" with quantity "50"
    And a stock movement should exist for product "PROD-002" with quantity "30"
    And the stock item for product "PROD-001" should have physical_quantity "50"
    And the stock item for product "PROD-002" should have physical_quantity "30"

  Scenario: Création automatique de StockItem si n'existe pas
    Given a purchase order "PO-004" exists for supplier "Fournisseur Test" with status "confirmed"
    And the purchase order "PO-004" has a line with product "PROD-001" and quantity "25"
    And no stock item exists for product "PROD-001" at location "WH-001"
    When I mark the purchase order line as received with quantity "25"
    Then a stock item should be created for product "PROD-001" at location "WH-001"
    And the stock item should have physical_quantity "25"
    And a stock movement should exist for product "PROD-001" with quantity "25"

  Scenario: Cumul des quantités lors de plusieurs réceptions
    Given a purchase order "PO-005" exists for supplier "Fournisseur Test" with status "confirmed"
    And the purchase order "PO-005" has a line with product "PROD-001" and quantity "100"
    And a stock item exists for product "PROD-001" at location "WH-001" with physical_quantity "50"
    When I mark the purchase order line as received with quantity "100"
    Then the stock item should have physical_quantity "150"
    And a stock movement should exist for product "PROD-001" with quantity "100"






