import re
from decimal import Decimal

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from expenses.models import Expense, ExpenseCategory
from expenses.views import rebuild_equal_split
from notifications.models import Notification
from notifications.utils import create_notification
from payments.models import Payment


CATEGORY_KEYWORDS = {
    'Food': ['food', 'dinner', 'lunch', 'breakfast', 'meal', 'restaurant', 'pizza'],
    'Rent': ['rent', 'house', 'room'],
    'Travel': ['taxi', 'uber', 'bus', 'train', 'flight', 'trip', 'travel'],
    'Utilities': ['electricity', 'water', 'wifi', 'internet', 'utility', 'utilities'],
    'Shopping': ['shopping', 'clothes', 'market'],
    'Events': ['event', 'party', 'ticket'],
}


def ensure_default_categories():
    for name in ['Food', 'Rent', 'Travel', 'Utilities', 'Shopping', 'Events', 'Other']:
        ExpenseCategory.objects.get_or_create(name=name)


def parse_expense_prompt(prompt, group, payer):
    ensure_default_categories()
    lowered = prompt.lower()
    amount_match = re.search(r'(\d+(?:\.\d{1,2})?)', prompt)
    amount = Decimal(amount_match.group(1)).quantize(Decimal('0.01')) if amount_match else None
    title_match = re.search(r'for\s+(.+?)(?:\s+with\s+|$)', prompt, flags=re.IGNORECASE)
    title = title_match.group(1).strip().title() if title_match else 'Shared Expense'
    category_name = 'Other'
    for candidate, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            category_name = candidate
            break
    category = ExpenseCategory.objects.get(name=category_name)
    members = [membership.user for membership in group.memberships.select_related('user')]
    participants = []
    for member in members:
        searchable = ' '.join(filter(None, [
            member.username,
            member.first_name,
            member.last_name,
            member.email.split('@')[0] if member.email else '',
        ])).lower()
        if any(part and part in lowered for part in searchable.split()):
            participants.append(member)
    if payer not in participants:
        participants.insert(0, payer)
    return {
        'title': title,
        'amount': amount,
        'category': category,
        'participants': participants,
        'payer': payer,
        'confidence': 'Ready' if amount and len(participants) > 1 else 'Needs review',
    }


def create_expense_from_draft(group, draft, created_by):
    if not draft['amount']:
        raise ValueError('The assistant could not find an amount in the prompt.')
    expense = Expense.objects.create(
        group=group,
        title=draft['title'],
        amount=draft['amount'],
        paid_by=draft['payer'],
        category=draft['category'],
        expense_date=timezone.localdate(),
        created_by=created_by,
        description='Created by Expense Assistant.',
    )
    rebuild_equal_split(expense, draft['participants'])
    return expense


def settlement_suggestions(group):
    payments = Payment.objects.filter(
        expense__group=group,
        status__in=[Payment.Status.PENDING, Payment.Status.REJECTED],
    ).select_related('expense', 'payer', 'receiver')
    return list(payments)


def email_settlement_reminders(group, sender):
    reminders = settlement_suggestions(group)
    sent = 0
    for payment in reminders:
        if not payment.payer.email:
            continue
        send_mail(
            subject=f'Payment reminder for {group.name}',
            message=(
                f'Hi {payment.payer.username},\n\n'
                f'You have a pending payment of {payment.amount} to {payment.receiver.username} '
                f'for "{payment.expense.title}".\n\n'
                'Please log in to upload proof after payment.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[payment.payer.email],
            fail_silently=False,
        )
        create_notification(
            payment.payer,
            f'Reminder: {payment.amount} is pending for "{payment.expense.title}".',
            Notification.Type.PAYMENT,
            payment,
        )
        sent += 1
    create_notification(sender, f'Settlement Agent sent {sent} reminders for {group.name}.', Notification.Type.PAYMENT, group)
    return sent
