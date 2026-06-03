from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from accounts.emailing import EmailDeliveryError, send_expense_tracker_mail
from notifications.models import Notification
from notifications.utils import create_notification

from .forms import AddMemberForm, ExpenseGroupForm, GroupInvitationForm
from .models import ExpenseGroup, GroupInvitation, GroupMembership


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
    expenses = group.expenses.select_related('paid_by', 'category').prefetch_related('payments').order_by('-expense_date', '-created_at')[:25]
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


@login_required
def invite_member(request, pk):
    group = get_object_or_404(user_groups(request.user), pk=pk)
    if not group.is_admin(request.user):
        messages.error(request, 'Only group admins can invite members.')
        return redirect('group_detail', pk=group.pk)
    form = GroupInvitationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email'].lower()
        invitation = GroupInvitation.objects.filter(group=group, email=email, status=GroupInvitation.Status.PENDING).first()
        created = invitation is None
        if created:
            invitation = GroupInvitation(group=group, email=email, invited_by=request.user)
        if not created:
            messages.info(request, f'A pending invitation already exists for {email}. Sending the link again.')
        accept_url = request.build_absolute_uri(reverse('accept_group_invitation', args=[invitation.token]))
        try:
            send_expense_tracker_mail(
                subject=f'Invitation to join group: {group.name}',
                message=(
                    f'{request.user.username} invited you to join the expense group "{group.name}".\n\n'
                    f'Open this link to accept the invitation:\n{accept_url}\n\n'
                    'If you do not have an account yet, register with this email and verify it before accepting.'
                ),
                recipient_list=[email],
            )
        except EmailDeliveryError as exc:
            messages.error(request, f'Invitation was not sent. Check email settings and try again. ({exc})')
            return render(request, 'groups/invite_member.html', {'form': form, 'group': group})
        if created:
            invitation.save()
        messages.success(request, f'Invitation sent to {email}.')
        return redirect('group_detail', pk=group.pk)
    return render(request, 'groups/invite_member.html', {'form': form, 'group': group})


@login_required
def accept_group_invitation(request, token):
    invitation = get_object_or_404(
        GroupInvitation.objects.select_related('group'),
        token=token,
        status=GroupInvitation.Status.PENDING,
    )
    if not request.user.email or invitation.email.lower() != request.user.email.lower():
        messages.error(request, 'Log in with the same email address that received this invitation.')
        return redirect('dashboard')
    if not request.user.is_active:
        messages.error(request, 'Verify your email before accepting invitations.')
        return redirect('dashboard')
    GroupMembership.objects.get_or_create(group=invitation.group, user=request.user)
    invitation.status = GroupInvitation.Status.ACCEPTED
    invitation.accepted_by = request.user
    invitation.accepted_at = timezone.now()
    invitation.save()
    create_notification(request.user, f'You joined "{invitation.group.name}".', Notification.Type.GROUP, invitation.group)
    create_notification(invitation.invited_by, f'{request.user.username} accepted the invitation to "{invitation.group.name}".', Notification.Type.GROUP, invitation.group)
    messages.success(request, f'You joined "{invitation.group.name}".')
    return redirect('group_detail', pk=invitation.group.pk)

