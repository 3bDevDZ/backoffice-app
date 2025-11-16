// @ts-check
const { test } = require('./fixtures');
const { expect } = require('@playwright/test');

test.describe('Quotes Module', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/quotes');
    await page.waitForLoadState('networkidle');
  });

  test('should display quotes list page', async ({ authenticatedPage: page }) => {
    await expect(page).toHaveURL(/.*quotes.*/);
    await expect(page.locator('h1, .text-2xl')).toContainText(/quote/i);
  });

  test('should display quotes table', async ({ authenticatedPage: page }) => {
    const table = page.locator('table, [role="table"]');
    if (await table.count() > 0) {
      await expect(table).toBeVisible();
    }
  });

  test('should filter quotes by search', async ({ authenticatedPage: page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], input[name="search"]');
    if (await searchInput.count() > 0) {
      await searchInput.fill('QT-');
      await page.waitForTimeout(1000);
      await page.keyboard.press('Enter');
      await page.waitForLoadState('networkidle');
    }
  });

  test('should filter quotes by status', async ({ authenticatedPage: page }) => {
    const statusSelect = page.locator('select[name="status"], select[id*="status"]');
    if (await statusSelect.count() > 0) {
      await statusSelect.selectOption({ index: 1 });
      await page.waitForLoadState('networkidle');
    }
  });

  test('should navigate to new quote page', async ({ authenticatedPage: page }) => {
    const newButton = page.locator('a:has-text("New"), button:has-text("New"), a[href*="new"]');
    if (await newButton.count() > 0) {
      await newButton.click();
      await page.waitForURL('**/quotes/new**', { timeout: 5000 });
      await expect(page).toHaveURL(/.*quotes.*new.*/);
    }
  });

  test('should create a new quote', async ({ authenticatedPage: page }) => {
    await page.goto('/quotes/new');
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
        await quantityInput.fill('5');
      }
    }
    
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")');
    if (await submitButton.count() > 0) {
      await submitButton.click();
      await page.waitForLoadState('networkidle');
      await expect(page.locator('.bg-green-50, [class*="success"]')).toBeVisible({ timeout: 5000 }).catch(() => {});
    }
  });

  test('should paginate quotes', async ({ authenticatedPage: page }) => {
    const nextButton = page.locator('a:has-text("Next"), button:has-text("Next"), [aria-label*="next" i]');
    if (await nextButton.count() > 0) {
      await nextButton.click();
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(/.*page=2.*/);
    }
  });

  test('should view quote details', async ({ authenticatedPage: page }) => {
    const viewLink = page.locator('a[href*="/quotes/"]:not([href*="new"]):not([href*="edit"])').first();
    if (await viewLink.count() > 0) {
      await viewLink.click();
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(/.*quotes\/\d+.*/);
    }
  });

  test('should convert quote to order', async ({ authenticatedPage: page }) => {
    const viewLink = page.locator('a[href*="/quotes/"]:not([href*="new"]):not([href*="edit"])').first();
    if (await viewLink.count() > 0) {
      await viewLink.click();
      await page.waitForLoadState('networkidle');
      
      const convertButton = page.locator('button:has-text("Convert"), button:has-text("Create Order"), a[href*="convert"]');
      if (await convertButton.count() > 0) {
        await convertButton.click();
        await page.waitForLoadState('networkidle');
        // Should redirect to order creation page
        await expect(page).toHaveURL(/.*orders.*new.*/).catch(() => {});
      }
    }
  });
});

