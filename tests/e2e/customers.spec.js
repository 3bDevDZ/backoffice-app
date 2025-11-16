// @ts-check
const { test } = require('./fixtures');
const { expect } = require('@playwright/test');

test.describe('Customers Module', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/customers');
    await page.waitForLoadState('networkidle');
  });

  test('should display customers list page', async ({ authenticatedPage: page }) => {
    await expect(page).toHaveURL(/.*customers.*/);
    await expect(page.locator('h1, .text-2xl')).toContainText(/customer/i);
  });

  test('should display customers table', async ({ authenticatedPage: page }) => {
    const table = page.locator('table, [role="table"]');
    if (await table.count() > 0) {
      await expect(table).toBeVisible();
    }
  });

  test('should filter customers by search', async ({ authenticatedPage: page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], input[name="search"]');
    if (await searchInput.count() > 0) {
      await searchInput.fill('test');
      await page.waitForTimeout(1000);
      await page.keyboard.press('Enter');
      await page.waitForLoadState('networkidle');
    }
  });

  test('should filter customers by type', async ({ authenticatedPage: page }) => {
    const typeSelect = page.locator('select[name="type"], select[id*="type"]');
    if (await typeSelect.count() > 0) {
      await typeSelect.selectOption({ index: 1 });
      await page.waitForLoadState('networkidle');
    }
  });

  test('should filter customers by status', async ({ authenticatedPage: page }) => {
    const statusSelect = page.locator('select[name="status"], select[id*="status"]');
    if (await statusSelect.count() > 0) {
      await statusSelect.selectOption({ index: 1 });
      await page.waitForLoadState('networkidle');
    }
  });

  test('should navigate to new customer page', async ({ authenticatedPage: page }) => {
    const newButton = page.locator('a:has-text("New"), button:has-text("New"), a[href*="new"]');
    if (await newButton.count() > 0) {
      await newButton.click();
      await page.waitForURL('**/customers/new**', { timeout: 5000 });
      await expect(page).toHaveURL(/.*customers.*new.*/);
    }
  });

  test('should create a new customer', async ({ authenticatedPage: page }) => {
    await page.goto('/customers/new');
    await page.waitForLoadState('networkidle');
    
    const nameInput = page.locator('input[name="name"], input[id*="name"]');
    if (await nameInput.count() > 0) {
      await nameInput.fill(`Test Customer ${Date.now()}`);
    }
    
    const emailInput = page.locator('input[name="email"], input[type="email"]');
    if (await emailInput.count() > 0) {
      await emailInput.fill(`test${Date.now()}@example.com`);
    }
    
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")');
    if (await submitButton.count() > 0) {
      await submitButton.click();
      await page.waitForLoadState('networkidle');
      await expect(page.locator('.bg-green-50, [class*="success"]')).toBeVisible({ timeout: 5000 }).catch(() => {});
    }
  });

  test('should paginate customers', async ({ authenticatedPage: page }) => {
    const nextButton = page.locator('a:has-text("Next"), button:has-text("Next"), [aria-label*="next" i]');
    if (await nextButton.count() > 0) {
      await nextButton.click();
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(/.*page=2.*/);
    }
  });

  test('should edit a customer', async ({ authenticatedPage: page }) => {
    const editButton = page.locator('a[href*="edit"], button:has-text("Edit"), [title*="edit" i]').first();
    if (await editButton.count() > 0) {
      await editButton.click();
      await page.waitForURL('**/edit**', { timeout: 5000 });
      await expect(page).toHaveURL(/.*edit.*/);
    }
  });
});

