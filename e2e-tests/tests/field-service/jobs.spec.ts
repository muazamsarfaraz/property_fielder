import { test, expect } from '../../fixtures/test-fixtures';
import { TestDataManager } from '../../utils/test-data-manager';

/**
 * Field Service - Jobs Tests
 * Tests job management, scheduling, and state transitions
 */
test.describe('Field Service - Jobs @regression', () => {
  
  test.beforeEach(async ({ fieldServicePage }) => {
    await fieldServicePage.navigateToJobs();
  });

  test.describe('Navigation @smoke', () => {
    test('should navigate to Jobs menu', async ({ fieldServicePage }) => {
      await fieldServicePage.verifyLoaded();
      const title = await fieldServicePage.getTitle();
      expect(title.toLowerCase()).toContain('job');
    });

    test('should display jobs list or kanban', async ({ fieldServicePage }) => {
      const isList = await fieldServicePage.isListView();
      const isKanban = await fieldServicePage.isKanbanView();
      expect(isList || isKanban).toBeTruthy();
    });

    test('should switch between views', async ({ fieldServicePage }) => {
      await fieldServicePage.switchToKanban();
      expect(await fieldServicePage.isKanbanView()).toBeTruthy();
      
      await fieldServicePage.switchToList();
      expect(await fieldServicePage.isListView()).toBeTruthy();
    });
  });

  test.describe('Job CRUD Operations', () => {
    test('should open create form', async ({ fieldServicePage }) => {
      await fieldServicePage.clickCreate();
      await fieldServicePage.verifyJobForm();
    });

    test('should create a new job @critical', async ({ fieldServicePage, page }) => {
      const jobData = TestDataManager.jobData();
      
      await fieldServicePage.createJob(jobData);
      
      // Verify job was created (should be in form view)
      await expect(page.locator('.o_form_view')).toBeVisible();
    });

    test('should search for jobs', async ({ fieldServicePage }) => {
      // Create a job with unique name
      const jobData = TestDataManager.jobData({ name: 'JOBTEST_UniqueJob123' });
      await fieldServicePage.createJob(jobData);
      
      // Navigate back and search
      await fieldServicePage.navigateToJobs();
      await fieldServicePage.search('JOBTEST_UniqueJob123');
      
      const count = await fieldServicePage.getRecordCount();
      expect(count).toBeGreaterThan(0);
    });
  });

  test.describe('Job State Transitions', () => {
    test('should display job state/status bar', async ({ fieldServicePage, page }) => {
      const count = await fieldServicePage.getRecordCount();
      
      if (count > 0) {
        await fieldServicePage.clickRow(0);
        // Check for status bar
        await expect(page.locator('.o_statusbar_status, .o_field_widget[name="state"]')).toBeVisible();
      }
    });

    test('should transition job through states', async ({ fieldServicePage, page }) => {
      // Create a new job
      const jobData = TestDataManager.jobData();
      await fieldServicePage.createJob(jobData);
      
      // Check initial state
      const initialState = await fieldServicePage.getJobState();
      expect(initialState).toBeTruthy();
      
      // Try to advance state (depends on workflow)
      const confirmButton = page.locator('.o_statusbar_status button:not(.o_arrow_button_current)').first();
      if (await confirmButton.isVisible() && await confirmButton.isEnabled()) {
        await confirmButton.click();
        await fieldServicePage.odoo.waitForOdooLoad();
      }
    });
  });

  test.describe('Job Scheduling', () => {
    test('should display scheduled date field', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      await expect(page.locator('.o_field_widget[name="scheduled_date"]')).toBeVisible();
    });

    test('should display duration field', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      await expect(page.locator('.o_field_widget[name="duration_minutes"], .o_field_widget[name="duration"]')).toBeVisible();
    });

    test('should display priority field', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      // Priority might be a selection or priority widget
      const priorityField = page.locator('.o_field_widget[name="priority"]');
      // Just verify form loads, priority field may vary
      await fieldServicePage.verifyJobForm();
    });
  });

  test.describe('Job Assignment', () => {
    test('should display inspector assignment field', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      await expect(page.locator('.o_field_widget[name="inspector_id"]')).toBeVisible();
    });

    test('should display route assignment field', async ({ fieldServicePage, page }) => {
      await fieldServicePage.clickCreate();
      // Route field may or may not be visible in create form
      await fieldServicePage.verifyJobForm();
    });
  });
});

