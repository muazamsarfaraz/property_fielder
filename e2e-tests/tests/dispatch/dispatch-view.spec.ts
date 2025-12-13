import { test, expect } from '../../fixtures/test-fixtures';

/**
 * Dispatch View Tests
 * Tests the enhanced dispatch view with PLAN/OPTIMIZE/SCHEDULE tabs
 */
test.describe('Dispatch View @regression', () => {
  
  test.beforeEach(async ({ dispatchPage }) => {
    await dispatchPage.navigate();
    await dispatchPage.waitForLoad();
  });

  test.describe('Navigation @smoke @critical', () => {
    test('should navigate to Dispatch view', async ({ dispatchPage }) => {
      await expect(dispatchPage.dispatchContainer).toBeVisible();
    });

    test('should display dispatch navbar', async ({ dispatchPage }) => {
      await expect(dispatchPage.navbar).toBeVisible();
    });

    test('should display all three tabs', async ({ dispatchPage }) => {
      await expect(dispatchPage.planTab).toBeVisible();
      await expect(dispatchPage.optimizeTab).toBeVisible();
      await expect(dispatchPage.scheduleTab).toBeVisible();
    });

    test('should display date selector', async ({ dispatchPage }) => {
      await expect(dispatchPage.dateInput).toBeVisible();
    });

    test('should display refresh button', async ({ dispatchPage }) => {
      await expect(dispatchPage.refreshButton).toBeVisible();
    });
  });

  test.describe('Tab Navigation', () => {
    test('should start on PLAN tab', async ({ dispatchPage }) => {
      const activeTab = await dispatchPage.getActiveTab();
      expect(activeTab).toContain('PLAN');
    });

    test('should switch to OPTIMIZE tab', async ({ dispatchPage }) => {
      await dispatchPage.switchToOptimize();
      const activeTab = await dispatchPage.getActiveTab();
      expect(activeTab).toContain('OPTIMIZE');
    });

    test('should switch to SCHEDULE tab', async ({ dispatchPage }) => {
      await dispatchPage.switchToSchedule();
      const activeTab = await dispatchPage.getActiveTab();
      expect(activeTab).toContain('SCHEDULE');
    });

    test('should switch back to PLAN tab', async ({ dispatchPage }) => {
      await dispatchPage.switchToSchedule();
      await dispatchPage.switchToPlan();
      const activeTab = await dispatchPage.getActiveTab();
      expect(activeTab).toContain('PLAN');
    });
  });

  test.describe('Map Display', () => {
    test('should display map container', async ({ dispatchPage }) => {
      await dispatchPage.verifyMapDisplayed();
    });

    test('should persist map across tab switches', async ({ dispatchPage }) => {
      await dispatchPage.verifyMapDisplayed();
      
      await dispatchPage.switchToOptimize();
      await dispatchPage.verifyMapDisplayed();
      
      await dispatchPage.switchToSchedule();
      await dispatchPage.verifyMapDisplayed();
    });
  });

  test.describe('Date Selection', () => {
    test('should change date', async ({ dispatchPage }) => {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const dateStr = tomorrow.toISOString().split('T')[0];
      
      await dispatchPage.setDate(dateStr);
      
      const currentValue = await dispatchPage.dateInput.inputValue();
      expect(currentValue).toBe(dateStr);
    });

    test('should refresh data on date change', async ({ dispatchPage, page }) => {
      // Monitor network activity
      let requestMade = false;
      page.on('request', (request) => {
        if (request.url().includes('/web/dataset/call_kw')) {
          requestMade = true;
        }
      });

      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      const dateStr = yesterday.toISOString().split('T')[0];
      
      await dispatchPage.setDate(dateStr);
      
      // Allow time for request
      await page.waitForTimeout(1000);
      expect(requestMade).toBeTruthy();
    });
  });

  test.describe('Refresh Functionality', () => {
    test('should refresh data on button click', async ({ dispatchPage, page }) => {
      let requestMade = false;
      page.on('request', (request) => {
        if (request.url().includes('/web/dataset/call_kw')) {
          requestMade = true;
        }
      });

      await dispatchPage.refresh();
      
      await page.waitForTimeout(1000);
      expect(requestMade).toBeTruthy();
    });
  });
});

