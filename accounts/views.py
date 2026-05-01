from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import redirect, render

from expenses.models import Expense
from groups.models import ExpenseGroup
from payments.models import Payment

from .forms import RegistrationForm


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    groups = ExpenseGroup.objects.filter(memberships__user=request.user).distinct()
    payments_due = Payment.objects.filter(payer=request.user).exclude(status=Payment.Status.VERIFIED)
    payments_to_verify = Payment.objects.filter(receiver=request.user, status=Payment.Status.PAID)
    recent_expenses = Expense.objects.filter(group__memberships__user=request.user).select_related('group', 'paid_by', 'category').distinct()[:5]
    stats = {
        'group_count': groups.count(),
        'pending_total': payments_due.filter(status__in=[Payment.Status.PENDING, Payment.Status.REJECTED]).aggregate(total=Sum('amount'))['total'] or 0,
        'verification_count': payments_to_verify.count(),
        'unread_notifications': request.user.notifications.filter(is_read=False).count(),
    }
    categories = (
        Expense.objects.filter(group__memberships__user=request.user)
        .values('category__name')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')[:5]
    )
    return render(request, 'accounts/dashboard.html', {
        'groups': groups,
        'payments_due': payments_due[:5],
        'payments_to_verify': payments_to_verify[:5],
        'recent_expenses': recent_expenses,
        'stats': stats,
        'categories': categories,
    })

# Create your views here.
