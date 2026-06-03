from django.conf import settings
from django.db import models


def payment_proof_path(instance, filename):
    return f'payment_proofs/payment_{instance.pk or "new"}/{filename}'


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        VERIFIED = 'verified', 'Verified'
        REJECTED = 'rejected', 'Rejected'

    expense = models.ForeignKey('expenses.Expense', on_delete=models.CASCADE, related_name='payments')
    payer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments_to_make')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments_to_receive')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    proof_file = models.FileField(upload_to=payment_proof_path, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-expense__expense_date', '-id']
        unique_together = ('expense', 'payer', 'receiver')

    def __str__(self):
        return f'{self.payer} pays {self.receiver} {self.amount}'

# Create your models here.
