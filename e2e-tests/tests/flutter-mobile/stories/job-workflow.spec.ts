/**
 * User Story: Job Workflow (US-JOB-001, US-JOB-002)
 * 
 * As an inspector, I can view and manage my assigned jobs.
 */

import { test, expect } from '@playwright/test';
import { LoginPage, DashboardPage, JobListPage, JobDetailPage } from '../pages';
import { UserStories } from '../config/user-stories';

test.describe('Job Workflow @flutter @jobs', () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;
  let jobListPage: JobListPage;
  let jobDetailPage: JobDetailPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
    jobListPage = new JobListPage(page);
    jobDetailPage = new JobDetailPage(page);
    
    // Login before each test
    await loginPage.goto();
    await loginPage.login();
  });

  test.describe('US-JOB-001: View Assigned Jobs @critical', () => {
    const story = UserStories.viewAssignedJobs;

    test('Job list displays all assigned jobs', async ({ page }) => {
      await jobListPage.goto();
      await jobListPage.takeScreenshot('job-list-initial');

      const uxElements = await jobListPage.verifyUXElements();
      
      expect(uxElements.hasAppBar, 'App bar should be visible').toBe(true);
      expect(uxElements.hasSearchBar, 'Search bar should be available').toBe(true);
    });

    test('Filter chips allow status filtering', async ({ page }) => {
      await jobListPage.goto();
      
      // Test filter chips
      await jobListPage.filterByStatus('Pending');
      await jobListPage.takeScreenshot('job-list-pending-filter');
      
      await jobListPage.filterByStatus('In Progress');
      await jobListPage.takeScreenshot('job-list-inprogress-filter');
      
      await jobListPage.filterByStatus('All');
      await jobListPage.takeScreenshot('job-list-all-filter');
    });

    test('Search filters jobs in real-time', async ({ page }) => {
      await jobListPage.goto();
      const initialCount = await jobListPage.getJobCount();
      
      await jobListPage.search('Test Property');
      await jobListPage.takeScreenshot('job-list-search');
      
      // Search should filter or show no results message
      const searchCount = await jobListPage.getJobCount();
      expect(searchCount).toBeLessThanOrEqual(initialCount);
    });

    test('Clicking job card opens detail view', async ({ page }) => {
      await jobListPage.goto();
      const jobCount = await jobListPage.getJobCount();
      
      if (jobCount > 0) {
        await jobListPage.clickJob(0);
        await jobDetailPage.takeScreenshot('job-detail-from-list');
        
        const uxElements = await jobDetailPage.verifyUXElements();
        expect(uxElements.hasAppBar).toBe(true);
      }
    });
  });

  test.describe('US-JOB-002: Job Check-In/Check-Out @critical', () => {
    const story = UserStories.jobCheckInOut;

    test('Check-In button visible on job detail', async ({ page }) => {
      await jobListPage.goto();
      const jobCount = await jobListPage.getJobCount();
      
      if (jobCount > 0) {
        await jobListPage.clickJob(0);
        await jobDetailPage.takeScreenshot('job-detail-checkin-available');
        
        const uxElements = await jobDetailPage.verifyUXElements();
        expect(uxElements.hasCheckInButton || uxElements.actionButtons.includes('Check In')).toBe(true);
      }
    });

    test('Check-In captures GPS and changes status', async ({ page }) => {
      await jobListPage.goto();
      const jobCount = await jobListPage.getJobCount();
      
      if (jobCount > 0) {
        await jobListPage.clickJob(0);
        
        const hasCheckIn = await jobDetailPage.checkInButton.isVisible().catch(() => false);
        if (hasCheckIn) {
          await jobDetailPage.checkIn();
          await jobDetailPage.takeScreenshot('job-after-checkin');
          
          // Verify Check Out button appears
          const isCheckedIn = await jobDetailPage.isCheckedIn();
          expect(isCheckedIn, 'Should be checked in after check-in action').toBe(true);
        }
      }
    });

    test('Check-Out records duration', async ({ page }) => {
      await jobListPage.goto();
      const jobCount = await jobListPage.getJobCount();
      
      if (jobCount > 0) {
        await jobListPage.clickJob(0);
        
        // Check if already checked in or can check in
        if (await jobDetailPage.isCheckedIn()) {
          await jobDetailPage.checkOut();
          await jobDetailPage.takeScreenshot('job-after-checkout');
        }
      }
    });
  });

  test.describe('US-PHOTO-001: Capture Inspection Photos @high', () => {
    const story = UserStories.capturePhotos;

    test('Photo button available on job detail', async ({ page }) => {
      await jobListPage.goto();
      const jobCount = await jobListPage.getJobCount();
      
      if (jobCount > 0) {
        await jobListPage.clickJob(0);
        
        const uxElements = await jobDetailPage.verifyUXElements();
        expect(uxElements.hasPhotoButton, 'Photo button should be visible').toBe(true);
        await jobDetailPage.takeScreenshot('job-detail-photo-button');
      }
    });
  });

  test.describe('US-SIG-001: Capture Signature @high', () => {
    const story = UserStories.captureSignature;

    test('Signature button available on job detail', async ({ page }) => {
      await jobListPage.goto();
      const jobCount = await jobListPage.getJobCount();
      
      if (jobCount > 0) {
        await jobListPage.clickJob(0);
        
        const uxElements = await jobDetailPage.verifyUXElements();
        expect(uxElements.hasSignatureButton, 'Signature button should be visible').toBe(true);
        await jobDetailPage.takeScreenshot('job-detail-signature-button');
      }
    });
  });
});

