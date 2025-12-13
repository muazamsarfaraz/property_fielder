import { test, expect } from '../fixtures/test-fixtures';

/**
 * Smoke Tests - Quick sanity checks for all major features
 * Run these first to ensure the application is working
 */
test.describe('Smoke Tests @smoke @critical', () => {
  
  test.describe('Application Health', () => {
    test('should load Odoo home page', async ({ page }) => {
      await page.goto('/web');
      await expect(page.locator('.o_main_navbar')).toBeVisible({ timeout: 30000 });
    });

    test('should display application menu', async ({ page }) => {
      await page.goto('/web');
      await expect(page.locator('nav')).toBeVisible();

      // Click home menu to see apps (Odoo 19 uses title attribute)
      await page.locator('button[title="Home Menu"]').click();
      await page.waitForSelector('[role="menuitem"]');

      // Should have at least Property Management or Field Service
      const hasPropertyMgmt = await page.locator('[role="menuitem"]:has-text("Property")').isVisible();
      const hasFieldService = await page.locator('[role="menuitem"]:has-text("Field Service")').isVisible();
      expect(hasPropertyMgmt || hasFieldService).toBeTruthy();
    });
  });

  test.describe('Property Management Module', () => {
    test('should access Property Management', async ({ propertyPage }) => {
      await propertyPage.navigate();
      await propertyPage.verifyLoaded();
    });

    test('should access Properties list', async ({ propertyPage }) => {
      await propertyPage.navigateToProperties();
      await propertyPage.verifyLoaded();
    });

    test('should access Certifications list', async ({ propertyPage }) => {
      await propertyPage.navigateToCertifications();
      await propertyPage.verifyLoaded();
    });
  });

  test.describe('Field Service Module', () => {
    test('should access Field Service', async ({ fieldServicePage }) => {
      await fieldServicePage.navigate();
      await fieldServicePage.verifyLoaded();
    });

    test('should access Jobs list', async ({ fieldServicePage }) => {
      await fieldServicePage.navigateToJobs();
      await fieldServicePage.verifyLoaded();
    });

    test('should access Inspectors list', async ({ fieldServicePage }) => {
      await fieldServicePage.navigateToInspectors();
      await fieldServicePage.verifyLoaded();
    });

    test('should access Routes list', async ({ fieldServicePage }) => {
      await fieldServicePage.navigateToRoutes();
      await fieldServicePage.verifyLoaded();
    });
  });

  test.describe('Dispatch View', () => {
    test('should access Dispatch view', async ({ dispatchPage }) => {
      await dispatchPage.navigate();
      await dispatchPage.waitForLoad();
      await expect(dispatchPage.dispatchContainer).toBeVisible();
    });

    test('should display map in Dispatch view', async ({ dispatchPage }) => {
      await dispatchPage.navigate();
      await dispatchPage.waitForLoad();
      await dispatchPage.verifyMapDisplayed();
    });

    test('should navigate through all tabs', async ({ dispatchPage }) => {
      await dispatchPage.navigate();
      await dispatchPage.waitForLoad();
      
      // PLAN tab (default)
      expect(await dispatchPage.getActiveTab()).toContain('PLAN');
      
      // OPTIMIZE tab
      await dispatchPage.switchToOptimize();
      expect(await dispatchPage.getActiveTab()).toContain('OPTIMIZE');
      
      // SCHEDULE tab
      await dispatchPage.switchToSchedule();
      expect(await dispatchPage.getActiveTab()).toContain('SCHEDULE');
    });
  });
});

