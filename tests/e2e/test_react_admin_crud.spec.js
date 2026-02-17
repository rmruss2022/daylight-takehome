const { test, expect } = require('@playwright/test');

const REACT_URL = process.env.REACT_URL || 'http://localhost:3000';
const ADMIN_USER = process.env.REACT_ADMIN_USER || 'admin';
const ADMIN_PASS = process.env.REACT_ADMIN_PASS || 'admin';

async function loginAsAdmin(page) {
  await page.goto(REACT_URL);
  await page.fill('input[name="username"], input[type="text"]', ADMIN_USER);
  await page.fill('input[name="password"], input[type="password"]', ADMIN_PASS);
  await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
  await page.waitForURL(/dashboard/, { timeout: 15000 });
}

test.describe('React Admin CRUD', () => {
  test('admin can create, edit, and delete users', async ({ page }) => {
    const stamp = Date.now();
    const username = `e2e_user_${stamp}`;
    const updatedEmail = `updated_${stamp}@example.com`;

    await loginAsAdmin(page);
    await page.click('a[href="/users"]');

    await page.click('button:has-text("Add User")');
    const addForm = page.locator('form', { has: page.locator('h3:has-text("Add User")') });
    await addForm.locator('input').nth(0).fill(username);
    await addForm.locator('input').nth(1).fill(`${username}@example.com`);
    await addForm.locator('input').nth(4).fill('UserPass123');
    await addForm.locator('input').nth(5).fill('UserPass123');
    await addForm.locator('button[type="submit"]').click();

    await expect(page.locator(`strong:has-text("${username}")`)).toBeVisible({ timeout: 10000 });

    await page.locator(`xpath=//strong[normalize-space()="${username}"]/ancestor::div[1]//button[normalize-space()="Edit"]`).click();
    const editForm = page.locator('form', { has: page.locator(`h3:has-text("Edit User: ${username}")`) });
    await editForm.locator('input').nth(1).fill(updatedEmail);
    await editForm.locator('button[type="submit"]').click();
    await expect(page.locator(`text=${updatedEmail}`)).toBeVisible({ timeout: 10000 });

    page.once('dialog', (dialog) => dialog.accept());
    await page.locator(`xpath=//strong[normalize-space()="${username}"]/ancestor::div[1]//button[normalize-space()="Delete"]`).click();
    await expect(page.locator(`text=${username}`)).toHaveCount(0, { timeout: 10000 });
  });

  test('admin can create, edit, and delete generators', async ({ page }) => {
    const stamp = Date.now();
    const name = `E2E Generator ${stamp}`;
    const updatedName = `${name} Updated`;

    await loginAsAdmin(page);
    await page.click('a[href="/generators"]');
    await expect(page.locator('h1:has-text("Generators")')).toBeVisible({ timeout: 10000 });

    await page.click('button:has-text("Add")');
    const addForm = page.locator('form', { has: page.locator('h3:has-text("Add Generators")') });
    await addForm.locator('input[type="text"]').fill(name);
    await addForm.locator('input[type="number"]').fill('1500');
    await addForm.locator('button[type="submit"]').click();
    await expect(page.locator(`h3:has-text("${name}")`)).toBeVisible({ timeout: 10000 });

    const card = page.locator('article', { has: page.locator(`h3:has-text("${name}")`) }).first();
    await card.locator('button:has-text("Edit")').click();
    const editForm = page.locator('form', { has: page.locator(`h3:has-text("Edit ${name}")`) });
    await editForm.locator('input[type="text"]').fill(updatedName);
    await editForm.locator('button[type="submit"]').click();
    await expect(page.locator(`h3:has-text("${updatedName}")`)).toBeVisible({ timeout: 10000 });

    const updatedCard = page.locator('article', { has: page.locator(`h3:has-text("${updatedName}")`) }).first();
    page.once('dialog', (dialog) => dialog.accept());
    await updatedCard.locator('button:has-text("Delete")').click();
    await expect(page.locator(`h3:has-text("${updatedName}")`)).toHaveCount(0, { timeout: 10000 });
  });
});
