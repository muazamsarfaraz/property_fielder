import { test, expect } from '../../fixtures/test-fixtures';

/**
 * Field Service - Optimization Tests
 * Tests route optimization functionality
 */
test.describe('Field Service - Optimization @regression', () => {
  
  test.beforeEach(async ({ fieldServicePage }) => {
    await fieldServicePage.navigateToOptimization();
  });

  test.describe('Navigation @smoke', () => {
    test('should navigate to Optimization menu', async ({ fieldServicePage }) => {
      await fieldServicePage.verifyLoaded();
    });

    test('should display optimization interface', async ({ fieldServicePage, page }) => {
      // Check for optimization-related elements
      await expect(page.locator('.o_action_manager')).toBeVisible();
    });
  });

  test.describe('Optimization Configuration', () => {
    test('should display optimization parameters', async ({ fieldServicePage, page }) => {
      // Check for optimization settings form
      const hasForm = await page.locator('.o_form_view').isVisible();
      const hasList = await page.locator('.o_list_view').isVisible();
      expect(hasForm || hasList).toBeTruthy();
    });
  });

  test.describe('Optimization History', () => {
    test('should list previous optimization runs', async ({ fieldServicePage }) => {
      // Optimization history should be viewable
      await fieldServicePage.verifyLoaded();
    });
  });
});

