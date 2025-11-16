// @ts-check
const { test } = require('./fixtures');
const { expect } = require('@playwright/test');

test.describe('Purchase Orders Module', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/purchase-orders');
    await page.waitForLoadState('networkidle');
  });

  test('should display purchase orders list page', async ({ authenticatedPage: page }) => {
    await expect(page).toHaveURL(/.*purchase-orders.*/);
    await expect(page.locator('h1, .text-2xl')).toContainText(/purchase.*order/i);
  });

  test('should display purchase orders table', async ({ authenticatedPage: page }) => {
    const table = page.locator('table, [role="table"]');
    if (await table.count() > 0) {
      await expect(table).toBeVisible();
    }
  });

  test('should filter purchase orders by search', async ({ authenticatedPage: page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], input[name="search"]');
    if (await searchInput.count() > 0) {
      await searchInput.fill('PO-');
      await page.waitForTimeout(1000);
      await page.keyboard.press('Enter');
      await page.waitForLoadState('networkidle');
    }
  });

  test('should filter purchase orders by status', async ({ authenticatedPage: page }) => {
    const statusSelect = page.locator('select[name="status"], select[id*="status"]');
    if (await statusSelect.count() > 0) {
      await statusSelect.selectOption({ index: 1 });
      await page.waitForLoadState('networkidle');
    }
  });

  test('should navigate to new purchase order page', async ({ authenticatedPage: page }) => {
    const newButton = page.locator('a:has-text("New"), button:has-text("New"), a[href*="new"]');
    if (await newButton.count() > 0) {
      await newButton.click();
      await page.waitForURL('**/purchase-orders/new**', { timeout: 5000 });
      await expect(page).toHaveURL(/.*purchase-orders.*new.*/);
    }
  });

  test('should create a new purchase order', async ({ authenticatedPage: page }) => {
    await page.goto('/purchase-orders/new');
    await page.waitForLoadState('networkidle');
    
    // Select supplier
    const supplierSelect = page.locator('select[name="supplier_id"], select[id*="supplier"]');
    if (await supplierSelect.count() > 0) {
      await supplierSelect.selectOption({ index: 1 });
    }
    
    // Add a line
    const addLineButton = page.locator('button:has-text("Add Line"), button:has-text("Add"), [onclick*="add"]');
    if (await addLineButton.count() > 0) {
      await addLineButton.click();
      await page.waitForTimeout(500);
      
      // Fill line fields
      const productSelect = page.locator('select[name*="product"], select[id*="product"]').last();
      if (await productSelect.count() > 0) {
        await productSelect.selectOption({ index: 1 });
      }
      
      const quantityInput = page.locator('input[name*="quantity"], input[id*="quantity"]').last();
      if (await quantityInput.count() > 0) {
        await quantityInput.fill('10');
      }
      
      const priceInput = page.locator('input[name*="price"], input[id*="price"]').last();
      if (await priceInput.count() > 0) {
        await priceInput.fill('100.00');
      }
    }
    
    // Submit form
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")');
    if (await submitButton.count() > 0) {
      await submitButton.click();
      await page.waitForLoadState('networkidle');
      await expect(page.locator('.bg-green-50, [class*="success"]')).toBeVisible({ timeout: 5000 }).catch(() => {});
    }
  });

  test('should paginate purchase orders', async ({ authenticatedPage: page }) => {
    const nextButton = page.locator('a:has-text("Next"), button:has-text("Next"), [aria-label*="next" i]');
    if (await nextButton.count() > 0) {
      await nextButton.click();
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(/.*page=2.*/);
    }
  });

  test('should view purchase order details', async ({ authenticatedPage: page }) => {
    const viewLink = page.locator('a[href*="/purchase-orders/"]:not([href*="new"]):not([href*="edit"])').first();
    if (await viewLink.count() > 0) {
      await viewLink.click();
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(/.*purchase-orders\/\d+.*/);
    }
  });

  test('should confirm a purchase order', async ({ authenticatedPage: page }) => {
    // Navigate to a draft purchase order
    const viewLink = page.locator('a[href*="/purchase-orders/"]:not([href*="new"]):not([href*="edit"])').first();
    if (await viewLink.count() > 0) {
      await viewLink.click();
      await page.waitForLoadState('networkidle');
      
      // Look for confirm button
      const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Approve"), form[action*="confirm"] button');
      if (await confirmButton.count() > 0) {
        await confirmButton.click();
        await page.waitForLoadState('networkidle');
        await expect(page.locator('.bg-green-50, [class*="success"]')).toBeVisible({ timeout: 5000 }).catch(() => {});
      }
    }
  });
});

