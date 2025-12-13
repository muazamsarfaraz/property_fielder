import { test, expect } from '../../fixtures/test-fixtures';

/**
 * Dispatch View - SCHEDULE Tab Tests
 * Tests route viewing and timeline functionality
 */
test.describe('Dispatch View - SCHEDULE Tab @regression', () => {
  
  test.beforeEach(async ({ dispatchPage }) => {
    await dispatchPage.navigate();
    await dispatchPage.waitForLoad();
    await dispatchPage.switchToSchedule();
  });

  test.describe('Route Details Panel @smoke', () => {
    test('should display Routes panel', async ({ dispatchPage }) => {
      await expect(dispatchPage.routeDetailsPanel).toBeVisible();
    });

    test('should display panel header', async ({ dispatchPage, page }) => {
      await expect(page.locator('.floating-panel:has-text("Routes") .floating-panel-header')).toBeVisible();
    });

    test('should display date in routes section', async ({ dispatchPage, page }) => {
      await expect(page.locator('.floating-panel:has-text("Routes") h6')).toBeVisible();
    });
  });

  test.describe('Route List', () => {
    test('should display route list container', async ({ dispatchPage, page }) => {
      await expect(page.locator('.route-list')).toBeVisible();
    });

    test('should show info when no routes exist', async ({ dispatchPage, page }) => {
      const routeCount = await dispatchPage.getRouteCount();
      
      if (routeCount === 0) {
        // Should show info message
        await expect(page.locator('.alert-info:has-text("No routes")')).toBeVisible();
      }
    });

    test('should display route items when routes exist', async ({ dispatchPage, page }) => {
      const routeCount = await dispatchPage.getRouteCount();
      
      if (routeCount > 0) {
        const routeItems = await page.locator('.route-item').count();
        expect(routeItems).toBe(routeCount);
      }
    });

    test('should display route name in each item', async ({ dispatchPage, page }) => {
      const routeCount = await dispatchPage.getRouteCount();
      
      if (routeCount > 0) {
        await expect(page.locator('.route-item .route-name').first()).toBeVisible();
      }
    });

    test('should display route status badge', async ({ dispatchPage, page }) => {
      const routeCount = await dispatchPage.getRouteCount();
      
      if (routeCount > 0) {
        await expect(page.locator('.route-item .badge').first()).toBeVisible();
      }
    });

    test('should display inspector info', async ({ dispatchPage, page }) => {
      const routeCount = await dispatchPage.getRouteCount();
      
      if (routeCount > 0) {
        await expect(page.locator('.route-item .route-meta').first()).toBeVisible();
      }
    });

    test('should display job count per route', async ({ dispatchPage, page }) => {
      const routeCount = await dispatchPage.getRouteCount();
      
      if (routeCount > 0) {
        await expect(page.locator('.route-item .route-meta :has-text("jobs")').first()).toBeVisible();
      }
    });
  });

  test.describe('Route Selection', () => {
    test('should highlight selected route', async ({ dispatchPage, page }) => {
      const routeCount = await dispatchPage.getRouteCount();
      
      if (routeCount > 0) {
        await page.locator('.route-item').first().click();
        
        await expect(page.locator('.route-item.selected')).toBeVisible();
      }
    });

    test('should allow switching between routes', async ({ dispatchPage, page }) => {
      const routeCount = await dispatchPage.getRouteCount();
      
      if (routeCount > 1) {
        // Select first route
        await page.locator('.route-item').nth(0).click();
        await expect(page.locator('.route-item').nth(0)).toHaveClass(/selected/);
        
        // Select second route
        await page.locator('.route-item').nth(1).click();
        await expect(page.locator('.route-item').nth(1)).toHaveClass(/selected/);
      }
    });
  });

  test.describe('Timeline Display', () => {
    test('should display timeline container', async ({ dispatchPage }) => {
      await dispatchPage.verifyTimelineDisplayed();
    });

    test('should display timeline widget', async ({ dispatchPage, page }) => {
      await expect(page.locator('.dispatch-timeline-container')).toBeVisible();
    });
  });

  test.describe('Panel Close Button', () => {
    test('should have close button on routes panel', async ({ dispatchPage, page }) => {
      await expect(page.locator('.floating-panel:has-text("Routes") .floating-panel-header button')).toBeVisible();
    });

    test('should close panel when close button clicked', async ({ dispatchPage, page }) => {
      await page.locator('.floating-panel:has-text("Routes") .floating-panel-header button:has(.fa-times)').click();
      
      await expect(dispatchPage.routeDetailsPanel).not.toBeVisible();
    });
  });
});

