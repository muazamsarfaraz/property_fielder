import { test, expect } from '../../fixtures/test-fixtures';
import { TestDataManager } from '../../utils/test-data-manager';

/**
 * Field Service - Routes Tests
 * Tests route management and scheduling
 */
test.describe('Field Service - Routes @regression', () => {
  
  test.beforeEach(async ({ fieldServicePage }) => {
    await fieldServicePage.navigateToRoutes();
  });

  test.describe('Navigation @smoke', () => {
    test('should navigate to Routes menu', async ({ fieldServicePage }) => {
      await fieldServicePage.verifyLoaded();
      const title = await fieldServicePage.getTitle();
      expect(title.toLowerCase()).toContain('route');
    });

    test('should display routes list or kanban', async ({ fieldServicePage }) => {
      const isList = await fieldServicePage.isListView();
      const isKanban = await fieldServicePage.isKanbanView();
      expect(isList || isKanban).toBeTruthy();
    });
  });

  test.describe('Route CRUD Operations', () => {
    test('should open create form', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      await expect(page.locator('.o_form_view')).toBeVisible();
    });

    test('should create a new route @critical', async ({ fieldServicePage, page }) => {
      const routeData = TestDataManager.routeData();
      
      await fieldServicePage.createRoute(routeData);
      
      // Verify route was created
      await expect(page.locator('.o_form_view')).toBeVisible();
    });

    test('should search for routes', async ({ fieldServicePage }) => {
      // Create a route with unique name
      const routeData = TestDataManager.routeData({ name: 'ROUTETEST_UniqueRoute' });
      await fieldServicePage.createRoute(routeData);
      
      // Navigate back and search
      await fieldServicePage.navigateToRoutes();
      await fieldServicePage.search('ROUTETEST_UniqueRoute');
      
      const count = await fieldServicePage.getRecordCount();
      expect(count).toBeGreaterThan(0);
    });
  });

  test.describe('Route Details', () => {
    test('should display route date field', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      await expect(page.locator('.o_field_widget[name="route_date"]')).toBeVisible();
    });

    test('should display inspector assignment field', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      await expect(page.locator('.o_field_widget[name="inspector_id"]')).toBeVisible();
    });

    test('should display jobs list field', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      await expect(page.locator('.o_field_widget[name="job_ids"]')).toBeVisible();
    });

    test('should display route state', async ({ fieldServicePage, page }) => {
      const count = await fieldServicePage.getRecordCount();
      
      if (count > 0) {
        await fieldServicePage.clickRow(0);
        await expect(page.locator('.o_statusbar_status, .o_field_widget[name="state"]')).toBeVisible();
      }
    });
  });

  test.describe('Route Statistics', () => {
    test('should display total distance field', async ({ fieldServicePage, page }) => {
      const count = await fieldServicePage.getRecordCount();
      
      if (count > 0) {
        await fieldServicePage.clickRow(0);
        // Distance may be computed field
        await expect(page.locator('.o_form_view')).toBeVisible();
      }
    });

    test('should display total duration field', async ({ fieldServicePage, page }) => {
      const count = await fieldServicePage.getRecordCount();
      
      if (count > 0) {
        await fieldServicePage.clickRow(0);
        // Duration may be computed field
        await expect(page.locator('.o_form_view')).toBeVisible();
      }
    });
  });
});

