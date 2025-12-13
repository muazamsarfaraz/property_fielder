import { Page, expect } from '@playwright/test';

/**
 * Odoo-specific helper functions for Playwright tests
 */
export class OdooHelpers {
  constructor(private page: Page) {}

  /**
   * Wait for Odoo to finish loading (spinner gone, RPC complete)
   */
  async waitForOdooLoad(): Promise<void> {
    // Wait for loading spinner to disappear
    await this.page.waitForSelector('.o_loading', { state: 'hidden', timeout: 10000 }).catch(() => {});
    // Wait for DOM to be stable (shorter timeout, more resilient)
    await this.page.waitForLoadState('domcontentloaded').catch(() => {});
    // Small delay to let Odoo JS settle
    await this.page.waitForTimeout(500);
  }

  /**
   * Navigate to a specific Odoo menu by its text
   */
  async navigateToMenu(menuPath: string[]): Promise<void> {
    for (let i = 0; i < menuPath.length; i++) {
      const menuItem = menuPath[i];
      if (i === 0) {
        // Top-level menu in navbar
        await this.page.click(`.o_main_navbar .o_menu_brand:has-text("${menuItem}"), .o_main_navbar a:has-text("${menuItem}")`);
      } else {
        // Submenu item
        await this.page.click(`.o_menu_sections a:has-text("${menuItem}"), .dropdown-menu a:has-text("${menuItem}")`);
      }
      await this.waitForOdooLoad();
    }
  }

  /**
   * Click an Odoo action button by its text
   */
  async clickButton(buttonText: string): Promise<void> {
    await this.page.click(`button:has-text("${buttonText}"), .btn:has-text("${buttonText}")`);
    await this.waitForOdooLoad();
  }

  /**
   * Fill an Odoo form field by label
   */
  async fillField(fieldLabel: string, value: string): Promise<void> {
    const field = this.page.locator(`.o_field_widget`).filter({ has: this.page.locator(`label:has-text("${fieldLabel}")`) }).locator('input, textarea');
    await field.fill(value);
  }

  /**
   * Select a value from an Odoo Many2one dropdown
   */
  async selectMany2one(fieldLabel: string, searchText: string): Promise<void> {
    const fieldContainer = this.page.locator('.o_field_widget').filter({ has: this.page.locator(`label:has-text("${fieldLabel}")`) });
    await fieldContainer.locator('input').click();
    await fieldContainer.locator('input').fill(searchText);
    await this.page.waitForTimeout(500); // Wait for autocomplete
    await this.page.click(`.o_m2o_dropdown_option:has-text("${searchText}"), .dropdown-item:has-text("${searchText}")`);
  }

  /**
   * Save the current form
   */
  async saveForm(): Promise<void> {
    await this.page.click('.o_form_button_save, button:has-text("Save")');
    await this.waitForOdooLoad();
  }

  /**
   * Create a new record from list view
   */
  async clickCreate(): Promise<void> {
    await this.page.click('.o_list_button_add, button:has-text("New"), button:has-text("Create")');
    await this.waitForOdooLoad();
  }

  /**
   * Switch view type
   */
  async switchView(viewType: 'list' | 'kanban' | 'form' | 'calendar' | 'map'): Promise<void> {
    const viewButton = this.page.locator(`.o_switch_view.o_${viewType}, .o_cp_switch_buttons button[data-tooltip="${viewType}"]`);
    if (await viewButton.isVisible()) {
      await viewButton.click();
      await this.waitForOdooLoad();
    }
  }

  /**
   * Search for records using the search bar
   */
  async search(searchTerm: string): Promise<void> {
    await this.page.fill('.o_searchview_input', searchTerm);
    await this.page.keyboard.press('Enter');
    await this.waitForOdooLoad();
  }

  /**
   * Clear all search filters
   */
  async clearSearch(): Promise<void> {
    const closeButtons = this.page.locator('.o_searchview_facet .o_facet_remove');
    while (await closeButtons.count() > 0) {
      await closeButtons.first().click();
      await this.waitForOdooLoad();
    }
  }

  /**
   * Get the count of records in current view
   */
  async getRecordCount(): Promise<number> {
    const pager = await this.page.locator('.o_pager_value').textContent();
    if (pager) {
      const match = pager.match(/of\s+(\d+)/);
      return match ? parseInt(match[1]) : 0;
    }
    return 0;
  }

  /**
   * Click a record in list view by row index
   */
  async clickListRow(index: number): Promise<void> {
    await this.page.locator('.o_list_view tbody tr').nth(index).click();
    await this.waitForOdooLoad();
  }

  /**
   * Check if a notification is displayed
   */
  async expectNotification(type: 'success' | 'warning' | 'danger' | 'info', messageContains?: string): Promise<void> {
    const notification = this.page.locator(`.o_notification.border-${type}, .o_notification_${type}`);
    await expect(notification).toBeVisible();
    if (messageContains) {
      await expect(notification).toContainText(messageContains);
    }
  }

  /**
   * Dismiss any open dialogs
   */
  async dismissDialog(): Promise<void> {
    const closeButton = this.page.locator('.modal .btn-close, .modal button:has-text("Cancel"), .modal button:has-text("Close")');
    if (await closeButton.isVisible()) {
      await closeButton.click();
      await this.page.waitForSelector('.modal', { state: 'hidden' });
    }
  }
}

