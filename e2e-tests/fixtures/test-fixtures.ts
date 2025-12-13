import { test as base, Page } from '@playwright/test';
import { PropertyManagementPage } from '../pages/property-management.page';
import { FieldServicePage } from '../pages/field-service.page';
import { DispatchPage } from '../pages/dispatch.page';
import { TestDataManager } from '../utils/test-data-manager';
import { OdooHelpers } from '../utils/odoo-helpers';

/**
 * Extended test fixtures with page objects and utilities
 */
type PropertyFielderFixtures = {
  propertyPage: PropertyManagementPage;
  fieldServicePage: FieldServicePage;
  dispatchPage: DispatchPage;
  testData: TestDataManager;
  odoo: OdooHelpers;
};

/**
 * Extended test function with all page objects pre-initialized
 */
export const test = base.extend<PropertyFielderFixtures>({
  propertyPage: async ({ page }, use) => {
    const propertyPage = new PropertyManagementPage(page);
    await use(propertyPage);
  },

  fieldServicePage: async ({ page }, use) => {
    const fieldServicePage = new FieldServicePage(page);
    await use(fieldServicePage);
  },

  dispatchPage: async ({ page }, use) => {
    const dispatchPage = new DispatchPage(page);
    await use(dispatchPage);
  },

  testData: async ({ page }, use) => {
    const testData = new TestDataManager(page);
    await use(testData);
    // Cleanup after test (optional - can be disabled)
    testData.clearTracking();
  },

  odoo: async ({ page }, use) => {
    const odoo = new OdooHelpers(page);
    await use(odoo);
  },
});

export { expect } from '@playwright/test';

/**
 * Test tags for filtering
 */
export const tags = {
  smoke: '@smoke',
  regression: '@regression',
  critical: '@critical',
  slow: '@slow',
  flaky: '@flaky',
};

/**
 * Common test setup helper
 */
export async function ensureLoggedIn(page: Page): Promise<void> {
  // Check if already logged in
  const isLoggedIn = await page.locator('.o_main_navbar').isVisible().catch(() => false);
  
  if (!isLoggedIn) {
    await page.goto('/web');
    await page.waitForSelector('.o_main_navbar', { timeout: 10000 });
  }
}

/**
 * Navigate to home/apps
 */
export async function goToApps(page: Page): Promise<void> {
  await page.goto('/web');
  await page.waitForSelector('.o_main_navbar');
}

