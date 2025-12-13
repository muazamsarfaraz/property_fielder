/**
 * Cleanup Utility for Stress Test Data
 * 
 * This test finds and deletes ALL test data created by stress tests
 * by searching for records with "StressTest" in their name.
 * 
 * Run with: npx playwright test tests/stress/cleanup-all.spec.ts
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.ODOO_URL || 'http://localhost:8069';
const USERNAME = process.env.ODOO_USERNAME || 'admin';
const PASSWORD = process.env.ODOO_PASSWORD || 'admin';

async function waitForOdooLoad(page) {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(300);
}

async function login(page) {
  await page.goto(`${BASE_URL}/web/login`);
  await page.fill('input[name="login"]', USERNAME);
  await page.fill('input[name="password"]', PASSWORD);
  await page.click('button[type="submit"]');
  await waitForOdooLoad(page);
}

test.describe('Cleanup All Stress Test Data', () => {
  
  test('Find and delete all StressTest records', async ({ page }) => {
    test.setTimeout(600000); // 10 minutes for cleanup
    await login(page);
    await waitForOdooLoad(page);

    console.log('=== Starting Comprehensive Cleanup ===\n');

    // 1. Find and delete jobs linked to StressTest properties
    console.log('Step 1: Finding jobs from StressTest properties...');
    const jobsResult = await page.evaluate(async () => {
      // First find StressTest properties
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
          id: 1,
        }),
      });
      const propResult = await propResponse.json();
      const propertyIds = propResult.result || [];

      if (propertyIds.length === 0) return { deleted: 0, propertyIds: [] };

      // Find inspections for these properties
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
          id: 2,
        }),
      });
      const inspResult = await inspResponse.json();
      const jobIds = (inspResult.result || [])
        .filter(i => i.job_id)
        .map(i => i.job_id[0]);

      if (jobIds.length === 0) return { deleted: 0, propertyIds };

      // Delete jobs
      const deleteResponse = await fetch('/web/dataset/call_kw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'property_fielder.job',
            method: 'unlink',
            args: [jobIds],
            kwargs: {},
          },
          id: 3,
        }),
      });
      const deleteResult = await deleteResponse.json();
      return { deleted: jobIds.length, propertyIds, result: deleteResult.result };
    });
    console.log(`  Jobs deleted: ${jobsResult.deleted}`);

    // 2. Find and delete inspections
    console.log('Step 2: Deleting inspections from StressTest properties...');
    const inspectionsResult = await page.evaluate(async (propertyIds) => {
      if (!propertyIds || propertyIds.length === 0) return { deleted: 0 };

      const searchResponse = await fetch('/web/dataset/call_kw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'property_fielder.property.inspection',
            method: 'search',
            args: [[['property_id', 'in', propertyIds]]],
            kwargs: {},
          },
          id: 4,
        }),
      });
      const searchResult = await searchResponse.json();
      const ids = searchResult.result || [];

      if (ids.length === 0) return { deleted: 0 };

      const deleteResponse = await fetch('/web/dataset/call_kw', {
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
          id: 5,
        }),
      });
      return { deleted: ids.length };
    }, jobsResult.propertyIds);
    console.log(`  Inspections deleted: ${inspectionsResult.deleted}`);

    // 3. Delete properties
    console.log('Step 3: Deleting StressTest properties...');
    const propertiesResult = await page.evaluate(async () => {
      const searchResponse = await fetch('/web/dataset/call_kw', {
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
          id: 6,
        }),
      });
      const searchResult = await searchResponse.json();
      const ids = searchResult.result || [];

      if (ids.length === 0) return { deleted: 0 };

      const deleteResponse = await fetch('/web/dataset/call_kw', {
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
          id: 7,
        }),
      });
      return { deleted: ids.length };
    });
    console.log(`  Properties deleted: ${propertiesResult.deleted}`);

    // 4. Delete test partners (customers)
    console.log('Step 4: Deleting StressTest customers...');
    const partnersResult = await page.evaluate(async () => {
      const searchResponse = await fetch('/web/dataset/call_kw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'res.partner',
            method: 'search',
            args: [[['name', 'ilike', 'StressTest']]],
            kwargs: {},
          },
          id: 8,
        }),
      });
      const searchResult = await searchResponse.json();
      const ids = searchResult.result || [];

      if (ids.length === 0) return { deleted: 0 };

      const deleteResponse = await fetch('/web/dataset/call_kw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'res.partner',
            method: 'unlink',
            args: [ids],
            kwargs: {},
          },
          id: 9,
        }),
      });
      return { deleted: ids.length };
    });
    console.log(`  Partners deleted: ${partnersResult.deleted}`);

    console.log('\n=== Cleanup Complete ===');
    console.log(`Summary:`);
    console.log(`  - Jobs: ${jobsResult.deleted}`);
    console.log(`  - Inspections: ${inspectionsResult.deleted}`);
    console.log(`  - Properties: ${propertiesResult.deleted}`);
    console.log(`  - Partners: ${partnersResult.deleted}`);
  });

  test('Delete jobs with StressTest in name directly', async ({ page }) => {
    test.setTimeout(300000);
    await login(page);
    await waitForOdooLoad(page);

    console.log('Finding and deleting jobs with StressTest or Inspection in name...');

    const result = await page.evaluate(async () => {
      // Search for jobs that might be from stress tests
      const searchResponse = await fetch('/web/dataset/call_kw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'call',
          params: {
            model: 'property_fielder.job',
            method: 'search',
            args: [[['name', 'ilike', 'StressTest']]],
            kwargs: {},
          },
          id: 10,
        }),
      });
      const searchResult = await searchResponse.json();
      const ids = searchResult.result || [];

      if (ids.length === 0) return { found: 0, deleted: 0 };

      const deleteResponse = await fetch('/web/dataset/call_kw', {
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
          id: 11,
        }),
      });
      return { found: ids.length, deleted: ids.length };
    });

    console.log(`Jobs found: ${result.found}, deleted: ${result.deleted}`);
  });
});

