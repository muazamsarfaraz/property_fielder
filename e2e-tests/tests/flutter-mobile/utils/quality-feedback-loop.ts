/**
 * Quality Feedback Loop Utility
 * 
 * Parses Gemini analysis and generates actionable fix recommendations
 * for Flutter developers to iterate on UI improvements.
 */

import * as fs from 'fs';
import * as path from 'path';

export interface FixRecommendation {
  id: string;
  priority: 1 | 2 | 3 | 4; // 1 = Critical, 4 = Suggestion
  screen: string;
  issue: string;
  recommendation: string;
  flutterHint?: string;
  file?: string;
  lineHint?: string;
  estimatedEffort: 'small' | 'medium' | 'large';
  status: 'pending' | 'in_progress' | 'fixed' | 'wont_fix';
}

export interface FeedbackReport {
  generatedAt: string;
  analysisSource: string;
  overallScore: number;
  targetScore: number;
  recommendations: FixRecommendation[];
  summary: {
    critical: number;
    major: number;
    minor: number;
    suggestions: number;
    totalEffort: string;
  };
}

/**
 * Parse Gemini analysis markdown and extract fix recommendations
 */
export function parseGeminiAnalysis(analysisMarkdown: string): FixRecommendation[] {
  const recommendations: FixRecommendation[] = [];
  let id = 1;

  // Extract score
  const scoreMatch = analysisMarkdown.match(/Score[:\s]*(\d+)/i);
  
  // Parse critical issues
  const criticalSection = analysisMarkdown.match(/Critical Issues[\s\S]*?(?=###|$)/i);
  if (criticalSection) {
    const issues = extractIssues(criticalSection[0], 1);
    recommendations.push(...issues.map(i => ({ ...i, id: `FIX-${id++}` })));
  }

  // Parse major issues
  const majorSection = analysisMarkdown.match(/Major Issues[\s\S]*?(?=###|$)/i);
  if (majorSection) {
    const issues = extractIssues(majorSection[0], 2);
    recommendations.push(...issues.map(i => ({ ...i, id: `FIX-${id++}` })));
  }

  // Parse minor issues
  const minorSection = analysisMarkdown.match(/Minor Issues[\s\S]*?(?=###|$)/i);
  if (minorSection) {
    const issues = extractIssues(minorSection[0], 3);
    recommendations.push(...issues.map(i => ({ ...i, id: `FIX-${id++}` })));
  }

  return recommendations;
}

function extractIssues(section: string, priority: 1 | 2 | 3 | 4): Omit<FixRecommendation, 'id'>[] {
  const issues: Omit<FixRecommendation, 'id'>[] = [];
  
  // Match bullet points or numbered items
  const lines = section.split('\n').filter(l => l.trim().startsWith('-') || l.trim().match(/^\d+\./));
  
  for (const line of lines) {
    const cleanLine = line.replace(/^[\s-]*\d*\.?\s*/, '').trim();
    if (cleanLine.length > 10) {
      issues.push({
        priority,
        screen: extractScreen(cleanLine),
        issue: cleanLine,
        recommendation: `Review and fix: ${cleanLine}`,
        estimatedEffort: priority <= 2 ? 'medium' : 'small',
        status: 'pending',
      });
    }
  }
  
  return issues;
}

function extractScreen(text: string): string {
  const screens = ['Login', 'Dashboard', 'Job List', 'Job Detail', 'Safety', 'Template', 'Settings'];
  for (const screen of screens) {
    if (text.toLowerCase().includes(screen.toLowerCase())) {
      return screen;
    }
  }
  return 'General';
}

/**
 * Generate a developer-friendly fix report
 */
export function generateFixReport(recommendations: FixRecommendation[], score: number): FeedbackReport {
  const critical = recommendations.filter(r => r.priority === 1).length;
  const major = recommendations.filter(r => r.priority === 2).length;
  const minor = recommendations.filter(r => r.priority === 3).length;
  const suggestions = recommendations.filter(r => r.priority === 4).length;

  const effortHours = critical * 4 + major * 2 + minor * 1 + suggestions * 0.5;
  
  return {
    generatedAt: new Date().toISOString(),
    analysisSource: 'gemini-2.5-pro-preview',
    overallScore: score,
    targetScore: Math.min(100, score + 15),
    recommendations,
    summary: {
      critical,
      major,
      minor,
      suggestions,
      totalEffort: `${effortHours.toFixed(1)} hours estimated`,
    },
  };
}

/**
 * Generate markdown report for developers
 */
export function generateMarkdownReport(report: FeedbackReport): string {
  const priorityLabels = { 1: '🔴 Critical', 2: '🟠 Major', 3: '🟡 Minor', 4: '🔵 Suggestion' };
  
  return `# Flutter UI Fix Report

Generated: ${report.generatedAt}
Current Score: **${report.overallScore}/100** → Target: **${report.targetScore}/100**

## Summary
- 🔴 Critical: ${report.summary.critical}
- 🟠 Major: ${report.summary.major}
- 🟡 Minor: ${report.summary.minor}
- 🔵 Suggestions: ${report.summary.suggestions}
- ⏱️ Estimated Effort: ${report.summary.totalEffort}

## Recommendations

${report.recommendations.map(r => `
### ${r.id}: ${priorityLabels[r.priority]}
**Screen:** ${r.screen}
**Issue:** ${r.issue}
**Recommendation:** ${r.recommendation}
${r.flutterHint ? `**Flutter Hint:** \`${r.flutterHint}\`` : ''}
**Status:** ${r.status}
`).join('\n---\n')}

## Next Steps
1. Fix all Critical issues first
2. Re-run UI Quality Assessment
3. Compare scores
4. Iterate until target score reached
`;
}

/**
 * Load and process existing analysis
 */
export function processExistingAnalysis(analysisDir: string): FeedbackReport | null {
  const analysisPath = path.join(analysisDir, 'gemini-analysis.md');
  
  if (!fs.existsSync(analysisPath)) {
    return null;
  }
  
  const analysisMarkdown = fs.readFileSync(analysisPath, 'utf-8');
  const recommendations = parseGeminiAnalysis(analysisMarkdown);
  
  const scoreMatch = analysisMarkdown.match(/Score[:\s]*(\d+)/i);
  const score = scoreMatch ? parseInt(scoreMatch[1]) : 50;
  
  return generateFixReport(recommendations, score);
}

