# Playwright E2E Testing Guide

This document explains how to run Playwright tests for the GMFlow frontend and interpret the results.

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   npx playwright install chromium
   ```

2. **Start the Flask application:**
   ```bash
   python run.py
   ```
   The app should be running on `http://localhost:5000`

3. **Run all tests:**
   ```bash
   npm test
   ```

4. **Generate comprehensive report:**
   ```bash
   npm run test:run-and-report
   ```

## Test Structure

### Modules Tested

1. **Authentication** (`auth.spec.js`)
   - Login with valid/invalid credentials
   - Logout functionality
   - Protected route access

2. **Dashboard** (`dashboard.spec.js`)
   - Dashboard display
   - Sidebar navigation
   - Sidebar toggle functionality

3. **Products** (`products.spec.js`)
   - List display
   - Search filter
   - Category filter
   - Status filter
   - Create new product
   - Edit product
   - View product details
   - Pagination

4. **Customers** (`customers.spec.js`)
   - List display
   - Search filter
   - Type filter (B2B/B2C)
   - Status filter
   - Create new customer
   - Edit customer
   - Pagination

5. **Suppliers** (`suppliers.spec.js`)
   - List display
   - Search filter
   - Create new supplier
   - Edit supplier
   - Pagination

6. **Purchase Orders** (`purchase-orders.spec.js`)
   - List display
   - Search filter
   - Status filter
   - Create new purchase order
   - View purchase order details
   - Confirm purchase order
   - Pagination

7. **Quotes** (`quotes.spec.js`)
   - List display
   - Search filter
   - Status filter
   - Create new quote
   - View quote details
   - Convert quote to order
   - Pagination

8. **Sales Orders** (`sales-orders.spec.js`)
   - List display
   - Search filter
   - Status filter
   - Create new order
   - View order details
   - Confirm order
   - Pagination

9. **Stock** (`stock.spec.js`)
   - Stock levels display
   - Search filter
   - Location filter
   - Minimum quantity filter
   - Pagination
   - Locations/Warehouses CRUD
   - Stock movements display
   - Stock alerts display

10. **Global Features** (`global.spec.js`)
    - Flash messages display
    - Language switching (FR/AR)
    - Responsive sidebar
    - Error handling

## Running Tests

### Run All Tests
```bash
npm test
```

### Run Tests in UI Mode (Interactive)
```bash
npm run test:ui
```

### Run Tests in Headed Mode (See Browser)
```bash
npm run test:headed
```

### Run Tests in Debug Mode
```bash
npm run test:debug
```

### Run Specific Test File
```bash
npx playwright test tests/e2e/products.spec.js
```

### Run Tests for Specific Module
```bash
npx playwright test tests/e2e/products.spec.js --grep "should create"
```

## Test Reports

### HTML Report
After running tests, view the HTML report:
```bash
npm run test:report
```

### Generate Markdown Report
Generate a comprehensive markdown report:
```bash
npm run test:generate-report
```

This creates `TEST_REPORT.md` with:
- Summary statistics
- Test coverage by module
- List of issues found
- Detailed test results
- Recommendations

## Understanding Test Results

### Test Status

- ✅ **Passed**: Test completed successfully
- ❌ **Failed**: Test encountered an error
- ⏭️ **Skipped**: Test was skipped (usually due to missing elements)

### Common Issues

1. **Element Not Found**
   - The selector might be incorrect
   - The element might not exist on the page
   - The page might not have loaded yet

2. **Timeout Errors**
   - The page might be slow to load
   - Network requests might be taking too long
   - Increase timeout in test if needed

3. **Authentication Failures**
   - Check if admin credentials are correct
   - Verify login flow is working

4. **Form Submission Failures**
   - Check if required fields are filled
   - Verify form validation is working
   - Check for JavaScript errors

## Fixing Issues

1. **Review the HTML Report**
   - Open `playwright-report/index.html`
   - Check screenshots and videos of failed tests
   - Review error messages

2. **Check the Markdown Report**
   - Read `TEST_REPORT.md` for a summary
   - Review recommendations

3. **Debug Failed Tests**
   - Run in debug mode: `npm run test:debug`
   - Use UI mode for step-by-step debugging: `npm run test:ui`

4. **Fix Frontend Issues**
   - Update selectors if UI changed
   - Fix JavaScript errors
   - Ensure forms work correctly
   - Verify API endpoints are working

5. **Re-run Tests**
   - After fixes, run tests again
   - Verify all issues are resolved

## Configuration

### Base URL
Default: `http://localhost:5000`

Override with environment variable:
```bash
BASE_URL=http://192.168.100.76:5000 npm test
```

### Browser
Default: Chromium

Change in `playwright.config.js`:
```javascript
projects: [
  {
    name: 'firefox',
    use: { ...devices['Desktop Firefox'] },
  },
]
```

### Timeouts
Default timeouts can be adjusted in `playwright.config.js`:
```javascript
use: {
  actionTimeout: 10000, // 10 seconds
  navigationTimeout: 30000, // 30 seconds
}
```

## Best Practices

1. **Run tests regularly** - Catch issues early
2. **Fix failing tests immediately** - Don't let them accumulate
3. **Update tests when UI changes** - Keep tests in sync with frontend
4. **Use descriptive test names** - Makes it easier to understand failures
5. **Keep tests independent** - Each test should work standalone
6. **Use fixtures** - Reuse authentication and setup code

## Troubleshooting

### Tests fail with "Page not found"
- Ensure Flask app is running on `http://localhost:5000`
- Check `BASE_URL` in `playwright.config.js`

### Tests fail with "Element not found"
- Check if selectors match current HTML
- Verify page has loaded completely
- Check for JavaScript errors in browser console

### Tests are slow
- Reduce `workers` in `playwright.config.js`
- Check network requests in browser DevTools
- Optimize page load times

### Authentication fails
- Verify admin user exists in database
- Check login route is working
- Verify session management

## Next Steps

After running tests and reviewing the report:

1. **Fix Critical Issues** - Address failing tests first
2. **Update Tests** - If UI changes are intentional, update tests
3. **Add More Tests** - Cover edge cases and error scenarios
4. **Monitor Performance** - Track test execution time
5. **CI/CD Integration** - Add tests to continuous integration pipeline

