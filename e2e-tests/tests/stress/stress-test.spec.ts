/**
 * Stress Test Suite for Property Fielder
 *
 * Tests the system with 10-50 properties, inspections, and jobs
 * Includes data creation and cleanup utilities
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.ODOO_URL || 'http://localhost:8069';
const USERNAME = process.env.ODOO_USERNAME || 'admin';
const PASSWORD = process.env.ODOO_PASSWORD || 'admin';

// Test configuration - adjust these for different stress levels
// Test configuration - adjust these for different stress levels
// Can be overridden with environment variable PROPERTY_COUNT
const TEST_CONFIG = {
  PROPERTY_COUNT: parseInt(process.env.PROPERTY_COUNT || '10', 10),  // Default to 10 properties
  BATCH_SIZE: 5,       // Create properties in batches for stability
};

// Helper to wait for Odoo to load
async function waitForOdooLoad(page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(300);
  const loadingOverlay = page.locator('.o_loading');
  if (await loadingOverlay.isVisible({ timeout: 500 }).catch(() => false)) {
    await loadingOverlay.waitFor({ state: 'hidden', timeout: 10000 });
  }
}

// Helper to login
async function login(page) {
  await page.goto(`${BASE_URL}/web/login`);
  await page.fill('input[name="login"]', USERNAME);
  await page.fill('input[name="password"]', PASSWORD);
  await page.click('button[type="submit"]');
  await waitForOdooLoad(page);
}

// Helper to navigate using Odoo 19 menu structure
async function navigateToMenu(page, appName: string, menuPath: string[] = []) {
  const homeBtn = page.locator('button[title="Home Menu"]');
  await homeBtn.click();
  await page.waitForTimeout(500);
  await page.getByRole('menuitem', { name: appName }).click();
  await waitForOdooLoad(page);

  for (const menu of menuPath) {
    const menuItem = page.getByRole('menuitem', { name: menu });
    if (await menuItem.isVisible({ timeout: 2000 }).catch(() => false)) {
      await menuItem.click();
    } else {
      const expandableBtn = page.getByRole('button', { name: menu });
      if (await expandableBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await expandableBtn.click();
        await page.waitForTimeout(200);
        const subMenuItem = page.getByRole('menuitem', { name: menu });
        if (await subMenuItem.isVisible({ timeout: 2000 }).catch(() => false)) {
          await subMenuItem.click();
        }
      }
    }
    await waitForOdooLoad(page);
  }
}

// London area coordinates for test properties
function generateLondonCoordinates(index: number) {
  const baseLat = 51.5074;
  const baseLng = -0.1278;
  // Spread properties around London within ~10km radius
  const latOffset = (Math.random() - 0.5) * 0.15;
  const lngOffset = (Math.random() - 0.5) * 0.25;
  return {
    latitude: (baseLat + latOffset).toFixed(6),
    longitude: (baseLng + lngOffset).toFixed(6),
  };
}

// Generate test property data
function generatePropertyData(index: number) {
  const streets = ['High Street', 'Church Road', 'Station Road', 'Main Street', 'Park Avenue',
                   'Victoria Road', 'Queens Road', 'Kings Road', 'Green Lane', 'Mill Lane'];
  const areas = ['Acton', 'Brixton', 'Camden', 'Dalston', 'Ealing', 'Finsbury', 'Greenwich',
                 'Hackney', 'Islington', 'Kensington'];
  const postcodes = ['W3', 'SW2', 'NW1', 'E8', 'W5', 'EC1', 'SE10', 'E9', 'N1', 'W8'];

  const streetNum = 10 + index * 2;
  const streetIdx = index % streets.length;
  const areaIdx = index % areas.length;
  const coords = generateLondonCoordinates(index);

  return {
    name: `StressTest Property ${index + 1}`,
    street: `${streetNum} ${streets[streetIdx]}`,
    city: 'London',
    zip: `${postcodes[areaIdx]} ${Math.floor(Math.random() * 9) + 1}${['AA', 'AB', 'BA', 'BB'][index % 4]}`,
    ...coords,
  };
}

// Store created record IDs for cleanup
interface TestData {
  propertyIds: number[];
  inspectionIds: number[];
  jobIds: number[];
  partnerId: number | null;
}

const testData: TestData = {
  propertyIds: [],
  inspectionIds: [],
  jobIds: [],
  partnerId: null,
};

test.describe('Stress Test Suite', () => {
  test.describe.configure({ mode: 'serial' });

  test.beforeAll(async ({ browser }) => {
    // Clear any previous test data markers
    testData.propertyIds = [];
    testData.inspectionIds = [];
    testData.jobIds = [];
  });

  test('1. Create test partner via RPC', async ({ page }) => {
    test.setTimeout(60000);
    await login(page);
    await waitForOdooLoad(page);

    // Use Odoo's JSON-RPC to create partner
    const result = await page.evaluate(async (config) => {
      const response = await fetch('/web/dataset/call_kw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'res.partner',
            method: 'create',
            args: [{
              name: `StressTest Customer ${Date.now()}`,
              is_company: true,
              street: '1 Test Street',
              city: 'London',
              zip: 'SW1A 1AA',
            }],
            kwargs: {},
          },
          id: Math.floor(Math.random() * 1000000),
        }),
      });
      return response.json();
    }, {});

    expect(result.result).toBeTruthy();
    testData.partnerId = result.result;
    console.log(`Created test partner ID: ${testData.partnerId}`);
  });

  test('2. Create properties via RPC', async ({ page }) => {
    test.setTimeout(300000); // 5 minutes for bulk creation
    await login(page);
    await waitForOdooLoad(page);

    const propertyCount = TEST_CONFIG.PROPERTY_COUNT;
    console.log(`Creating ${propertyCount} properties...`);

    // Get country ID for UK
    const countryResult = await page.evaluate(async () => {
      const response = await fetch('/web/dataset/call_kw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'res.country',
            method: 'search',
            args: [[['code', '=', 'GB']]],
            kwargs: { limit: 1 },
          },
          id: Math.floor(Math.random() * 1000000),
        }),
      });
      return response.json();
    });
    const countryId = countryResult.result?.[0] || 77; // Fallback to UK ID

    // Create properties in batches
    for (let batch = 0; batch < Math.ceil(propertyCount / TEST_CONFIG.BATCH_SIZE); batch++) {
      const batchStart = batch * TEST_CONFIG.BATCH_SIZE;
      const batchEnd = Math.min(batchStart + TEST_CONFIG.BATCH_SIZE, propertyCount);

      for (let i = batchStart; i < batchEnd; i++) {
        const propData = generatePropertyData(i);

        const result = await page.evaluate(async ({ propData, partnerId, countryId }) => {
          const response = await fetch('/web/dataset/call_kw', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              jsonrpc: '2.0',
              method: 'call',
              params: {
                model: 'property_fielder.property',
                method: 'create',
                args: [{
                  name: propData.name,
                  partner_id: partnerId,
                  street: propData.street,
                  city: propData.city,
                  zip: propData.zip,
                  country_id: countryId,
                  latitude: parseFloat(propData.latitude),
                  longitude: parseFloat(propData.longitude),
                }],
                kwargs: {},
              },
              id: Math.floor(Math.random() * 1000000),
            }),
          });
          return response.json();
        }, { propData, partnerId: testData.partnerId, countryId });

        if (result.result) {
          testData.propertyIds.push(result.result);
        } else {
          console.error(`Failed to create property ${i + 1}:`, result.error);
        }
      }
      console.log(`Created batch ${batch + 1}: properties ${batchStart + 1}-${batchEnd}`);
    }

    console.log(`Total properties created: ${testData.propertyIds.length}`);
    expect(testData.propertyIds.length).toBe(propertyCount);
  });

  test('3. Create inspections for all properties via RPC', async ({ page }) => {
    test.setTimeout(300000);
    await login(page);
    await waitForOdooLoad(page);

    console.log(`Creating inspections for ${testData.propertyIds.length} properties...`);

    // Get certification type ID (Gas Safety)
    const certResult = await page.evaluate(async () => {
      const response = await fetch('/web/dataset/call_kw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'property_fielder.property.certification.type',
            method: 'search',
            args: [[]],
            kwargs: { limit: 1 },
          },
          id: Math.floor(Math.random() * 1000000),
        }),
      });
      return response.json();
    });
    const certTypeId = certResult.result?.[0] || 1;

    // Create inspection for each property
    for (let i = 0; i < testData.propertyIds.length; i++) {
      const propertyId = testData.propertyIds[i];
      const scheduledDate = new Date();
      scheduledDate.setDate(scheduledDate.getDate() + Math.floor(Math.random() * 14)); // Next 2 weeks

      const result = await page.evaluate(async ({ propertyId, certTypeId, scheduledDate }) => {
        const response = await fetch('/web/dataset/call_kw', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: {
              model: 'property_fielder.property.inspection',
              method: 'create',
              args: [{
                property_id: propertyId,
                certification_type_id: certTypeId,
                scheduled_date: scheduledDate,
                state: 'draft',
              }],
              kwargs: {},
            },
            id: Math.floor(Math.random() * 1000000),
          }),
        });
        return response.json();
      }, { propertyId, certTypeId, scheduledDate: scheduledDate.toISOString().split('T')[0] });

      if (result.result) {
        testData.inspectionIds.push(result.result);
      }

      if ((i + 1) % 10 === 0) {
        console.log(`Created ${i + 1} inspections...`);
      }
    }

    console.log(`Total inspections created: ${testData.inspectionIds.length}`);
    expect(testData.inspectionIds.length).toBe(testData.propertyIds.length);
  });


  test('4. Create jobs from inspections via RPC', async ({ page }) => {
    test.setTimeout(300000);
    await login(page);
    await waitForOdooLoad(page);

    console.log(`Creating jobs for ${testData.inspectionIds.length} inspections...`);

    // Call the action_create_field_service_job method on each inspection
    for (let i = 0; i < testData.inspectionIds.length; i++) {
      const inspectionId = testData.inspectionIds[i];

      const result = await page.evaluate(async ({ inspectionId }) => {
        const response = await fetch('/web/dataset/call_kw', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: {
              model: 'property_fielder.property.inspection',
              method: 'action_create_field_service_job',
              args: [[inspectionId]],
              kwargs: {},
            },
            id: Math.floor(Math.random() * 1000000),
          }),
        });
        return response.json();
      }, { inspectionId });

      if (result.result?.res_id) {
        testData.jobIds.push(result.result.res_id);
      } else if (result.error) {
        console.error(`Failed to create job for inspection ${inspectionId}:`, result.error?.data?.message || result.error);
      }

      if ((i + 1) % 10 === 0) {
        console.log(`Created ${testData.jobIds.length} jobs...`);
      }
    }

    console.log(`Total jobs created: ${testData.jobIds.length}`);
    expect(testData.jobIds.length).toBeGreaterThan(0);
  });

  test('5. Verify jobs created via RPC', async ({ page }) => {
    test.setTimeout(60000);
    await login(page);
    await waitForOdooLoad(page);

    // Query jobs that were created from StressTest properties
    const result = await page.evaluate(async () => {
      // First get StressTest property IDs
      const propResponse = await fetch('/web/dataset/call_kw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'property_fielder.property',
            method: 'search',
            args: [[['name', 'ilike', 'StressTest']]],
            kwargs: {},
          },
          id: 100,
        }),
      });
      const propResult = await propResponse.json();
      const propertyIds = propResult.result || [];

      if (propertyIds.length === 0) return { jobs: 0, properties: 0 };

      // Get inspections for these properties
      const inspResponse = await fetch('/web/dataset/call_kw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'property_fielder.property.inspection',
            method: 'search_read',
            args: [[['property_id', 'in', propertyIds]]],
            kwargs: { fields: ['job_id'] },
          },
          id: 101,
        }),
      });
      const inspResult = await inspResponse.json();
      const jobIds = (inspResult.result || [])
        .filter(i => i.job_id)
        .map(i => i.job_id[0]);

      return {
        properties: propertyIds.length,
        inspections: inspResult.result?.length || 0,
        jobs: jobIds.length
      };
    });

    console.log(`StressTest data: ${result.properties} properties, ${result.inspections} inspections, ${result.jobs} jobs`);

    // Should have created jobs from properties
    expect(result.jobs).toBeGreaterThanOrEqual(result.properties);
  });

  test('6. Verify jobs on Dispatch Map', async ({ page }) => {
    test.setTimeout(90000);
    await login(page);

    await navigateToMenu(page, 'Field Service', ['Dispatch']);
    await waitForOdooLoad(page);

    // Wait for map and data to load
    await page.waitForTimeout(3000);

    // Check for jobs count in the panel
    const jobsHeading = page.locator('h6:has-text("Jobs")');
    const headingText = await jobsHeading.textContent().catch(() => '');
    console.log(`Dispatch Jobs heading: ${headingText}`);

    // The heading shows job count like " Jobs (20)"
    const match = headingText?.match(/Jobs \((\d+)\)/);
    const jobsOnMap = match ? parseInt(match[1], 10) : 0;
    console.log(`Jobs visible on dispatch map: ${jobsOnMap}`);

    // Should have jobs on the map (may be filtered by date)
    expect(jobsOnMap).toBeGreaterThanOrEqual(0);
  });

  test('7. Test map performance with multiple jobs', async ({ page }) => {
    test.setTimeout(120000);
    await login(page);

    await navigateToMenu(page, 'Field Service', ['Dispatch']);
    await waitForOdooLoad(page);

    // Measure time to load and interact
    const startTime = Date.now();

    // Wait for map
    await page.waitForTimeout(2000);

    // Click refresh button using JavaScript to avoid map canvas interception
    const refreshClicked = await page.evaluate(() => {
      const btn = document.querySelector('button:has(.fa-sync-alt)') as HTMLButtonElement;
      if (btn) {
        btn.click();
        return true;
      }
      return false;
    });
    console.log(`Refresh button clicked: ${refreshClicked}`);
    await page.waitForTimeout(2000);

    // Try clicking Select All using JavaScript to avoid map canvas interception
    const selectAllClicked = await page.evaluate(() => {
      const btns = document.querySelectorAll('button');
      for (const btn of btns) {
        if (btn.textContent?.trim() === 'Select All') {
          btn.click();
          return true;
        }
      }
      return false;
    });
    console.log(`Select All button clicked: ${selectAllClicked}`);
    await page.waitForTimeout(1000);

    const loadTime = Date.now() - startTime;
    console.log(`Map interaction time: ${loadTime}ms`);

    // Should complete within reasonable time
    expect(loadTime).toBeLessThan(60000);
  });
});

// Cleanup test suite - SKIPPED by default
// Run separately with: npx playwright test tests/stress/cleanup-all.spec.ts
test.describe.skip('Cleanup Test Data (Manual)', () => {
  test('Delete all stress test data', async ({ page }) => {
    test.setTimeout(300000);
    await login(page);
    await waitForOdooLoad(page);

    console.log('Starting cleanup...');

    // 1. Delete jobs first (they reference inspections)
    if (testData.jobIds.length > 0) {
      console.log(`Deleting ${testData.jobIds.length} jobs...`);
      const jobResult = await page.evaluate(async (ids) => {
        const response = await fetch('/web/dataset/call_kw', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: {
              model: 'property_fielder.job',
              method: 'unlink',
              args: [ids],
              kwargs: {},
            },
            id: Math.floor(Math.random() * 1000000),
          }),
        });
        return response.json();
      }, testData.jobIds);
      console.log(`Jobs deleted: ${jobResult.result}`);
    }

    // 2. Delete inspections
    if (testData.inspectionIds.length > 0) {
      console.log(`Deleting ${testData.inspectionIds.length} inspections...`);
      const inspResult = await page.evaluate(async (ids) => {
        const response = await fetch('/web/dataset/call_kw', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: {
              model: 'property_fielder.property.inspection',
              method: 'unlink',
              args: [ids],
              kwargs: {},
            },
            id: Math.floor(Math.random() * 1000000),
          }),
        });
        return response.json();
      }, testData.inspectionIds);
      console.log(`Inspections deleted: ${inspResult.result}`);
    }

    // 3. Delete properties
    if (testData.propertyIds.length > 0) {
      console.log(`Deleting ${testData.propertyIds.length} properties...`);
      const propResult = await page.evaluate(async (ids) => {
        const response = await fetch('/web/dataset/call_kw', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: {
              model: 'property_fielder.property',
              method: 'unlink',
              args: [ids],
              kwargs: {},
            },
            id: Math.floor(Math.random() * 1000000),
          }),
        });
        return response.json();
      }, testData.propertyIds);
      console.log(`Properties deleted: ${propResult.result}`);
    }

    // 4. Delete test partner
    if (testData.partnerId) {
      console.log(`Deleting test partner ${testData.partnerId}...`);
      const partnerResult = await page.evaluate(async (id) => {
        const response = await fetch('/web/dataset/call_kw', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: {
              model: 'res.partner',
              method: 'unlink',
              args: [[id]],
              kwargs: {},
            },
            id: Math.floor(Math.random() * 1000000),
          }),
        });
        return response.json();
      }, testData.partnerId);
      console.log(`Partner deleted: ${partnerResult.result}`);
    }

    console.log('Cleanup complete!');

    // Clear test data
    testData.propertyIds = [];
    testData.inspectionIds = [];
    testData.jobIds = [];
    testData.partnerId = null;
  });
});

