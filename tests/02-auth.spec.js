// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Authentication Flow', () => {

  test('register page loads with all fields', async ({ page }) => {
    await page.goto('/register/');
    await expect(page.locator('input[name="first_name"]')).toBeVisible();
    await expect(page.locator('input[name="last_name"]')).toBeVisible();
    await expect(page.locator('input[name="email"]')).toBeVisible();
    await expect(page.locator('input[name="password1"]')).toBeVisible();
    await expect(page.getByRole('button', { name: /Register/i })).toBeVisible();
  });

  test('Google sign-in button is visible when configured', async ({ page }) => {
    await page.goto('/register/');
    // Only assert if env has Google OAuth set
    const googleBtn = page.locator('.google-login-btn');
    const isVisible = await googleBtn.isVisible().catch(() => false);
    if (isVisible) {
      await expect(googleBtn).toContainText(/Continue with Google/i);
    } else {
      console.log('ℹ️  Google OAuth not configured — skipping');
    }
  });

  test('register validates Gmail-only emails', async ({ page }) => {
    await page.goto('/register/');
    await page.fill('input[name="first_name"]', 'Test');
    await page.fill('input[name="last_name"]', 'User');
    await page.fill('input[name="email"]', 'not-a-gmail@yahoo.com');
    await page.fill('input[name="password1"]', 'StrongPass123!');
    await page.getByRole('button', { name: /Register/i }).click();
    // Should stay on register and show error
    await expect(page).toHaveURL(/register/);
  });

  test('register validates short password', async ({ page }) => {
    await page.goto('/register/');
    await page.fill('input[name="first_name"]', 'Test');
    await page.fill('input[name="last_name"]', 'User');
    await page.fill('input[name="email"]', `test${Date.now()}@gmail.com`);
    await page.fill('input[name="password1"]', 'short');
    await page.getByRole('button', { name: /Register/i }).click();
    await expect(page).toHaveURL(/register/);
  });

  test('login page loads', async ({ page }) => {
    await page.goto('/login/');
    await expect(page.locator('input[name="username"]')).toBeVisible();
    await expect(page.locator('input[name="password"]')).toBeVisible();
    await expect(page.getByRole('button', { name: /Sign in/i })).toBeVisible();
  });

  test('login with wrong credentials shows error', async ({ page }) => {
    await page.goto('/login/');
    await page.fill('input[name="username"]', 'nobody@gmail.com');
    await page.fill('input[name="password"]', 'WrongPass123');
    await page.getByRole('button', { name: /Sign in/i }).click();
    await expect(page).toHaveURL(/login/);
    await expect(page.locator('.alert-danger')).toBeVisible();
  });

  test('OTP login page loads', async ({ page }) => {
    await page.goto('/login/otp/');
    await expect(page.locator('input[name="email"]')).toBeVisible();
  });

  test('protected routes redirect to login', async ({ page }) => {
    await page.goto('/dashboard/');
    await expect(page).toHaveURL(/login/);
  });
});
