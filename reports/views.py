import calendar

from django.contrib.auth.decorators import login_required
from django.db.models import Case, DecimalField, Q, Sum, When
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
    month = max(1, min(12, month))

    expenses = Expense.objects.filter(
        group__memberships__user=request.user,
        expense_date__year=year,
        expense_date__month=month,
    ).select_related('group', 'category').distinct()

    by_category = list(expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total'))
    by_group = list(expenses.values('group__name').annotate(total=Sum('amount')).order_by('-total'))

    grand_total = expenses.aggregate(total=Sum('amount'))['total'] or 0

    # Add percentage for bar chart rendering
    for row in by_category:
        row['pct'] = int(row['total'] / grand_total * 100) if grand_total else 0
    for row in by_group:
        row['pct'] = int(row['total'] / grand_total * 100) if grand_total else 0

    payments = Payment.objects.filter(
        expense__group__memberships__user=request.user,
        expense__expense_date__year=year,
        expense__expense_date__month=month,
    ).distinct()

    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    return render(request, 'reports/monthly_report.html', {
        'year': year,
        'month': month,
        'months': months,
        'month_name': calendar.month_name[month],
        'total': grand_total,
        'by_category': by_category,
        'by_group': by_group,
        'pending_total': payments.filter(status__in=[Payment.Status.PENDING, Payment.Status.REJECTED]).aggregate(total=Sum('amount'))['total'] or 0,
        'verified_total': payments.filter(status=Payment.Status.VERIFIED).aggregate(total=Sum('amount'))['total'] or 0,
    })


@login_required
def group_summary(request):
    # Single query using conditional aggregation — no N+1
    groups = (
        ExpenseGroup.objects.filter(memberships__user=request.user)
        .distinct()
        .annotate(
            total_expenses=Sum('expenses__amount'),
            pending_total=Sum(
                Case(
                    When(expenses__payments__status__in=[Payment.Status.PENDING, Payment.Status.REJECTED], then='expenses__payments__amount'),
                    default=None,
                    output_field=DecimalField(),
                )
            ),
            verified_total=Sum(
                Case(
                    When(expenses__payments__status=Payment.Status.VERIFIED, then='expenses__payments__amount'),
                    default=None,
                    output_field=DecimalField(),
                )
            ),
        )
    )
    rows = [
        {
            'group': g,
            'total': g.total_expenses or 0,
            'pending': g.pending_total or 0,
            'verified': g.verified_total or 0,
        }
        for g in groups
    ]
    return render(request, 'reports/group_summary.html', {'rows': rows})

# Create your views here.
