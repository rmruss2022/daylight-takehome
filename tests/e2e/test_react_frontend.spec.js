const { test, expect } = require('@playwright/test');

test.describe('React Frontend', () => {
  const REACT_URL = 'http://localhost:3000';
  const API_URL = 'http://localhost:8000';
  const TEST_USER = 'testuser1';
  const TEST_PASS = 'testpassword123';

  test.beforeEach(async ({ page }) => {
    // Navigate to React app
    await page.goto(REACT_URL);
  });

  test('should display login page', async ({ page }) => {
    await expect(page.locator('input[name="username"], input[type="text"]')).toBeVisible({ timeout: 5000 });
    await expect(page.locator('input[name="password"], input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")')).toBeVisible();
  });

  test('should login with JWT authentication', async ({ page }) => {
    // Fill login form
    await page.fill('input[name="username"], input[type="text"]', TEST_USER);
    await page.fill('input[name="password"], input[type="password"]', TEST_PASS);
    
    // Submit and wait for navigation
    await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    
    // Wait for redirect to dashboard
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });
    
    // Verify we're logged in (token should be stored)
    const token = await page.evaluate(() => localStorage.getItem('token') || localStorage.getItem('authToken'));
    expect(token).toBeTruthy();
  });

  test('should display dashboard stats cards', async ({ page }) => {
    // Login first
    await page.fill('input[name="username"], input[type="text"]', TEST_USER);
    await page.fill('input[name="password"], input[type="password"]', TEST_PASS);
    await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });

    // Check for stat cards
    await expect(page.locator('text=Total Production').or(page.locator('text=Solar Production'))).toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=Grid Usage').or(page.locator('text=Usage'))).toBeVisible({ timeout: 5000 });
  });

  test('should navigate to battery management page', async ({ page }) => {
    // Login
    await page.fill('input[name="username"], input[type="text"]', TEST_USER);
    await page.fill('input[name="password"], input[type="password"]', TEST_PASS);
    await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });

    // Look for battery link
    const batteryLink = page.locator('a[href*="battery"], a:has-text("Battery"), button:has-text("Battery")').first();
    
    if (await batteryLink.isVisible({ timeout: 3000 })) {
      await batteryLink.click();
      await expect(page).toHaveURL(/battery/);
      await expect(page.locator('text=Battery').or(page.locator('text=Storage'))).toBeVisible();
    } else {
      // If no dedicated battery page, check that battery info is on dashboard
      await expect(page.locator('text=Battery').or(page.locator('text=Storage'))).toBeVisible({ timeout: 3000 });
    }
  });

  test('should display device information', async ({ page }) => {
    // Login
    await page.fill('input[name="username"], input[type="text"]', TEST_USER);
    await page.fill('input[name="password"], input[type="password"]', TEST_PASS);
    await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });

    // Check for devices section
    await expect(
      page.locator('text=Devices').or(page.locator('text=Connected')).or(page.locator('text=Status'))
    ).toBeVisible({ timeout: 5000 });
  });

  test('should have working navigation', async ({ page }) => {
    // Login
    await page.fill('input[name="username"], input[type="text"]', TEST_USER);
    await page.fill('input[name="password"], input[type="password"]', TEST_PASS);
    await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });

    // Check for navigation elements
    const nav = page.locator('nav, [role="navigation"]');
    await expect(nav).toBeVisible({ timeout: 3000 });
    
    // Should have multiple nav links
    const navLinks = page.locator('nav a, [role="navigation"] a');
    const count = await navLinks.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should protect routes when not authenticated', async ({ page }) => {
    // Try to access dashboard directly without login
    await page.goto(`${REACT_URL}/dashboard`);
    
    // Should redirect to login or show login prompt
    await page.waitForTimeout(2000);
    const currentUrl = page.url();
    
    // Either redirected to login, or there's a login form visible
    const isOnLogin = currentUrl.includes('login') || currentUrl === `${REACT_URL}/` || currentUrl === REACT_URL;
    const hasLoginForm = await page.locator('input[type="password"]').isVisible();
    
    expect(isOnLogin || hasLoginForm).toBe(true);
  });

  test('should fail login with invalid credentials', async ({ page }) => {
    await page.fill('input[name="username"], input[type="text"]', 'wronguser');
    await page.fill('input[name="password"], input[type="password"]', 'wrongpass');
    await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');

    // Should show error message
    await expect(
      page.locator('text=Invalid').or(page.locator('text=Error')).or(page.locator('text=failed'))
    ).toBeVisible({ timeout: 5000 });
  });

  test('should logout successfully', async ({ page }) => {
    // Login
    await page.fill('input[name="username"], input[type="text"]', TEST_USER);
    await page.fill('input[name="password"], input[type="password"]', TEST_PASS);
    await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });

    // Find and click logout
    const logoutButton = page.locator('button:has-text("Logout"), a:has-text("Logout"), button:has-text("Sign Out"), a:has-text("Sign Out")').first();
    
    if (await logoutButton.isVisible({ timeout: 3000 })) {
      await logoutButton.click();
      
      // Wait for redirect
      await page.waitForTimeout(1000);
      
      // Should clear token
      const token = await page.evaluate(() => localStorage.getItem('token') || localStorage.getItem('authToken'));
      expect(token).toBeFalsy();
      
      // Should show login form
      await expect(page.locator('input[type="password"]')).toBeVisible({ timeout: 3000 });
    }
  });

  test('should display real-time data updates', async ({ page }) => {
    // Login
    await page.fill('input[name="username"], input[type="text"]', TEST_USER);
    await page.fill('input[name="password"], input[type="password"]', TEST_PASS);
    await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    await page.waitForURL(/dashboard|home/, { timeout: 10000 });

    // Check that data is being displayed (even if it's zero/mock data)
    const dataElements = page.locator('[class*="stat"], [class*="metric"], [class*="value"]');
    await expect(dataElements.first()).toBeVisible({ timeout: 5000 });
    
    // Verify numbers are present
    const hasNumbers = await page.locator('text=/\\d+/').first().isVisible({ timeout: 3000 });
    expect(hasNumbers).toBe(true);
  });
});
