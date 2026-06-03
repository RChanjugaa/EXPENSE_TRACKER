from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import EmailLoginOTP, EmailVerification


class EmailVerificationTests(TestCase):
    def test_registration_sends_verification_code_and_activation_otp_enables_login(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@gmail.com',
            'password1': 'strong-pass-123',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('verify_registration_otp'))
        self.assertEqual(len(mail.outbox), 1)
        user = get_user_model().objects.get(username='newuser')
        self.assertFalse(user.is_active)

        verification = EmailVerification.objects.get(user=user)
        self.assertIn(verification.code, mail.outbox[0].body)
        response = self.client.post(reverse('verify_registration_otp'), {'code': verification.code})

        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_registration_requires_gmail_address(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Not',
            'last_name': 'Gmail',
            'email': 'notgmail@example.com',
            'password1': 'strong-pass-123',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Use a valid Gmail address')
        self.assertFalse(get_user_model().objects.filter(username='notgmail').exists())

    def test_verified_user_can_login_with_email(self):
        user = get_user_model().objects.create_user(
            username='verified',
            email='verified@gmail.com',
            password='strong-pass-123',
        )
        EmailVerification.objects.create(user=user, verified_at='2026-05-02T00:00:00Z')

        response = self.client.post(reverse('login'), {
            'username': 'verified@gmail.com',
            'password': 'strong-pass-123',
        })

        self.assertEqual(response.status_code, 302)

    def test_private_pages_redirect_anonymous_users_to_login(self):
        response = self.client.get(reverse('payment_history'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_verified_user_can_request_and_use_email_otp(self):
        user = get_user_model().objects.create_user(
            username='otpuser',
            email='otpuser@gmail.com',
            password='strong-pass-123',
        )
        EmailVerification.objects.create(user=user, verified_at='2026-05-02T00:00:00Z')

        response = self.client.post(reverse('request_login_otp'), {'email': 'otpuser@gmail.com'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('verify_login_otp'))
        self.assertEqual(len(mail.outbox), 1)
        otp = EmailLoginOTP.objects.get(user=user)
        self.assertIn(otp.code, mail.outbox[0].body)

        response = self.client.post(reverse('verify_login_otp'), {'code': otp.code})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('dashboard'))
        otp.refresh_from_db()
        self.assertIsNotNone(otp.used_at)
