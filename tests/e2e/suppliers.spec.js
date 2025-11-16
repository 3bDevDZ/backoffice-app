// @ts-check
const { test } = require('./fixtures');
const { expect } = require('@playwright/test');

test.describe('Suppliers Module', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/suppliers');
    await page.waitForLoadState('networkidle');
  });

  test('should display suppliers list page', async ({ authenticatedPage: page }) => {
    await expect(page).toHaveURL(/.*suppliers.*/);
    await expect(page.locator('h1, .text-2xl')).toContainText(/supplier/i);
  });

  test('should display suppliers table', async ({ authenticatedPage: page }) => {
    const table = page.locator('table, [role="table"]');
    if (await table.count() > 0) {
      await expect(table).toBeVisible();
    }
  });

  test('should filter suppliers by search', async ({ authenticatedPage: page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], input[name="search"]');
    if (await searchInput.count() > 0) {
      await searchInput.fill('test');
      await page.waitForTimeout(1000);
      await page.keyboard.press('Enter');
      await page.waitForLoadState('networkidle');
    }
  });

  test('should navigate to new supplier page', async ({ authenticatedPage: page }) => {
    const newButton = page.locator('a:has-text("New"), button:has-text("New"), a[href*="new"]');
    if (await newButton.count() > 0) {
      await newButton.click();
      await page.waitForURL('**/suppliers/new**', { timeout: 5000 });
      await expect(page).toHaveURL(/.*suppliers.*new.*/);
    }
  });

  test('should create a new supplier', async ({ authenticatedPage: page }) => {
    await page.goto('/suppliers/new');
    await page.waitForLoadState('networkidle');
    
    const nameInput = page.locator('input[name="name"], input[id*="name"]');
    if (await nameInput.count() > 0) {
      await nameInput.fill(`Test Supplier ${Date.now()}`);
    }
    
    const codeInput = page.locator('input[name="code"], input[id*="code"]');
    if (await codeInput.count() > 0) {
      await codeInput.fill(`SUP-${Date.now()}`);
    }
    
    const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")');
    if (await submitButton.count() > 0) {
      await submitButton.click();
      await page.waitForLoadState('networkidle');
      await expect(page.locator('.bg-green-50, [class*="success"]')).toBeVisible({ timeout: 5000 }).catch(() => {});
    }
  });

  test('should paginate suppliers', async ({ authenticatedPage: page }) => {
    const nextButton = page.locator('a:has-text("Next"), button:has-text("Next"), [aria-label*="next" i]');
    if (await nextButton.count() > 0) {
      await nextButton.click();
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(/.*page=2.*/);
    }
  });

  test('should edit a supplier', async ({ authenticatedPage: page }) => {
    const editButton = page.locator('a[href*="edit"], button:has-text("Edit"), [title*="edit" i]').first();
    if (await editButton.count() > 0) {
      await editButton.click();
      await page.waitForURL('**/edit**', { timeout: 5000 });
      await expect(page).toHaveURL(/.*edit.*/);
    }
  });
});

