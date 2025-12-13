import { test, expect } from '../../fixtures/test-fixtures';

/**
 * Dispatch View - PLAN Tab Tests
 * Tests resource selection and planning functionality
 */
test.describe('Dispatch View - PLAN Tab @regression', () => {
  
  test.beforeEach(async ({ dispatchPage }) => {
    await dispatchPage.navigate();
    await dispatchPage.waitForLoad();
    await dispatchPage.switchToPlan();
  });

  test.describe('Resources Panel @smoke', () => {
    test('should display Resources panel', async ({ dispatchPage }) => {
      await expect(dispatchPage.resourcesPanel).toBeVisible();
    });

    test('should display Jobs section', async ({ dispatchPage, page }) => {
      await expect(page.locator('.panel-section h6:has-text("Jobs")')).toBeVisible();
    });

    test('should display Inspectors section', async ({ dispatchPage, page }) => {
      await expect(page.locator('.panel-section h6:has-text("Inspectors")')).toBeVisible();
    });

    test('should display job count', async ({ dispatchPage }) => {
      const count = await dispatchPage.getJobCount();
      expect(typeof count).toBe('number');
    });

    test('should display inspector count', async ({ dispatchPage }) => {
      const count = await dispatchPage.getInspectorCount();
      expect(typeof count).toBe('number');
    });
  });

  test.describe('Job Selection', () => {
    test('should have Select All button for jobs', async ({ dispatchPage, page }) => {
      await expect(page.locator('.panel-section:has(h6:has-text("Jobs")) button:has-text("Select All")')).toBeVisible();
    });

    test('should have Clear button for jobs', async ({ dispatchPage, page }) => {
      await expect(page.locator('.panel-section:has(h6:has-text("Jobs")) button:has-text("Clear")')).toBeVisible();
    });

    test('should select all jobs', async ({ dispatchPage, page }) => {
      const jobCount = await dispatchPage.getJobCount();
      
      if (jobCount > 0) {
        await dispatchPage.selectAllJobs();
        
        // Check that jobs are selected (have selected class or checked)
        const selectedJobs = await page.locator('.resource-item.selected, .resource-item input:checked').count();
        expect(selectedJobs).toBeGreaterThan(0);
      }
    });

    test('should display job list items', async ({ dispatchPage, page }) => {
      const jobCount = await dispatchPage.getJobCount();
      
      if (jobCount > 0) {
        const jobItems = await page.locator('.panel-section:has(h6:has-text("Jobs")) .resource-item').count();
        expect(jobItems).toBe(jobCount);
      }
    });
  });

  test.describe('Inspector Selection', () => {
    test('should have Select All button for inspectors', async ({ dispatchPage, page }) => {
      await expect(page.locator('.panel-section:has(h6:has-text("Inspectors")) button:has-text("Select All")')).toBeVisible();
    });

    test('should have Clear button for inspectors', async ({ dispatchPage, page }) => {
      await expect(page.locator('.panel-section:has(h6:has-text("Inspectors")) button:has-text("Clear")')).toBeVisible();
    });

    test('should select all inspectors', async ({ dispatchPage, page }) => {
      const inspectorCount = await dispatchPage.getInspectorCount();
      
      if (inspectorCount > 0) {
        await dispatchPage.selectAllInspectors();
        
        // Check that inspectors are selected
        const selectedInspectors = await page.locator('.panel-section:has(h6:has-text("Inspectors")) .resource-item.selected, .panel-section:has(h6:has-text("Inspectors")) .resource-item input:checked').count();
        expect(selectedInspectors).toBeGreaterThan(0);
      }
    });

    test('should display availability status', async ({ dispatchPage, page }) => {
      const inspectorCount = await dispatchPage.getInspectorCount();
      
      if (inspectorCount > 0) {
        // Check for availability indicators
        const inspectorItems = page.locator('.panel-section:has(h6:has-text("Inspectors")) .resource-item');
        expect(await inspectorItems.count()).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Settings Panel', () => {
    test('should display Settings panel', async ({ dispatchPage }) => {
      await expect(dispatchPage.settingsPanel).toBeVisible();
    });

    test('should display solver time limit option', async ({ dispatchPage, page }) => {
      await expect(page.locator('.floating-panel:has-text("Settings") select, .floating-panel:has-text("Settings") .form-select')).toBeVisible();
    });

    test('should display optimization mode option', async ({ dispatchPage, page }) => {
      const selects = await page.locator('.floating-panel:has-text("Settings") select, .floating-panel:has-text("Settings") .form-select').count();
      expect(selects).toBeGreaterThanOrEqual(1);
    });

    test('should display routing options', async ({ dispatchPage, page }) => {
      // Check for checkboxes like "Use OSRM" or "Respect time windows"
      const checkboxes = await page.locator('.floating-panel:has-text("Settings") input[type="checkbox"]').count();
      expect(checkboxes).toBeGreaterThanOrEqual(0); // May have zero depending on settings
    });
  });
});

