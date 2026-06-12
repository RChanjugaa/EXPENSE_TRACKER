// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Visual / Responsive Checks', () => {

  test('landing page is responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 }); // iPhone X
    await page.goto('/');
    await expect(page.locator('.landing-title')).toBeVisible();
    await page.screenshot({ path: 'test-results/screenshots/landing-mobile.png', fullPage: true });
  });

  test('landing page is responsive on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    await page.screenshot({ path: 'test-results/screenshots/landing-tablet.png', fullPage: true });
  });

  test('landing page is responsive on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto('/');
    await page.screenshot({ path: 'test-results/screenshots/landing-desktop.png', fullPage: true });
  });

  test('register page renders all critical elements', async ({ page }) => {
    await page.goto('/register/');
    await page.screenshot({ path: 'test-results/screenshots/register.png', fullPage: true });
    await expect(page.locator('.auth-brand-panel')).toBeVisible();
    await expect(page.locator('form')).toBeVisible();
  });

  test('login page renders all critical elements', async ({ page }) => {
    await page.goto('/login/');
    await page.screenshot({ path: 'test-results/screenshots/login.png', fullPage: true });
    await expect(page.locator('.auth-brand-panel')).toBeVisible();
  });

  test('no console errors on landing', async ({ page }) => {
    const errors = [];
    page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    expect(errors.filter(e => !e.includes('favicon'))).toHaveLength(0);
  });

  test('no broken images on landing', async ({ page }) => {
    await page.goto('/');
    const brokenImages = await page.evaluate(() => {
      return [...document.querySelectorAll('img')]
        .filter(img => !img.complete || img.naturalWidth === 0)
        .map(img => img.src);
    });
    expect(brokenImages).toEqual([]);
  });
});
