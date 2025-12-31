/**
 * Login Page Object
 * 
 * Page object for Flutter mobile app login screen.
 */

import { Page, expect } from '@playwright/test';
import { FlutterBasePage } from './flutter-base.page';
import { FlutterRoutes } from '../config/flutter-config';

export class LoginPage extends FlutterBasePage {
  constructor(page: Page) {
    super(page);
  }

  /**
   * Navigate to login page
   */
  async goto(): Promise<void> {
    await this.navigateTo(FlutterRoutes.login);
  }

  /**
   * Get email/username input
   */
  get emailInput() {
    return this.page.locator(this.selectors.login.emailInput).first();
  }

  /**
   * Get password input
   */
  get passwordInput() {
    return this.page.locator(this.selectors.login.passwordInput).first();
  }

  /**
   * Get login button
   */
  get loginButton() {
    return this.page.locator(this.selectors.login.loginButton).first();
  }

  /**
   * Get error message
   */
  get errorMessage() {
    return this.page.locator(this.selectors.login.errorMessage);
  }

  /**
   * Fill login credentials
   */
  async fillCredentials(email: string, password: string): Promise<void> {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
  }

  /**
   * Submit login form
   */
  async submit(): Promise<void> {
    await this.loginButton.click();
    await this.waitForFlutterReady();
  }

  /**
   * Perform complete login
   */
  async login(email?: string, password?: string): Promise<void> {
    const credentials = {
      email: email || this.config.credentials.username,
      password: password || this.config.credentials.password,
    };

    await this.fillCredentials(credentials.email, credentials.password);
    await this.submit();
    
    // Wait for navigation away from login
    await this.page.waitForURL(/(?!.*login).*/, { 
      timeout: this.config.timeouts.navigation 
    });
  }

  /**
   * Check if login form is visible
   */
  async isLoginFormVisible(): Promise<boolean> {
    const emailVisible = await this.emailInput.isVisible({ timeout: 2000 }).catch(() => false);
    const passwordVisible = await this.passwordInput.isVisible({ timeout: 2000 }).catch(() => false);
    return emailVisible && passwordVisible;
  }

  /**
   * Check if login button is enabled
   */
  async isLoginButtonEnabled(): Promise<boolean> {
    return await this.loginButton.isEnabled();
  }

  /**
   * Get error message text
   */
  async getErrorMessage(): Promise<string | null> {
    if (await this.errorMessage.isVisible({ timeout: 2000 }).catch(() => false)) {
      return await this.errorMessage.textContent();
    }
    return null;
  }

  /**
   * Verify login page elements for UX assessment
   */
  async verifyUXElements(): Promise<{
    hasEmailField: boolean;
    hasPasswordField: boolean;
    hasLoginButton: boolean;
    hasLogo: boolean;
    isButtonEnabled: boolean;
  }> {
    return {
      hasEmailField: await this.emailInput.isVisible().catch(() => false),
      hasPasswordField: await this.passwordInput.isVisible().catch(() => false),
      hasLoginButton: await this.loginButton.isVisible().catch(() => false),
      hasLogo: await this.page.locator('img, svg').first().isVisible().catch(() => false),
      isButtonEnabled: await this.loginButton.isEnabled().catch(() => false),
    };
  }
}

export default LoginPage;

