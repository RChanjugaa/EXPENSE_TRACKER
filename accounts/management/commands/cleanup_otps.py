from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import EmailLoginOTP


class Command(BaseCommand):
    help = 'Delete used and expired OTP records older than 24 hours.'

    def handle(self, *args, **options):
        cutoff = timezone.now() - timezone.timedelta(hours=24)
        deleted, _ = EmailLoginOTP.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted} stale OTP records.'))
