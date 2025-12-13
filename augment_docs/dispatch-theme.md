# Property Fielder Dispatch UI Theme
> Modern Odoo-inspired design system for the Enhanced Dispatch View

## 🎨 Color Palette

### Primary Colors (Odoo Purple Accent)
| Token | Hex | Usage |
|-------|-----|-------|
| `--pf-primary` | `#714B67` | Primary actions, active states, brand |
| `--pf-primary-light` | `#8A6A80` | Hover states, secondary accent |
| `--pf-primary-dark` | `#5A3C53` | Pressed states, borders |
| `--pf-primary-bg` | `rgba(113, 75, 103, 0.08)` | Subtle backgrounds |

### Semantic Colors
| Token | Hex | Usage |
|-------|-----|-------|
| `--pf-success` | `#2ECC71` | Completed, positive actions |
| `--pf-warning` | `#F39C12` | Warnings, pending states |
| `--pf-danger` | `#E74C3C` | Errors, destructive actions |
| `--pf-info` | `#3498DB` | Informational, links |

### Neutral Colors
| Token | Hex | Usage |
|-------|-----|-------|
| `--pf-gray-900` | `#1a252f` | Headers, primary text |
| `--pf-gray-700` | `#2c3e50` | Secondary text, titles |
| `--pf-gray-500` | `#6c757d` | Muted text, icons |
| `--pf-gray-300` | `#dee2e6` | Borders, dividers |
| `--pf-gray-100` | `#f8f9fa` | Backgrounds |
| `--pf-white` | `#ffffff` | Cards, panels |

### Job Status Colors
| Status | Color | Hex |
|--------|-------|-----|
| Draft | Gray | `#6c757d` |
| Pending | Amber | `#F39C12` |
| Assigned | Blue | `#3498DB` |
| In Progress | Purple | `#714B67` |
| Completed | Green | `#2ECC71` |
| Cancelled | Red | `#E74C3C` |

---

## 📝 Typography

### Font Stack
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Scale
| Element | Size | Weight | Letter-spacing |
|---------|------|--------|----------------|
| Brand | 1.1rem | 600 | -0.01em |
| Panel Title | 1rem | 600 | -0.01em |
| Body | 0.875rem | 400 | 0 |
| Small/Label | 0.75rem | 500 | 0.02em |
| Badge | 0.7rem | 500 | 0.01em |

---

## 📐 Spacing & Radius

### Spacing Scale
| Token | Value | Usage |
|-------|-------|-------|
| `--pf-space-xs` | 0.25rem | Tight gaps |
| `--pf-space-sm` | 0.5rem | Component padding |
| `--pf-space-md` | 1rem | Section spacing |
| `--pf-space-lg` | 1.5rem | Panel padding |
| `--pf-space-xl` | 2rem | Large gaps |

### Border Radius
| Token | Value | Usage |
|-------|-------|-------|
| `--pf-radius-sm` | 4px | Buttons, inputs |
| `--pf-radius-md` | 8px | Cards, list items |
| `--pf-radius-lg` | 12px | Panels, modals |
| `--pf-radius-pill` | 20px | Badges, tags |

---

## 🎭 Shadows

### Elevation System
```css
/* Level 1 - Subtle (lists, inputs) */
--pf-shadow-sm: 0 1px 3px rgba(0,0,0,0.05);

/* Level 2 - Cards, panels */
--pf-shadow-md: 0 4px 12px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.05);

/* Level 3 - Floating panels, dropdowns */
--pf-shadow-lg: 0 8px 24px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.08);

/* Level 4 - Modals, dialogs */
--pf-shadow-xl: 0 16px 48px rgba(0,0,0,0.15), 0 4px 12px rgba(0,0,0,0.1);
```

---

## 🧩 Component Styles

### Glassmorphism Header
```css
.dispatch-navbar {
    background: rgba(26, 37, 47, 0.88);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
}
```

### Floating Panels
```css
.floating-panel {
    background: var(--pf-white);
    border-radius: var(--pf-radius-lg);
    box-shadow: var(--pf-shadow-lg);
    border: 1px solid rgba(0,0,0,0.06);
}

.floating-panel-header {
    background: linear-gradient(135deg, var(--pf-primary) 0%, var(--pf-primary-dark) 100%);
    color: white;
    padding: 0.875rem 1.25rem;
    border-radius: var(--pf-radius-lg) var(--pf-radius-lg) 0 0;
}
```

### Tab Buttons
```css
.dispatch-tab {
    padding: 0.5rem 1.25rem;
    background: rgba(255,255,255,0.08);
    color: rgba(255,255,255,0.7);
    border-radius: var(--pf-radius-sm);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    transform: translateY(0);
}

.dispatch-tab:hover {
    background: rgba(255,255,255,0.15);
    transform: translateY(-2px);
}

.dispatch-tab.active {
    background: var(--pf-primary);
    color: white;
    box-shadow: 0 4px 12px rgba(113, 75, 103, 0.35);
}
```

### Resource List Cards
```css
.resource-item {
    background: var(--pf-gray-100);
    border-radius: var(--pf-radius-md);
    border: 1px solid transparent;
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    transition: all 0.15s ease;
}

.resource-item:hover {
    background: var(--pf-white);
    border-color: var(--pf-primary-light);
    box-shadow: 0 2px 8px rgba(113, 75, 103, 0.1);
    transform: translateX(4px);
}

.resource-item.selected {
    background: var(--pf-primary-bg);
    border-color: var(--pf-primary);
}
```

### Status Badges (Pill Style)
```css
.badge {
    font-size: 0.7rem;
    font-weight: 500;
    padding: 0.35em 0.75em;
    border-radius: var(--pf-radius-pill);
    display: inline-flex;
    align-items: center;
    gap: 4px;
    text-transform: capitalize;
}

.badge-draft { background: #e9ecef; color: #495057; }
.badge-pending { background: #fff3cd; color: #856404; }
.badge-assigned { background: #cce5ff; color: #004085; }
.badge-in_progress { background: #f3e8f1; color: #714B67; }
.badge-completed { background: #d4edda; color: #155724; }
.badge-cancelled { background: #f8d7da; color: #721c24; }
```

### Map Pin Markers
```css
.job-pin {
    --pin-color: var(--pf-primary);
    width: 32px;
    height: 40px;
    background: var(--pin-color);
    border-radius: 50% 50% 50% 0;
    transform: rotate(-45deg);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.job-pin:hover {
    transform: rotate(-45deg) scale(1.15) translateY(-4px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}
```

---

## ✨ Animations

### Micro-interactions
```css
/* Hover lift effect */
@keyframes hover-lift {
    from { transform: translateY(0); }
    to { transform: translateY(-2px); }
}

/* Subtle pulse for attention */
@keyframes gentle-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
}

/* Skeleton loading shimmer */
@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* Slide up notification */
@keyframes slideUpFade {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Scale in for modals/panels */
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}
```

### Skeleton Loading
```css
.skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s ease-in-out infinite;
    border-radius: var(--pf-radius-sm);
}

.skeleton-text { height: 1rem; margin-bottom: 0.5rem; }
.skeleton-title { height: 1.5rem; width: 60%; }
.skeleton-avatar { width: 40px; height: 40px; border-radius: 50%; }
```

---

## 🌙 Dark Mode (Optional)

```css
[data-theme="dark"] {
    --pf-gray-900: #f8f9fa;
    --pf-gray-700: #e9ecef;
    --pf-gray-500: #adb5bd;
    --pf-gray-300: #495057;
    --pf-gray-100: #212529;
    --pf-white: #1a1a2e;

    --pf-primary-bg: rgba(113, 75, 103, 0.15);
}

[data-theme="dark"] .dispatch-navbar {
    background: rgba(10, 10, 20, 0.92);
}

[data-theme="dark"] .floating-panel {
    background: #1e1e2f;
    border-color: rgba(255,255,255,0.08);
}
```

---

## 📱 Responsive Breakpoints

| Breakpoint | Width | Adjustments |
|------------|-------|-------------|
| Mobile | < 576px | Stack tabs, hide panel titles |
| Tablet | 576-991px | Smaller panels, condensed spacing |
| Desktop | 992-1199px | Default layout |
| Large | ≥ 1200px | Larger panels, expanded view |

---

## 🔧 Implementation Checklist

- [ ] Add CSS custom properties (variables) at root
- [ ] Update navbar to glassmorphism style
- [ ] Apply Odoo purple color palette
- [ ] Redesign floating panels with softer shadows
- [ ] Add micro-interaction animations to tabs/buttons
- [ ] Update badge styles to pill format
- [ ] Improve resource list item hover states
- [ ] Add skeleton loading states
- [ ] Refine map pin markers with better shadows
- [ ] Test dark mode toggle (optional)
```

