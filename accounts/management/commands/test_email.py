from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Send a test email using the configured Django email backend.'

    def add_arguments(self, parser):
        parser.add_argument('recipient', nargs='?', default=None)

    def handle(self, *args, **options):
        recipient = options['recipient'] or settings.EMAIL_HOST_USER
        if not recipient:
            raise CommandError('No recipient provided and EMAIL_HOST_USER is empty.')

        self.stdout.write(f'Email backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'Email host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}')
        self.stdout.write(f'Email user: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'Sending test email to: {recipient}')

        try:
            sent = send_mail(
                subject='Expense Tracker email test',
                message='If you received this message, Expense Tracker email sending is working.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
        except Exception as exc:
            raise CommandError(f'Email test failed: {exc}') from exc

        if sent:
            self.stdout.write(self.style.SUCCESS('Email test sent successfully. Check the inbox and spam folder.'))
        else:
            raise CommandError('Django did not send the email, but no exception was raised.')
