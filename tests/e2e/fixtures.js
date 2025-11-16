// Helper functions for tests
const { test: baseTest } = require('@playwright/test');
const { login } = require('./auth-helper');

/**
 * Extend test with authenticated page fixture
 */
const test = baseTest.extend({
  authenticatedPage: async ({ page }, use) => {
    await login(page);
    await use(page);
  },
});

module.exports = { test, login };

