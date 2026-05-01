from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from notifications.models import Notification
from notifications.utils import create_notification

from .forms import PaymentProofForm, PaymentRejectForm
from .models import Payment


def visible_payments(user):
    return Payment.objects.filter(Q(payer=user) | Q(receiver=user)).select_related('expense', 'payer', 'receiver', 'expense__group')


@login_required
def payment_history(request):
    payments = visible_payments(request.user)
    status = request.GET.get('status')
    group_id = request.GET.get('group')
    if status:
        payments = payments.filter(status=status)
    if group_id:
        payments = payments.filter(expense__group_id=group_id)
    groups = request.user.expense_memberships.select_related('group')
    return render(request, 'payments/payment_history.html', {
        'payments': payments,
        'groups': [membership.group for membership in groups],
        'status_choices': Payment.Status.choices,
    })


@login_required
def upload_proof(request, pk):
    payment = get_object_or_404(Payment, pk=pk, payer=request.user)
    form = PaymentProofForm(request.POST or None, request.FILES or None, instance=payment)
    if request.method == 'POST' and form.is_valid():
        payment = form.save(commit=False)
        payment.status = Payment.Status.PAID
        payment.paid_at = timezone.now()
        payment.rejection_reason = ''
        payment.save()
        create_notification(payment.receiver, f'{payment.payer.username} uploaded proof for "{payment.expense.title}".', Notification.Type.PAYMENT, payment)
        messages.success(request, 'Proof uploaded. Waiting for receiver verification.')
        return redirect('payment_history')
    return render(request, 'payments/upload_proof.html', {'form': form, 'payment': payment})


@login_required
def verify_payment(request, pk):
    payment = get_object_or_404(Payment, pk=pk, receiver=request.user)
    reject_form = PaymentRejectForm()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            payment.status = Payment.Status.VERIFIED
            payment.verified_at = timezone.now()
            payment.rejection_reason = ''
            payment.save()
            create_notification(payment.payer, f'Your payment for "{payment.expense.title}" was verified.', Notification.Type.PAYMENT, payment)
            messages.success(request, 'Payment verified.')
            return redirect('payment_history')
        if action == 'reject':
            reject_form = PaymentRejectForm(request.POST)
            if reject_form.is_valid():
                payment.status = Payment.Status.REJECTED
                payment.rejection_reason = reject_form.cleaned_data['rejection_reason']
                payment.save()
                create_notification(payment.payer, f'Your payment proof for "{payment.expense.title}" was rejected.', Notification.Type.PAYMENT, payment)
                messages.success(request, 'Payment rejected with a reason.')
                return redirect('payment_history')
    return render(request, 'payments/verify_payment.html', {'payment': payment, 'reject_form': reject_form})

# Create your views here.
