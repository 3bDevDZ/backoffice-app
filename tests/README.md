# Testing Guide

This directory contains unit tests and BDD (Behavior-Driven Development) tests for the Commercial Management MVP.

## Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_product_handlers.py
│   ├── test_domain_event_handlers.py
│   └── test_domain_events.py
├── bdd/                     # BDD tests (Behave)
│   ├── features/
│   │   └── product_management.feature
│   ├── steps/
│   │   └── product_steps.py
│   └── environment.py
├── conftest.py              # Pytest fixtures
└── README.md
```

## Running Tests

### Unit Tests

Run all unit tests:
```bash
pytest tests/unit/
```

Run with coverage:
```bash
pytest tests/unit/ --cov=app --cov-report=html
```

Run specific test file:
```bash
pytest tests/unit/test_product_handlers.py
```

Run specific test:
```bash
pytest tests/unit/test_product_handlers.py::TestCreateProductHandler::test_create_product_success
```

### BDD Tests

Run all BDD tests:
```bash
behave tests/bdd/features/
```

Run specific feature:
```bash
behave tests/bdd/features/product_management.feature
```

Run with verbose output:
```bash
behave tests/bdd/features/ -v
```

## Test Coverage

The tests cover:

### Unit Tests
- **Command Handlers**: Create, Update, Archive, Delete operations
- **Domain Event Handlers**: Event mapping, outbox saving, internal logic
- **Domain Events**: Event infrastructure, aggregate root behavior

### BDD Tests
- **Product Management**: End-to-end scenarios for product CRUD operations
- **Domain Events**: Verification of event raising
- **Integration Events**: Verification of outbox saving

## Writing New Tests

### Unit Test Example

```python
def test_my_feature(db_session):
    """Test description."""
    # Arrange
    handler = MyHandler()
    command = MyCommand(param="value")
    
    # Act
    result = handler.handle(command)
    
    # Assert
    assert result is not None
    assert result.field == "expected_value"
```

### BDD Feature Example

```gherkin
Feature: My Feature
  Scenario: Do something
    Given some precondition
    When I perform an action
    Then the result should be expected
```

## Test Fixtures

Available fixtures in `conftest.py`:
- `db_session`: In-memory SQLite database session
- `sample_category`: Pre-created category for testing
- `sample_product`: Pre-created product for testing

## Notes

- Unit tests use in-memory SQLite for fast execution
- BDD tests also use in-memory SQLite
- All tests are isolated and can run in parallel
- Domain events are tested for proper raising and handling
- Integration events are verified to be saved to outbox

