# Flutter Mobile App Test Suite

Playwright E2E tests for the Property Fielder Inspector mobile app (Flutter Web).

## Overview

This test suite provides:

1. **User Story Tests** - Test actual user workflows (login, jobs, safety, inspections)
2. **UI Spider** - Crawls all screens and captures screenshots
3. **UI Quality Assessment** - Gemini AI-powered analysis with actionable feedback
4. **Iterative Improvement** - Track progress across multiple assessment runs

## Quick Start

```bash
# Navigate to e2e-tests directory
cd property_fielder/e2e-tests

# Install dependencies (if not already done)
npm install

# Run all Flutter tests
npm run test:flutter

# Run with browser visible
npm run test:flutter:headed
```

## Test Commands

| Command | Description |
|---------|-------------|
| `npm run test:flutter` | Run all Flutter tests |
| `npm run test:flutter:headed` | Run with browser visible |
| `npm run test:flutter:stories` | Run user story tests |
| `npm run test:flutter:spider` | Crawl all screens & capture screenshots |
| `npm run test:flutter:quality` | AI-powered UI quality analysis |
| `npm run test:flutter:iterate` | Process analysis & track progress |
| `npm run test:flutter:auth` | Test login workflow |
| `npm run test:flutter:jobs` | Test job workflow |
| `npm run test:flutter:safety` | Test safety timer |
| `npm run test:flutter:inspection` | Test inspection templates |

## Configuration

Set environment variables before running tests:

```bash
# Flutter app URL
export FLUTTER_URL=http://localhost:8080

# Test credentials
export FLUTTER_USERNAME=inspector@test.com
export FLUTTER_PASSWORD=test123

# Enable Gemini AI analysis
export ENABLE_GEMINI_ANALYSIS=true
export GEMINI_API_KEY=your_gemini_api_key
```

Or create a `.env` file in the e2e-tests directory.

## UI Quality Feedback Loop

### Step 1: Run Initial Assessment

```bash
npm run test:flutter:quality
```

This captures screenshots and sends them to Gemini for analysis.

### Step 2: Review Reports

Check the generated reports:

```
test-results/flutter-mobile/analysis/
├── gemini-analysis.md      # Raw Gemini analysis
├── quality-report.json     # Structured report
├── fix-report.md           # Developer-friendly fixes
└── task-list.md            # Prioritized task list
```

### Step 3: Fix Issues

Work through the task list, focusing on:
1. 🔴 Critical issues first
2. 🟠 Major issues next
3. 🟡 Minor issues
4. 🔵 Suggestions

### Step 4: Re-assess

```bash
npm run test:flutter:iterate
```

This compares with previous runs and tracks improvement.

### Step 5: Repeat

Continue the loop until the target score is reached.

## Directory Structure

```
tests/flutter-mobile/
├── config/
│   ├── flutter-config.ts     # App configuration
│   └── user-stories.ts       # User story definitions
├── pages/
│   ├── flutter-base.page.ts  # Base page object
│   ├── login.page.ts         # Login screen
│   ├── dashboard.page.ts     # Dashboard screen
│   ├── job-list.page.ts      # Job list screen
│   ├── job-detail.page.ts    # Job detail screen
│   ├── safety-timer.page.ts  # Safety timer screen
│   └── template-execution.page.ts
├── stories/
│   ├── inspector-login.spec.ts
│   ├── job-workflow.spec.ts
│   ├── safety-timer.spec.ts
│   └── inspection-template.spec.ts
├── quality/
│   ├── flutter-spider.spec.ts
│   ├── ui-quality-assessment.spec.ts
│   └── iterative-assessment.spec.ts
└── utils/
    └── quality-feedback-loop.ts
```

## User Stories Covered

| ID | Story | Priority |
|----|-------|----------|
| US-AUTH-001 | Inspector Login | Critical |
| US-JOB-001 | View Assigned Jobs | Critical |
| US-JOB-002 | Job Check-In/Check-Out | Critical |
| US-PHOTO-001 | Capture Photos | High |
| US-SIG-001 | Capture Signature | High |
| US-SAFETY-001 | Safety Timer | Critical |
| US-SAFETY-002 | Panic Button | Critical |
| US-TEMPLATE-001 | Execute Template | High |

## Flutter Web Requirements

Before running tests, ensure:

1. Flutter app is built for web: `flutter build web`
2. App is running: `flutter run -d chrome --web-renderer html`
3. Or served statically: `python -m http.server 8080 -d build/web`

Note: Use `--web-renderer html` for better Playwright compatibility.

## Troubleshooting

### Flutter app not loading
- Check if the app is running at the configured URL
- Try increasing timeouts in flutter-config.ts

### Gemini analysis failing
- Verify GEMINI_API_KEY is set correctly
- Check API quota and limits

### Selectors not finding elements
- Flutter web DOM can vary; update selectors in flutter-config.ts
- Use Playwright codegen: `npm run codegen:flutter`

