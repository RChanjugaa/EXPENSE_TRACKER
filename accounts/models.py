from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string


def generate_verification_token():
    return get_random_string(48)


class EmailVerification(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_verification')
    token = models.CharField(max_length=64, unique=True, default=generate_verification_token)
    code = models.CharField(max_length=6, blank=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_verified(self):
        return self.verified_at is not None

    @property
    def is_code_valid(self):
        return self.verified_at is None and self.created_at >= timezone.now() - timezone.timedelta(minutes=10)

    def __str__(self):
        return f'Email verification for {self.user}'


class EmailLoginOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_login_otps')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_valid(self):
        return self.used_at is None and self.created_at >= timezone.now() - timezone.timedelta(minutes=10)

    def __str__(self):
        return f'OTP for {self.user}'

# Create your models here.
