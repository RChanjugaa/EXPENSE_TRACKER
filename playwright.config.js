// @ts-check
const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: false, // Sequential — Django dev server has shared SQLite
  retries: 0,
  workers: 1,
  reporter: [['html', { open: 'never' }], ['list']],
  timeout: 30_000,

  use: {
    baseURL: 'http://127.0.0.1:8000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Auto-start the Django server before tests
  webServer: {
    command: '.\\.venv\\Scripts\\python.exe manage.py runserver 127.0.0.1:8000 --noreload',
    url: 'http://127.0.0.1:8000/',
    reuseExistingServer: true,
    timeout: 60_000,
  },
});
