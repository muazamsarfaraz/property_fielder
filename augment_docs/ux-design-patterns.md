# UX Design Patterns - Property Fielder

> Auto-generated UX guidelines from Gemini 3 Pro Preview analysis.  
> Last updated: 2025-12-14

## Automated UX Analysis Workflow

We use an automated Playwright + Gemini AI workflow to evaluate and iterate on UX:

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Playwright     │────▶│  Screenshot      │────▶│  Gemini 3 Pro   │
│  E2E Test       │     │  Capture (JPEG)  │     │  Analysis       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │  UX Report      │
                                                 │  (Markdown)     │
                                                 └─────────────────┘
```

### Running UX Analysis

```bash
cd e2e-tests
npm run test:ux-analysis
```

Screenshots saved to: `test-results/ux-analysis/`  
Report saved to: `test-results/ux-analysis/ux-analysis-report.md`

---

## Core Design Principles

### 1. Never Block the Primary Workspace

❌ **Don't:** Use center-screen modals that block the main content (map, calendar, etc.)

✅ **Do:** Use corner notifications, inline empty states, or collapsible panels

```css
/* Corner notification instead of blocking modal */
.empty-state-notice {
  position: absolute;
  top: 1rem;
  right: 1rem;
  max-width: 300px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  padding: 1rem;
}
```

### 2. Dock Control Panels (No Floating)

❌ **Don't:** Use floating/draggable panels that obscure content

✅ **Do:** Use fixed sidebars with solid backgrounds

```css
.dispatch-container {
  display: grid;
  grid-template-columns: 350px 1fr; /* Fixed sidebar, flexible content */
  grid-template-rows: 60px 1fr 200px; /* Header, Main, Timeline */
  height: 100vh;
}

.control-sidebar {
  grid-column: 1;
  grid-row: 2 / -1;
  background: #f8f9fa; /* Solid, not glassmorphism */
  border-right: 1px solid #ddd;
  overflow-y: auto;
}
```

### 3. Progressive Disclosure (Stepper Pattern)

❌ **Don't:** Allow users to access tabs/steps without prerequisites

✅ **Do:** Lock steps until prerequisites are met, show clear feedback

```javascript
function onTabChange(targetTab) {
  const hasJobs = this.state.selectedJobIds.length > 0;
  const hasInspectors = this.state.selectedInspectorIds.length > 0;

  if (targetTab === 'optimize' && (!hasJobs || !hasInspectors)) {
    this.notification.add('Select jobs and inspectors first', { type: 'warning' });
    return; // Prevent navigation
  }
  this.currentTab = targetTab;
}
```

### 4. Immediate Visual Feedback

When user selects an item in a list, reflect it immediately on the map/canvas:

```javascript
onInspectorSelect(inspectorId) {
  // Update sidebar state
  this.state.selectedInspectors.add(inspectorId);
  
  // Immediately highlight on map
  this.mapComponent.highlightLocation(inspector.homeLocation, {
    color: '#7C3AED',
    pulse: true
  });
}
```

### 5. Smart Defaults

- Auto-select the date range with available data
- Pre-select commonly used inspectors
- Remember user's last filter settings

```javascript
async loadInitialData() {
  const dateWithMostJobs = await this.findDateWithData();
  if (dateWithMostJobs) {
    this.state.selectedDate = dateWithMostJobs;
  }
}
```

---

## Component Patterns

### Sidebar Layout (Docked)

```
┌────────────────────────────────────────────────────────┐
│ Header / Navigation Bar                                │
├──────────────┬─────────────────────────────────────────┤
│              │                                         │
│  SIDEBAR     │         MAP / MAIN CONTENT              │
│  (350px)     │                                         │
│              │                                         │
│  - Resources │                                         │
│  - Settings  │                                         │
│  - Actions   │                                         │
│              ├─────────────────────────────────────────┤
│              │         TIMELINE (collapsible)          │
└──────────────┴─────────────────────────────────────────┘
```

### Button States

| State | Appearance | Behavior |
|-------|------------|----------|
| Enabled | Solid purple `#7C3AED` | Clickable |
| Disabled | Gray `#9CA3AF` | Tooltip explains why |
| Loading | Purple with spinner | Not clickable |
| Success | Green flash | Auto-revert |

### Empty States

Instead of blocking modals, use inline empty states:

```html
<div class="empty-state-inline">
  <svg class="empty-icon"><!-- calendar icon --></svg>
  <h3>No jobs scheduled for this date</h3>
  <p>Select a different date or load test data</p>
  <button class="btn-secondary">← Change Date</button>
</div>
```

---

## Color Palette

| Purpose | Color | Hex |
|---------|-------|-----|
| Primary Action | Purple | `#7C3AED` |
| Secondary | Gray | `#6B7280` |
| Success | Green | `#10B981` |
| Warning | Amber | `#F59E0B` |
| Error | Red | `#EF4444` |
| Background | Light Gray | `#F8F9FA` |
| Border | Medium Gray | `#E5E7EB` |

---

## Checklist for New Views

Before shipping any new view, verify:

- [ ] No blocking center modals
- [ ] Sidebars are docked, not floating
- [ ] Tabs/steps have prerequisite validation
- [ ] Empty states are inline, not modal
- [ ] Selection reflects immediately on map/main content
- [ ] Disabled buttons have tooltips explaining why
- [ ] Date/filter defaults to data-populated range
- [ ] Run `npm run test:ux-analysis` and score > 7/10

