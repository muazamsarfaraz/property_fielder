# Property Fielder E2E Tests

Comprehensive Playwright end-to-end tests for the Property Fielder Odoo application.

## Setup

```bash
cd property_fielder/e2e-tests
npm install
npx playwright install
```

Copy the example environment file and update with your credentials:
```bash
cp .env.example .env
```

## Running Tests

### All Tests
```bash
npm test
```

### Headed Mode (with browser visible)
```bash
npm run test:headed
```

### Interactive UI Mode
```bash
npm run test:ui
```

### Debug Mode
```bash
npm run test:debug
```

### Specific Test Suites
```bash
npm run test:auth           # Authentication tests
npm run test:properties     # Property Management tests
npm run test:field-service  # Field Service tests
npm run test:dispatch       # Dispatch View tests
```

### By Tag
```bash
npm run test:smoke       # Quick sanity checks
npm run test:regression  # Full regression suite
npm run test:critical    # Critical path tests only
```

### UX Analysis Tests
```bash
# UI Link Spider - crawls all menus and takes screenshots
npx playwright test --grep @link-spider

# With Gemini AI analysis
ENABLE_GEMINI_ANALYSIS=true GEMINI_API_KEY=your-key npx playwright test --grep @link-spider

# Dispatch UX Analysis
npx playwright test --grep @ux-analysis
```

## Test Structure

```
e2e-tests/
├── fixtures/           # Test fixtures and extensions
├── pages/              # Page Object Models
│   ├── base.page.ts
│   ├── property-management.page.ts
│   ├── field-service.page.ts
│   └── dispatch.page.ts
├── utils/              # Helper utilities
│   ├── odoo-helpers.ts
│   └── test-data-manager.ts
├── tests/              # Test specs
│   ├── auth/           # Authentication tests
│   ├── property-management/
│   ├── field-service/
│   ├── dispatch/
│   ├── ux-analysis/    # UX analysis tests
│   │   ├── dispatch-ux-analysis.spec.ts  # Dispatch UX with Gemini
│   │   └── link-spider.spec.ts           # UI link crawler
│   └── smoke.spec.ts   # Quick smoke tests
├── playwright.config.ts
└── global.setup.ts     # Authentication setup
```

## Tags

Use tags to filter tests:
- `@smoke` - Quick sanity tests (< 5 min)
- `@regression` - Full regression suite
- `@critical` - Critical business flows
- `@slow` - Long-running tests
- `@link-spider` - UI link crawler (crawls all menus)
- `@ux-analysis` - UX analysis with Gemini AI

## Adding New Tests

1. **Create Page Object** (if new module):
   ```typescript
   // pages/new-module.page.ts
   export class NewModulePage extends BasePage {
     // Add selectors and methods
   }
   ```

2. **Add to fixtures**:
   ```typescript
   // fixtures/test-fixtures.ts
   newModulePage: async ({ page }, use) => {
     await use(new NewModulePage(page));
   },
   ```

3. **Create test file**:
   ```typescript
   // tests/new-module/feature.spec.ts
   import { test, expect } from '../../fixtures/test-fixtures';
   
   test.describe('New Feature @regression', () => {
     test('should do something', async ({ newModulePage }) => {
       // Test implementation
     });
   });
   ```

## Test Data

Test data is generated on-demand using `TestDataManager`:

```typescript
const propertyData = TestDataManager.propertyData({
  name: 'Custom Name',  // Override defaults
});
```

## Reports

After running tests, view the HTML report:
```bash
npm run report
```

Reports are generated in `playwright-report/`.

## CI/CD Integration

The tests are configured for CI environments:
- Retries: 2 (on failure)
- Screenshots: On failure
- Video: On first retry
- Traces: On first retry

Set `CI=true` environment variable in CI pipelines.

