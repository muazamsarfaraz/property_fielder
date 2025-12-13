/**
 * Test for Dispatch View Test Data Buttons
 * 
 * Tests the Load Test Data and Delete Test Data functionality
 * accessible from the Dispatch view's Test Data dropdown menu.
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.ODOO_URL || 'http://localhost:8069';
const USERNAME = process.env.ODOO_USERNAME || 'admin';
const PASSWORD = process.env.ODOO_PASSWORD || 'admin';

async function waitForOdooLoad(page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(300);
  const loadingOverlay = page.locator('.o_loading');
  if (await loadingOverlay.isVisible({ timeout: 500 }).catch(() => false)) {
    await loadingOverlay.waitFor({ state: 'hidden', timeout: 30000 });
  }
}

async function login(page) {
  await page.goto(`${BASE_URL}/web/login`);
  await page.fill('input[name="login"]', USERNAME);
  await page.fill('input[name="password"]', PASSWORD);
  await page.click('button[type="submit"]');
  await waitForOdooLoad(page);
}

async function navigateToDispatch(page) {
  const homeBtn = page.locator('button[title="Home Menu"]');
  await homeBtn.click();
  await page.waitForTimeout(500);
  await page.getByRole('menuitem', { name: 'Field Service' }).click();
  await waitForOdooLoad(page);
  
  const dispatchMenu = page.getByRole('menuitem', { name: 'Dispatch' });
  if (await dispatchMenu.isVisible({ timeout: 2000 }).catch(() => false)) {
    await dispatchMenu.click();
    await waitForOdooLoad(page);
  }
}

test.describe('Dispatch Test Data Buttons', () => {
  test.describe.configure({ mode: 'serial' });

  test('1. Navigate to Dispatch and find Test Data dropdown', async ({ page }) => {
    test.setTimeout(60000);
    await login(page);
    await navigateToDispatch(page);

    // Wait for dispatch view and map to fully load
    await page.waitForTimeout(3000);

    // Wait for the Resources panel to be visible (Plan tab should show it)
    const resourcesPanel = page.locator('.floating-panel:has-text("Resources")');
    await expect(resourcesPanel).toBeVisible({ timeout: 10000 });

    // Take screenshot of dispatch view with panels visible
    await page.screenshot({ path: 'test-results/dispatch-view.png', fullPage: true });

    // Find the Test Data dropdown button (flask icon button - ghost style)
    const testDataBtn = page.locator('button.btn-ghost.dropdown-toggle');
    await expect(testDataBtn).toBeVisible({ timeout: 10000 });

    // Click to open dropdown and take screenshot
    await testDataBtn.click();
    await page.waitForTimeout(300);
    await page.screenshot({ path: 'test-results/dispatch-dropdown-open.png', fullPage: true });

    console.log('Test Data dropdown button found');
  });

  test('2. Load Test Data via dropdown menu', async ({ page }) => {
    test.setTimeout(120000);
    await login(page);
    await navigateToDispatch(page);
    await page.waitForTimeout(2000);

    // Click the Test Data dropdown (flask icon button)
    const testDataBtn = page.locator('button.btn-ghost.dropdown-toggle');
    await testDataBtn.click();
    await page.waitForTimeout(300);

    // Click "Load 20 Test Jobs"
    const loadBtn = page.locator('a:has-text("Load 20 Test Jobs")');
    await expect(loadBtn).toBeVisible({ timeout: 5000 });
    await loadBtn.click();

    // Wait for the loading to complete - notification should appear
    await page.waitForTimeout(3000);

    // Take screenshot after loading (shows notification)
    await page.screenshot({ path: 'test-results/dispatch-after-load.png', fullPage: true });

    // Check for success notification
    const notification = page.locator('.o_notification');
    const notificationText = await notification.textContent().catch(() => '');
    console.log(`Notification: ${notificationText}`);

    // Wait for data to load and map to animate to fit bounds
    await page.waitForTimeout(6000);

    // Verify jobs were created by checking the Jobs panel
    const jobsHeading = page.locator('h6:has-text("Jobs")');
    const headingText = await jobsHeading.textContent().catch(() => '');
    console.log(`Jobs heading: ${headingText}`);

    // Should have created jobs
    const match = headingText?.match(/Jobs \((\d+)\)/);
    const jobCount = match ? parseInt(match[1], 10) : 0;
    console.log(`Jobs on map: ${jobCount}`);

    // Take screenshot with jobs loaded and map zoomed to fit
    await page.screenshot({ path: 'test-results/dispatch-jobs-loaded.png', fullPage: true });

    expect(jobCount).toBeGreaterThan(0);
  });

  test('3. Click on map pin and verify popup appears', async ({ page }) => {
    test.setTimeout(120000);
    await login(page);
    await navigateToDispatch(page);
    await page.waitForTimeout(3000);

    // Wait for the map to be loaded
    const mapContainer = page.locator('.mapboxgl-map');
    await expect(mapContainer).toBeVisible({ timeout: 10000 });

    // Wait for job pins to appear on the map
    const jobPins = page.locator('.job-pin-marker');
    const pinCount = await jobPins.count();
    console.log(`Found ${pinCount} job pins on map`);

    if (pinCount === 0) {
      // Load test data first if no pins
      console.log('No pins found, loading test data...');
      const testDataBtn = page.locator('button.btn-ghost.dropdown-toggle');
      await testDataBtn.click();
      await page.waitForTimeout(300);
      const loadBtn = page.locator('a:has-text("Load 20 Test Jobs")');
      await loadBtn.click();
      await page.waitForTimeout(6000);
    }

    // Wait for pins to be visible
    await expect(page.locator('.job-pin-marker').first()).toBeVisible({ timeout: 15000 });

    const pinsAfter = page.locator('.job-pin-marker');
    const pinCountAfter = await pinsAfter.count();
    console.log(`Pins after loading: ${pinCountAfter}`);

    // Click on the first visible pin
    const firstPin = page.locator('.job-pin-marker').first();
    await firstPin.click();
    await page.waitForTimeout(500);

    // Verify popup appears
    const popup = page.locator('.mapboxgl-popup');
    await expect(popup).toBeVisible({ timeout: 5000 });

    // Verify popup content has job info
    const popupContent = page.locator('.mapboxgl-popup-content');
    const popupText = await popupContent.textContent().catch(() => '');
    console.log(`Popup content: ${popupText}`);

    // Take screenshot showing popup
    await page.screenshot({ path: 'test-results/dispatch-pin-popup.png', fullPage: true });

    // Popup should contain customer/status info
    expect(popupText).toContain('Customer');
    expect(popupText).toContain('Status');

    // Close popup by clicking elsewhere
    await mapContainer.click({ position: { x: 50, y: 50 } });
    await page.waitForTimeout(300);
  });

  test('4. Delete Test Data via dropdown menu', async ({ page }) => {
    test.setTimeout(120000);
    await login(page);
    await navigateToDispatch(page);
    await page.waitForTimeout(2000);

    // Set up dialog handler to accept the confirmation
    page.on('dialog', async dialog => {
      console.log(`Dialog message: ${dialog.message()}`);
      await dialog.accept();
    });

    // Click the Test Data dropdown (flask icon button)
    const testDataBtn = page.locator('button.btn-ghost.dropdown-toggle');
    await testDataBtn.click();
    await page.waitForTimeout(300);

    // Click "Delete All Test Data"
    const deleteBtn = page.locator('a:has-text("Delete All Test Data")');
    await expect(deleteBtn).toBeVisible({ timeout: 5000 });
    await deleteBtn.click();

    // Wait for deletion to complete (includes confirmation dialog + backend processing)
    await page.waitForTimeout(6000);

    // Check for success notification
    const notification = page.locator('.o_notification');
    const notificationText = await notification.textContent().catch(() => '');
    console.log(`Notification: ${notificationText}`);

    // Verify test data was deleted
    const result = await page.evaluate(async () => {
      const response = await fetch('/web/dataset/call_kw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'property_fielder.property',
            method: 'search_count',
            args: [[['name', 'ilike', 'StressTest']]],
            kwargs: {},
          },
          id: 1,
        }),
      });
      return response.json();
    });

    console.log(`Remaining StressTest properties: ${result.result}`);
    expect(result.result).toBe(0);
  });
});

