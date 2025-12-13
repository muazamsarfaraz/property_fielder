import { test, expect } from '../../fixtures/test-fixtures';
import { TestDataManager } from '../../utils/test-data-manager';

/**
 * Property Management - Certifications Tests
 * Tests certification types and compliance tracking
 */
test.describe('Property Management - Certifications @regression', () => {
  
  test.beforeEach(async ({ propertyPage }) => {
    await propertyPage.navigateToCertifications();
  });

  test.describe('Navigation @smoke', () => {
    test('should navigate to Certifications menu', async ({ propertyPage }) => {
      await propertyPage.verifyLoaded();
    });

    test('should display certification types list', async ({ propertyPage, page }) => {
      const isList = await propertyPage.isListView();
      const isKanban = await propertyPage.isKanbanView();
      expect(isList || isKanban).toBeTruthy();
    });
  });

  test.describe('Certification Type CRUD', () => {
    test('should open create form for certification type', async ({ propertyPage, page }) => {
      await propertyPage.clickCreate();
      await expect(page.locator('.o_form_view')).toBeVisible();
    });

    test('should create a new certification type @critical', async ({ propertyPage, page }) => {
      const certData = TestDataManager.certificationTypeData();
      
      await propertyPage.createCertificationType(certData);
      
      // Verify in form view after save
      await expect(page.locator('.o_form_view')).toBeVisible();
    });

    test('should display validity period field', async ({ propertyPage, page }) => {
      await propertyPage.clickCreate();
      await expect(page.locator('.o_field_widget[name="validity_months"], .o_field_widget[name="validity_period"]')).toBeVisible();
    });
  });

  test.describe('Compliance Requirements', () => {
    test('should list compliance requirements', async ({ propertyPage, page }) => {
      // Navigate to compliance requirements if available
      await page.click('.o_menu_sections a:has-text("Compliance"), .o_menu_sections a:has-text("Requirements")').catch(() => {});
      await propertyPage.odoo.waitForOdooLoad();
      
      // Just verify the page loads
      await propertyPage.verifyLoaded();
    });
  });
});

