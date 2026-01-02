// Quick test script to login to the app
// Run with: node test_login.js

const puppeteer = require('puppeteer');

async function testLogin() {
  console.log('🚀 Starting login test...');
  
  // Connect to the Chrome instance that Flutter opened
  // We need to find the debugging port
  const browser = await puppeteer.launch({
    headless: false,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080 });
  
  console.log('📱 Navigating to app...');
  await page.goto('http://localhost:51233', { waitUntil: 'networkidle2' });
  
  // Wait for the app to load
  await page.waitForTimeout(5000);
  
  console.log('📸 Taking screenshot of current state...');
  await page.screenshot({ path: 'app_state.png', fullPage: true });
  
  console.log('✅ Screenshot saved as app_state.png');
  
  // Try to find login form
  const loginForm = await page.$('input[type="text"], input[type="email"]');
  if (loginForm) {
    console.log('✅ Found login form!');
    
    // Fill in credentials
    const usernameInput = await page.$('input[type="text"], input[type="email"]');
    const passwordInput = await page.$('input[type="password"]');
    
    if (usernameInput && passwordInput) {
      console.log('📝 Filling in credentials...');
      await usernameInput.type('admin');
      await passwordInput.type('admin');
      
      // Find and click login button
      const loginButton = await page.$('button');
      if (loginButton) {
        console.log('🔐 Clicking login button...');
        await loginButton.click();
        
        // Wait for navigation
        await page.waitForTimeout(3000);
        
        console.log('📸 Taking screenshot after login...');
        await page.screenshot({ path: 'after_login.png', fullPage: true });
        console.log('✅ Screenshot saved as after_login.png');
      }
    }
  } else {
    console.log('⚠️ No login form found - app might still be loading');
  }
  
  console.log('✅ Test complete!');
  // Don't close browser so we can inspect
  // await browser.close();
}

testLogin().catch(console.error);

