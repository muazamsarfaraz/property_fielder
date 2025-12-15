/**
 * Dispatch View UX Analysis Test
 * 
 * Automated Playwright test that:
 * 1. Uses 1920x1200 resolution
 * 2. Loads 20 test data set
 * 3. Creates inspections and plans routes
 * 4. Takes screenshots at key stages
 * 5. Sends screenshots to Gemini 3 Pro Preview for UX analysis
 * 6. Outputs actionable recommendations
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

const SCREENSHOT_DIR = 'test-results/ux-analysis';

// Ensure screenshot directory exists
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

  // Odoo 19 shows a user selection screen first - check if we see it
  const userButton = page.locator('button:has-text("admin")');
  if (await userButton.isVisible({ timeout: 2000 }).catch(() => false)) {
    // Click on the admin user to reveal password field
    await userButton.click();
    await page.waitForTimeout(300);
  }

  // Now fill in the login form - try multiple selectors for email/login field
  const loginInput = page.locator('input[name="login"], input[placeholder*="email" i], input[placeholder*="Enter your email" i]').first();
  if (await loginInput.isVisible({ timeout: 1000 }).catch(() => false)) {
    await loginInput.fill(USERNAME);
  }

  // Fill password field
  const passwordInput = page.locator('input[name="password"], input[type="password"]').first();
  await passwordInput.fill(PASSWORD);

  // Click login button
  await page.getByRole('button', { name: 'Log in' }).click();
  await waitForOdooLoad(page);

  // Wait for navigation to complete
  await page.waitForURL(/\/odoo\/|\/web(?!\/login)/, { timeout: 15000 });
}

async function navigateToDispatch(page: Page): Promise<void> {
  // Odoo 19: The home/apps menu button is the first button in the nav bar (hamburger icon)
  // It often has an empty name, so we need to find it by position in nav
  const homeBtn = page.locator('nav button').first();
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

async function takeScreenshot(page: Page, stage: string, description: string): Promise<string> {
  const filename = `${stage.replace(/\s+/g, '-').toLowerCase()}.png`;
  const filepath = path.join(SCREENSHOT_DIR, filename);
  // Use viewport screenshot (PNG for high quality local storage)
  await page.screenshot({ path: filepath, fullPage: false });
  screenshots.push({ path: filepath, stage, description });
  console.log(`📸 Screenshot: ${stage} - ${description}`);
  return filepath;
}

async function convertToJpegBase64(pngPath: string): Promise<string | null> {
  // Convert PNG to JPEG with compression for Gemini upload
  if (!fs.existsSync(pngPath)) return null;

  try {
    const jpegBuffer = await sharp(pngPath)
      .jpeg({ quality: 70 })
      .toBuffer();
    return jpegBuffer.toString('base64');
  } catch (error) {
    console.error(`Failed to convert ${pngPath} to JPEG:`, error);
    return null;
  }
}

async function analyzeWithGemini(screenshotPaths: Screenshot[]): Promise<string> {
  if (!GEMINI_API_KEY) {
    console.warn('⚠️  GEMINI_API_KEY not set. Skipping AI analysis.');
    return 'GEMINI_API_KEY not set. Screenshots saved for manual review.';
  }

  // Select key screenshots for analysis (limit to 3 to avoid timeout)
  const keyStages = ['04-data-loaded', '09-optimize-tab', '12-final-overview'];
  const keyScreenshots = screenshotPaths.filter(s =>
    keyStages.some(stage => s.stage.includes(stage))
  );

  // If no key screenshots found, use first 3
  const selectedScreenshots = keyScreenshots.length > 0 ? keyScreenshots.slice(0, 3) : screenshotPaths.slice(0, 3);

  console.log(`📊 Selected ${selectedScreenshots.length} key screenshots for Gemini analysis`);
  selectedScreenshots.forEach(s => console.log(`   - ${s.stage}: ${s.description}`));

  const imageParts: any[] = [];
  for (const screenshot of selectedScreenshots) {
    if (fs.existsSync(screenshot.path)) {
      // Convert PNG to compressed JPEG for upload
      const jpegBase64 = await convertToJpegBase64(screenshot.path);
      if (jpegBase64) {
        const fileSizeKB = Math.round(jpegBase64.length * 0.75 / 1024); // base64 is ~33% larger
        console.log(`   📁 ${screenshot.stage}: ${fileSizeKB}KB (JPEG compressed)`);
        imageParts.push({
          inline_data: {
            mime_type: 'image/jpeg',
            data: jpegBase64
          }
        });
      }
    }
  }

  if (imageParts.length === 0) {
    return 'No screenshots available for analysis.';
  }

  const stageDescriptions = selectedScreenshots
    .map((s, i) => `${i + 1}. **${s.stage}**: ${s.description}`)
    .join('\n');

  const prompt = `You are a UX/UI expert specializing in enterprise field service applications.

Analyze these ${imageParts.length} screenshots from a Property Fielder Dispatch view workflow:

${stageDescriptions}

The application is built on Odoo 19 for property inspectors to manage field service jobs.

Please provide a structured analysis:

## 1. Overall UX Score (1-10)
Rate the overall user experience with justification.

## 2. Visual Design Assessment
- Color scheme and contrast
- Typography and readability
- Visual hierarchy
- Consistency with modern design standards

## 3. Layout and Information Architecture
- Panel organization
- Map integration
- Data density
- Screen real estate usage

## 4. Interaction Design
- Button placement and discoverability
- Workflow clarity
- Feedback mechanisms
- Error prevention

## 5. Top 5 Critical Issues
List the most urgent UX problems to fix.

## 6. Actionable Recommendations
Provide 8-10 specific, implementable improvements with:
- What to change
- Why it matters
- How to implement (CSS/layout changes)

## 7. Code Suggestions
Provide specific CSS or layout code snippets to implement the top 3 recommendations.

Focus on practical improvements for field service dispatchers who need efficiency.`;

  const requestBody = {
    contents: [{
      parts: [{ text: prompt }, ...imageParts]
    }],
    generationConfig: {
      temperature: 0.7,
      maxOutputTokens: 8192
    }
  };

  console.log('\n🤖 Sending to Gemini 3 Pro Preview for analysis...\n');
  console.log(`📤 Sending ${imageParts.length} screenshots to model: ${GEMINI_MODEL}`);

  // Add timeout controller for API call (2 minutes)
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
      return 'Gemini API call timed out after 2 minutes. Try with fewer screenshots.';
    }
    throw error;
  }
}

// Set viewport to 1920x1200 at top level
test.use({
  viewport: { width: 1920, height: 1200 },
});

test.describe('Dispatch UX Analysis @ux-analysis', () => {
  test.describe.configure({ mode: 'serial' });

  test('Complete Dispatch Workflow with UX Analysis', async ({ page }) => {
    test.setTimeout(300000); // 5 minutes for full workflow

    console.log('🚀 Starting Dispatch UX Analysis Test');
    console.log(`📐 Viewport: 1920x1200`);
    console.log(`🌐 URL: ${BASE_URL}`);

    // Step 1: Login
    await login(page);
    await takeScreenshot(page, '01-home', 'Odoo home page after login');

    // Step 2: Navigate to Dispatch
    await navigateToDispatch(page);
    await page.waitForTimeout(3000);
    await takeScreenshot(page, '02-dispatch-empty', 'Dispatch view initial state (empty)');

    // Step 3: Load 20 Test Data
    console.log('\n📦 Loading 20 Test Jobs...');
    const testDataBtn = page.locator('button.btn-ghost.dropdown-toggle');
    await testDataBtn.click();
    await page.waitForTimeout(500);
    await takeScreenshot(page, '03-dropdown-open', 'Test Data dropdown menu open');

    const loadBtn = page.locator('a:has-text("Load 20 Test Jobs")');
    if (await loadBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
      await loadBtn.click();
      console.log('⏳ Waiting for test data to load...');
      // Wait for notification to appear
      await page.waitForTimeout(3000);
      // Wait for data to fully load and map to update
      await page.waitForTimeout(6000);
    } else {
      console.log('⚠️ Load button not found, test data may already exist');
    }
    await takeScreenshot(page, '04-data-loaded', 'After loading 20 test jobs');

    // Step 4: Verify jobs loaded
    const jobsHeading = page.locator('h6:has-text("Jobs")');
    const headingText = await jobsHeading.textContent().catch(() => 'Jobs (0)');
    console.log(`📋 ${headingText}`);

    // Extract job count
    const match = headingText?.match(/Jobs \((\d+)\)/);
    const jobCount = match ? parseInt(match[1], 10) : 0;
    console.log(`📊 Job count: ${jobCount}`);

    // Step 5: Explore map with job pins
    await page.waitForTimeout(2000);
    await takeScreenshot(page, '05-map-with-pins', 'Map view with job pins visible');

    // Step 6: Click on a job pin to show popup
    const jobPin = page.locator('.job-pin-marker').first();
    if (await jobPin.isVisible({ timeout: 3000 }).catch(() => false)) {
      await jobPin.click();
      await page.waitForTimeout(500);
      await takeScreenshot(page, '06-pin-popup', 'Job pin popup/tooltip');
    }

    // Step 7: Select jobs and inspectors
    console.log('\n👥 Selecting resources...');
    const selectAllJobsBtn = page.locator('button:has-text("Select All")').first();
    if (await selectAllJobsBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      await selectAllJobsBtn.click();
      await page.waitForTimeout(500);
    }
    await takeScreenshot(page, '07-jobs-selected', 'All jobs selected');

    // Select all inspectors
    const inspectorSelectAll = page.locator('button:has-text("Select All")').nth(1);
    if (await inspectorSelectAll.isVisible({ timeout: 2000 }).catch(() => false)) {
      await inspectorSelectAll.click();
      await page.waitForTimeout(500);
    }
    await takeScreenshot(page, '08-inspectors-selected', 'Jobs and inspectors selected');

    // Step 8: Switch to Optimize tab
    console.log('\n⚡ Switching to Optimize tab...');
    const optimizeTab = page.locator('button:has-text("Optimize")');
    if (await optimizeTab.isVisible({ timeout: 2000 }).catch(() => false)) {
      await optimizeTab.click();
      await page.waitForTimeout(1000);
    }
    await takeScreenshot(page, '09-optimize-tab', 'Optimize tab view');

    // Step 9: Run optimization (if available and enabled)
    const startOptBtn = page.locator('button:has-text("Start Optimization")');
    if (await startOptBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      const isDisabled = await startOptBtn.isDisabled().catch(() => true);
      if (!isDisabled) {
        await startOptBtn.click();
        console.log('🔄 Running optimization...');
        // Wait for optimization to complete
        await page.waitForTimeout(30000);
        await takeScreenshot(page, '10-optimization-complete', 'After route optimization');
      } else {
        console.log('⚠️ Start Optimization button is disabled (no jobs/inspectors selected)');
        await takeScreenshot(page, '10-optimization-disabled', 'Optimization button disabled state');
      }
    }

    // Step 10: Switch to Schedule tab
    console.log('\n📅 Switching to Schedule tab...');
    const scheduleTab = page.locator('button:has-text("Schedule")');
    if (await scheduleTab.isVisible({ timeout: 2000 }).catch(() => false)) {
      await scheduleTab.click();
      await page.waitForTimeout(1000);
    }
    await takeScreenshot(page, '11-schedule-tab', 'Schedule tab with timeline');

    // Step 11: Final overview screenshot
    await page.waitForTimeout(1000);
    await takeScreenshot(page, '12-final-overview', 'Final workflow state overview');

    // Step 12: Run Gemini Analysis
    console.log('\n' + '='.repeat(80));
    console.log('🤖 GEMINI 3 PRO PREVIEW UX ANALYSIS');
    console.log('='.repeat(80));

    try {
      const analysis = await analyzeWithGemini(screenshots);
      console.log(analysis);

      // Save analysis to file
      const analysisPath = path.join(SCREENSHOT_DIR, 'ux-analysis-report.md');
      const reportContent = `# Dispatch View UX Analysis Report

Generated: ${new Date().toISOString()}
Model: Gemini 3 Pro Preview
Viewport: 1920x1200

## Screenshots Analyzed
${screenshots.map(s => `- **${s.stage}**: ${s.description}`).join('\n')}

---

${analysis}
`;
      fs.writeFileSync(analysisPath, reportContent);
      console.log(`\n📄 Report saved to: ${analysisPath}`);
    } catch (error) {
      console.error('❌ Gemini analysis failed:', error);
    }

    console.log('\n' + '='.repeat(80));
    console.log('✅ UX Analysis Test Complete');
    console.log(`📁 Screenshots saved to: ${SCREENSHOT_DIR}`);
    console.log('='.repeat(80));
  });
});

