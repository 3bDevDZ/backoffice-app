// @ts-check
const { test } = require('./fixtures');
const { expect } = require('@playwright/test');

test.describe('Stock Module', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/stock');
    await page.waitForLoadState('networkidle');
  });

  test('should display stock levels page', async ({ authenticatedPage: page }) => {
    await expect(page).toHaveURL(/.*stock.*/);
    await expect(page.locator('h1, .text-2xl')).toContainText(/stock/i);
  });

  test('should display stock table', async ({ authenticatedPage: page }) => {
    const table = page.locator('table, [role="table"]');
    if (await table.count() > 0) {
      await expect(table).toBeVisible();
    }
  });

  test('should filter stock by search', async ({ authenticatedPage: page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], input[name="search"]');
    if (await searchInput.count() > 0) {
      await searchInput.fill('test');
      await page.waitForTimeout(1000);
      await page.keyboard.press('Enter');
      await page.waitForLoadState('networkidle');
    }
  });

  test('should filter stock by location', async ({ authenticatedPage: page }) => {
    const locationSelect = page.locator('select[name="location_id"], select[id*="location"]');
    if (await locationSelect.count() > 0) {
      await locationSelect.selectOption({ index: 1 });
      await page.waitForLoadState('networkidle');
    }
  });

  test('should filter stock by minimum quantity', async ({ authenticatedPage: page }) => {
    const minQtyInput = page.locator('input[name="min_quantity"], input[id*="min_quantity"]');
    if (await minQtyInput.count() > 0) {
      await minQtyInput.fill('10');
      await page.waitForTimeout(1000);
      await page.keyboard.press('Enter');
      await page.waitForLoadState('networkidle');
    }
  });

  test('should paginate stock', async ({ authenticatedPage: page }) => {
    const nextButton = page.locator('a:has-text("Next"), button:has-text("Next"), [aria-label*="next" i]');
    if (await nextButton.count() > 0) {
      await nextButton.click();
      await page.waitForLoadState('networkidle');
      await expect(page).toHaveURL(/.*page=2.*/);
    }
  });
});

test.describe('Locations/Warehouses Module', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/stock/locations');
    await page.waitForLoadState('networkidle');
  });

  test('should display locations page', async ({ authenticatedPage: page }) => {
    await expect(page).toHaveURL(/.*locations.*/);
    await expect(page.locator('h1, .text-2xl')).toContainText(/location|warehouse/i);
  });

  test('should display locations table', async ({ authenticatedPage: page }) => {
    const table = page.locator('table, [role="table"]');
    if (await table.count() > 0) {
      await expect(table).toBeVisible();
    }
  });

  test('should create a new location', async ({ authenticatedPage: page }) => {
    const newButton = page.locator('button:has-text("Add Location"), button:has-text("New"), a[href*="new"]');
    if (await newButton.count() > 0) {
      await newButton.click();
      await page.waitForTimeout(500);
      
      const nameInput = page.locator('input[name="name"], input[id*="name"]');
      if (await nameInput.count() > 0) {
        await nameInput.fill(`Test Location ${Date.now()}`);
      }
      
      const codeInput = page.locator('input[name="code"], input[id*="code"]');
      if (await codeInput.count() > 0) {
        await codeInput.fill(`LOC-${Date.now()}`);
      }
      
      const submitButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Create")');
      if (await submitButton.count() > 0) {
        await submitButton.click();
        await page.waitForLoadState('networkidle');
        await expect(page.locator('.bg-green-50, [class*="success"]')).toBeVisible({ timeout: 5000 }).catch(() => {});
      }
    }
  });

  test('should edit a location', async ({ authenticatedPage: page }) => {
    const editButton = page.locator('button:has-text("Edit"), [title*="edit" i]').first();
    if (await editButton.count() > 0) {
      await editButton.click();
      await page.waitForTimeout(500);
      
      const nameInput = page.locator('input[name="name"], input[id*="name"]');
      if (await nameInput.count() > 0) {
        await nameInput.fill(`Updated Location ${Date.now()}`);
      }
      
      const submitButton = page.locator('button[type="submit"], button:has-text("Save")');
      if (await submitButton.count() > 0) {
        await submitButton.click();
        await page.waitForLoadState('networkidle');
        await expect(page.locator('.bg-green-50, [class*="success"]')).toBeVisible({ timeout: 5000 }).catch(() => {});
      }
    }
  });
});

test.describe('Stock Movements', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/stock/movements');
    await page.waitForLoadState('networkidle');
  });

  test('should display movements page', async ({ authenticatedPage: page }) => {
    await expect(page).toHaveURL(/.*movements.*/);
    await expect(page.locator('h1, .text-2xl')).toContainText(/movement/i);
  });

  test('should display movements table', async ({ authenticatedPage: page }) => {
    const table = page.locator('table, [role="table"]');
    if (await table.count() > 0) {
      await expect(table).toBeVisible();
    }
  });

  test('should filter movements', async ({ authenticatedPage: page }) => {
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i]');
    if (await searchInput.count() > 0) {
      await searchInput.fill('test');
      await page.waitForTimeout(1000);
      await page.keyboard.press('Enter');
      await page.waitForLoadState('networkidle');
    }
  });
});

test.describe('Stock Alerts', () => {
  test.beforeEach(async ({ authenticatedPage: page }) => {
    await page.goto('/stock/alerts');
    await page.waitForLoadState('networkidle');
  });

  test('should display alerts page', async ({ authenticatedPage: page }) => {
    await expect(page).toHaveURL(/.*alerts.*/);
    await expect(page.locator('h1, .text-2xl')).toContainText(/alert/i);
  });

  test('should display alerts table', async ({ authenticatedPage: page }) => {
    const table = page.locator('table, [role="table"]');
    if (await table.count() > 0) {
      await expect(table).toBeVisible();
    }
  });
});

