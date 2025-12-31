/**
 * Flutter Web Test Configuration
 * 
 * Configuration for testing Flutter web apps with Playwright.
 * Supports both HTML and CanvasKit renderers.
 */

export const FlutterConfig = {
  // Base URL for Flutter web app
  baseUrl: process.env.FLUTTER_URL || 'http://localhost:8080',
  
  // API base URL for backend
  apiUrl: process.env.API_URL || 'http://localhost:8069',
  
  // Test credentials
  credentials: {
    username: process.env.FLUTTER_USERNAME || 'inspector@test.com',
    password: process.env.FLUTTER_PASSWORD || 'test123',
  },
  
  // Gemini configuration
  gemini: {
    apiKey: process.env.GEMINI_API_KEY || '',
    model: process.env.GEMINI_MODEL || 'gemini-2.5-pro-preview-06-05',
    enableAnalysis: process.env.ENABLE_GEMINI_ANALYSIS === 'true',
  },
  
  // Screenshot settings
  screenshots: {
    dir: 'test-results/flutter-mobile',
    fullPage: false,
    quality: 80,
  },
  
  // Timeouts
  timeouts: {
    navigation: 30000,
    action: 10000,
    animation: 500,
    apiCall: 15000,
  },
};

/**
 * Flutter App Routes
 * Maps to AppRouter routes in the Flutter app
 */
export const FlutterRoutes = {
  splash: '/',
  login: '/login',
  dashboard: '/dashboard',
  jobList: '/jobs',
  jobDetail: '/jobs/detail',
  jobMap: '/jobs/map',
  routeList: '/routes',
  photoGallery: '/photos',
  signatureCapture: '/signature',
  noteList: '/notes',
  sync: '/sync',
  settings: '/settings',
  safetyTimer: '/safety',
  templateExecution: '/inspection/execute',
};

/**
 * Flutter Selectors
 * 
 * Flutter web uses semantic labels and specific DOM structure.
 * These selectors work with Flutter's HTML renderer mode.
 */
export const FlutterSelectors = {
  // General
  loading: '[aria-busy="true"], .loading-indicator',
  errorDialog: '[role="alertdialog"]',
  snackbar: '[role="status"]',
  
  // Login Screen
  login: {
    emailInput: 'input[type="email"], [aria-label*="email" i], [aria-label*="username" i]',
    passwordInput: 'input[type="password"], [aria-label*="password" i]',
    loginButton: 'button:has-text("Login"), button:has-text("Sign In"), [aria-label*="login" i]',
    errorMessage: '[role="alert"], .error-message',
  },
  
  // Dashboard
  dashboard: {
    jobCount: '[aria-label*="jobs" i], .job-count',
    syncStatus: '[aria-label*="sync" i], .sync-status',
    navigationDrawer: '[role="navigation"], .drawer',
    menuButton: 'button[aria-label*="menu" i], .menu-button',
  },
  
  // Job List
  jobList: {
    jobCard: '[role="listitem"], .job-card',
    filterChip: '[role="button"][aria-pressed], .filter-chip',
    searchInput: 'input[type="search"], [aria-label*="search" i]',
    refreshButton: 'button[aria-label*="refresh" i]',
  },
  
  // Job Detail
  jobDetail: {
    propertyName: '.property-name, [aria-label*="property" i]',
    checkInButton: 'button:has-text("Check In"), [aria-label*="check in" i]',
    checkOutButton: 'button:has-text("Check Out"), [aria-label*="check out" i]',
    startInspectionButton: 'button:has-text("Start Inspection"), [aria-label*="inspection" i]',
    photoButton: 'button[aria-label*="photo" i], button:has-text("Photo")',
    signatureButton: 'button[aria-label*="signature" i], button:has-text("Signature")',
    notesButton: 'button[aria-label*="notes" i], button:has-text("Notes")',
  },
  
  // Safety Timer
  safetyTimer: {
    timerDisplay: '.timer-display, [aria-label*="timer" i]',
    startButton: 'button:has-text("Start"), [aria-label*="start timer" i]',
    extendButton: 'button:has-text("Extend"), [aria-label*="extend" i]',
    cancelButton: 'button:has-text("Safe"), button:has-text("Complete")',
    panicButton: '.panic-button, button:has-text("PANIC"), [aria-label*="panic" i]',
    durationChip: '[role="radio"], .duration-chip',
  },
  
  // Template Execution
  template: {
    sectionIndicator: '.section-indicator, [role="tablist"]',
    checklistItem: '.checklist-item, [role="listitem"]',
    yesButton: 'button:has-text("Yes")',
    noButton: 'button:has-text("No")',
    naButton: 'button:has-text("N/A")',
    severityChip: '[role="radio"]:has-text("Good"), [role="radio"]:has-text("Minor")',
    nextButton: 'button:has-text("Next")',
    prevButton: 'button:has-text("Previous")',
    submitButton: 'button:has-text("Submit")',
    progressIndicator: '.progress-indicator, [role="progressbar"]',
  },
  
  // Common Navigation
  nav: {
    backButton: 'button[aria-label*="back" i], .back-button',
    appBar: '[role="banner"], .app-bar',
    bottomNav: '[role="navigation"]:last-child, .bottom-nav',
    fab: '[role="button"].fab, button.floating-action',
  },
};

/**
 * User Story Definitions
 * Each story represents a complete user workflow
 */
export const UserStories = {
  inspectorLogin: {
    id: 'US-001',
    name: 'Inspector Login',
    description: 'As an inspector, I can log into the mobile app to access my assigned jobs',
    steps: ['Open app', 'Enter credentials', 'Submit login', 'See dashboard'],
    acceptanceCriteria: ['Dashboard loads', 'Job count visible', 'Sync status shown'],
  },
  viewAssignedJobs: {
    id: 'US-002',
    name: 'View Assigned Jobs',
    description: 'As an inspector, I can view my assigned jobs for today',
    steps: ['Navigate to jobs', 'See job list', 'Filter by status', 'View job details'],
    acceptanceCriteria: ['Jobs load', 'Filters work', 'Details accessible'],
  },
  // ... more stories added in next file
};

export default FlutterConfig;

