/**
 * Property Management UX Analysis Test
 * 
 * Automated Playwright test that:
 * 1. Tests both desktop and mobile views
 * 2. Navigates through property list and detail pages
 * 3. Takes screenshots at key stages
 * 4. Sends screenshots to Gemini for UX analysis
 * 5. Outputs actionable recommendations
 */

import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import sharp from 'sharp';

const BASE_URL = process.env.ODOO_URL || 'http://localhost:8069';
const USERNAME = process.env.ODOO_USERNAME || 'admin';
const PASSWORD = process.env.ODOO_PASSWORD || 'admin';
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_MODEL = 'gemini-3-pro-preview';

const SCREENSHOT_DIR = 'test-results/ux-analysis/property-management';

if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

interface Screenshot {
  path: string;
  stage: string;
  description: string;
}

const screenshots: Screenshot[] = [];

async function waitForOdooLoad(page: Page): Promise<void> {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(300);
  const loadingOverlay = page.locator('.o_loading');
  if (await loadingOverlay.isVisible({ timeout: 500 }).catch(() => false)) {
    await loadingOverlay.waitFor({ state: 'hidden', timeout: 30000 });
  }
}

async function login(page: Page): Promise<void> {
  await page.goto(`${BASE_URL}/web/login`);
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(500);

  const userButton = page.locator('button:has-text("admin")');
  if (await userButton.isVisible({ timeout: 2000 }).catch(() => false)) {
    await userButton.click();
    await page.waitForTimeout(300);
  }

  const loginInput = page.locator('input[name="login"], input[placeholder*="email" i]').first();
  if (await loginInput.isVisible({ timeout: 1000 }).catch(() => false)) {
    await loginInput.fill(USERNAME);
  }

  const passwordInput = page.locator('input[name="password"], input[type="password"]').first();
  await passwordInput.fill(PASSWORD);
  await page.getByRole('button', { name: 'Log in' }).click();
  await waitForOdooLoad(page);
  await page.waitForURL(/\/odoo\/|\/web(?!\/login)/, { timeout: 15000 });
}

async function takeScreenshot(page: Page, stage: string, description: string): Promise<string> {
  const filename = `${stage.replace(/\s+/g, '-').toLowerCase()}.png`;
  const filepath = path.join(SCREENSHOT_DIR, filename);
  await page.screenshot({ path: filepath, fullPage: false });
  screenshots.push({ path: filepath, stage, description });
  return filepath;
}

async function compressForGemini(imagePath: string): Promise<Buffer> {
  return sharp(imagePath)
    .resize({ width: 1200, height: 900, fit: 'inside', withoutEnlargement: true })
    .jpeg({ quality: 75 })
    .toBuffer();
}

async function analyzeWithGemini(screenshotPaths: Screenshot[]): Promise<string> {
  if (!GEMINI_API_KEY) {
    return 'GEMINI_API_KEY not set - skipping AI analysis';
  }

  const images = await Promise.all(
    screenshotPaths.map(async (s) => ({
      stage: s.stage,
      description: s.description,
      data: (await compressForGemini(s.path)).toString('base64'),
    }))
  );

  const prompt = `You are a senior UX designer reviewing Property Management screens for a property inspection scheduling system.

Analyze these screenshots and provide:
1. A UX score from 1-10
2. Top 3 critical issues to fix immediately
3. Top 3 quick wins for improvement
4. Mobile-specific issues (if any)
5. Desktop-specific issues (if any)

Focus on: Information hierarchy, form usability, data density, navigation clarity, compliance status visibility.

Screenshots:
${images.map((img, i) => `${i + 1}. ${img.stage}: ${img.description}`).join('\n')}`;

  const requestBody = {
    contents: [{
      parts: [
        { text: prompt },
        ...images.map((img) => ({
          inline_data: { mime_type: 'image/jpeg', data: img.data }
        }))
      ]
    }],
    generationConfig: { temperature: 0.3, maxOutputTokens: 2000 }
  };

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`,
    { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(requestBody) }
  );

  const data = await response.json();
  return data.candidates?.[0]?.content?.parts?.[0]?.text || JSON.stringify(data, null, 2);
}

test.describe('Property Management UX Analysis', () => {
  test.setTimeout(180000);

  test('Analyze property list and detail views', async ({ page }) => {
    // Desktop views
    await page.setViewportSize({ width: 1920, height: 1200 });
    await login(page);

    await page.goto(`${BASE_URL}/odoo/action-294`);
    await waitForOdooLoad(page);
    await page.waitForTimeout(1000);
    await takeScreenshot(page, '01-property-list-desktop', 'Property list view on desktop');

    const firstProperty = page.locator('tr.o_data_row').first();
    if (await firstProperty.isVisible({ timeout: 3000 }).catch(() => false)) {
      await firstProperty.click();
      await waitForOdooLoad(page);
      await page.waitForTimeout(1000);
      await takeScreenshot(page, '02-property-detail-desktop', 'Property detail view with form and chatter side-by-side');
    }

    // Mobile views
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto(`${BASE_URL}/odoo/action-294`);
    await waitForOdooLoad(page);
    await page.waitForTimeout(1000);
    await takeScreenshot(page, '03-property-list-mobile', 'Property list view on mobile');

    if (await firstProperty.isVisible({ timeout: 3000 }).catch(() => false)) {
      await firstProperty.click();
      await waitForOdooLoad(page);
      await page.waitForTimeout(1000);
      await takeScreenshot(page, '04-property-detail-mobile', 'Property detail view on mobile with stacked layout');
    }

    // Run Gemini analysis
    const analysis = await analyzeWithGemini(screenshots);
    console.log('\n========== PROPERTY MANAGEMENT UX ANALYSIS ==========\n');
    console.log(analysis);
    console.log('\n======================================================\n');

    // Save analysis to file
    const analysisPath = path.join(SCREENSHOT_DIR, 'ux-analysis-report.md');
    fs.writeFileSync(analysisPath, `# Property Management UX Analysis\n\n${analysis}`);
    console.log(`Analysis saved to: ${analysisPath}`);
  });
});

