from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from expenses.models import Expense
from groups.models import ExpenseGroup
from payments.models import Payment


@login_required
def monthly_report(request):
    today = timezone.localdate()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    expenses = Expense.objects.filter(
        group__memberships__user=request.user,
        expense_date__year=year,
        expense_date__month=month,
    ).select_related('group', 'category').distinct()
    by_category = expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total')
    by_group = expenses.values('group__name').annotate(total=Sum('amount')).order_by('-total')
    payments = Payment.objects.filter(
        expense__group__memberships__user=request.user,
        expense__expense_date__year=year,
        expense__expense_date__month=month,
    ).distinct()
    return render(request, 'reports/monthly_report.html', {
        'year': year,
        'month': month,
        'total': expenses.aggregate(total=Sum('amount'))['total'] or 0,
        'by_category': by_category,
        'by_group': by_group,
        'pending_total': payments.filter(status__in=[Payment.Status.PENDING, Payment.Status.REJECTED]).aggregate(total=Sum('amount'))['total'] or 0,
        'verified_total': payments.filter(status=Payment.Status.VERIFIED).aggregate(total=Sum('amount'))['total'] or 0,
    })


@login_required
def group_summary(request):
    groups = ExpenseGroup.objects.filter(memberships__user=request.user).distinct()
    rows = []
    for group in groups:
        expenses = group.expenses.all()
        payments = Payment.objects.filter(expense__group=group)
        rows.append({
            'group': group,
            'total': expenses.aggregate(total=Sum('amount'))['total'] or 0,
            'pending': payments.filter(status__in=[Payment.Status.PENDING, Payment.Status.REJECTED]).aggregate(total=Sum('amount'))['total'] or 0,
            'verified': payments.filter(status=Payment.Status.VERIFIED).aggregate(total=Sum('amount'))['total'] or 0,
        })
    return render(request, 'reports/group_summary.html', {'rows': rows})

# Create your views here.
