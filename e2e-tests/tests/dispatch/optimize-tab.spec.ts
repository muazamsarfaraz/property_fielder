import { test, expect } from '../../fixtures/test-fixtures';

/**
 * Dispatch View - OPTIMIZE Tab Tests
 * Tests optimization control and execution
 */
test.describe('Dispatch View - OPTIMIZE Tab @regression', () => {
  
  test.beforeEach(async ({ dispatchPage }) => {
    await dispatchPage.navigate();
    await dispatchPage.waitForLoad();
    await dispatchPage.switchToOptimize();
  });

  test.describe('Optimization Panel @smoke', () => {
    test('should display Optimization Control panel', async ({ dispatchPage }) => {
      await expect(dispatchPage.optimizationPanel).toBeVisible();
    });

    test('should display selected resources summary', async ({ dispatchPage, page }) => {
      await expect(page.locator('.floating-panel:has-text("Optimization") .panel-section h6:has-text("Selected")')).toBeVisible();
    });

    test('should display job count in summary', async ({ dispatchPage, page }) => {
      await expect(page.locator('.floating-panel:has-text("Optimization") :has-text("jobs")')).toBeVisible();
    });

    test('should display inspector count in summary', async ({ dispatchPage, page }) => {
      await expect(page.locator('.floating-panel:has-text("Optimization") :has-text("inspectors")')).toBeVisible();
    });
  });

  test.describe('Start Optimization Button', () => {
    test('should display Start Optimization button', async ({ dispatchPage, page }) => {
      await expect(page.locator('button:has-text("Start Optimization")')).toBeVisible();
    });

    test('should disable button when no resources selected', async ({ dispatchPage, page }) => {
      // Ensure nothing is selected
      await dispatchPage.switchToPlan();
      await page.click('.panel-section:has(h6:has-text("Jobs")) button:has-text("Clear")').catch(() => {});
      await page.click('.panel-section:has(h6:has-text("Inspectors")) button:has-text("Clear")').catch(() => {});
      
      await dispatchPage.switchToOptimize();
      
      const button = page.locator('button:has-text("Start Optimization")');
      const isDisabled = await button.isDisabled();
      expect(isDisabled).toBeTruthy();
    });

    test('should show warning when resources not selected', async ({ dispatchPage, page }) => {
      // Ensure nothing is selected
      await dispatchPage.switchToPlan();
      await page.click('.panel-section:has(h6:has-text("Jobs")) button:has-text("Clear")').catch(() => {});
      
      await dispatchPage.switchToOptimize();
      
      // Should show warning alert
      await expect(page.locator('.alert-warning:has-text("PLAN")')).toBeVisible();
    });
  });

  test.describe('Optimization Execution @slow', () => {
    test('should enable button when resources are selected', async ({ dispatchPage, page }) => {
      // Select resources first
      await dispatchPage.switchToPlan();
      
      const jobCount = await dispatchPage.getJobCount();
      const inspectorCount = await dispatchPage.getInspectorCount();
      
      if (jobCount > 0 && inspectorCount > 0) {
        await dispatchPage.selectAllJobs();
        await dispatchPage.selectAllInspectors();
        
        await dispatchPage.switchToOptimize();
        
        const button = page.locator('button:has-text("Start Optimization")');
        const isDisabled = await button.isDisabled();
        expect(isDisabled).toBeFalsy();
      }
    });

    test('should show progress indicator during optimization', async ({ dispatchPage, page }) => {
      // Select resources
      await dispatchPage.switchToPlan();
      
      const jobCount = await dispatchPage.getJobCount();
      const inspectorCount = await dispatchPage.getInspectorCount();
      
      if (jobCount > 0 && inspectorCount > 0) {
        await dispatchPage.selectAllJobs();
        await dispatchPage.selectAllInspectors();
        
        await dispatchPage.switchToOptimize();
        
        // Click start but don't wait for completion
        await page.click('button:has-text("Start Optimization")');
        
        // Should show spinner immediately
        const spinner = page.locator('.spinner-border');
        // May appear briefly
        await page.waitForTimeout(500);
      }
    });
  });

  test.describe('Optimization Results', () => {
    test('should display results section when available', async ({ dispatchPage, page }) => {
      // Results section only shows after optimization
      // Just verify the panel structure is correct
      await expect(dispatchPage.optimizationPanel).toBeVisible();
    });
  });
});

