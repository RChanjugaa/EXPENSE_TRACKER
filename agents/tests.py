from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from expenses.models import Expense, ExpenseCategory, ExpenseParticipant
from groups.models import ExpenseGroup, GroupMembership
from payments.models import Payment


class AgentTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin', email='admin@gmail.com', password='pass12345')
        self.member = User.objects.create_user(username='amal', email='amal@gmail.com', password='pass12345')
        self.group = ExpenseGroup.objects.create(name='Trip', created_by=self.admin)
        GroupMembership.objects.create(group=self.group, user=self.admin, role=GroupMembership.Role.ADMIN)
        GroupMembership.objects.create(group=self.group, user=self.member)

    def test_expense_assistant_creates_expense_from_prompt(self):
        self.client.login(username='admin', password='pass12345')
        response = self.client.post(reverse('agent_dashboard'), {
            'agent': 'expense',
            'expense-group': self.group.pk,
            'expense-prompt': 'I paid 4500 for dinner with amal',
            'expense-create_expense': 'on',
        })

        self.assertEqual(response.status_code, 302)
        expense = Expense.objects.get(title='Dinner')
        self.assertEqual(expense.amount, Decimal('4500.00'))
        self.assertEqual(ExpenseParticipant.objects.filter(expense=expense).count(), 2)
        self.assertEqual(Payment.objects.get(expense=expense, payer=self.member).amount, Decimal('2250.00'))

    def test_settlement_agent_sends_pending_payment_reminder(self):
        category = ExpenseCategory.objects.create(name='Food')
        expense = Expense.objects.create(
            group=self.group,
            title='Snacks',
            amount=Decimal('100.00'),
            paid_by=self.admin,
            category=category,
            expense_date='2026-05-02',
            created_by=self.admin,
        )
        Payment.objects.create(expense=expense, payer=self.member, receiver=self.admin, amount=Decimal('50.00'))
        self.client.login(username='admin', password='pass12345')

        response = self.client.post(reverse('agent_dashboard'), {
            'agent': 'settlement',
            'settlement-group': self.group.pk,
            'settlement-send_reminders': 'on',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Payment reminder', mail.outbox[0].subject)

