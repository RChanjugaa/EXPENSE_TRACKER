# 🎭 Playwright Testing Guide

## What's Tested

| File | What it covers |
|---|---|
| `01-landing.spec.js` | Landing page loads, hero, features, footer, navigation |
| `02-auth.spec.js` | Register form, login, OTP, validation, Google button |
| `03-authenticated-flow.spec.js` | Full user journey — dashboard, groups, payments, reports |
| `04-visual.spec.js` | Responsive design (mobile/tablet/desktop), screenshots, console errors |

---

## 🚀 First-Time Setup

```powershell
# Install dependencies (one-time)
cd "C:\Users\Brunotech\OneDrive\Desktop\EXPENSE_TRACKER-main"
npm install
npx playwright install
```

---

## ▶️ Running Tests

| Command | What it does |
|---|---|
| `npm test` | Run ALL tests (headless, fast) |
| `npm run test:headed` | Watch the browser as tests run (cool!) |
| `npm run test:ui` | Interactive UI — best for debugging |
| `npm run test:landing` | Only landing page tests |
| `npm run test:auth` | Only auth tests |
| `npm run test:flow` | Only authenticated user journey |
| `npm run test:visual` | Only responsive/visual tests |
| `npm run test:report` | Open the last HTML report |

---

## 📊 Viewing Results

After tests finish, an HTML report is generated. Open it with:

```powershell
npm run test:report
```

Or just open `playwright-report/index.html` in your browser.

Screenshots from visual tests are saved in `test-results/screenshots/`.

---

## 🎬 Demo Mode (Great for Showing Off!)

Run with the browser visible — perfect for showing in a video or to mentors:

```powershell
npm run test:headed
```

Playwright will pop up Chrome and execute each test in front of you. Perfect for recording a demo of automated testing!

---

## 🐛 Debugging a Failed Test

```powershell
npx playwright test --debug
```

This pauses on each step so you can step through.

---

## ⚙️ How It Works

- Playwright **auto-starts** your Django server when tests begin (using `webServer` in `playwright.config.js`)
- If the server is already running, it reuses it (no conflict)
- Tests run **sequentially** because SQLite isn't great with concurrent writes
- The authenticated tests create a real test user via `manage.py shell`

---

## 🎯 For Your LinkedIn Post / CV

You can now claim:
> ✅ **End-to-end tested with Playwright** — 25+ automated tests covering landing, authentication, user journey, and responsive design.

That's a serious credential boost!
