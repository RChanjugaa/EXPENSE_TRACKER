from django.dispatch import receiver
from django.utils import timezone

try:
    from allauth.socialaccount.signals import social_account_added, social_account_updated
except Exception:  # pragma: no cover - allauth optional until installed
    social_account_added = None
    social_account_updated = None

from .models import EmailVerification


def mark_social_email_verified(user):
    if not user or not user.email:
        return
    verification, _ = EmailVerification.objects.get_or_create(user=user)
    if verification.verified_at is None:
        verification.verified_at = timezone.now()
        verification.save(update_fields=['verified_at'])


if social_account_added:
    @receiver(social_account_added)
    def social_account_added_handler(request, sociallogin, **kwargs):
        mark_social_email_verified(sociallogin.user)


if social_account_updated:
    @receiver(social_account_updated)
    def social_account_updated_handler(request, sociallogin, **kwargs):
        mark_social_email_verified(sociallogin.user)
