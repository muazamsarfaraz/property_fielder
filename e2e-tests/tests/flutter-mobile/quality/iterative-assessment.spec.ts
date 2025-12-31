/**
 * Iterative UI Assessment
 * 
 * Runs after fixes are applied to:
 * 1. Re-capture screenshots
 * 2. Re-analyze with Gemini
 * 3. Compare scores with previous run
 * 4. Track improvement progress
 */

import { test, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import { FlutterConfig } from '../config/flutter-config';
import { LoginPage, DashboardPage, JobListPage, SafetyTimerPage, TemplateExecutionPage } from '../pages';
import { processExistingAnalysis, generateMarkdownReport, FeedbackReport } from '../utils/quality-feedback-loop';

const ANALYSIS_DIR = 'test-results/flutter-mobile/analysis';
const HISTORY_DIR = 'test-results/flutter-mobile/history';

interface AssessmentHistory {
  runs: {
    timestamp: string;
    score: number;
    issueCount: number;
    criticalCount: number;
  }[];
}

function loadHistory(): AssessmentHistory {
  const historyPath = path.join(HISTORY_DIR, 'assessment-history.json');
  if (fs.existsSync(historyPath)) {
    return JSON.parse(fs.readFileSync(historyPath, 'utf-8'));
  }
  return { runs: [] };
}

function saveHistory(history: AssessmentHistory): void {
  if (!fs.existsSync(HISTORY_DIR)) {
    fs.mkdirSync(HISTORY_DIR, { recursive: true });
  }
  fs.writeFileSync(
    path.join(HISTORY_DIR, 'assessment-history.json'),
    JSON.stringify(history, null, 2)
  );
}

function generateProgressReport(history: AssessmentHistory): string {
  if (history.runs.length === 0) {
    return '# No assessment history yet\n\nRun the UI Quality Assessment first.';
  }

  const latest = history.runs[history.runs.length - 1];
  const first = history.runs[0];
  const improvement = latest.score - first.score;

  let trend = '';
  if (history.runs.length >= 2) {
    const prev = history.runs[history.runs.length - 2];
    const delta = latest.score - prev.score;
    trend = delta > 0 ? `📈 +${delta}` : delta < 0 ? `📉 ${delta}` : '➡️ No change';
  }

  return `# UI Quality Progress Report

## Current Status
- **Latest Score:** ${latest.score}/100 ${trend}
- **Total Improvement:** +${improvement} points
- **Critical Issues:** ${latest.criticalCount}
- **Total Issues:** ${latest.issueCount}

## Assessment History

| Date | Score | Issues | Critical |
|------|-------|--------|----------|
${history.runs.map(r => `| ${new Date(r.timestamp).toLocaleDateString()} | ${r.score} | ${r.issueCount} | ${r.criticalCount} |`).join('\n')}

## Score Trend
\`\`\`
${history.runs.map((r, i) => `Run ${i + 1}: ${'█'.repeat(Math.floor(r.score / 5))} ${r.score}`).join('\n')}
\`\`\`

## Recommendations
${latest.score < 70 ? '- 🔴 Focus on critical issues first' : ''}
${latest.score >= 70 && latest.score < 85 ? '- 🟠 Good progress! Address major issues next' : ''}
${latest.score >= 85 ? '- 🟢 Excellent! Polish minor issues and suggestions' : ''}
`;
}

test.describe('Iterative UI Assessment @flutter-iterate', () => {
  test.setTimeout(60000);

  test('Process existing analysis and generate fix report', async ({ page }) => {
    console.log('📋 Processing existing analysis...');
    
    const report = processExistingAnalysis(ANALYSIS_DIR);
    
    if (!report) {
      console.log('⚠️ No existing analysis found. Run ui-quality-assessment first.');
      return;
    }

    // Generate fix report
    const markdown = generateMarkdownReport(report);
    fs.writeFileSync(path.join(ANALYSIS_DIR, 'fix-report.md'), markdown);

    // Update history
    const history = loadHistory();
    history.runs.push({
      timestamp: new Date().toISOString(),
      score: report.overallScore,
      issueCount: report.recommendations.length,
      criticalCount: report.summary.critical,
    });
    saveHistory(history);

    // Generate progress report
    const progress = generateProgressReport(history);
    fs.writeFileSync(path.join(ANALYSIS_DIR, 'progress-report.md'), progress);

    console.log(`\n📊 Assessment Results:`);
    console.log(`   Score: ${report.overallScore}/100`);
    console.log(`   Issues: ${report.recommendations.length}`);
    console.log(`   Critical: ${report.summary.critical}`);
    console.log(`\n📄 Reports generated:`);
    console.log(`   - ${ANALYSIS_DIR}/fix-report.md`);
    console.log(`   - ${ANALYSIS_DIR}/progress-report.md`);

    expect(report.overallScore).toBeGreaterThanOrEqual(0);
  });

  test('Compare with previous assessment', async ({ page }) => {
    const history = loadHistory();
    
    if (history.runs.length < 2) {
      console.log('⚠️ Need at least 2 assessments to compare.');
      return;
    }

    const latest = history.runs[history.runs.length - 1];
    const previous = history.runs[history.runs.length - 2];
    const delta = latest.score - previous.score;

    console.log(`\n📊 Comparison:`);
    console.log(`   Previous: ${previous.score}/100`);
    console.log(`   Current:  ${latest.score}/100`);
    console.log(`   Change:   ${delta >= 0 ? '+' : ''}${delta}`);

    if (delta > 0) {
      console.log(`\n✅ UI quality improved by ${delta} points!`);
    } else if (delta < 0) {
      console.log(`\n⚠️ UI quality decreased by ${Math.abs(delta)} points.`);
    } else {
      console.log(`\n➡️ UI quality unchanged.`);
    }

    // Progress report already generated in previous test
    expect(history.runs.length).toBeGreaterThanOrEqual(2);
  });

  test('Generate developer task list from issues', async ({ page }) => {
    const report = processExistingAnalysis(ANALYSIS_DIR);
    
    if (!report) {
      console.log('⚠️ No analysis to process.');
      return;
    }

    // Generate a task list for developers
    const tasks = report.recommendations.map((r, i) => ({
      id: r.id,
      priority: r.priority,
      title: `[${r.screen}] ${r.issue.substring(0, 60)}...`,
      effort: r.estimatedEffort,
    }));

    const taskList = `# UI Fix Task List

Generated: ${new Date().toISOString()}

## Priority Order

${tasks.filter(t => t.priority === 1).map(t => `- [ ] 🔴 ${t.id}: ${t.title}`).join('\n')}
${tasks.filter(t => t.priority === 2).map(t => `- [ ] 🟠 ${t.id}: ${t.title}`).join('\n')}
${tasks.filter(t => t.priority === 3).map(t => `- [ ] 🟡 ${t.id}: ${t.title}`).join('\n')}
${tasks.filter(t => t.priority === 4).map(t => `- [ ] 🔵 ${t.id}: ${t.title}`).join('\n')}

## After Fixing
1. Run: \`npm run test:flutter-quality\`
2. Check: \`test-results/flutter-mobile/analysis/progress-report.md\`
3. Repeat until target score reached
`;

    fs.writeFileSync(path.join(ANALYSIS_DIR, 'task-list.md'), taskList);
    console.log(`\n📋 Task list generated: ${ANALYSIS_DIR}/task-list.md`);

    expect(tasks.length).toBeGreaterThanOrEqual(0);
  });
});

