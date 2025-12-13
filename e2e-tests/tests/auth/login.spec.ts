import { test, expect } from '@playwright/test';

/**
 * Authentication Tests
 * Tests login functionality and session management
 */
test.describe('Authentication @smoke @critical', () => {
  
  test.describe('Login Page', () => {
    test('should display login form', async ({ page }) => {
      await page.goto('/web/login');
      
      await expect(page.locator('input[name="login"]')).toBeVisible();
      await expect(page.locator('input[name="password"]')).toBeVisible();
      await expect(page.locator('button[type="submit"]')).toBeVisible();
    });

    test('should show error for invalid credentials', async ({ page }) => {
      await page.goto('/web/login');
      
      await page.fill('input[name="login"]', 'invalid_user');
      await page.fill('input[name="password"]', 'invalid_password');
      await page.click('button[type="submit"]');
      
      // Expect error message
      await expect(page.locator('.alert-danger, .o_login_error')).toBeVisible({ timeout: 10000 });
    });

    test('should login successfully with valid credentials', async ({ page }) => {
      await page.goto('/web/login');
      
      await page.fill('input[name="login"]', process.env.ADMIN_LOGIN || 'admin');
      await page.fill('input[name="password"]', process.env.ADMIN_PASSWORD || 'admin');
      await page.click('button[type="submit"]');
      
      // Wait for successful redirect to main interface
      await expect(page.locator('.o_main_navbar')).toBeVisible({ timeout: 30000 });
    });
  });

  test.describe('Session Management', () => {
    test('should maintain session after navigation', async ({ page }) => {
      // This test uses the authenticated state from global setup
      await page.goto('/web');
      await expect(page.locator('.o_main_navbar')).toBeVisible();
      
      // Navigate to a different page
      await page.goto('/web#action=');
      await expect(page.locator('.o_main_navbar')).toBeVisible();
    });

    test('should logout successfully', async ({ page }) => {
      await page.goto('/web');
      await expect(page.locator('.o_main_navbar')).toBeVisible();
      
      // Click user menu
      await page.click('.o_user_menu .dropdown-toggle, .o_navbar_profile');
      
      // Click logout
      await page.click('a:has-text("Log out"), a[data-menu="logout"]');
      
      // Verify redirected to login
      await expect(page.locator('input[name="login"]')).toBeVisible({ timeout: 10000 });
    });
  });
});

