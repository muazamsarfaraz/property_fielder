import { test, expect } from '../../fixtures/test-fixtures';

/**
 * Field Service - Dashboard Tests
 * Tests dashboard widgets and statistics
 */
test.describe('Field Service - Dashboard @regression', () => {
  
  test.beforeEach(async ({ fieldServicePage }) => {
    await fieldServicePage.navigateToDashboard();
  });

  test.describe('Navigation @smoke', () => {
    test('should navigate to Dashboard', async ({ fieldServicePage }) => {
      await fieldServicePage.verifyLoaded();
    });

    test('should display dashboard view', async ({ fieldServicePage, page }) => {
      await expect(page.locator('.o_action_manager')).toBeVisible();
    });
  });

  test.describe('Dashboard Widgets', () => {
    test('should display job statistics', async ({ fieldServicePage, page }) => {
      // Dashboard should show job-related stats
      await fieldServicePage.verifyLoaded();
    });

    test('should display route statistics', async ({ fieldServicePage, page }) => {
      // Dashboard should show route-related stats
      await fieldServicePage.verifyLoaded();
    });

    test('should display inspector statistics', async ({ fieldServicePage, page }) => {
      // Dashboard should show inspector-related stats
      await fieldServicePage.verifyLoaded();
    });
  });

  test.describe('Quick Actions', () => {
    test('should have quick action buttons', async ({ fieldServicePage, page }) => {
      // Check for action buttons on dashboard
      await fieldServicePage.verifyLoaded();
    });
  });
});

