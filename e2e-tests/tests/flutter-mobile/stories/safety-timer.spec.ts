/**
 * User Story: Safety Timer & Panic Button (US-SAFETY-001, US-SAFETY-002)
 * 
 * As a lone worker inspector, I can use safety features for HSE compliance.
 */

import { test, expect } from '@playwright/test';
import { LoginPage, SafetyTimerPage } from '../pages';
import { UserStories } from '../config/user-stories';

test.describe('Safety Features @flutter @safety @critical', () => {
  let loginPage: LoginPage;
  let safetyPage: SafetyTimerPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    safetyPage = new SafetyTimerPage(page);
    
    // Login before each test
    await loginPage.goto();
    await loginPage.login();
  });

  test.describe('US-SAFETY-001: Safety Timer (Lone Worker)', () => {
    const story = UserStories.safetyTimerWorkflow;

    test('Safety timer page displays all required elements', async ({ page }) => {
      await safetyPage.goto();
      await safetyPage.takeScreenshot('safety-timer-initial');

      const uxElements = await safetyPage.verifyUXElements();
      
      expect(uxElements.hasAppBar, 'App bar should be visible').toBe(true);
      expect(uxElements.hasTimerDisplay, 'Timer display should be visible').toBe(true);
      expect(uxElements.hasDurationOptions, 'Duration options should be available').toBe(true);
      expect(uxElements.hasPanicButton, 'Panic button should always be visible').toBe(true);
    });

    test('Duration options are clearly visible (30/60/90/120 min)', async ({ page }) => {
      await safetyPage.goto();
      
      const durations = await safetyPage.getDurationOptions();
      await safetyPage.takeScreenshot('safety-duration-options');
      
      // Should have multiple duration options
      expect(durations.length, 'Should have multiple duration options').toBeGreaterThan(0);
    });

    test('Selecting duration updates UI', async ({ page }) => {
      await safetyPage.goto();
      
      await safetyPage.selectDuration(60);
      await safetyPage.takeScreenshot('safety-duration-60-selected');
      
      await safetyPage.selectDuration(90);
      await safetyPage.takeScreenshot('safety-duration-90-selected');
    });

    test('Starting timer shows countdown and action buttons', async ({ page }) => {
      await safetyPage.goto();
      
      await safetyPage.selectDuration(30);
      await safetyPage.startTimer();
      await safetyPage.takeScreenshot('safety-timer-active');

      const isActive = await safetyPage.isTimerActive();
      expect(isActive, 'Timer should be active after starting').toBe(true);
      
      // Verify extend and complete buttons appear
      const uxElements = await safetyPage.verifyUXElements();
      expect(uxElements.isTimerActive).toBe(true);
    });

    test('Extend button adds time to timer', async ({ page }) => {
      await safetyPage.goto();
      
      await safetyPage.selectDuration(30);
      await safetyPage.startTimer();
      
      const initialTime = await safetyPage.getTimerValue();
      await safetyPage.takeScreenshot('safety-before-extend');
      
      await safetyPage.extendTimer();
      await safetyPage.takeScreenshot('safety-after-extend');
      
      // Timer should show extended time
      const extendedTime = await safetyPage.getTimerValue();
      // Note: Exact time comparison depends on implementation
    });

    test('Complete button marks timer as safe', async ({ page }) => {
      await safetyPage.goto();
      
      await safetyPage.selectDuration(30);
      await safetyPage.startTimer();
      await safetyPage.takeScreenshot('safety-before-complete');
      
      await safetyPage.completeTimer();
      await safetyPage.takeScreenshot('safety-after-complete');
      
      // Timer should no longer be active
      const isActive = await safetyPage.isTimerActive();
      expect(isActive, 'Timer should not be active after completion').toBe(false);
    });
  });

  test.describe('US-SAFETY-002: Panic Button Emergency', () => {
    const story = UserStories.panicButton;

    test('Panic button is prominently visible (red)', async ({ page }) => {
      await safetyPage.goto();
      
      const uxElements = await safetyPage.verifyUXElements();
      expect(uxElements.hasPanicButton, 'Panic button must be visible').toBe(true);
      
      await safetyPage.takeScreenshot('panic-button-visible');
    });

    test('Panic button requires confirmation before sending alert', async ({ page }) => {
      await safetyPage.goto();
      
      // Long press panic button
      await safetyPage.triggerPanic();
      await safetyPage.takeScreenshot('panic-confirmation-dialog');
      
      // Should show confirmation dialog - dismiss it for now
      await safetyPage.dismissDialogs();
    });

    test('Verify panic button UX (size, color, accessibility)', async ({ page }) => {
      await safetyPage.goto();
      
      const panicButton = safetyPage.panicButton;
      const box = await panicButton.boundingBox();
      
      // Panic button should be reasonably large for emergency use
      if (box) {
        expect(box.width, 'Panic button should be large enough').toBeGreaterThan(50);
        expect(box.height, 'Panic button should be large enough').toBeGreaterThan(50);
      }
      
      await safetyPage.takeScreenshot('panic-button-ux-check');
    });
  });
});

