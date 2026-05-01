from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from notifications.models import Notification
from notifications.utils import create_notification

from .forms import AddMemberForm, ExpenseGroupForm
from .models import ExpenseGroup, GroupMembership


def user_groups(user):
    return ExpenseGroup.objects.filter(memberships__user=user).distinct()


@login_required
def group_list(request):
    return render(request, 'groups/group_list.html', {'groups': user_groups(request.user)})


@login_required
def group_create(request):
    if request.method == 'POST':
        form = ExpenseGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            GroupMembership.objects.create(group=group, user=request.user, role=GroupMembership.Role.ADMIN)
            create_notification(request.user, f'Group "{group.name}" was created.', Notification.Type.GROUP, group)
            messages.success(request, 'Group created.')
            return redirect('group_detail', pk=group.pk)
    else:
        form = ExpenseGroupForm()
    return render(request, 'groups/group_form.html', {'form': form, 'title': 'Create group'})


@login_required
def group_edit(request, pk):
    group = get_object_or_404(user_groups(request.user), pk=pk)
    if not group.is_admin(request.user):
        messages.error(request, 'Only group admins can edit this group.')
        return redirect('group_detail', pk=group.pk)
    form = ExpenseGroupForm(request.POST or None, instance=group)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Group updated.')
        return redirect('group_detail', pk=group.pk)
    return render(request, 'groups/group_form.html', {'form': form, 'title': 'Edit group'})


@login_required
def group_detail(request, pk):
    group = get_object_or_404(user_groups(request.user), pk=pk)
    expenses = group.expenses.select_related('paid_by', 'category').prefetch_related('payments')[:25]
    payments = []
    for expense in expenses:
        payments.extend(expense.payments.all())
    summary = {
        'total_expenses': sum(expense.amount for expense in expenses),
        'pending_total': sum(payment.amount for payment in payments if payment.status in ['pending', 'rejected']),
        'verified_total': sum(payment.amount for payment in payments if payment.status == 'verified'),
    }
    return render(request, 'groups/group_detail.html', {
        'group': group,
        'expenses': expenses,
        'summary': summary,
        'is_admin': group.is_admin(request.user),
    })


@login_required
def add_member(request, pk):
    group = get_object_or_404(user_groups(request.user), pk=pk)
    if not group.is_admin(request.user):
        messages.error(request, 'Only group admins can add members.')
        return redirect('group_detail', pk=group.pk)
    form = AddMemberForm(request.POST or None, group=group)
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data['user']
        GroupMembership.objects.create(group=group, user=user)
        create_notification(user, f'You were added to "{group.name}".', Notification.Type.GROUP, group)
        messages.success(request, f'{user.username} was added.')
        return redirect('group_detail', pk=group.pk)
    return render(request, 'groups/add_member.html', {'form': form, 'group': group})

# Create your views here.
