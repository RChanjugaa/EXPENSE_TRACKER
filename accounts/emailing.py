from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail


SMTP_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
CONSOLE_BACKEND = 'django.core.mail.backends.console.EmailBackend'


class EmailDeliveryError(Exception):
    pass


def is_console_email_backend():
    return settings.EMAIL_BACKEND == CONSOLE_BACKEND


def is_smtp_email_backend():
    return settings.EMAIL_BACKEND == SMTP_BACKEND


def email_delivery_context():
    is_console = is_console_email_backend()
    has_smtp_credentials = bool(settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD)
    return {
        'email_backend': settings.EMAIL_BACKEND,
        'emails_deliver_to_inbox': not is_console and has_smtp_credentials,
        'email_setup_warning': (
            'Email is currently in console mode, so codes print in the server terminal instead of arriving in Gmail.'
            if is_console else ''
        ),
    }


def validate_email_delivery_settings():
    if not is_smtp_email_backend():
        return
    missing_settings = [
        name for name in ['EMAIL_HOST', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD', 'DEFAULT_FROM_EMAIL']
        if not getattr(settings, name, '')
    ]
    if missing_settings:
        raise ImproperlyConfigured(
            'SMTP email delivery is enabled but these settings are missing: '
            + ', '.join(missing_settings)
        )
    if settings.EMAIL_HOST == 'smtp.gmail.com' and not settings.EMAIL_HOST_USER.lower().endswith('@gmail.com'):
        raise ImproperlyConfigured('Gmail SMTP requires EMAIL_HOST_USER to be a Gmail address.')


def send_expense_tracker_mail(subject, message, recipient_list):
    try:
        validate_email_delivery_settings()
        sent = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
    except Exception as exc:
        raise EmailDeliveryError(str(exc)) from exc
    if sent != len(recipient_list):
        raise EmailDeliveryError('Django reported that not all messages were accepted for delivery.')
    return sent
