from decimal import Decimal, ROUND_DOWN

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from groups.models import ExpenseGroup
from groups.models import GroupMembership
from notifications.models import Notification
from notifications.utils import create_notification
from payments.models import Payment

from .forms import AddExpenseParticipantForm, ExpenseForm, ExpenseInvitationForm
from .models import Expense, ExpenseCategory, ExpenseInvitation, ExpenseParticipant


def member_groups(user):
    return ExpenseGroup.objects.filter(memberships__user=user).distinct()


def split_amounts(total, users):
    base = (total / Decimal(len(users))).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    shares = [base for _ in users]
    remainder = total - sum(shares)
    shares[-1] += remainder
    return shares


def can_recalculate_expense(expense):
    return not expense.payments.exclude(status=Payment.Status.PENDING).exists()


def rebuild_equal_split(expense, users):
    if not users:
        return
    shares = split_amounts(expense.amount, users)
    expense.participants.all().delete()
    expense.payments.all().delete()
    for user, share in zip(users, shares):
        ExpenseParticipant.objects.create(expense=expense, user=user, share_amount=share)
        if user != expense.paid_by:
            Payment.objects.create(expense=expense, payer=user, receiver=expense.paid_by, amount=share)
        create_notification(user, f'Expense "{expense.title}" was updated in {expense.group.name}.', Notification.Type.EXPENSE, expense)


def can_manage_expense_members(expense, user):
    return expense.created_by == user or expense.group.is_admin(user)


@login_required
def expense_create(request, group_pk):
    group = get_object_or_404(member_groups(request.user), pk=group_pk)
    if not ExpenseCategory.objects.exists():
        ExpenseCategory.objects.bulk_create([
            ExpenseCategory(name=name)
            for name in ['Food', 'Rent', 'Travel', 'Utilities', 'Shopping', 'Events', 'Other']
        ])
    form = ExpenseForm(request.POST or None, group=group)
    if request.method == 'POST' and form.is_valid():
        participants = list(form.cleaned_data['participants'])
        if not participants:
            form.add_error('participants', 'Select at least one participant.')
        else:
            with transaction.atomic():
                expense = form.save(commit=False)
                expense.group = group
                expense.created_by = request.user
                expense.save()
                rebuild_equal_split(expense, participants)
                messages.success(request, 'Expense added and payments calculated.')
                return redirect('expense_detail', pk=expense.pk)
    return render(request, 'expenses/expense_form.html', {'form': form, 'group': group})


@login_required
def expense_detail(request, pk):
    expense = get_object_or_404(
        Expense.objects.select_related('group', 'paid_by', 'category').prefetch_related('participants__user', 'payments__payer'),
        pk=pk,
        group__memberships__user=request.user,
    )
    return render(request, 'expenses/expense_detail.html', {
        'expense': expense,
        'can_invite': can_manage_expense_members(expense, request.user) and can_recalculate_expense(expense),
    })


@login_required
def invite_to_expense(request, pk):
    expense = get_object_or_404(
        Expense.objects.select_related('group', 'created_by'),
        pk=pk,
        group__memberships__user=request.user,
    )
    if not can_manage_expense_members(expense, request.user):
        messages.error(request, 'Only the expense creator or group admin can invite members to this expense.')
        return redirect('expense_detail', pk=expense.pk)
    if not can_recalculate_expense(expense):
        messages.error(request, 'Members cannot be added after a payment has been marked paid, verified, or rejected.')
        return redirect('expense_detail', pk=expense.pk)

    form = ExpenseInvitationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email'].lower()
        invitation, created = ExpenseInvitation.objects.get_or_create(
            expense=expense,
            email=email,
            status=ExpenseInvitation.Status.PENDING,
            defaults={'invited_by': request.user},
        )
        if not created:
            messages.info(request, f'A pending invitation already exists for {email}. Sending the link again.')
        accept_url = request.build_absolute_uri(reverse('accept_expense_invitation', args=[invitation.token]))
        send_mail(
            subject=f'Invitation to join expense: {expense.title}',
            message=(
                f'{request.user.username} invited you to join the expense "{expense.title}" '
                f'in the group "{expense.group.name}".\n\n'
                f'Open this link to accept the invitation:\n{accept_url}\n\n'
                'If you do not have an account yet, register with this email and verify it before accepting.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        messages.success(request, f'Invitation sent to {email}.')
        return redirect('expense_detail', pk=expense.pk)
    return render(request, 'expenses/invite_to_expense.html', {'expense': expense, 'form': form})


@login_required
def add_expense_participant(request, pk):
    expense = get_object_or_404(
        Expense.objects.select_related('group', 'created_by'),
        pk=pk,
        group__memberships__user=request.user,
    )
    if not can_manage_expense_members(expense, request.user):
        messages.error(request, 'Only the expense creator or group admin can add members to this expense.')
        return redirect('expense_detail', pk=expense.pk)
    if not can_recalculate_expense(expense):
        messages.error(request, 'Members cannot be added after a payment has been marked paid, verified, or rejected.')
        return redirect('expense_detail', pk=expense.pk)

    form = AddExpenseParticipantForm(request.POST or None, expense=expense)
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data['user']
        participant_users = [participant.user for participant in expense.participants.select_related('user')]
        participant_users.append(user)
        with transaction.atomic():
            rebuild_equal_split(expense, participant_users)
        messages.success(request, f'{user.username} was added to this expense and shares were recalculated.')
        return redirect('expense_detail', pk=expense.pk)
    return render(request, 'expenses/add_expense_participant.html', {'expense': expense, 'form': form})


@login_required
def accept_expense_invitation(request, token):
    invitation = get_object_or_404(
        ExpenseInvitation.objects.select_related('expense', 'expense__group'),
        token=token,
        status=ExpenseInvitation.Status.PENDING,
    )
    expense = invitation.expense
    if not request.user.email or invitation.email.lower() != request.user.email.lower():
        messages.error(request, 'Log in with the same email address that received this invitation.')
        return redirect('dashboard')
    if not request.user.is_active:
        messages.error(request, 'Verify your email before accepting invitations.')
        return redirect('dashboard')
    if not can_recalculate_expense(expense):
        messages.error(request, 'This expense can no longer accept new members because payment activity has already started.')
        return redirect('dashboard')

    with transaction.atomic():
        GroupMembership.objects.get_or_create(group=expense.group, user=request.user)
        participant_users = [participant.user for participant in expense.participants.select_related('user')]
        if request.user not in participant_users:
            participant_users.append(request.user)
        rebuild_equal_split(expense, participant_users)
        invitation.status = ExpenseInvitation.Status.ACCEPTED
        invitation.accepted_by = request.user
        invitation.accepted_at = timezone.now()
        invitation.save()
        create_notification(expense.created_by, f'{request.user.username} accepted the invitation to "{expense.title}".', Notification.Type.EXPENSE, expense)
    messages.success(request, f'You joined "{expense.title}".')
    return redirect('expense_detail', pk=expense.pk)

# Create your views here.
