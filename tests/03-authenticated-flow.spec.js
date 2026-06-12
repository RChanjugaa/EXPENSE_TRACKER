// @ts-check
const { test, expect } = require('@playwright/test');

// Test user — must exist before running these tests.
// Created by: tests/setup-test-user.ps1 OR manually via manage.py shell.
const TEST_USER = {
  email: 'testuser.playwright@gmail.com',
  password: 'PlaywrightTest123!',
};

async function loginAsTestUser(page) {
  await page.goto('/login/');
  await page.fill('input[name="username"]', TEST_USER.email);
  await page.fill('input[name="password"]', TEST_USER.password);
  await page.getByRole('button', { name: /Sign in/i }).click();
  await page.waitForURL(/dashboard/, { timeout: 10_000 });
}

test.describe('Authenticated User Journey', () => {

  test('dashboard loads after login', async ({ page }) => {
    await loginAsTestUser(page);
    await expect(page).toHaveURL(/dashboard/);
    await expect(page.locator('.page-title')).toContainText(/Good to see you/);
  });

  test('navigation bar shows all menu items', async ({ page }) => {
    await loginAsTestUser(page);
    await expect(page.getByRole('link', { name: /Groups/i }).first()).toBeVisible();
    await expect(page.getByRole('link', { name: /Payments/i }).first()).toBeVisible();
    await expect(page.getByRole('link', { name: /Summaries/i }).first()).toBeVisible();
    await expect(page.getByRole('link', { name: /Reports/i }).first()).toBeVisible();
    await expect(page.getByRole('link', { name: /Alerts/i }).first()).toBeVisible();
  });

  test('create a new group', async ({ page }) => {
    await loginAsTestUser(page);
    const groupName = `Test Group ${Date.now()}`;
    await page.goto('/groups/new/');
    await page.fill('input[name="name"]', groupName);
    await page.fill('textarea[name="description"]', 'Created by Playwright test');
    // Click the "Save Group" button specifically — the navbar has a Logout form too
    await page.getByRole('button', { name: /Save Group/i }).click();
    await page.waitForLoadState('networkidle');
    // The group should now appear in the group list
    await page.goto('/groups/');
    await expect(page.locator('body')).toContainText(groupName);
  });

  test('group list page works', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/groups/');
    await expect(page.locator('.page-title')).toContainText(/Your Groups/);
  });

  test('payment history page works', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/payments/');
    await expect(page.locator('.page-title')).toContainText(/Payment History/);
  });

  test('monthly report page works', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/reports/monthly/');
    await expect(page.locator('.page-title')).toContainText(/Report/);
  });

  test('group summary page works', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/reports/groups/');
    await expect(page.locator('.page-title')).toContainText(/Group Summaries/i);
  });

  test('notifications page works', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/notifications/');
    await expect(page.locator('.page-title')).toContainText(/Notifications/);
  });

  test('AI agent dashboard loads', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/agents/');
    // Just verify page renders without 500
    await expect(page.locator('body')).toBeVisible();
    const status = page.url();
    expect(status).not.toContain('/login/');
  });

  test('logout works', async ({ page }) => {
    await loginAsTestUser(page);
    await page.goto('/dashboard/');
    // Logout is inside a form in the navbar
    await page.locator('form[action="/logout/"] button[type="submit"]').click();
    await page.waitForURL(/login|landing|\/$/, { timeout: 10_000 });
    await expect(page).not.toHaveURL(/dashboard/);
  });
});
