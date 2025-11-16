// Helper function for authentication in tests
const { test } = require('@playwright/test');

/**
 * Login helper function
 */
async function login(page) {
  await page.goto('/login');
  await page.fill('input[name="username"]', 'admin');
  await page.fill('input[name="password"]', 'admin');
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard**', { timeout: 10000 });
  await page.waitForSelector('.sidebar-text', { timeout: 5000 });
}

module.exports = { login };


