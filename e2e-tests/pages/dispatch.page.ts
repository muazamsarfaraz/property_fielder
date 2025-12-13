import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';

/**
 * Page object for Enhanced Dispatch View
 */
export class DispatchPage extends BasePage {
  // Dispatch-specific selectors
  readonly dispatchContainer: Locator;
  readonly navbar: Locator;
  readonly planTab: Locator;
  readonly optimizeTab: Locator;
  readonly scheduleTab: Locator;
  readonly mapContainer: Locator;
  readonly resourcesPanel: Locator;
  readonly settingsPanel: Locator;
  readonly optimizationPanel: Locator;
  readonly routeDetailsPanel: Locator;
  readonly timelineContainer: Locator;
  readonly dateInput: Locator;
  readonly refreshButton: Locator;
  readonly loadingOverlay: Locator;

  constructor(page: Page) {
    super(page);
    // Dispatch view container - look for the main content area
    this.dispatchContainer = page.locator('.o_action_manager');
    this.navbar = page.locator('.o_main_navbar');
    // Tab buttons - use .dispatch-tab class
    this.planTab = page.locator('.dispatch-tab:has-text("PLAN")');
    this.optimizeTab = page.locator('.dispatch-tab:has-text("OPTIMIZE")');
    this.scheduleTab = page.locator('.dispatch-tab:has-text("SCHEDULE")');
    // Map container - Mapbox region
    this.mapContainer = page.locator('[role="region"][aria-label="Map"]');
    this.resourcesPanel = page.locator('text=Resources').locator('..');
    this.settingsPanel = page.locator('text=Optimization Settings').locator('..');
    this.optimizationPanel = page.locator('text=Optimization Settings').locator('..');
    this.routeDetailsPanel = page.locator('text=Routes').locator('..');
    this.timelineContainer = page.locator('.dispatch-timeline-container');
    this.dateInput = page.locator('input[type="date"]');
    this.refreshButton = page.locator('button:has-text("Refresh data")');
    this.loadingOverlay = page.locator('.dispatch-loading-overlay');
  }

  async navigate(): Promise<void> {
    // Navigate to Field Service > Dispatch
    await this.navigateToApp('Field Service');
    const dispatchMenu = this.page.locator('[role="menuitem"]:has-text("Dispatch")');
    if (await dispatchMenu.isVisible()) {
      await dispatchMenu.click();
      await this.odoo.waitForOdooLoad();
    }
  }

  /**
   * Wait for dispatch view to fully load
   */
  async waitForLoad(): Promise<void> {
    await expect(this.dispatchContainer).toBeVisible({ timeout: 15000 });
    await this.loadingOverlay.waitFor({ state: 'hidden', timeout: 10000 }).catch(() => {});
  }

  /**
   * Switch to PLAN tab
   */
  async switchToPlan(): Promise<void> {
    await this.planTab.click();
    await this.odoo.waitForOdooLoad();
  }

  /**
   * Switch to OPTIMIZE tab
   */
  async switchToOptimize(): Promise<void> {
    await this.optimizeTab.click();
    await this.odoo.waitForOdooLoad();
  }

  /**
   * Switch to SCHEDULE tab
   */
  async switchToSchedule(): Promise<void> {
    await this.scheduleTab.click();
    await this.odoo.waitForOdooLoad();
  }

  /**
   * Get current active tab
   */
  async getActiveTab(): Promise<string> {
    // The active tab has the .active class
    const activeTab = this.page.locator('.dispatch-tab.active');
    const text = await activeTab.textContent();
    return text?.trim() || 'PLAN';
  }

  /**
   * Change the selected date
   */
  async setDate(date: string): Promise<void> {
    await this.dateInput.fill(date);
    await this.dateInput.press('Enter');
    await this.odoo.waitForOdooLoad();
  }

  /**
   * Click refresh button
   */
  async refresh(): Promise<void> {
    await this.refreshButton.click();
    await this.odoo.waitForOdooLoad();
  }

  /**
   * Get job count displayed
   */
  async getJobCount(): Promise<number> {
    const jobsText = await this.page.locator('.panel-section h6:has-text("Jobs")').textContent();
    const match = jobsText?.match(/\((\d+)\)/);
    return match ? parseInt(match[1]) : 0;
  }

  /**
   * Get inspector count displayed
   */
  async getInspectorCount(): Promise<number> {
    const inspectorsText = await this.page.locator('.panel-section h6:has-text("Inspectors")').textContent();
    const match = inspectorsText?.match(/\((\d+)\)/);
    return match ? parseInt(match[1]) : 0;
  }

  /**
   * Select all jobs
   */
  async selectAllJobs(): Promise<void> {
    await this.page.click('button:has-text("Select All"):near(.panel-section h6:has-text("Jobs"))');
  }

  /**
   * Select all inspectors
   */
  async selectAllInspectors(): Promise<void> {
    await this.page.click('button:has-text("Select All"):near(.panel-section h6:has-text("Inspectors"))');
  }

  /**
   * Start optimization
   */
  async startOptimization(): Promise<void> {
    await this.switchToOptimize();
    const startButton = this.page.locator('button:has-text("Start Optimization")');
    await expect(startButton).toBeEnabled();
    await startButton.click();
    // Wait for optimization to complete
    await this.page.locator('.spinner-border').waitFor({ state: 'hidden', timeout: 120000 }).catch(() => {});
  }

  /**
   * Verify map is displayed
   */
  async verifyMapDisplayed(): Promise<void> {
    await expect(this.mapContainer).toBeVisible();
  }

  /**
   * Verify timeline is displayed (SCHEDULE tab)
   */
  async verifyTimelineDisplayed(): Promise<void> {
    await this.switchToSchedule();
    await expect(this.timelineContainer).toBeVisible();
  }

  /**
   * Get route count
   */
  async getRouteCount(): Promise<number> {
    const routeItems = this.page.locator('.route-item');
    return await routeItems.count();
  }

  /**
   * Click a specific route
   */
  async selectRoute(routeName: string): Promise<void> {
    await this.page.click(`.route-item:has-text("${routeName}")`);
  }
}

