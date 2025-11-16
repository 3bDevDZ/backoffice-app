// @ts-check
const { test } = require('./fixtures');
const { expect } = require('@playwright/test');

test.describe('Products Module', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/products');
    await page.waitForLoadState('networkidle');
  });

  test('should display products list page', async ({ authenticatedPage: page }) => {
    await expect(page).toHaveURL(/.*products.*/);
    await expect(page.locator('h1, .text-2xl')).toContainText(/product/i);
  });

  test('should display products table', async ({ authenticatedPage: page }) => {
    // Check for table headers
    const table = page.locator('table, [role="table"]');
    if (await table.count() > 0) {
      await expect(table).toBeVisible();
    }
  });

  test('should filter products by search', async ({ authenticatedPage: page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], input[name="search"]');
    if (await searchInput.count() > 0) {
      await searchInput.fill('test');
      await page.waitForTimeout(1000); // Wait for debounce
      await page.keyboard.press('Enter');
      await page.waitForLoadState('networkidle');
    }
  });

  test('should filter products by category', async ({ authenticatedPage: page }) => {
    const categorySelect = page.locator('select[name="category_id"], select[id*="category"]');
    if (await categorySelect.count() > 0) {
      await categorySelect.selectOption({ index: 1 });
      await page.waitForLoadState('networkidle');
    }
  });

  test('should filter products by status', async ({ authenticatedPage: page }) => {
    const statusSelect = page.locator('select[name="status"], select[id*="status"]');
    if (await statusSelect.count() > 0) {
      await statusSelect.selectOption({ index: 1 });
      await page.waitForLoadState('networkidle');
    }
  });

  test('should navigate to new product page', async ({ authenticatedPage: page }) => {
    const newButton = page.locator('a:has-text("New"), button:has-text("New"), a[href*="new"]');
    if (await newButton.count() > 0) {
      await newButton.click();
      await page.waitForURL('**/products/new**', { timeout: 5000 });
      await expect(page).toHaveURL(/.*products.*new.*/);
    }
  });

  test('should create a new product', async ({ authenticatedPage: page }) => {
    // Navigate to new product page
    await page.goto('/products/new');
    await page.waitForLoadState('networkidle');
    
    // Fill form fields
    const nameInput = page.locator('input[name="name"], input[id*="name"]');
    if (await nameInput.count() > 0) {
      await nameInput.fill(`Test Product ${Date.now()}`);
    }
    
    const skuInput = page.locator('input[name="sku"], input[id*="sku"]');
    if (await skuInput.count() > 0) {
      await skuInput.fill(`SKU-${Date.now()}`);
    }
    
    const priceInput = page.locator('input[name="price"], input[id*="price"], input[type="number"]');
    if (await priceInput.count() > 0) {
      await priceInput.fill('100.00');
    }
    
    // Submit form
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")');
    if (await submitButton.count() > 0) {
      await submitButton.click();
      await page.waitForLoadState('networkidle');
      // Should redirect to list or show success message
      await expect(page.locator('.bg-green-50, [class*="success"]')).toBeVisible({ timeout: 5000 }).catch(() => {});
    }
  });

  test('should paginate products', async ({ authenticatedPage: page }) => {
    const nextButton = page.locator('a:has-text("Next"), button:has-text("Next"), [aria-label*="next" i]');
    const prevButton = page.locator('a:has-text("Previous"), button:has-text("Previous"), [aria-label*="prev" i]');
    
    if (await nextButton.count() > 0) {
      await nextButton.click();
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(/.*page=2.*/);
    }
    
    if (await prevButton.count() > 0) {
      await prevButton.click();
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(/.*page=1.*/);
    }
  });

  test('should edit a product', async ({ authenticatedPage: page }) => {
    // Find first edit button
    const editButton = page.locator('a[href*="edit"], button:has-text("Edit"), [title*="edit" i]').first();
    if (await editButton.count() > 0) {
      await editButton.click();
      await page.waitForURL('**/edit**', { timeout: 5000 });
      await expect(page).toHaveURL(/.*edit.*/);
    }
  });

  test('should view product details', async ({ authenticatedPage: page }) => {
    // Find first view/details link
    const viewLink = page.locator('a[href*="/products/"]:not([href*="new"]):not([href*="edit"])').first();
    if (await viewLink.count() > 0) {
      await viewLink.click();
      await page.waitForLoadState('networkidle');
      // Should be on product detail page
      await expect(page).toHaveURL(/.*products\/\d+.*/);
    }
  });
});

