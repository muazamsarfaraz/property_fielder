/**
 * UI Quality Assessment
 * 
 * Analyzes Flutter app screenshots using Gemini AI to:
 * 1. Assess UI quality and consistency
 * 2. Identify UX issues
 * 3. Generate actionable improvement recommendations
 * 4. Create reports for iterative fixes
 */

import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import sharp from 'sharp';
import { FlutterConfig, FlutterRoutes } from '../config/flutter-config';
import { UserStories } from '../config/user-stories';
import { LoginPage, DashboardPage, JobListPage, SafetyTimerPage, TemplateExecutionPage } from '../pages';

const SCREENSHOT_DIR = 'test-results/flutter-mobile';
const ANALYSIS_DIR = 'test-results/flutter-mobile/analysis';

interface QualityIssue {
  severity: 'critical' | 'major' | 'minor' | 'suggestion';
  category: 'consistency' | 'accessibility' | 'usability' | 'visual' | 'performance';
  screen: string;
  description: string;
  recommendation: string;
  codeHint?: string;
}

interface QualityReport {
  timestamp: string;
  overallScore: number;
  screens: string[];
  issues: QualityIssue[];
  summary: string;
  geminiAnalysis?: string;
}

// Ensure directories exist
[SCREENSHOT_DIR, ANALYSIS_DIR].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

async function convertToJpegBase64(pngPath: string): Promise<string | null> {
  if (!fs.existsSync(pngPath)) return null;
  try {
    const jpegBuffer = await sharp(pngPath)
      .jpeg({ quality: 70 })
      .resize(1280, 800, { fit: 'inside' })
      .toBuffer();
    return jpegBuffer.toString('base64');
  } catch {
    return null;
  }
}

async function analyzeWithGemini(screenshotPaths: string[], userStoryContext: string): Promise<string> {
  const { gemini } = FlutterConfig;
  
  if (!gemini.apiKey || !gemini.enableAnalysis) {
    return 'Gemini analysis skipped (ENABLE_GEMINI_ANALYSIS not set or no API key)';
  }

  console.log(`📊 Analyzing ${screenshotPaths.length} screenshots with Gemini...`);

  const imageParts: any[] = [];
  for (const screenshotPath of screenshotPaths) {
    const base64 = await convertToJpegBase64(screenshotPath);
    if (base64) {
      imageParts.push({
        inline_data: { mime_type: 'image/jpeg', data: base64 }
      });
    }
  }

  if (imageParts.length === 0) {
    return 'No valid screenshots for analysis.';
  }

  const prompt = `You are a Senior UX/UI Expert analyzing a Flutter mobile app for field service inspectors.

## Context
${userStoryContext}

## Analysis Required

Analyze these ${imageParts.length} screenshots and provide:

### 1. Overall UI Quality Score (1-100)
Rate based on: visual consistency, usability, accessibility, mobile best practices.

### 2. Critical Issues (Fix Immediately)
Issues that block user tasks or cause confusion.

### 3. Major Issues (Fix Soon)
Issues that significantly impact user experience.

### 4. Minor Issues & Suggestions
Nice-to-have improvements.

### 5. Specific Recommendations
For each issue, provide:
- **Screen:** Which screen has the issue
- **Problem:** Clear description
- **Fix:** Specific actionable recommendation
- **Code Hint:** If applicable, suggest Flutter widget/pattern to use

### 6. Accessibility Review
- Contrast issues
- Touch target sizes (min 48x48dp)
- Screen reader compatibility

### 7. Consistency Check
- Are colors consistent across screens?
- Are fonts and spacing consistent?
- Do similar actions have similar UI patterns?

Format your response as structured markdown that can be parsed.`;

  const requestBody = {
    contents: [{ parts: [{ text: prompt }, ...imageParts] }],
    generationConfig: { temperature: 0.7, maxOutputTokens: 8192 }
  };

  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/${gemini.model}:generateContent?key=${gemini.apiKey}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
        signal: AbortSignal.timeout(180000)
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
    return 'Unexpected response format from Gemini.';
  } catch (error: any) {
    return `Gemini error: ${error.message}`;
  }
}

function generateQualityReport(analysis: string, screens: string[]): QualityReport {
  // Parse score from analysis if present
  const scoreMatch = analysis.match(/Score[:\s]*(\d+)/i);
  const overallScore = scoreMatch ? parseInt(scoreMatch[1]) : 0;

  return {
    timestamp: new Date().toISOString(),
    overallScore,
    screens,
    issues: [], // Would be parsed from analysis
    summary: analysis.substring(0, 500),
    geminiAnalysis: analysis,
  };
}

test.describe('UI Quality Assessment @flutter-quality @gemini', () => {
  test.setTimeout(300000);

  test('Comprehensive UI quality analysis with Gemini', async ({ page }) => {
    const screenshots: string[] = [];
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);
    const jobListPage = new JobListPage(page);
    const safetyPage = new SafetyTimerPage(page);

    // Login and capture screens
    await loginPage.goto();
    screenshots.push(await loginPage.takeScreenshot('quality-login'));
    await loginPage.login();

    screenshots.push(await dashboardPage.takeScreenshot('quality-dashboard'));
    await jobListPage.goto();
    screenshots.push(await jobListPage.takeScreenshot('quality-job-list'));
    await safetyPage.goto();
    screenshots.push(await safetyPage.takeScreenshot('quality-safety-timer'));

    // Build user story context
    const storyContext = Object.values(UserStories)
      .map(s => `- ${s.id}: ${s.name} - ${s.description}`)
      .join('\n');

    // Analyze with Gemini
    const analysis = await analyzeWithGemini(screenshots, storyContext);
    const report = generateQualityReport(analysis, screenshots);

    // Save reports
    fs.writeFileSync(path.join(ANALYSIS_DIR, 'quality-report.json'), JSON.stringify(report, null, 2));
    fs.writeFileSync(path.join(ANALYSIS_DIR, 'gemini-analysis.md'), `# Gemini UI Analysis\n\n${analysis}`);

    console.log('\n📊 UI Quality Analysis Complete');
    console.log(`📈 Overall Score: ${report.overallScore}/100`);
    console.log(`📄 Report: ${ANALYSIS_DIR}/quality-report.json`);

    expect(screenshots.length).toBeGreaterThan(0);
  });
});

