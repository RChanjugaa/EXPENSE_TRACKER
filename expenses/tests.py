from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from groups.models import ExpenseGroup, GroupMembership
from payments.models import Payment

from .models import Expense, ExpenseCategory, ExpenseInvitation, ExpenseParticipant


class ExpenseCreationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', password='pass12345')
        self.member = User.objects.create_user(username='member', password='pass12345')
        self.group = ExpenseGroup.objects.create(name='Trip', created_by=self.admin)
        GroupMembership.objects.create(group=self.group, user=self.admin, role=GroupMembership.Role.ADMIN)
        GroupMembership.objects.create(group=self.group, user=self.member)
        self.category = ExpenseCategory.objects.create(name='Food')

    def test_expense_creation_splits_payment_for_non_payer(self):
        self.client.login(username='admin', password='pass12345')
        response = self.client.post(reverse('expense_create', args=[self.group.pk]), {
            'title': 'Dinner',
            'amount': '100.00',
            'paid_by': self.admin.pk,
            'category': self.category.pk,
            'expense_date': timezone.localdate(),
            'description': '',
            'participants': [self.admin.pk, self.member.pk],
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(ExpenseParticipant.objects.count(), 2)
        payment = Payment.objects.get()
        self.assertEqual(payment.payer, self.member)
        self.assertEqual(payment.receiver, self.admin)
        self.assertEqual(payment.amount, Decimal('50.00'))
        self.assertEqual(payment.status, Payment.Status.PENDING)


class ExpenseInvitationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.creator = User.objects.create_user(username='creator', email='creator@example.com', password='pass12345')
        self.invited = User.objects.create_user(username='invited', email='invited@example.com', password='pass12345')
        self.group = ExpenseGroup.objects.create(name='Trip', created_by=self.creator)
        GroupMembership.objects.create(group=self.group, user=self.creator, role=GroupMembership.Role.ADMIN)
        self.category = ExpenseCategory.objects.create(name='Travel')
        self.expense = Expense.objects.create(
            group=self.group,
            title='Taxi',
            amount=Decimal('90.00'),
            paid_by=self.creator,
            category=self.category,
            expense_date=timezone.localdate(),
            created_by=self.creator,
        )
        ExpenseParticipant.objects.create(expense=self.expense, user=self.creator, share_amount=Decimal('90.00'))

    def test_creator_can_email_invitation_and_acceptance_recalculates_split(self):
        self.client.login(username='creator', password='pass12345')
        response = self.client.post(reverse('invite_to_expense', args=[self.expense.pk]), {'email': 'invited@example.com'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

        invitation = ExpenseInvitation.objects.get()
        self.client.logout()
        self.client.login(username='invited', password='pass12345')
        response = self.client.get(reverse('accept_expense_invitation', args=[invitation.token]))

        self.assertEqual(response.status_code, 302)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, ExpenseInvitation.Status.ACCEPTED)
        self.assertTrue(GroupMembership.objects.filter(group=self.group, user=self.invited).exists())
        self.assertEqual(ExpenseParticipant.objects.get(expense=self.expense, user=self.creator).share_amount, Decimal('45.00'))
        self.assertEqual(Payment.objects.get(expense=self.expense, payer=self.invited).amount, Decimal('45.00'))

# Create your tests here.
