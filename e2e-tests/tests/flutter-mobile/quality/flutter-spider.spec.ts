/**
 * Flutter UI Spider
 * 
 * Crawls all Flutter app screens to:
 * 1. Discover all accessible pages/routes
 * 2. Take screenshots of each view
 * 3. Detect errors or issues
 * 4. Collect data for Gemini analysis
 */

import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { FlutterConfig, FlutterRoutes, FlutterSelectors } from '../config/flutter-config';
import { LoginPage } from '../pages';

const SCREENSHOT_DIR = 'test-results/flutter-mobile';

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
  await page.waitForTimeout(FlutterConfig.timeouts.animation);
  
  const loading = page.locator(FlutterSelectors.loading);
  if (await loading.isVisible({ timeout: 500 }).catch(() => false)) {
    await loading.waitFor({ state: 'hidden', timeout: 30000 });
  }
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

test.describe('Flutter UI Spider @flutter-spider', () => {
  test.setTimeout(300000); // 5 minutes

  test('Crawl all Flutter app screens', async ({ page }) => {
    console.log('🕷️  Starting Flutter UI Spider');
    console.log(`🌐 URL: ${FlutterConfig.baseUrl}`);
    console.log(`📸 Screenshots: ${SCREENSHOT_DIR}`);

    // Login first
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    
    // Capture login screen before logging in
    const loginInfo = await captureScreen(page, '/login', 'Login');
    discoveredScreens.push(loginInfo);
    console.log('📸 Login screen captured');

    // Perform login
    await loginPage.login();
    console.log('✅ Logged in successfully');

    // Define routes to crawl (from FlutterRoutes)
    const routesToCrawl = [
      { route: FlutterRoutes.dashboard, name: 'Dashboard' },
      { route: FlutterRoutes.jobList, name: 'Job List' },
      { route: FlutterRoutes.jobDetail, name: 'Job Detail' },
      { route: FlutterRoutes.routeList, name: 'Route List' },
      { route: FlutterRoutes.safetyTimer, name: 'Safety Timer' },
      { route: FlutterRoutes.templateExecution, name: 'Template Execution' },
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

    // Generate report
    const report = generateSpiderReport(discoveredScreens);
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

function generateSpiderReport(screens: ScreenInfo[]): string {
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
`;
}

