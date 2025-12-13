import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base.page';
import { PropertyData, CertificationTypeData } from '../utils/test-data-manager';

/**
 * Page object for Property Management module
 */
export class PropertyManagementPage extends BasePage {
  // Module-specific selectors
  readonly propertiesList: Locator;
  readonly certificationsList: Locator;
  readonly complianceDashboard: Locator;

  constructor(page: Page) {
    super(page);
    this.propertiesList = page.locator('.o_list_view[data-model="property_fielder.property"]');
    this.certificationsList = page.locator('.o_list_view[data-model="property_fielder.certification.type"]');
    this.complianceDashboard = page.locator('.o_action_manager');
  }

  async navigate(): Promise<void> {
    await this.navigateToApp('Property Management');
  }

  /**
   * Navigate to Properties submenu
   */
  async navigateToProperties(): Promise<void> {
    await this.navigate();
    // Click Properties in menu
    const propertiesMenu = this.page.locator('[role="menuitem"]:has-text("Properties")');
    if (await propertiesMenu.isVisible()) {
      await propertiesMenu.click();
      await this.odoo.waitForOdooLoad();
    }
  }

  /**
   * Navigate to Certifications submenu
   */
  async navigateToCertifications(): Promise<void> {
    await this.navigate();
    // Look for Certification menu item
    const certMenu = this.page.locator('[role="menuitem"]:has-text("Certification")');
    if (await certMenu.isVisible()) {
      await certMenu.click();
      await this.odoo.waitForOdooLoad();
    }
  }

  /**
   * Navigate to Compliance Dashboard
   */
  async navigateToComplianceDashboard(): Promise<void> {
    await this.navigate();
    const dashMenu = this.page.locator('[role="menuitem"]:has-text("Dashboard"), [role="menuitem"]:has-text("Compliance")');
    if (await dashMenu.first().isVisible()) {
      await dashMenu.first().click();
      await this.odoo.waitForOdooLoad();
    }
  }

  /**
   * Create a new property
   */
  async createProperty(data: PropertyData): Promise<void> {
    await this.clickCreate();
    
    // Fill property form
    await this.page.fill('input[name="name"], .o_field_widget[name="name"] input', data.name);
    await this.page.fill('input[name="street"], .o_field_widget[name="street"] input', data.street);
    await this.page.fill('input[name="city"], .o_field_widget[name="city"] input', data.city);
    
    if (data.postcode) {
      await this.page.fill('input[name="postcode"], .o_field_widget[name="postcode"] input', data.postcode);
    }

    // Select property type if available
    if (data.property_type) {
      const typeField = this.page.locator('.o_field_widget[name="property_type"] select');
      if (await typeField.isVisible()) {
        await typeField.selectOption(data.property_type);
      }
    }

    await this.save();
  }

  /**
   * Create a new certification type
   */
  async createCertificationType(data: CertificationTypeData): Promise<void> {
    await this.clickCreate();
    
    await this.page.fill('input[name="name"], .o_field_widget[name="name"] input', data.name);
    await this.page.fill('input[name="code"], .o_field_widget[name="code"] input', data.code);
    
    if (data.validity_months) {
      await this.page.fill('input[name="validity_months"], .o_field_widget[name="validity_months"] input', 
        data.validity_months.toString());
    }

    await this.save();
  }

  /**
   * Open a property by name
   */
  async openProperty(propertyName: string): Promise<void> {
    await this.search(propertyName);
    await this.page.click(`.o_data_row:has-text("${propertyName}")`);
    await this.odoo.waitForOdooLoad();
  }

  /**
   * Check if property exists
   */
  async propertyExists(propertyName: string): Promise<boolean> {
    await this.search(propertyName);
    const rows = await this.page.locator('.o_data_row').count();
    return rows > 0;
  }

  /**
   * Get property compliance status
   */
  async getComplianceStatus(): Promise<string> {
    const statusBadge = this.page.locator('.o_field_widget[name="compliance_status"] .badge, .o_field_badge[name="compliance_status"]');
    return await statusBadge.textContent() || '';
  }

  /**
   * Create job from property
   */
  async createJobFromProperty(): Promise<void> {
    await this.page.click('button:has-text("Create Job"), .o_button_action:has-text("Create Job")');
    await this.odoo.waitForOdooLoad();
  }

  /**
   * Verify property form is displayed
   */
  async verifyPropertyForm(): Promise<void> {
    await expect(this.page.locator('.o_form_view')).toBeVisible();
    await expect(this.page.locator('.o_field_widget[name="name"]')).toBeVisible();
  }
}

