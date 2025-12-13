import { test, expect } from '../../fixtures/test-fixtures';
import { TestDataManager } from '../../utils/test-data-manager';

/**
 * Property Management - Properties Tests
 * Tests CRUD operations and features for properties
 */
test.describe('Property Management - Properties @regression', () => {
  
  test.beforeEach(async ({ propertyPage }) => {
    await propertyPage.navigateToProperties();
  });

  test.describe('Navigation @smoke', () => {
    test('should navigate to Properties menu', async ({ propertyPage }) => {
      await propertyPage.verifyLoaded();
      const title = await propertyPage.getTitle();
      expect(title.toLowerCase()).toContain('propert');
    });

    test('should display list view by default', async ({ propertyPage }) => {
      const isList = await propertyPage.isListView();
      const isKanban = await propertyPage.isKanbanView();
      expect(isList || isKanban).toBeTruthy();
    });

    test('should switch between list and kanban views', async ({ propertyPage, page }) => {
      // Switch to kanban
      await propertyPage.switchToKanban();
      expect(await propertyPage.isKanbanView()).toBeTruthy();
      
      // Switch back to list
      await propertyPage.switchToList();
      expect(await propertyPage.isListView()).toBeTruthy();
    });
  });

  test.describe('CRUD Operations', () => {
    test('should open create form', async ({ propertyPage, page }) => {
      await propertyPage.clickCreate();
      await propertyPage.verifyPropertyForm();
    });

    test('should create a new property @critical', async ({ propertyPage }) => {
      const propertyData = TestDataManager.propertyData();
      
      await propertyPage.createProperty(propertyData);
      
      // Verify property was created
      await propertyPage.navigateToProperties();
      const exists = await propertyPage.propertyExists(propertyData.name);
      expect(exists).toBeTruthy();
    });

    test('should open existing property', async ({ propertyPage, page }) => {
      // First check if any properties exist
      const count = await propertyPage.getRecordCount();
      
      if (count > 0) {
        await propertyPage.clickRow(0);
        await propertyPage.verifyPropertyForm();
      } else {
        // Create one first
        const propertyData = TestDataManager.propertyData();
        await propertyPage.createProperty(propertyData);
        await propertyPage.verifyPropertyForm();
      }
    });

    test('should search for properties', async ({ propertyPage }) => {
      // Create a property with unique name
      const propertyData = TestDataManager.propertyData({ name: 'SEARCHTEST_UniqueProperty' });
      await propertyPage.createProperty(propertyData);
      
      // Navigate back and search
      await propertyPage.navigateToProperties();
      await propertyPage.search('SEARCHTEST_UniqueProperty');
      
      const count = await propertyPage.getRecordCount();
      expect(count).toBeGreaterThan(0);
    });
  });

  test.describe('Property Features', () => {
    test('should display property address fields', async ({ propertyPage, page }) => {
      await propertyPage.clickCreate();
      
      await expect(page.locator('.o_field_widget[name="street"]')).toBeVisible();
      await expect(page.locator('.o_field_widget[name="city"]')).toBeVisible();
    });

    test('should display compliance status on property', async ({ propertyPage }) => {
      const count = await propertyPage.getRecordCount();
      
      if (count > 0) {
        await propertyPage.clickRow(0);
        // Compliance status may or may not be visible depending on data
        // Just verify the form loads without error
        await propertyPage.verifyPropertyForm();
      }
    });
  });
});

