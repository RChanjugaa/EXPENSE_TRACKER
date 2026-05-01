from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from expenses.models import Expense, ExpenseCategory
from groups.models import ExpenseGroup, GroupMembership

from .models import Payment


class PaymentFlowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.payer = User.objects.create_user(username='payer', password='pass12345')
        self.receiver = User.objects.create_user(username='receiver', password='pass12345')
        group = ExpenseGroup.objects.create(name='Roommates', created_by=self.receiver)
        GroupMembership.objects.create(group=group, user=self.payer)
        GroupMembership.objects.create(group=group, user=self.receiver, role=GroupMembership.Role.ADMIN)
        category = ExpenseCategory.objects.create(name='Rent')
        expense = Expense.objects.create(
            group=group,
            title='Rent',
            amount=Decimal('200.00'),
            paid_by=self.receiver,
            category=category,
            expense_date=timezone.localdate(),
            created_by=self.receiver,
        )
        self.payment = Payment.objects.create(
            expense=expense,
            payer=self.payer,
            receiver=self.receiver,
            amount=Decimal('100.00'),
        )

    def test_payer_uploads_proof_and_receiver_verifies(self):
        self.client.login(username='payer', password='pass12345')
        proof = SimpleUploadedFile('receipt.pdf', BytesIO(b'%PDF-1.4 test').read(), content_type='application/pdf')
        response = self.client.post(reverse('upload_proof', args=[self.payment.pk]), {'proof_file': proof})
        self.assertEqual(response.status_code, 302)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.Status.PAID)

        self.client.logout()
        self.client.login(username='receiver', password='pass12345')
        response = self.client.post(reverse('verify_payment', args=[self.payment.pk]), {'action': 'approve'})
        self.assertEqual(response.status_code, 302)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.Status.VERIFIED)

# Create your tests here.
