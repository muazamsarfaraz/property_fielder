/**
 * Flutter Base Page Object
 * 
 * Base class for all Flutter page objects with common functionality
 * for Flutter web app testing.
 */

import { Page, Locator, expect } from '@playwright/test';
import { FlutterConfig, FlutterSelectors } from '../config/flutter-config';

export class FlutterBasePage {
  readonly page: Page;
  readonly config = FlutterConfig;
  readonly selectors = FlutterSelectors;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * Wait for Flutter app to be fully loaded
   * Flutter web apps need time to initialize
   */
  async waitForFlutterReady(): Promise<void> {
    // Wait for Flutter to initialize
    await this.page.waitForLoadState('domcontentloaded');
    
    // Wait for any loading indicators to disappear
    const loading = this.page.locator(this.selectors.loading);
    if (await loading.isVisible({ timeout: 1000 }).catch(() => false)) {
      await loading.waitFor({ state: 'hidden', timeout: this.config.timeouts.navigation });
    }
    
    // Additional wait for Flutter animations
    await this.page.waitForTimeout(this.config.timeouts.animation);
  }

  /**
   * Navigate to a Flutter route
   */
  async navigateTo(route: string): Promise<void> {
    const url = `${this.config.baseUrl}/#${route}`;
    await this.page.goto(url);
    await this.waitForFlutterReady();
  }

  /**
   * Take a screenshot with consistent naming
   */
  async takeScreenshot(name: string): Promise<string> {
    const filename = `${name.replace(/[^a-zA-Z0-9-]/g, '_')}.png`;
    const filepath = `${this.config.screenshots.dir}/${filename}`;
    await this.page.screenshot({ 
      path: filepath, 
      fullPage: this.config.screenshots.fullPage 
    });
    return filepath;
  }

  /**
   * Check for error dialogs or snackbars
   */
  async hasError(): Promise<{ hasError: boolean; message?: string }> {
    const errorDialog = this.page.locator(this.selectors.errorDialog);
    if (await errorDialog.isVisible({ timeout: 500 }).catch(() => false)) {
      const message = await errorDialog.textContent();
      return { hasError: true, message: message || undefined };
    }
    return { hasError: false };
  }

  /**
   * Dismiss any visible dialogs
   */
  async dismissDialogs(): Promise<void> {
    await this.page.keyboard.press('Escape');
    await this.page.waitForTimeout(300);
  }

  /**
   * Get text content by aria-label (Flutter semantic labels)
   */
  async getBySemanticLabel(label: string): Promise<Locator> {
    return this.page.locator(`[aria-label*="${label}" i]`);
  }

  /**
   * Click a button by text content
   */
  async clickButton(text: string): Promise<void> {
    await this.page.getByRole('button', { name: text }).click();
    await this.page.waitForTimeout(this.config.timeouts.animation);
  }

  /**
   * Fill a text field by label
   */
  async fillField(label: string, value: string): Promise<void> {
    const field = this.page.locator(`[aria-label*="${label}" i]`).first();
    await field.fill(value);
  }

  /**
   * Tap the back button in app bar
   */
  async goBack(): Promise<void> {
    const backButton = this.page.locator(this.selectors.nav.backButton);
    if (await backButton.isVisible()) {
      await backButton.click();
      await this.waitForFlutterReady();
    }
  }

  /**
   * Get current route from URL hash
   */
  async getCurrentRoute(): Promise<string> {
    const url = this.page.url();
    const hash = url.split('#')[1] || '/';
    return hash;
  }

  /**
   * Wait for a specific route
   */
  async waitForRoute(route: string): Promise<void> {
    await this.page.waitForURL(`**/#${route}*`, { 
      timeout: this.config.timeouts.navigation 
    });
  }

  /**
   * Check if element is visible
   */
  async isVisible(selector: string): Promise<boolean> {
    return await this.page.locator(selector).isVisible({ timeout: 2000 }).catch(() => false);
  }

  /**
   * Get page title from app bar
   */
  async getPageTitle(): Promise<string> {
    const appBar = this.page.locator(this.selectors.nav.appBar);
    const title = await appBar.textContent();
    return title?.trim() || '';
  }

  /**
   * Scroll to element
   */
  async scrollToElement(selector: string): Promise<void> {
    await this.page.locator(selector).scrollIntoViewIfNeeded();
  }

  /**
   * Get count of list items
   */
  async getListItemCount(selector: string): Promise<number> {
    return await this.page.locator(selector).count();
  }
}

export default FlutterBasePage;

