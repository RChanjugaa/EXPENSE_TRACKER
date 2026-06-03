from django.core.exceptions import ValidationError


def validate_gmail_address(email):
    email = (email or '').strip().lower()
    if not email.endswith('@gmail.com'):
        raise ValidationError('Use a valid Gmail address ending in @gmail.com.')
    return email
