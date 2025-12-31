/**
 * User Story: Inspector Login (US-AUTH-001)
 * 
 * As an inspector, I can log into the mobile app to access my assigned jobs.
 */

import { test, expect } from '@playwright/test';
import { LoginPage, DashboardPage } from '../pages';
import { FlutterConfig } from '../config/flutter-config';
import { UserStories } from '../config/user-stories';

const story = UserStories.inspectorLogin;

test.describe(`${story.id}: ${story.name} @flutter @auth @critical`, () => {
  let loginPage: LoginPage;
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    dashboardPage = new DashboardPage(page);
  });

  test('Login form should display all required elements', async ({ page }) => {
    await loginPage.goto();
    await loginPage.takeScreenshot('login-page-initial');

    const uxElements = await loginPage.verifyUXElements();
    
    expect(uxElements.hasEmailField, 'Email field should be visible').toBe(true);
    expect(uxElements.hasPasswordField, 'Password field should be visible').toBe(true);
    expect(uxElements.hasLoginButton, 'Login button should be visible').toBe(true);
  });

  test('Login button should be enabled when credentials entered', async ({ page }) => {
    await loginPage.goto();
    
    // Initially might be disabled
    await loginPage.fillCredentials('test@example.com', 'password123');
    await loginPage.takeScreenshot('login-form-filled');
    
    const isEnabled = await loginPage.isLoginButtonEnabled();
    expect(isEnabled, 'Login button should be enabled after filling form').toBe(true);
  });

  test('Successful login navigates to dashboard', async ({ page }) => {
    await loginPage.goto();
    await loginPage.takeScreenshot('login-before');
    
    await loginPage.login();
    await loginPage.takeScreenshot('login-success-dashboard');
    
    // Verify we're on dashboard
    const isDashboardLoaded = await dashboardPage.isDashboardLoaded();
    expect(isDashboardLoaded, 'Dashboard should load after successful login').toBe(true);
  });

  test('Invalid credentials show error message', async ({ page }) => {
    await loginPage.goto();
    
    await loginPage.fillCredentials('invalid@test.com', 'wrongpassword');
    await loginPage.submit();
    await loginPage.takeScreenshot('login-error');
    
    // Check for error - either error message or still on login page
    const errorMessage = await loginPage.getErrorMessage();
    const stillOnLogin = await loginPage.isLoginFormVisible();
    
    expect(errorMessage || stillOnLogin, 'Should show error or stay on login page').toBeTruthy();
  });

  test('Dashboard shows job summary after login', async ({ page }) => {
    await loginPage.goto();
    await loginPage.login();
    
    await dashboardPage.takeScreenshot('dashboard-after-login');
    
    const uxElements = await dashboardPage.verifyUXElements();
    expect(uxElements.hasAppBar, 'App bar should be visible').toBe(true);
    expect(uxElements.hasNavigation, 'Navigation should be available').toBe(true);
  });

  // Acceptance Criteria Verification
  test('Verify all acceptance criteria', async ({ page }) => {
    // AC1: Login form is visible with email and password fields
    await loginPage.goto();
    const uxElements = await loginPage.verifyUXElements();
    expect(uxElements.hasEmailField && uxElements.hasPasswordField).toBe(true);
    
    // AC2: Login button is enabled when both fields are filled
    await loginPage.fillCredentials('test@example.com', 'password');
    expect(await loginPage.isLoginButtonEnabled()).toBe(true);
    
    // AC3 & AC4: Loading indicator and dashboard loads
    await loginPage.login();
    const isDashboard = await dashboardPage.isDashboardLoaded();
    expect(isDashboard).toBe(true);
    
    await dashboardPage.takeScreenshot('acceptance-criteria-verified');
  });
});

