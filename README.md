# Shared Expense Tracker

A Django web application for shared expense tracking, Gmail/Google login, group and expense invitations, payment proof uploads, receiver verification, notifications, settlement reminders, and reports.

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item -LiteralPath .env.example -Destination .env -Force
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Open http://127.0.0.1:8000/register/ to create your first account.

On this machine, you can also run:

```powershell
.\run_app.ps1
```

## Test

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

## Google Login Setup

Google sign-in is handled by `django-allauth`. Add these values to `.env`:

```text
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
```

In Google Cloud Console, configure the OAuth client as a Web application and add these Authorized redirect URIs for local development:

```text
http://127.0.0.1:8000/accounts/google/login/callback/
http://localhost:8000/accounts/google/login/callback/
```

The app accepts Gmail accounts only. Google sign-in marks the Gmail address verified automatically.

## Email Verification and Invitations

Registration, passwordless Gmail login, group invitations, expense invitations, and settlement reminders use Django email settings.

The authentication flow is:

1. Register with a Gmail address and password, or continue with Google.
2. Password registration sends a 6-digit Gmail verification code.
3. Log in with Gmail/password, Google, or a 6-digit Gmail login code.

Group and expense invitations also require Gmail addresses so invite acceptance can be matched to a verified user account.

Local development can use console email, where codes and invitation bodies print in the server terminal. For a real inbox, configure SMTP.

To send real Gmail messages, create a Gmail app password and set these in `.env`:

```text
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-gmail-address@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=your-gmail-address@gmail.com
```

Never commit `.env` or real credentials.

## Safe Local Smoke Test

Keep this setting in `.env`:

```text
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Then start the server and walk through:

1. Register with a Gmail address.
2. Read the verification code from the server terminal.
3. Create a group and send a group invitation to another Gmail address.
4. Create an expense and send an expense invitation.
5. Open `/agents/`, select a group with pending payments, and send settlement reminders.

Console mode prints email content locally instead of delivering to Gmail, so it is the safest smoke test.

To verify real Gmail SMTP delivery after adding an app password:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test_email your-gmail-address@gmail.com
```

## AI Agents

The `/agents/` page includes:

- Expense Assistant: parses natural language like `I paid 4500 for dinner with amal` and can create the expense.
- Settlement Agent: lists pending payments for a group and can send email reminders plus in-app notifications.
