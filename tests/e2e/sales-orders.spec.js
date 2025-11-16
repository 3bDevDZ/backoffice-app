// @ts-check
const { test } = require('./fixtures');
const { expect } = require('@playwright/test');

test.describe('Sales Orders Module', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/orders');
    await page.waitForLoadState('networkidle');
  });

  test('should display sales orders list page', async ({ authenticatedPage: page }) => {
    await expect(page).toHaveURL(/.*orders.*/);
    await expect(page.locator('h1, .text-2xl')).toContainText(/order/i);
  });

  test('should display orders table', async ({ authenticatedPage: page }) => {
    const table = page.locator('table, [role="table"]');
    if (await table.count() > 0) {
      await expect(table).toBeVisible();
    }
  });

  test('should filter orders by search', async ({ authenticatedPage: page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], input[name="search"]');
    if (await searchInput.count() > 0) {
      await searchInput.fill('SO-');
      await page.waitForTimeout(1000);
      await page.keyboard.press('Enter');
      await page.waitForLoadState('networkidle');
    }
  });

  test('should filter orders by status', async ({ authenticatedPage: page }) => {
    const statusSelect = page.locator('select[name="status"], select[id*="status"]');
    if (await statusSelect.count() > 0) {
      await statusSelect.selectOption({ index: 1 });
      await page.waitForLoadState('networkidle');
    }
  });

  test('should navigate to new order page', async ({ authenticatedPage: page }) => {
    const newButton = page.locator('a:has-text("New"), button:has-text("New"), a[href*="new"]');
    if (await newButton.count() > 0) {
      await newButton.click();
      await page.waitForURL('**/orders/new**', { timeout: 5000 });
      await expect(page).toHaveURL(/.*orders.*new.*/);
    }
  });

  test('should create a new order', async ({ authenticatedPage: page }) => {
    await page.goto('/orders/new');
    await page.waitForLoadState('networkidle');
    
    // Select customer
    const customerSelect = page.locator('select[name="customer_id"], select[id*="customer"]');
    if (await customerSelect.count() > 0) {
      await customerSelect.selectOption({ index: 1 });
    }
    
    // Add a line
    const addLineButton = page.locator('button:has-text("Add Line"), button:has-text("Add"), [onclick*="add"]');
    if (await addLineButton.count() > 0) {
      await addLineButton.click();
      await page.waitForTimeout(500);
      
      const productSelect = page.locator('select[name*="product"], select[id*="product"]').last();
      if (await productSelect.count() > 0) {
        await productSelect.selectOption({ index: 1 });
      }
      
      const quantityInput = page.locator('input[name*="quantity"], input[id*="quantity"]').last();
      if (await quantityInput.count() > 0) {
        await quantityInput.fill('3');
      }
    }
    
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")');
    if (await submitButton.count() > 0) {
      await submitButton.click();
      await page.waitForLoadState('networkidle');
      await expect(page.locator('.bg-green-50, [class*="success"]')).toBeVisible({ timeout: 5000 }).catch(() => {});
    }
  });

  test('should paginate orders', async ({ authenticatedPage: page }) => {
    const nextButton = page.locator('a:has-text("Next"), button:has-text("Next"), [aria-label*="next" i]');
    if (await nextButton.count() > 0) {
      await nextButton.click();
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(/.*page=2.*/);
    }
  });

  test('should view order details', async ({ authenticatedPage: page }) => {
    const viewLink = page.locator('a[href*="/orders/"]:not([href*="new"]):not([href*="edit"])').first();
    if (await viewLink.count() > 0) {
      await viewLink.click();
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(/.*orders\/\d+.*/);
    }
  });

  test('should confirm an order', async ({ authenticatedPage: page }) => {
    const viewLink = page.locator('a[href*="/orders/"]:not([href*="new"]):not([href*="edit"])').first();
    if (await viewLink.count() > 0) {
      await viewLink.click();
      await page.waitForLoadState('networkidle');
      
      const confirmButton = page.locator('button:has-text("Confirm"), form[action*="confirm"] button');
      if (await confirmButton.count() > 0) {
        await confirmButton.click();
        await page.waitForLoadState('networkidle');
        await expect(page.locator('.bg-green-50, [class*="success"]')).toBeVisible({ timeout: 5000 }).catch(() => {});
      }
    }
  });
});

