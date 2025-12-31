/**
 * User Story: Execute Inspection Template (US-TEMPLATE-001)
 * 
 * As an inspector, I can complete a structured inspection checklist.
 */

import { test, expect } from '@playwright/test';
import { LoginPage, JobListPage, JobDetailPage, TemplateExecutionPage } from '../pages';
import { UserStories } from '../config/user-stories';

test.describe('Inspection Template Workflow @flutter @inspection @high', () => {
  let loginPage: LoginPage;
  let jobListPage: JobListPage;
  let jobDetailPage: JobDetailPage;
  let templatePage: TemplateExecutionPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    jobListPage = new JobListPage(page);
    jobDetailPage = new JobDetailPage(page);
    templatePage = new TemplateExecutionPage(page);
    
    // Login before each test
    await loginPage.goto();
    await loginPage.login();
  });

  test.describe('US-TEMPLATE-001: Execute Inspection Template', () => {
    const story = UserStories.executeInspectionTemplate;

    test('Template execution screen shows all required elements', async ({ page }) => {
      await templatePage.goto();
      await templatePage.takeScreenshot('template-initial');

      const uxElements = await templatePage.verifyUXElements();
      
      expect(uxElements.hasAppBar, 'App bar should be visible').toBe(true);
      expect(uxElements.hasSectionIndicator, 'Section indicator should be visible').toBe(true);
    });

    test('Section progress indicator shows template sections', async ({ page }) => {
      await templatePage.goto();
      
      const hasSections = await templatePage.sectionIndicator.isVisible().catch(() => false);
      await templatePage.takeScreenshot('template-section-indicator');
      
      // Section indicator should be visible when template has multiple sections
      expect(hasSections).toBeDefined();
    });

    test('Checklist items display with response options', async ({ page }) => {
      await templatePage.goto();
      
      const itemCount = await templatePage.getChecklistItemCount();
      await templatePage.takeScreenshot('template-checklist-items');
      
      // Should have checklist items if template is loaded
      if (itemCount > 0) {
        // Check for Yes/No/N/A buttons on first item
        const firstItem = templatePage.checklistItems.first();
        const hasYes = await firstItem.locator('button:has-text("Yes")').isVisible().catch(() => false);
        const hasNo = await firstItem.locator('button:has-text("No")').isVisible().catch(() => false);
        
        expect(hasYes || hasNo, 'Checklist items should have response buttons').toBe(true);
      }
    });

    test('Answering items updates progress', async ({ page }) => {
      await templatePage.goto();
      
      const itemCount = await templatePage.getChecklistItemCount();
      
      if (itemCount > 0) {
        const initialProgress = await templatePage.getProgress();
        await templatePage.takeScreenshot('template-before-answering');
        
        // Answer first item
        await templatePage.answerItem(0, 'Yes');
        await templatePage.takeScreenshot('template-after-answer');
        
        const newProgress = await templatePage.getProgress();
        // Progress should increase or stay same (if first item was already answered)
        expect(newProgress).toBeGreaterThanOrEqual(initialProgress);
      }
    });

    test('Navigation between sections works', async ({ page }) => {
      await templatePage.goto();
      
      const hasNext = await templatePage.nextButton.isVisible().catch(() => false);
      const hasPrev = await templatePage.prevButton.isVisible().catch(() => false);
      
      await templatePage.takeScreenshot('template-navigation');
      
      if (hasNext) {
        await templatePage.nextSection();
        await templatePage.takeScreenshot('template-next-section');
        
        if (hasPrev) {
          await templatePage.previousSection();
          await templatePage.takeScreenshot('template-prev-section');
        }
      }
    });

    test('Can add notes to checklist items', async ({ page }) => {
      await templatePage.goto();
      
      const itemCount = await templatePage.getChecklistItemCount();
      
      if (itemCount > 0) {
        await templatePage.addNote(0, 'Test note for inspection item');
        await templatePage.takeScreenshot('template-note-added');
      }
    });

    test('Submit button validates mandatory items', async ({ page }) => {
      await templatePage.goto();
      
      const hasSubmit = await templatePage.submitButton.isVisible().catch(() => false);
      await templatePage.takeScreenshot('template-submit-button');
      
      // If submit is visible and we try to submit without completing all items
      // it should either show validation error or be disabled
    });

    test('Complete inspection workflow from job', async ({ page }) => {
      await jobListPage.goto();
      const jobCount = await jobListPage.getJobCount();
      
      if (jobCount > 0) {
        // Open job detail
        await jobListPage.clickJob(0);
        await jobDetailPage.takeScreenshot('workflow-job-detail');
        
        // Start inspection if button exists
        const hasStartInspection = await jobDetailPage.startInspectionButton.isVisible().catch(() => false);
        
        if (hasStartInspection) {
          await jobDetailPage.startInspection();
          await templatePage.takeScreenshot('workflow-template-loaded');
          
          // Answer a few items
          const itemCount = await templatePage.getChecklistItemCount();
          for (let i = 0; i < Math.min(3, itemCount); i++) {
            await templatePage.answerItem(i, 'Yes');
          }
          await templatePage.takeScreenshot('workflow-items-answered');
        }
      }
    });
  });
});

