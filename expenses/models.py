from django.conf import settings
from django.db import models
from django.utils.crypto import get_random_string


def generate_invitation_token():
    return get_random_string(48)


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'expense categories'

    def __str__(self):
        return self.name


class Expense(models.Model):
    group = models.ForeignKey('groups.ExpenseGroup', on_delete=models.CASCADE, related_name='expenses')
    title = models.CharField(max_length=160)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses_paid')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses')
    expense_date = models.DateField()
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses_created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-expense_date', '-created_at']

    def __str__(self):
        return self.title


class ExpenseParticipant(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expense_participations')
    share_amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('expense', 'user')
        ordering = ['user__username']

    def __str__(self):
        return f'{self.user} owes {self.share_amount} for {self.expense}'


class ExpenseInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        CANCELLED = 'cancelled', 'Cancelled'

    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expense_invitations_sent')
    token = models.CharField(max_length=64, unique=True, default=generate_invitation_token)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='expense_invitations_accepted',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('expense', 'email', 'status')

    def __str__(self):
        return f'{self.email} invited to {self.expense}'

# Create your models here.
