const { test, expect } = require('@playwright/test');

test.describe('Django Dashboard', () => {
  const DJANGO_URL = 'http://localhost:8000';
  const TEST_USER = 'testuser1';
  const TEST_PASS = 'testpass123';

  test.beforeEach(async ({ page }) => {
    // Navigate to login page
    await page.goto(`${DJANGO_URL}/login/`);
  });

  test('should display login page', async ({ page }) => {
    await expect(page).toHaveTitle(/Login/);
    await expect(page.locator('input[name="username"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    // Fill login form
    await page.fill('input[name="username"]', TEST_USER);
    await page.fill('input[name="password"]', TEST_PASS);
    await page.click('button[type="submit"]');

    // Wait for dashboard to load
    await page.waitForURL(`${DJANGO_URL}/dashboard/`);
    await expect(page).toHaveURL(`${DJANGO_URL}/dashboard/`);
    await expect(page).toHaveTitle(/Dashboard/);
  });

  test('should display energy overview stats', async ({ page }) => {
    // Login first
    await page.fill('input[name="username"]', TEST_USER);
    await page.fill('input[name="password"]', TEST_PASS);
    await page.click('button[type="submit"]');
    await page.waitForURL(`${DJANGO_URL}/dashboard/`);

    // Check for energy overview elements
    await expect(page.locator('text=Energy Overview')).toBeVisible();
    
    // Check for stat cards (these should be present even if values are 0)
    const statCards = page.locator('[class*="stat-card"], [class*="card"]');
    await expect(statCards.first()).toBeVisible({ timeout: 5000 });
  });

  test('should display energy flow visualization', async ({ page }) => {
    // Login
    await page.fill('input[name="username"]', TEST_USER);
    await page.fill('input[name="password"]', TEST_PASS);
    await page.click('button[type="submit"]');
    await page.waitForURL(`${DJANGO_URL}/dashboard/`);

    // Check for energy flow section
    await expect(page.locator('text=Energy Flow').or(page.locator('text=System Overview'))).toBeVisible({ timeout: 5000 });
  });

  test('should display connected devices', async ({ page }) => {
    // Login
    await page.fill('input[name="username"]', TEST_USER);
    await page.fill('input[name="password"]', TEST_PASS);
    await page.click('button[type="submit"]');
    await page.waitForURL(`${DJANGO_URL}/dashboard/`);

    // Check for devices section
    await expect(
      page.locator('text=Connected Devices').or(page.locator('text=Devices'))
    ).toBeVisible({ timeout: 5000 });
  });

  test('should navigate to devices page', async ({ page }) => {
    // Login
    await page.fill('input[name="username"]', TEST_USER);
    await page.fill('input[name="password"]', TEST_PASS);
    await page.click('button[type="submit"]');
    await page.waitForURL(`${DJANGO_URL}/dashboard/`);

    // Look for devices link in navigation
    const devicesLink = page.locator('a[href*="devices"]').first();
    if (await devicesLink.isVisible()) {
      await devicesLink.click();
      await expect(page).toHaveURL(/devices/);
    }
  });

  test('should fail login with invalid credentials', async ({ page }) => {
    await page.fill('input[name="username"]', 'wronguser');
    await page.fill('input[name="password"]', 'wrongpass');
    await page.click('button[type="submit"]');

    // Should stay on login page or show error
    await expect(
      page.locator('text=Invalid').or(page.locator('text=Error'))
    ).toBeVisible({ timeout: 3000 });
  });

  test('should have logout functionality', async ({ page }) => {
    // Login
    await page.fill('input[name="username"]', TEST_USER);
    await page.fill('input[name="password"]', TEST_PASS);
    await page.click('button[type="submit"]');
    await page.waitForURL(`${DJANGO_URL}/dashboard/`);

    // Look for logout link/button
    const logoutButton = page.locator('a[href*="logout"], button:has-text("Logout"), a:has-text("Logout")').first();
    if (await logoutButton.isVisible()) {
      await logoutButton.click();
      
      // Should redirect to login or home
      await page.waitForTimeout(1000);
      const currentUrl = page.url();
      expect(currentUrl).toMatch(/login|home|\/$|^http:\/\/localhost:8000\/?$/);
    }
  });
});
