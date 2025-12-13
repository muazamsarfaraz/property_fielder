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

  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Navigate to Odoo login
    await page.goto(`${baseURL}/web/login`);

    // Wait for login form
    await page.waitForSelector('input[name="login"]', { timeout: 10000 });

    // Fill login form
    await page.fill('input[name="login"]', process.env.ADMIN_LOGIN || 'admin');
    await page.fill('input[name="password"]', process.env.ADMIN_PASSWORD || 'admin');

    // Submit login
    await page.click('button[type="submit"]');

    // Wait for successful login (Odoo main interface)
    await page.waitForSelector('.o_main_navbar, .o_web_client', { timeout: 30000 });

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

