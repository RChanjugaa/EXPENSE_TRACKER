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

## Test

```powershell
.\.venv\Scripts\python.exe manage.py test
```

## Google Login Setup

This project uses `django-allauth` for Google registration and login.

1. Create OAuth credentials in Google Cloud Console.
2. Add this local redirect URI:

```text
http://127.0.0.1:8000/accounts/google/login/callback/
```

3. Create a Django admin user:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

4. Open `/admin/`, go to **Social applications**, and add:
   - Provider: Google
   - Client ID: your Google OAuth client ID
   - Secret key: your Google OAuth client secret
   - Sites: move `example.com` or your local site into the chosen sites box

For AWS, add the production callback URL too, for example:

```text
https://your-domain.com/accounts/google/login/callback/
```

## Gmail Invitation Setup

Invitations use Django email settings. Local development defaults to console email, so invitation links print in the server output.

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
