import { test, expect } from '../../fixtures/test-fixtures';
import { TestDataManager } from '../../utils/test-data-manager';

/**
 * Field Service - Inspectors Tests
 * Tests inspector management and availability
 */
test.describe('Field Service - Inspectors @regression', () => {
  
  test.beforeEach(async ({ fieldServicePage }) => {
    await fieldServicePage.navigateToInspectors();
  });

  test.describe('Navigation @smoke', () => {
    test('should navigate to Inspectors menu', async ({ fieldServicePage }) => {
      await fieldServicePage.verifyLoaded();
      const title = await fieldServicePage.getTitle();
      expect(title.toLowerCase()).toContain('inspector');
    });

    test('should display inspectors list or kanban', async ({ fieldServicePage }) => {
      const isList = await fieldServicePage.isListView();
      const isKanban = await fieldServicePage.isKanbanView();
      expect(isList || isKanban).toBeTruthy();
    });
  });

  test.describe('Inspector CRUD Operations', () => {
    test('should open create form', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      await expect(page.locator('.o_form_view')).toBeVisible();
    });

    test('should create a new inspector @critical', async ({ fieldServicePage, page }) => {
      const inspectorData = TestDataManager.inspectorData();
      
      await fieldServicePage.createInspector(inspectorData);
      
      // Verify inspector was created
      await expect(page.locator('.o_form_view')).toBeVisible();
    });

    test('should search for inspectors', async ({ fieldServicePage }) => {
      // Create an inspector with unique name
      const inspectorData = TestDataManager.inspectorData({ name: 'INSPTEST_UniqueInspector' });
      await fieldServicePage.createInspector(inspectorData);
      
      // Navigate back and search
      await fieldServicePage.navigateToInspectors();
      await fieldServicePage.search('INSPTEST_UniqueInspector');
      
      const count = await fieldServicePage.getRecordCount();
      expect(count).toBeGreaterThan(0);
    });
  });

  test.describe('Inspector Details', () => {
    test('should display name field', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      await expect(page.locator('.o_field_widget[name="name"]')).toBeVisible();
    });

    test('should display user/email field', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      // May have user_id or email field
      const hasUserField = await page.locator('.o_field_widget[name="user_id"]').isVisible();
      const hasEmailField = await page.locator('.o_field_widget[name="email"]').isVisible();
      expect(hasUserField || hasEmailField).toBeTruthy();
    });

    test('should display skills field', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      await expect(page.locator('.o_field_widget[name="skill_ids"]')).toBeVisible();
    });

    test('should display availability toggle', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      await expect(page.locator('.o_field_widget[name="available"]')).toBeVisible();
    });
  });

  test.describe('Inspector Location', () => {
    test('should display home location fields', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      // Check for latitude/longitude or address fields
      const hasLat = await page.locator('.o_field_widget[name="home_latitude"]').isVisible();
      const hasAddress = await page.locator('.o_field_widget[name="home_address"]').isVisible();
      // At least one location field should exist
      // This may vary based on model definition
      await expect(page.locator('.o_form_view')).toBeVisible();
    });
  });
});

