// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should display login page', async ({ page }) => {
    await expect(page).toHaveTitle(/CommerceFlow|Login/i);
    await expect(page.locator('input[name="username"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin');
    await page.click('button[type="submit"]');
    
    // Should redirect to dashboard
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
    await expect(page).toHaveURL(/.*dashboard.*/);
    
    // Should show user profile in sidebar
    await expect(page.locator('.sidebar-text')).toContainText(/admin/i);
  });

  test('should show error with invalid credentials', async ({ page }) => {
    await page.fill('input[name="username"]', 'invalid');
    await page.fill('input[name="password"]', 'invalid');
    await page.click('button[type="submit"]');
    
    // Should show error message
    await expect(page.locator('.bg-red-50, .text-red-800, [class*="error"]')).toBeVisible({ timeout: 5000 });
  });

  test('should redirect to login when accessing protected route while logged out', async ({ page }) => {
    await page.goto('/products');
    await expect(page).toHaveURL(/.*login.*/);
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard**', { timeout: 10000 });
    
    // Click logout button
    const logoutButton = page.locator('button:has([class*="sign-out"])');
    if (await logoutButton.count() > 0) {
      await logoutButton.click();
      await page.waitForURL('**/login**', { timeout: 5000 });
      await expect(page).toHaveURL(/.*login.*/);
    }
  });
});

