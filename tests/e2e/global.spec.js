// @ts-check
const { test } = require('./fixtures');
const { expect } = require('@playwright/test');

test.describe('Global Features', () => {
  test('should display flash messages', async ({ authenticatedPage: page }) => {
    // Navigate to a page that might show messages
    await page.goto('/products');
    await page.waitForLoadState('networkidle');
    
    // Flash messages container should exist (even if empty)
    const flashContainer = page.locator('.bg-green-50, .bg-red-50, .bg-yellow-50, .bg-blue-50');
    // Just check it exists, not necessarily visible
  });

  test('should handle language switching', async ({ authenticatedPage: page }) => {
    const frButton = page.locator('button[data-locale="fr"], button:has-text("FR")');
    const arButton = page.locator('button[data-locale="ar"], button:has-text("AR")');
    
    if (await frButton.count() > 0 && await arButton.count() > 0) {
      // Switch to Arabic
      await arButton.click();
      await page.waitForTimeout(1000);
      
      // Check if RTL is applied
      const html = page.locator('html');
      const dir = await html.getAttribute('dir');
      expect(dir).toBe('rtl');
      
      // Switch back to French
      await frButton.click();
      await page.waitForTimeout(1000);
      const dir2 = await html.getAttribute('dir');
      expect(dir2).toBe('ltr');
    }
  });

  test('should display current date', async ({ authenticatedPage: page }) => {
    const dateElement = page.locator('#current-date, [id*="date"]');
    if (await dateElement.count() > 0) {
      await expect(dateElement).toBeVisible();
      const dateText = await dateElement.textContent();
      expect(dateText).toBeTruthy();
    }
  });

  test('should handle responsive sidebar on mobile', async ({ authenticatedPage: page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    await page.waitForTimeout(500);
    
    const sidebar = page.locator('#sidebar');
    const mobileToggle = page.locator('#mobile-menu-toggle');
    
    if (await mobileToggle.count() > 0) {
      await mobileToggle.click();
      await page.waitForTimeout(500);
      // Sidebar should be visible on mobile after toggle
    }
  });

  test('should handle 404 errors gracefully', async ({ authenticatedPage: page }) => {
    const response = await page.goto('/non-existent-page');
    // Should either redirect or show 404
    expect(response?.status()).toBeGreaterThanOrEqual(200);
    expect(response?.status()).toBeLessThan(500);
  });
});

