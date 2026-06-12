// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Landing Page', () => {

  test('loads and shows hero', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Expense Tracker/);
    await expect(page.locator('.landing-title')).toContainText('Shared money');
  });

  test('has working Register button', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: /Get Started|Create your account/i }).first().click();
    await expect(page).toHaveURL(/register/);
    await expect(page.locator('h2')).toContainText('Create your account');
  });

  test('has working Login button', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: /^Sign in$|^Login$/i }).first().click();
    await expect(page).toHaveURL(/login/);
  });

  test('shows all feature cards', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.feature-card')).toHaveCount(6);
    await expect(page.locator('.feature-card').first()).toContainText(/Expense groups|Automatic|Proof/);
  });

  test('shows 3-step "How it works" section', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.step-item')).toHaveCount(3);
  });

  test('footer is present', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.app-footer')).toBeVisible();
    await expect(page.locator('.footer-copy')).toContainText('Expense Tracker');
  });
});
