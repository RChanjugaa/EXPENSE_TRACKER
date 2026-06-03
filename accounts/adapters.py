from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.utils import timezone

try:
    from allauth.core.exceptions import ImmediateHttpResponse
except ImportError:  # pragma: no cover - older allauth compatibility
    from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .models import EmailVerification
from .validators import validate_gmail_address


class GoogleGmailOnlySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = (sociallogin.user.email or '').lower()
        try:
            validate_gmail_address(email)
        except Exception:
            messages.error(request, 'Use a Google account with a Gmail address to continue.')
            raise ImmediateHttpResponse(redirect('login'))

        existing_user = get_user_model().objects.filter(email__iexact=email).first()
        if existing_user and not sociallogin.is_existing:
            sociallogin.connect(request, existing_user)

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        user.email = user.email.lower()
        user.is_active = True
        if not user.username:
            user.username = self._unique_username(user.email.split('@', 1)[0])
        user.save(update_fields=['email', 'is_active', 'username'])
        verification, _ = EmailVerification.objects.get_or_create(user=user)
        if verification.verified_at is None:
            verification.verified_at = timezone.now()
            verification.save(update_fields=['verified_at'])
        return user

    def _unique_username(self, username_base):
        User = get_user_model()
        username = username_base
        counter = 1
        while User.objects.filter(username__iexact=username).exists():
            counter += 1
            username = f'{username_base}{counter}'
        return username
