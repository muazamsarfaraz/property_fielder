import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';
import { JobData, InspectorData, RouteData } from '../utils/test-data-manager';

/**
 * Page object for Field Service module
 */
export class FieldServicePage extends BasePage {
  // Module-specific selectors
  readonly jobsList: Locator;
  readonly inspectorsList: Locator;
  readonly routesList: Locator;
  readonly dashboardStats: Locator;

  constructor(page: Page) {
    super(page);
    this.jobsList = page.locator('.o_list_view');
    this.inspectorsList = page.locator('.o_list_view');
    this.routesList = page.locator('.o_list_view');
    this.dashboardStats = page.locator('.o_dashboard');
  }

  async navigate(): Promise<void> {
    await this.navigateToApp('Field Service');
  }

  /**
   * Navigate to Jobs submenu
   */
  async navigateToJobs(): Promise<void> {
    await this.navigate();
    const jobsMenu = this.page.locator('[role="menuitem"]:has-text("Jobs")');
    if (await jobsMenu.isVisible()) {
      await jobsMenu.click();
      await this.odoo.waitForOdooLoad();
    }
  }

  /**
   * Navigate to Inspectors submenu
   */
  async navigateToInspectors(): Promise<void> {
    await this.navigate();
    const menu = this.page.locator('[role="menuitem"]:has-text("Inspectors")');
    if (await menu.isVisible()) {
      await menu.click();
      await this.odoo.waitForOdooLoad();
    }
  }

  /**
   * Navigate to Routes submenu
   */
  async navigateToRoutes(): Promise<void> {
    await this.navigate();
    const menu = this.page.locator('[role="menuitem"]:has-text("Routes")');
    if (await menu.isVisible()) {
      await menu.click();
      await this.odoo.waitForOdooLoad();
    }
  }

  /**
   * Navigate to Optimization submenu
   */
  async navigateToOptimization(): Promise<void> {
    await this.navigate();
    const menu = this.page.locator('[role="menuitem"]:has-text("Optimization")');
    if (await menu.isVisible()) {
      await menu.click();
      await this.odoo.waitForOdooLoad();
    }
  }

  /**
   * Navigate to Dashboard
   */
  async navigateToDashboard(): Promise<void> {
    await this.navigate();
    const menu = this.page.locator('[role="menuitem"]:has-text("Dashboard")');
    if (await menu.isVisible()) {
      await menu.click();
      await this.odoo.waitForOdooLoad();
    }
  }

  /**
   * Navigate to Dispatch View (Enhanced)
   */
  async navigateToDispatch(): Promise<void> {
    await this.navigate();
    const menu = this.page.locator('[role="menuitem"]:has-text("Dispatch")');
    if (await menu.isVisible()) {
      await menu.click();
      await this.odoo.waitForOdooLoad();
    }
  }

  /**
   * Create a new job
   */
  async createJob(data: JobData): Promise<void> {
    await this.clickCreate();
    
    await this.page.fill('input[name="name"], .o_field_widget[name="name"] input', data.name);
    
    // Set scheduled date
    const dateField = this.page.locator('.o_field_widget[name="scheduled_date"] input');
    if (await dateField.isVisible()) {
      await dateField.fill(data.scheduled_date);
    }

    // Set duration
    const durationField = this.page.locator('.o_field_widget[name="duration_minutes"] input');
    if (await durationField.isVisible()) {
      await durationField.fill(data.duration_minutes.toString());
    }

    // Set priority
    if (data.priority) {
      const priorityField = this.page.locator('.o_field_widget[name="priority"] select');
      if (await priorityField.isVisible()) {
        await priorityField.selectOption(data.priority);
      }
    }

    await this.save();
  }

  /**
   * Create a new inspector
   */
  async createInspector(data: InspectorData): Promise<void> {
    await this.clickCreate();
    
    await this.page.fill('input[name="name"], .o_field_widget[name="name"] input', data.name);
    
    if (data.email) {
      await this.page.fill('input[name="email"], .o_field_widget[name="email"] input', data.email);
    }

    await this.save();
  }

  /**
   * Create a new route
   */
  async createRoute(data: RouteData): Promise<void> {
    await this.clickCreate();
    
    await this.page.fill('input[name="name"], .o_field_widget[name="name"] input', data.name);
    
    const dateField = this.page.locator('.o_field_widget[name="route_date"] input');
    if (await dateField.isVisible()) {
      await dateField.fill(data.route_date);
    }

    await this.save();
  }

  /**
   * Get job state/status
   */
  async getJobState(): Promise<string> {
    const stateField = this.page.locator('.o_field_widget[name="state"] .badge, .o_statusbar_status button.o_arrow_button_current');
    return await stateField.textContent() || '';
  }

  /**
   * Change job state via status bar
   */
  async setJobState(targetState: string): Promise<void> {
    await this.page.click(`.o_statusbar_status button:has-text("${targetState}")`);
    await this.odoo.waitForOdooLoad();
  }

  /**
   * Assign job to inspector
   */
  async assignInspector(inspectorName: string): Promise<void> {
    await this.odoo.selectMany2one('Inspector', inspectorName);
  }

  /**
   * Verify job form is displayed
   */
  async verifyJobForm(): Promise<void> {
    await expect(this.page.locator('.o_form_view')).toBeVisible();
    await expect(this.page.locator('.o_field_widget[name="name"]')).toBeVisible();
  }
}

