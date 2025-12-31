/**
 * Template Execution Page Object
 * 
 * Page object for Flutter mobile app inspection template execution screen.
 */

import { Page, Locator } from '@playwright/test';
import { FlutterBasePage } from './flutter-base.page';
import { FlutterRoutes } from '../config/flutter-config';

export type ChecklistResponse = 'Yes' | 'No' | 'N/A';
export type SeverityLevel = 'Good' | 'Minor' | 'Major' | 'Critical';

export class TemplateExecutionPage extends FlutterBasePage {
  constructor(page: Page) {
    super(page);
  }

  /**
   * Navigate to template execution
   */
  async goto(): Promise<void> {
    await this.navigateTo(FlutterRoutes.templateExecution);
  }

  // Elements
  get sectionIndicator(): Locator {
    return this.page.locator(this.selectors.template.sectionIndicator);
  }

  get checklistItems(): Locator {
    return this.page.locator(this.selectors.template.checklistItem);
  }

  get nextButton(): Locator {
    return this.page.locator(this.selectors.template.nextButton).first();
  }

  get prevButton(): Locator {
    return this.page.locator(this.selectors.template.prevButton).first();
  }

  get submitButton(): Locator {
    return this.page.locator(this.selectors.template.submitButton).first();
  }

  get progressIndicator(): Locator {
    return this.page.locator(this.selectors.template.progressIndicator);
  }

  /**
   * Get current section name
   */
  async getCurrentSection(): Promise<string> {
    const title = await this.getPageTitle();
    return title || 'Unknown Section';
  }

  /**
   * Get checklist item count
   */
  async getChecklistItemCount(): Promise<number> {
    return await this.checklistItems.count();
  }

  /**
   * Answer a checklist item
   */
  async answerItem(index: number, response: ChecklistResponse): Promise<void> {
    const item = this.checklistItems.nth(index);
    const button = item.locator(`button:has-text("${response}")`);
    await button.click();
    await this.page.waitForTimeout(this.config.timeouts.animation);
  }

  /**
   * Set severity for a defect item
   */
  async setSeverity(index: number, severity: SeverityLevel): Promise<void> {
    const item = this.checklistItems.nth(index);
    const chip = item.locator(`[role="radio"]:has-text("${severity}")`);
    await chip.click();
    await this.page.waitForTimeout(this.config.timeouts.animation);
  }

  /**
   * Add note to a checklist item
   */
  async addNote(index: number, note: string): Promise<void> {
    const item = this.checklistItems.nth(index);
    const noteButton = item.locator('button:has-text("Note"), button[aria-label*="note" i]');
    await noteButton.click();
    await this.page.waitForTimeout(300);
    
    const noteInput = this.page.locator('textarea, input[type="text"]').last();
    await noteInput.fill(note);
  }

  /**
   * Go to next section
   */
  async nextSection(): Promise<void> {
    await this.nextButton.click();
    await this.waitForFlutterReady();
  }

  /**
   * Go to previous section
   */
  async previousSection(): Promise<void> {
    await this.prevButton.click();
    await this.waitForFlutterReady();
  }

  /**
   * Submit the inspection
   */
  async submit(): Promise<void> {
    await this.submitButton.click();
    await this.waitForFlutterReady();
  }

  /**
   * Answer all items in current section with same response
   */
  async answerAllItems(response: ChecklistResponse): Promise<void> {
    const count = await this.getChecklistItemCount();
    for (let i = 0; i < count; i++) {
      await this.answerItem(i, response);
    }
  }

  /**
   * Get progress percentage
   */
  async getProgress(): Promise<number> {
    const progressEl = this.progressIndicator;
    const ariaValue = await progressEl.getAttribute('aria-valuenow');
    if (ariaValue) {
      return parseFloat(ariaValue);
    }
    
    // Try to extract from text
    const text = await progressEl.textContent();
    const match = text?.match(/(\d+)%?/);
    return match ? parseInt(match[1]) : 0;
  }

  /**
   * Verify template execution UX elements
   */
  async verifyUXElements(): Promise<{
    hasAppBar: boolean;
    hasSectionIndicator: boolean;
    hasChecklistItems: boolean;
    hasNavigation: boolean;
    hasProgress: boolean;
    itemCount: number;
  }> {
    const itemCount = await this.getChecklistItemCount();
    
    return {
      hasAppBar: await this.page.locator(this.selectors.nav.appBar).isVisible().catch(() => false),
      hasSectionIndicator: await this.sectionIndicator.isVisible().catch(() => false),
      hasChecklistItems: itemCount > 0,
      hasNavigation: (await this.nextButton.isVisible().catch(() => false)) || 
                     (await this.prevButton.isVisible().catch(() => false)),
      hasProgress: await this.progressIndicator.isVisible().catch(() => false),
      itemCount,
    };
  }
}

export default TemplateExecutionPage;

