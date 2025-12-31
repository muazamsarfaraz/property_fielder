import { chromium, FullConfig } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';
import dotenv from 'dotenv';

dotenv.config();

async function globalSetup(config: FullConfig) {
  const { baseURL } = config.projects[0].use;
  const authDir = path.join(__dirname, 'playwright', '.auth');
  const authFile = path.join(authDir, 'user.json');

  // Create auth directory if it doesn't exist
  if (!fs.existsSync(authDir)) {
    fs.mkdirSync(authDir, { recursive: true });
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  const page = await context.newPage();

  try {
    // Navigate to Odoo login
    console.log('🔐 Navigating to login page...');
    await page.goto(`${baseURL}/web/login`, { waitUntil: 'load' });

    // Wait for Odoo 19 login form to load (it's loaded via JavaScript)
    console.log('⏳ Waiting for login form...');

    // Wait for the login input - use name attribute which is consistent
    const loginInput = page.locator('input[name="login"]');
    const passwordInput = page.locator('input[name="password"]');

    // Wait for login input to be attached to DOM first
    await loginInput.waitFor({ state: 'attached', timeout: 20000 });
    console.log('✓ Login input found in DOM');

    // Now wait for it to be visible (or force interaction if hidden due to CSS)
    try {
      await loginInput.waitFor({ state: 'visible', timeout: 5000 });
      console.log('✓ Login input is visible');
    } catch {
      console.log('⚠ Login input not visible, will try to interact anyway');
    }

    // Fill login form using evaluate to bypass visibility checks
    // This is needed because Odoo 19 CSS may hide elements based on viewport/JS state
    await page.evaluate((credentials) => {
      const loginEl = document.querySelector('input[name="login"]') as HTMLInputElement;
      const passEl = document.querySelector('input[name="password"]') as HTMLInputElement;
      if (loginEl) loginEl.value = credentials.login;
      if (passEl) passEl.value = credentials.password;
      // Trigger input events
      loginEl?.dispatchEvent(new Event('input', { bubbles: true }));
      passEl?.dispatchEvent(new Event('input', { bubbles: true }));
    }, { login: process.env.ADMIN_LOGIN || 'admin', password: process.env.ADMIN_PASSWORD || 'admin' });
    console.log('✓ Credentials filled');

    // Submit login - click the submit button via evaluate
    await page.evaluate(() => {
      const btn = document.querySelector('button[type="submit"]') as HTMLButtonElement;
      if (btn) btn.click();
    });
    console.log('✓ Login button clicked');

    // Wait for successful login (Odoo 19 main interface or legacy)
    await page.waitForURL(/\/odoo\/|\/web(?!\/login)/, { timeout: 30000 });

    // Save authentication state
    await context.storageState({ path: authFile });
    console.log('✅ Authentication successful - session saved');
  } catch (error) {
    console.error('❌ Authentication failed:', error);
    // Save a screenshot for debugging
    await page.screenshot({ path: path.join(authDir, 'login-error.png') });
    throw error;
  } finally {
    await browser.close();
  }
}

export default globalSetup;

