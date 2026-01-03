/**
 * Flutter UI Spider
 *
 * Crawls all Flutter app screens to:
 * 1. Discover all accessible pages/routes
 * 2. Take screenshots of each view
 * 3. Detect errors or issues
 * 4. Collect data for Gemini analysis
 *
 * Uses keyboard navigation for Flutter CanvasKit renderer compatibility.
 */

import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import sharp from 'sharp';
import { FlutterConfig, FlutterRoutes, FlutterSelectors } from '../config/flutter-config';

const SCREENSHOT_DIR = 'test-results/flutter-mobile';
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-2.0-flash';
const ENABLE_GEMINI_ANALYSIS = process.env.ENABLE_GEMINI_ANALYSIS === 'true';

export interface ScreenInfo {
  route: string;
  name: string;
  screenshotPath: string;
  timestamp: string;
  hasError: boolean;
  errorMessage?: string;
  elementCounts: {
    buttons: number;
    inputs: number;
    listItems: number;
  };
  accessibilityLabels: string[];
}

const discoveredScreens: ScreenInfo[] = [];

// Ensure screenshot directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function waitForFlutterReady(page: Page): Promise<void> {
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(1500); // Flutter needs more time to render

  const loading = page.locator(FlutterSelectors.loading);
  if (await loading.isVisible({ timeout: 500 }).catch(() => false)) {
    await loading.waitFor({ state: 'hidden', timeout: 30000 });
  }
}

/**
 * Login using keyboard navigation (works with CanvasKit renderer)
 */
async function loginWithKeyboard(page: Page): Promise<boolean> {
  console.log('🔑 Logging in with keyboard navigation...');

  // Wait for app to load
  await page.waitForTimeout(3000);

  // Tab to first input (username)
  await page.keyboard.press('Tab');
  await page.waitForTimeout(300);

  // Type username
  await page.keyboard.type(FlutterConfig.credentials.username, { delay: 50 });
  await page.waitForTimeout(200);

  // Tab to password field
  await page.keyboard.press('Tab');
  await page.waitForTimeout(300);

  // Type password
  await page.keyboard.type(FlutterConfig.credentials.password, { delay: 50 });
  await page.waitForTimeout(200);

  // Tab to login button
  await page.keyboard.press('Tab');
  await page.waitForTimeout(300);

  // Press Enter or Space to activate button
  await page.keyboard.press('Enter');

  // Wait for login to complete
  console.log('⏳ Waiting for login response...');
  await page.waitForTimeout(5000);

  // Check if we navigated away from login
  const url = page.url();
  const success = !url.includes('login');
  console.log(success ? '✅ Login successful' : '❌ Login may have failed');

  return success;
}

async function captureScreen(page: Page, route: string, name: string): Promise<ScreenInfo> {
  const safeName = name.replace(/[^a-zA-Z0-9-]/g, '_').toLowerCase();
  const filename = `flutter-${safeName}.png`;
  const filepath = path.join(SCREENSHOT_DIR, filename);
  
  await page.screenshot({ path: filepath, fullPage: false });
  
  // Check for errors
  let hasError = false;
  let errorMessage: string | undefined;
  const errorDialog = page.locator(FlutterSelectors.errorDialog);
  if (await errorDialog.isVisible({ timeout: 500 }).catch(() => false)) {
    hasError = true;
    errorMessage = await errorDialog.textContent() || 'Unknown error';
  }
  
  // Count elements
  const buttonCount = await page.getByRole('button').count();
  const inputCount = await page.locator('input, textarea').count();
  const listItemCount = await page.locator('[role="listitem"]').count();
  
  // Get accessibility labels
  const labels: string[] = [];
  const labeledElements = page.locator('[aria-label]');
  const labelCount = await labeledElements.count();
  for (let i = 0; i < Math.min(labelCount, 20); i++) {
    const label = await labeledElements.nth(i).getAttribute('aria-label');
    if (label) labels.push(label);
  }
  
  return {
    route,
    name,
    screenshotPath: filepath,
    timestamp: new Date().toISOString(),
    hasError,
    errorMessage,
    elementCounts: {
      buttons: buttonCount,
      inputs: inputCount,
      listItems: listItemCount,
    },
    accessibilityLabels: labels,
  };
}

async function navigateToRoute(page: Page, route: string): Promise<boolean> {
  try {
    const url = `${FlutterConfig.baseUrl}/#${route}`;
    await page.goto(url);
    await waitForFlutterReady(page);
    return true;
  } catch {
    return false;
  }
}

// Gemini analysis function
async function convertToJpegBase64(imagePath: string): Promise<string | null> {
  try {
    const buffer = await sharp(imagePath)
      .resize({ width: 1200, height: 900, fit: 'inside', withoutEnlargement: true })
      .jpeg({ quality: 75 })
      .toBuffer();
    return buffer.toString('base64');
  } catch (e) {
    console.warn(`Failed to convert ${imagePath}: ${e}`);
    return null;
  }
}

async function analyzeWithGemini(screens: ScreenInfo[]): Promise<string> {
  if (!GEMINI_API_KEY || !ENABLE_GEMINI_ANALYSIS) {
    return 'Gemini analysis skipped (ENABLE_GEMINI_ANALYSIS not set or no API key)';
  }

  console.log(`\n🤖 Analyzing ${screens.length} screenshots with Gemini...`);

  const imageParts: any[] = [];
  for (const screen of screens.slice(0, 8)) {  // Max 8 screenshots
    const base64 = await convertToJpegBase64(screen.screenshotPath);
    if (base64) {
      imageParts.push({
        inline_data: { mime_type: 'image/jpeg', data: base64 }
      });
    }
  }

  if (imageParts.length === 0) {
    return 'No valid screenshots for analysis.';
  }

  const prompt = `You are a senior UX/UI designer reviewing a mobile field service inspector app built with Flutter.

Analyze these ${imageParts.length} screenshots and provide:

## 1. Overall UX Score (0-100)
Rate the app's overall user experience.

## 2. Visual Design Assessment
- Color scheme and consistency
- Typography and readability
- Spacing and layout
- Icon usage and clarity

## 3. Usability Issues (Critical → Minor)
List any usability problems with severity:
- 🔴 Critical: Blocks user tasks
- 🟠 Major: Causes significant friction
- 🟡 Minor: Small improvements needed

## 4. Mobile-Specific Considerations
- Touch target sizes
- Thumb-zone accessibility
- Loading states
- Offline indicators

## 5. Top 5 Actionable Improvements
Specific, implementable changes to improve UX:
1. [Improvement]
2. [Improvement]
3. [Improvement]
4. [Improvement]
5. [Improvement]

Be specific and actionable. Reference specific screens when possible.`;

  const requestBody = {
    contents: [{
      parts: [{ text: prompt }, ...imageParts]
    }],
    generationConfig: {
      temperature: 0.4,
      maxOutputTokens: 4000,
    }
  };

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${GEMINI_API_KEY}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      }
    );

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
    return 'No analysis returned from Gemini.';
  } catch (e) {
    return `Gemini analysis error: ${e}`;
  }
}

test.describe('Flutter UI Spider @flutter-spider', () => {
  test.setTimeout(300000); // 5 minutes

  test('Crawl all Flutter app screens', async ({ page }) => {
    console.log('🕷️  Starting Flutter UI Spider');
    console.log(`🌐 URL: ${FlutterConfig.baseUrl}`);
    console.log(`📸 Screenshots: ${SCREENSHOT_DIR}`);
    console.log(`🤖 Gemini Analysis: ${ENABLE_GEMINI_ANALYSIS ? 'Enabled' : 'Disabled'}`);

    // Navigate to app
    await page.goto(FlutterConfig.baseUrl);
    await waitForFlutterReady(page);

    // Capture login screen before logging in
    const loginInfo = await captureScreen(page, '/login', 'Login');
    discoveredScreens.push(loginInfo);
    console.log('📸 Login screen captured');

    // Perform login with keyboard (CanvasKit compatible)
    await loginWithKeyboard(page);
    await waitForFlutterReady(page);

    // Define routes to crawl (from FlutterRoutes)
    const routesToCrawl = [
      { route: FlutterRoutes.dashboard, name: 'Dashboard' },
      { route: FlutterRoutes.jobList, name: 'Job List' },
      { route: FlutterRoutes.routeList, name: 'Route List' },
      { route: FlutterRoutes.safetyTimer, name: 'Safety Timer' },
      { route: FlutterRoutes.settings, name: 'Settings' },
      { route: FlutterRoutes.sync, name: 'Sync Status' },
    ];

    // Crawl each route
    for (const { route, name } of routesToCrawl) {
      console.log(`\n🔍 Crawling: ${name} (${route})`);

      const success = await navigateToRoute(page, route);
      if (!success) {
        console.log(`  ⚠️ Could not navigate to ${route}`);
        continue;
      }

      const screenInfo = await captureScreen(page, route, name);
      discoveredScreens.push(screenInfo);

      const status = screenInfo.hasError ? '❌' : '✅';
      console.log(`  ${status} ${name} - ${screenInfo.elementCounts.buttons} buttons`);
    }

    // Run Gemini analysis
    let geminiAnalysis = '';
    if (ENABLE_GEMINI_ANALYSIS && GEMINI_API_KEY) {
      geminiAnalysis = await analyzeWithGemini(discoveredScreens);
      console.log('\n' + '='.repeat(60));
      console.log('🤖 GEMINI UX ANALYSIS');
      console.log('='.repeat(60));
      console.log(geminiAnalysis);
    }

    // Generate report
    const report = generateSpiderReport(discoveredScreens, geminiAnalysis);
    const reportPath = path.join(SCREENSHOT_DIR, 'flutter-spider-report.md');
    fs.writeFileSync(reportPath, report);

    // Save JSON data
    const jsonPath = path.join(SCREENSHOT_DIR, 'flutter-spider-data.json');
    fs.writeFileSync(jsonPath, JSON.stringify(discoveredScreens, null, 2));

    console.log('\n' + '='.repeat(60));
    console.log('🕷️  FLUTTER UI SPIDER COMPLETE');
    console.log(`📄 Report: ${reportPath}`);
    console.log(`📸 Screenshots: ${discoveredScreens.length}`);
    console.log('='.repeat(60));

    // Assertions
    expect(discoveredScreens.length).toBeGreaterThan(0);
  });
});

function generateSpiderReport(screens: ScreenInfo[], geminiAnalysis?: string): string {
  const errors = screens.filter(s => s.hasError);
  return `# Flutter UI Spider Report

Generated: ${new Date().toISOString()}
Base URL: ${FlutterConfig.baseUrl}

## Summary
- **Screens Captured:** ${screens.length}
- **Errors Found:** ${errors.length}

## Screens Crawled

| Screen | Route | Buttons | Inputs | Status |
|--------|-------|---------|--------|--------|
${screens.map(s => `| ${s.name} | ${s.route} | ${s.elementCounts.buttons} | ${s.elementCounts.inputs} | ${s.hasError ? '❌' : '✅'} |`).join('\n')}

## Screenshots
All screenshots saved to: \`${SCREENSHOT_DIR}/\`

${geminiAnalysis ? `## 🤖 Gemini UX Analysis\n\n${geminiAnalysis}` : ''}
`;
}

