/**
 * UI Link Spider Test
 * 
 * Crawls all Odoo menu items and views to:
 * 1. Discover all accessible pages
 * 2. Take screenshots of each view
 * 3. Detect broken links or errors
 * 4. Optionally analyze with Gemini 3 Pro Preview
 */

import { test, expect, Page, Locator } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import sharp from 'sharp';

const BASE_URL = process.env.ODOO_URL || 'http://localhost:8069';
const USERNAME = process.env.ODOO_USERNAME || 'admin';
const PASSWORD = process.env.ODOO_PASSWORD || 'admin';
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_MODEL = 'gemini-2.0-flash';
const ENABLE_GEMINI_ANALYSIS = process.env.ENABLE_GEMINI_ANALYSIS === 'true';

const SCREENSHOT_DIR = 'test-results/link-spider';

interface PageInfo {
  appName: string;
  menuPath: string[];
  url: string;
  screenshotPath: string;
  title: string;
  hasError: boolean;
  errorMessage?: string;
  recordCount?: number;
}

interface AppMenu {
  name: string;
  subMenus: string[];
}

const discoveredPages: PageInfo[] = [];

// Ensure screenshot directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function waitForOdooLoad(page: Page): Promise<void> {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(300);
  const loadingOverlay = page.locator('.o_loading');
  if (await loadingOverlay.isVisible({ timeout: 500 }).catch(() => false)) {
    await loadingOverlay.waitFor({ state: 'hidden', timeout: 30000 });
  }
}

async function login(page: Page): Promise<void> {
  // Navigate to the property_fielder database directly
  await page.goto(`${BASE_URL}/odoo?db=property_fielder`, { waitUntil: 'load' });
  await page.waitForTimeout(2000);

  // Check if we're on a database selector page
  const dbLink = page.locator('a[href*="db=property_fielder"]');
  if (await dbLink.isVisible({ timeout: 1000 }).catch(() => false)) {
    await dbLink.click();
    await page.waitForTimeout(1000);
  }

  // Check if we need to login
  const url = page.url();
  if (url.includes('/web/login')) {
    await page.waitForTimeout(1500); // Wait for login form JS to load

    // Wait for login input to be in DOM
    const loginInput = page.locator('input[name="login"]');
    try {
      await loginInput.waitFor({ state: 'attached', timeout: 10000 });
    } catch {
      console.log('Login input not found, may already be logged in');
      return;
    }

    // Odoo 19 form may not be visible due to CSS - use evaluate to fill
    await page.evaluate((credentials) => {
      const loginEl = document.querySelector('input[name="login"]') as HTMLInputElement;
      const passEl = document.querySelector('input[name="password"]') as HTMLInputElement;
      if (loginEl) loginEl.value = credentials.login;
      if (passEl) passEl.value = credentials.password;
      // Trigger input events
      loginEl?.dispatchEvent(new Event('input', { bubbles: true }));
      passEl?.dispatchEvent(new Event('input', { bubbles: true }));
    }, { login: USERNAME, password: PASSWORD });

    // Click login button via evaluate
    await page.evaluate(() => {
      const btn = document.querySelector('button[type="submit"]') as HTMLButtonElement;
      if (btn) btn.click();
    });

    await waitForOdooLoad(page);
  }

  // Wait for main Odoo interface
  await page.waitForURL(/\/odoo\//, { timeout: 15000 });
}

async function openAppsMenu(page: Page): Promise<void> {
  // Odoo 19 uses a Home Menu button with title="Home Menu"
  const homeBtn = page.getByTitle('Home Menu');
  await homeBtn.click();
  await page.waitForTimeout(500);
}

async function getAppMenuItems(page: Page): Promise<string[]> {
  await openAppsMenu(page);
  const menuItems = page.locator('[role="menuitem"]');
  const names: string[] = [];
  const count = await menuItems.count();
  for (let i = 0; i < count; i++) {
    const name = await menuItems.nth(i).textContent();
    if (name && name.trim()) {
      names.push(name.trim());
    }
  }
  // Close menu by pressing Escape
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
  return names;
}

async function navigateToApp(page: Page, appName: string): Promise<boolean> {
  try {
    await openAppsMenu(page);
    const menuItem = page.getByRole('menuitem', { name: appName, exact: true });
    if (await menuItem.isVisible({ timeout: 2000 }).catch(() => false)) {
      await menuItem.click();
      await waitForOdooLoad(page);
      return true;
    }
    await page.keyboard.press('Escape');
    return false;
  } catch {
    return false;
  }
}

async function getSubMenuItems(page: Page): Promise<string[]> {
  const subMenus: string[] = [];
  // Odoo 19 uses .o_menu_sections for app submenus
  const menuSections = page.locator('.o_menu_sections [role="menuitem"], .o_menu_sections a');
  const count = await menuSections.count();
  for (let i = 0; i < count; i++) {
    const name = await menuSections.nth(i).textContent();
    if (name && name.trim() && !subMenus.includes(name.trim())) {
      subMenus.push(name.trim());
    }
  }
  return subMenus;
}

async function clickSubMenu(page: Page, menuName: string): Promise<boolean> {
  try {
    const menuItem = page.locator(`.o_menu_sections [role="menuitem"]:has-text("${menuName}")`).first();
    if (await menuItem.isVisible({ timeout: 2000 }).catch(() => false)) {
      await menuItem.click();
      await waitForOdooLoad(page);
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

async function takePageScreenshot(page: Page, appName: string, menuPath: string[]): Promise<string> {
  const safeName = [...menuPath, appName].join('-').replace(/[^a-zA-Z0-9-]/g, '_').toLowerCase();
  const filename = `${safeName}.png`;
  const filepath = path.join(SCREENSHOT_DIR, filename);
  await page.screenshot({ path: filepath, fullPage: false });
  return filepath;
}

async function checkForErrors(page: Page): Promise<{ hasError: boolean; message?: string }> {
  // Check for Odoo error dialogs
  const errorDialog = page.locator('.o_error_dialog, .modal-content:has(.o_error_detail)');
  if (await errorDialog.isVisible({ timeout: 500 }).catch(() => false)) {
    const errorText = await errorDialog.textContent().catch(() => 'Unknown error');
    return { hasError: true, message: errorText?.substring(0, 200) };
  }
  // Check for access denied
  const accessDenied = page.locator('text=Access Denied, text=Access Error');
  if (await accessDenied.isVisible({ timeout: 500 }).catch(() => false)) {
    return { hasError: true, message: 'Access Denied' };
  }
  return { hasError: false };
}

async function getRecordCount(page: Page): Promise<number | undefined> {
  try {
    const pager = await page.locator('.o_pager_value').textContent({ timeout: 1000 });
    if (pager) {
      const match = pager.match(/of\s+(\d+)/);
      return match ? parseInt(match[1]) : undefined;
    }
  } catch {
    return undefined;
  }
  return undefined;
}

async function convertToJpegBase64(pngPath: string): Promise<string | null> {
  if (!fs.existsSync(pngPath)) return null;
  try {
    const jpegBuffer = await sharp(pngPath)
      .jpeg({ quality: 60 })
      .resize(1280, 800, { fit: 'inside' })
      .toBuffer();
    return jpegBuffer.toString('base64');
  } catch {
    return null;
  }
}

async function analyzeWithGemini(pages: PageInfo[]): Promise<string> {
  if (!GEMINI_API_KEY || !ENABLE_GEMINI_ANALYSIS) {
    return 'Gemini analysis skipped (ENABLE_GEMINI_ANALYSIS not set to true)';
  }

  // Select up to 5 diverse screenshots for analysis
  const selectedPages = pages
    .filter(p => !p.hasError)
    .slice(0, 5);

  console.log(`📊 Analyzing ${selectedPages.length} pages with Gemini...`);

  const imageParts: any[] = [];
  for (const pageInfo of selectedPages) {
    const base64 = await convertToJpegBase64(pageInfo.screenshotPath);
    if (base64) {
      imageParts.push({
        inline_data: {
          mime_type: 'image/jpeg',
          data: base64
        }
      });
    }
  }

  if (imageParts.length === 0) {
    return 'No valid screenshots for analysis.';
  }

  const pageDescriptions = selectedPages
    .map((p, i) => `${i + 1}. **${p.appName}** > ${p.menuPath.join(' > ')} (${p.recordCount ?? 'N/A'} records)`)
    .join('\n');

  const prompt = `You are a UX/UI expert. Analyze these ${imageParts.length} screenshots from an Odoo-based Property Management application.

Pages analyzed:
${pageDescriptions}

Provide a comprehensive UX review:

## 1. Overall Application UX Score (1-10)
Rate the overall consistency and usability.

## 2. UI Consistency Assessment
- Are colors, fonts, and spacing consistent across views?
- Do similar actions have similar UI patterns?
- Is the navigation intuitive?

## 3. Issues Found
List any UX problems observed across the pages.

## 4. Top 5 Recommendations
Provide specific, actionable improvements.

## 5. Accessibility Observations
Note any accessibility concerns (contrast, readability, etc.)`;

  const requestBody = {
    contents: [{ parts: [{ text: prompt }, ...imageParts] }],
    generationConfig: { temperature: 0.7, maxOutputTokens: 4096 }
  };

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 120000);

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
        signal: controller.signal
      }
    );
    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Gemini API Error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    if (data.candidates?.[0]?.content?.parts) {
      return data.candidates[0].content.parts
        .filter((p: any) => p.text)
        .map((p: any) => p.text)
        .join('\n');
    }
    return 'Unexpected response format from Gemini.';
  } catch (error: any) {
    if (error.name === 'AbortError') {
      return 'Gemini API call timed out.';
    }
    return `Gemini error: ${error.message}`;
  }
}

function generateReport(pages: PageInfo[], geminiAnalysis: string): string {
  const errorPages = pages.filter(p => p.hasError);
  const successPages = pages.filter(p => !p.hasError);

  return `# UI Link Spider Report

Generated: ${new Date().toISOString()}
Base URL: ${BASE_URL}

## Summary
- **Total Pages Discovered:** ${pages.length}
- **Successful:** ${successPages.length}
- **Errors:** ${errorPages.length}

## Pages Crawled

| App | Menu Path | Records | Status |
|-----|-----------|---------|--------|
${pages.map(p => `| ${p.appName} | ${p.menuPath.join(' > ') || 'Home'} | ${p.recordCount ?? '-'} | ${p.hasError ? '❌ Error' : '✅ OK'} |`).join('\n')}

${errorPages.length > 0 ? `
## Errors Found

${errorPages.map(p => `### ${p.appName} > ${p.menuPath.join(' > ')}
- **URL:** ${p.url}
- **Error:** ${p.errorMessage}
`).join('\n')}` : ''}

## Gemini UX Analysis

${geminiAnalysis}

## Screenshots

All screenshots saved to: \`${SCREENSHOT_DIR}/\`
`;
}

// Main test
test.use({
  viewport: { width: 1920, height: 1080 },
});

test.describe('UI Link Spider @link-spider', () => {
  test('Crawl all Odoo menus and capture screenshots', async ({ page }) => {
    test.setTimeout(600000); // 10 minutes for full crawl

    console.log('🕷️  Starting UI Link Spider');
    console.log(`🌐 URL: ${BASE_URL}`);
    console.log(`📸 Screenshots: ${SCREENSHOT_DIR}`);

    // Login
    await login(page);
    console.log('✅ Logged in successfully');

    // Get all app menu items
    const apps = await getAppMenuItems(page);
    console.log(`\n📱 Found ${apps.length} apps: ${apps.join(', ')}`);

    // Crawl each app
    for (const appName of apps) {
      console.log(`\n🔍 Crawling: ${appName}`);

      const navigated = await navigateToApp(page, appName);
      if (!navigated) {
        console.log(`  ⚠️ Could not navigate to ${appName}`);
        continue;
      }

      await page.waitForTimeout(1000);

      // Take screenshot of app home
      const errorCheck = await checkForErrors(page);
      const screenshotPath = await takePageScreenshot(page, appName, []);
      const recordCount = await getRecordCount(page);

      discoveredPages.push({
        appName,
        menuPath: [],
        url: page.url(),
        screenshotPath,
        title: await page.title(),
        hasError: errorCheck.hasError,
        errorMessage: errorCheck.message,
        recordCount
      });

      console.log(`  📸 ${appName} home (${recordCount ?? 'N/A'} records)`);

      // Get and crawl submenus
      const subMenus = await getSubMenuItems(page);
      console.log(`  📂 Found ${subMenus.length} submenus`);

      for (const subMenu of subMenus) {
        const clicked = await clickSubMenu(page, subMenu);
        if (!clicked) continue;

        await page.waitForTimeout(800);

        const subErrorCheck = await checkForErrors(page);
        const subScreenshotPath = await takePageScreenshot(page, appName, [subMenu]);
        const subRecordCount = await getRecordCount(page);

        discoveredPages.push({
          appName,
          menuPath: [subMenu],
          url: page.url(),
          screenshotPath: subScreenshotPath,
          title: await page.title(),
          hasError: subErrorCheck.hasError,
          errorMessage: subErrorCheck.message,
          recordCount: subRecordCount
        });

        console.log(`    📸 ${subMenu} ${subErrorCheck.hasError ? '❌' : '✅'}`);

        // Dismiss any error dialogs
        if (subErrorCheck.hasError) {
          await page.keyboard.press('Escape');
          await page.waitForTimeout(300);
        }
      }
    }

    // Generate report
    console.log('\n📊 Generating report...');
    let geminiAnalysis = 'Gemini analysis disabled.';

    if (ENABLE_GEMINI_ANALYSIS && GEMINI_API_KEY) {
      geminiAnalysis = await analyzeWithGemini(discoveredPages);
      console.log('\n🤖 Gemini Analysis Complete');
    }

    const report = generateReport(discoveredPages, geminiAnalysis);
    const reportPath = path.join(SCREENSHOT_DIR, 'spider-report.md');
    fs.writeFileSync(reportPath, report);

    // Also save JSON data
    const jsonPath = path.join(SCREENSHOT_DIR, 'spider-data.json');
    fs.writeFileSync(jsonPath, JSON.stringify(discoveredPages, null, 2));

    console.log('\n' + '='.repeat(80));
    console.log('🕷️  UI LINK SPIDER COMPLETE');
    console.log('='.repeat(80));
    console.log(`📄 Report: ${reportPath}`);
    console.log(`📊 Data: ${jsonPath}`);
    console.log(`📸 Screenshots: ${discoveredPages.length} captured`);
    console.log(`✅ Success: ${discoveredPages.filter(p => !p.hasError).length}`);
    console.log(`❌ Errors: ${discoveredPages.filter(p => p.hasError).length}`);
    console.log('='.repeat(80));

    // Assert no critical errors (optional - can be relaxed)
    const errorCount = discoveredPages.filter(p => p.hasError).length;
    expect(errorCount, `Found ${errorCount} pages with errors`).toBeLessThan(discoveredPages.length * 0.5);
  });
});

