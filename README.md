# Shared Expense Tracker

A Django web application for group expense tracking, payment proof uploads, receiver verification, notifications, and reports.

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
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
.\.venv\Scripts\python.exe manage.py test
```

## Email Verification and Invitations

Registration, passwordless email login, group invitations, expense invitations, and settlement reminders use Django email settings.

The authentication flow is:

1. Register with username, email, and password.
2. Enter the 6-digit verification code sent to the registered email.
3. Log in with email/username and password, or request a 6-digit email login code.

Local development can use console email, where codes print in the server terminal. For a real inbox, configure SMTP.

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

To verify email delivery from your own PowerShell terminal:

```powershell
.\.venv\Scripts\python.exe manage.py test_email your-gmail-address@gmail.com
```

## AI Agents

The `/agents/` page includes:

- Expense Assistant: parses natural language like `I paid 4500 for dinner with amal` and can create the expense.
- Settlement Agent: lists pending payments for a group and can send email reminders plus in-app notifications.
