# Playwright E2E Tests for GMFlow

This directory contains end-to-end tests for the GMFlow frontend using Playwright.

## Setup

1. Install Node.js dependencies:
```bash
npm install
```

2. Install Playwright browsers:
```bash
npx playwright install
```

## Running Tests

### Run all tests:
```bash
npm test
```

### Run tests in UI mode:
```bash
npm run test:ui
```

### Run tests in headed mode (see browser):
```bash
npm run test:headed
```

### Run tests in debug mode:
```bash
npm run test:debug
```

### Run specific test file:
```bash
npx playwright test tests/e2e/products.spec.js
```

### View test report:
```bash
npm run test:report
```

## Test Structure

- `auth.spec.js` - Authentication tests (login, logout)
- `dashboard.spec.js` - Dashboard navigation and sidebar
- `products.spec.js` - Products module (CRUD, filters, pagination)
- `customers.spec.js` - Customers module (CRUD, filters, pagination)
- `suppliers.spec.js` - Suppliers module (CRUD, filters, pagination)
- `purchase-orders.spec.js` - Purchase Orders module (CRUD, filters, pagination, actions)
- `quotes.spec.js` - Quotes module (CRUD, filters, pagination, convert)
- `sales-orders.spec.js` - Sales Orders module (CRUD, filters, pagination, actions)
- `stock.spec.js` - Stock, Locations, Movements, and Alerts modules
- `global.spec.js` - Global features (flash messages, language switching, responsive)

## Configuration

Tests are configured in `playwright.config.js`. The base URL is set to `http://localhost:5000` by default, but can be overridden with the `BASE_URL` environment variable.

## Test Reports

After running tests, reports are generated in:
- HTML report: `playwright-report/index.html`
- JSON results: `playwright-report/results.json`

View the HTML report with:
```bash
npm run test:report
```

