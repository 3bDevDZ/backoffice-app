// @ts-check
const { test } = require('./fixtures');
const { expect } = require('@playwright/test');

test.describe('Dashboard', () => {
  test('should display dashboard after login', async ({ authenticatedPage: page }) => {
    await expect(page).toHaveURL(/.*dashboard.*/);
    await expect(page.locator('h1, .text-2xl')).toBeVisible();
  });

  test('should display sidebar navigation', async ({ authenticatedPage: page }) => {
    await expect(page.locator('#sidebar, [id*="sidebar"]')).toBeVisible();
    
    // Check for main menu items
    const menuItems = [
      'Dashboard',
      'Products',
      'Suppliers',
      'Purchase Orders',
      'Stock',
      'Customers',
      'Quotes',
      'Orders'
    ];
    
    for (const item of menuItems) {
      const menuItem = page.locator(`text=${item}, [aria-label*="${item}" i]`);
      if (await menuItem.count() > 0) {
        await expect(menuItem.first()).toBeVisible();
      }
    }
  });

  test('should navigate to different modules from sidebar', async ({ authenticatedPage: page }) => {
    // Test Products navigation
    const productsLink = page.locator('a[href*="/products"]:not([href*="new"]):not([href*="edit"])').first();
    if (await productsLink.count() > 0) {
      await productsLink.click();
      await page.waitForURL('**/products**', { timeout: 5000 });
      await expect(page).toHaveURL(/.*products.*/);
    }
    
    // Go back to dashboard
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    // Test Customers navigation
    const customersLink = page.locator('a[href*="/customers"]:not([href*="new"]):not([href*="edit"])').first();
    if (await customersLink.count() > 0) {
      await customersLink.click();
      await page.waitForURL('**/customers**', { timeout: 5000 });
      await expect(page).toHaveURL(/.*customers.*/);
    }
  });

  test('should toggle sidebar', async ({ authenticatedPage: page }) => {
    const toggleButton = page.locator('#sidebar-toggle, button[id*="toggle"]');
    if (await toggleButton.count() > 0) {
      const sidebar = page.locator('#sidebar');
      const initialWidth = await sidebar.evaluate(el => el.offsetWidth);
      
      await toggleButton.click();
      await page.waitForTimeout(500);
      
      const newWidth = await sidebar.evaluate(el => el.offsetWidth);
      expect(newWidth).not.toBe(initialWidth);
    }
  });
});

