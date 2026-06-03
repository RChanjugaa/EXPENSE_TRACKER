from django.conf import settings
from django.core.checks import Error, Warning, register

from .emailing import CONSOLE_BACKEND, SMTP_BACKEND


@register()
def email_settings_check(app_configs, **kwargs):
    issues = []
    if settings.EMAIL_BACKEND == CONSOLE_BACKEND and not settings.DEBUG:
        issues.append(Error(
            'Production email is configured to use the console backend.',
            hint='Set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend and configure Gmail SMTP credentials.',
            id='accounts.E001',
        ))

    if settings.EMAIL_BACKEND == SMTP_BACKEND:
        missing_settings = [
            name for name in ['EMAIL_HOST', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD', 'DEFAULT_FROM_EMAIL']
            if not getattr(settings, name, '')
        ]
        if missing_settings:
            issues.append(Error(
                'SMTP email delivery is enabled but required settings are missing.',
                hint='Set: ' + ', '.join(missing_settings),
                id='accounts.E002',
            ))
        if settings.EMAIL_HOST == 'smtp.gmail.com' and settings.EMAIL_PORT != 587:
            issues.append(Warning(
                'Gmail SMTP normally uses port 587 with TLS.',
                hint='Set EMAIL_PORT=587 and EMAIL_USE_TLS=True for Gmail app-password delivery.',
                id='accounts.W001',
            ))
        if settings.EMAIL_HOST == 'smtp.gmail.com' and not settings.EMAIL_USE_TLS:
            issues.append(Warning(
                'Gmail SMTP is configured without TLS.',
                hint='Set EMAIL_USE_TLS=True.',
                id='accounts.W002',
            ))
        if settings.EMAIL_HOST == 'smtp.gmail.com' and settings.EMAIL_HOST_USER and not settings.EMAIL_HOST_USER.lower().endswith('@gmail.com'):
            issues.append(Error(
                'Gmail SMTP requires EMAIL_HOST_USER to be a Gmail address.',
                hint='Use the Gmail address that owns the app password.',
                id='accounts.E003',
            ))
        if settings.DEFAULT_FROM_EMAIL and settings.EMAIL_HOST_USER and settings.DEFAULT_FROM_EMAIL.lower() != settings.EMAIL_HOST_USER.lower():
            issues.append(Warning(
                'DEFAULT_FROM_EMAIL does not match EMAIL_HOST_USER.',
                hint='Gmail may reject or rewrite From addresses that do not match the authenticated account.',
                id='accounts.W003',
            ))
    return issues
