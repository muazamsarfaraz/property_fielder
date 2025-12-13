import { Page, Locator, expect } from '@playwright/test';
import { OdooHelpers } from '../utils/odoo-helpers';

/**
 * Base page object with common Odoo functionality
 */
export abstract class BasePage {
  protected odoo: OdooHelpers;

  // Common selectors
  protected readonly navbar: Locator;
  protected readonly searchInput: Locator;
  protected readonly createButton: Locator;
  protected readonly saveButton: Locator;
  protected readonly editButton: Locator;
  protected readonly deleteButton: Locator;
  protected readonly pager: Locator;
  protected readonly homeMenuButton: Locator;

  constructor(protected page: Page) {
    this.odoo = new OdooHelpers(page);

    // Initialize common locators
    this.navbar = page.locator('.o_main_navbar');
    this.searchInput = page.locator('.o_searchview_input');
    this.createButton = page.locator('button:has-text("New")');
    this.saveButton = page.locator('button:has-text("Save")');
    this.editButton = page.locator('button:has-text("Edit")');
    this.deleteButton = page.locator('button:has-text("Delete"), button[name="action_delete"]');
    this.pager = page.locator('.o_pager');
    this.homeMenuButton = page.locator('button[title="Home Menu"]');
  }

  /**
   * Navigate to an app using the home menu (Odoo 19 style)
   */
  async navigateToApp(appName: string): Promise<void> {
    // Ensure we're on the web page first
    await this.page.goto('/web');
    await this.page.waitForSelector('button[title="Home Menu"]', { timeout: 15000 });

    // Click home menu button
    await this.homeMenuButton.click();
    // Wait for menu to appear
    await this.page.waitForSelector(`[role="menuitem"]:has-text("${appName}")`, { timeout: 10000 });
    // Click the app
    await this.page.locator(`[role="menuitem"]:has-text("${appName}")`).click();
    await this.odoo.waitForOdooLoad();
  }

  /**
   * Navigate to a submenu within current app
   */
  async navigateToSubmenu(menuText: string): Promise<void> {
    await this.page.locator(`[role="menuitem"]:has-text("${menuText}")`).click();
    await this.odoo.waitForOdooLoad();
  }

  /**
   * Navigate to this page's module menu
   */
  abstract navigate(): Promise<void>;

  /**
   * Get the page title/breadcrumb
   */
  async getTitle(): Promise<string> {
    const breadcrumb = this.page.locator('.o_breadcrumb .active, .breadcrumb-item.active');
    return await breadcrumb.textContent() || '';
  }

  /**
   * Check if on list view
   */
  async isListView(): Promise<boolean> {
    return await this.page.locator('.o_list_view').isVisible();
  }

  /**
   * Check if on form view
   */
  async isFormView(): Promise<boolean> {
    return await this.page.locator('.o_form_view').isVisible();
  }

  /**
   * Check if on kanban view
   */
  async isKanbanView(): Promise<boolean> {
    return await this.page.locator('.o_kanban_view').isVisible();
  }

  /**
   * Switch to list view
   */
  async switchToList(): Promise<void> {
    await this.odoo.switchView('list');
  }

  /**
   * Switch to kanban view
   */
  async switchToKanban(): Promise<void> {
    await this.odoo.switchView('kanban');
  }

  /**
   * Create a new record
   */
  async clickCreate(): Promise<void> {
    await this.createButton.click();
    await this.odoo.waitForOdooLoad();
  }

  /**
   * Save the current form
   */
  async save(): Promise<void> {
    await this.saveButton.click();
    await this.odoo.waitForOdooLoad();
  }

  /**
   * Search for records
   */
  async search(term: string): Promise<void> {
    await this.searchInput.fill(term);
    await this.page.keyboard.press('Enter');
    await this.odoo.waitForOdooLoad();
  }

  /**
   * Get record count from pager
   */
  async getRecordCount(): Promise<number> {
    return await this.odoo.getRecordCount();
  }

  /**
   * Click a list row by index
   */
  async clickRow(index: number): Promise<void> {
    await this.odoo.clickListRow(index);
  }

  /**
   * Verify page loaded successfully
   */
  async verifyLoaded(): Promise<void> {
    await expect(this.navbar).toBeVisible();
    await this.odoo.waitForOdooLoad();
  }

  /**
   * Get all visible records in list view
   */
  async getListRows(): Promise<Locator> {
    return this.page.locator('.o_list_view tbody tr.o_data_row');
  }

  /**
   * Get all visible kanban cards
   */
  async getKanbanCards(): Promise<Locator> {
    return this.page.locator('.o_kanban_record');
  }
}

