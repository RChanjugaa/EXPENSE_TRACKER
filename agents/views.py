from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ExpenseAssistantForm, SettlementAgentForm
from .services import (
    create_expense_from_draft,
    email_settlement_reminders,
    parse_expense_prompt,
    settlement_suggestions,
)


@login_required
def agent_dashboard(request):
    expense_form = ExpenseAssistantForm(user=request.user, prefix='expense')
    settlement_form = SettlementAgentForm(user=request.user, prefix='settlement')
    expense_draft = None
    settlements = None

    if request.method == 'POST' and request.POST.get('agent') == 'expense':
        expense_form = ExpenseAssistantForm(request.POST, user=request.user, prefix='expense')
        if expense_form.is_valid():
            group = expense_form.cleaned_data['group']
            expense_draft = parse_expense_prompt(expense_form.cleaned_data['prompt'], group, request.user)
            if expense_form.cleaned_data['create_expense']:
                expense = create_expense_from_draft(group, expense_draft, request.user)
                messages.success(request, f'Expense Assistant created "{expense.title}".')
                return redirect('expense_detail', pk=expense.pk)

    if request.method == 'POST' and request.POST.get('agent') == 'settlement':
        settlement_form = SettlementAgentForm(request.POST, user=request.user, prefix='settlement')
        if settlement_form.is_valid():
            group = settlement_form.cleaned_data['group']
            settlements = settlement_suggestions(group)
            if settlement_form.cleaned_data['send_reminders']:
                sent, failed = email_settlement_reminders(group, request.user)
                if failed:
                    messages.warning(request, f'Settlement Agent sent {sent} reminders and could not send {len(failed)}.')
                else:
                    messages.success(request, f'Settlement Agent sent {sent} email reminders.')

    return render(request, 'agents/dashboard.html', {
        'expense_form': expense_form,
        'settlement_form': settlement_form,
        'expense_draft': expense_draft,
        'settlements': settlements,
    })
