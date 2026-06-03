from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.crypto import get_random_string

from expenses.models import Expense
from groups.models import ExpenseGroup
from payments.models import Payment

from .emailing import email_delivery_context, is_console_email_backend, send_expense_tracker_mail
from .forms import RegistrationForm, RequestOTPForm, ResendVerificationForm, VerifyOTPForm
from .models import EmailLoginOTP, EmailVerification


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


def send_verification_email(user):
    verification, _ = EmailVerification.objects.get_or_create(user=user)
    verification.code = get_random_string(6, allowed_chars='0123456789')
    verification.created_at = timezone.now()
    verification.save(update_fields=['code', 'created_at'])
    send_expense_tracker_mail(
        subject='Your Expense Tracker verification code',
        message=(
            f'Hi {user.username},\n\n'
            f'Your Expense Tracker verification code is: {verification.code}\n\n'
            'This code expires in 10 minutes. After verification, you can join groups and accept invitations.'
        ),
        recipient_list=[user.email],
    )
    return verification


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.is_active = False
            user.save()
            try:
                verification = send_verification_email(user)
            except Exception as exc:
                user.delete()
                form.add_error(None, f'We could not send the verification code. Check email settings and try again. ({exc})')
            else:
                request.session['verify_user_id'] = user.pk
                if is_console_email_backend():
                    request.session['dev_registration_code'] = verification.code
                messages.success(request, f'We sent a 6-digit verification code to {user.email}.')
                return redirect('verify_registration_otp')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def verify_email(request, token):
    verification = get_object_or_404(EmailVerification.objects.select_related('user'), token=token)
    verification.verified_at = timezone.now()
    verification.save(update_fields=['verified_at'])
    verification.user.is_active = True
    verification.user.save(update_fields=['is_active'])
    messages.success(request, 'Email verified. You can log in now.')
    return redirect('login')


def verify_registration_otp(request):
    user_id = request.session.get('verify_user_id')
    if not user_id:
        messages.error(request, 'Register first to receive a verification code.')
        return redirect('register')
    user = get_object_or_404(get_user_model(), pk=user_id, is_active=False)
    form = VerifyOTPForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        verification = get_object_or_404(EmailVerification, user=user)
        if verification.code == form.cleaned_data['code'] and verification.is_code_valid:
            verification.verified_at = timezone.now()
            verification.save(update_fields=['verified_at'])
            user.is_active = True
            user.save(update_fields=['is_active'])
            request.session.pop('verify_user_id', None)
            request.session.pop('dev_registration_code', None)
            messages.success(request, 'Email verified. You can log in now.')
            return redirect('login')
        form.add_error('code', 'Invalid or expired verification code.')
    context = {'form': form, 'email': user.email, **email_delivery_context()}
    context['dev_code'] = request.session.get('dev_registration_code', '')
    return render(request, 'accounts/verify_registration_otp.html', context)


def resend_verification(request):
    form = ResendVerificationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = get_user_model().objects.filter(email__iexact=form.cleaned_data['email'], is_active=False).first()
        if user:
            try:
                verification = send_verification_email(user)
            except Exception as exc:
                form.add_error(None, f'We could not send the verification code. Check email settings and try again. ({exc})')
            else:
                request.session['verify_user_id'] = user.pk
                if is_console_email_backend():
                    request.session['dev_registration_code'] = verification.code
                messages.success(request, f'We sent a new verification code to {user.email}.')
                return redirect('verify_registration_otp')
        else:
            form.add_error('email', 'No inactive account was found for this email. Register first or log in if already verified.')
    return render(request, 'accounts/resend_verification.html', {'form': form, **email_delivery_context()})


def request_login_otp(request):
    form = RequestOTPForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email'].lower()
        user = get_user_model().objects.filter(email__iexact=email, is_active=True).first()
        if user:
            code = get_random_string(6, allowed_chars='0123456789')
            try:
                send_expense_tracker_mail(
                    subject='Your Expense Tracker login code',
                    message=(
                        f'Hi {user.username},\n\n'
                        f'Your Expense Tracker login code is: {code}\n\n'
                        'This code expires in 10 minutes.'
                    ),
                    recipient_list=[user.email],
                )
            except Exception as exc:
                form.add_error(None, f'We could not send the login code. Check email settings and try again. ({exc})')
            else:
                EmailLoginOTP.objects.create(user=user, code=code)
                request.session['otp_user_id'] = user.pk
                if is_console_email_backend():
                    request.session['dev_login_code'] = code
                messages.success(request, f'We sent a 6-digit login code to {user.email}.')
                return redirect('verify_login_otp')
        else:
            form.add_error('email', 'No verified account was found for this email. Register first or verify your account.')
    return render(request, 'accounts/request_login_otp.html', {'form': form, **email_delivery_context()})


def verify_login_otp(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        messages.error(request, 'Request a login code first.')
        return redirect('request_login_otp')
    user = get_object_or_404(get_user_model(), pk=user_id, is_active=True)
    form = VerifyOTPForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        otp = EmailLoginOTP.objects.filter(user=user, code=form.cleaned_data['code']).first()
        if otp and otp.is_valid:
            otp.used_at = timezone.now()
            otp.save(update_fields=['used_at'])
            request.session.pop('otp_user_id', None)
            request.session.pop('dev_login_code', None)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('dashboard')
        form.add_error('code', 'Invalid or expired code.')
    context = {'form': form, 'email': user.email, **email_delivery_context()}
    context['dev_code'] = request.session.get('dev_login_code', '')
    return render(request, 'accounts/verify_login_otp.html', context)


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
    raw_categories = list(
        Expense.objects.filter(group__memberships__user=request.user)
        .values('category__name')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')[:5]
    )
    max_cat = raw_categories[0]['total'] if raw_categories else 1
    for cat in raw_categories:
        cat['pct'] = int(cat['total'] / max_cat * 100)
    return render(request, 'accounts/dashboard.html', {
        'groups': groups,
        'payments_due': payments_due[:5],
        'payments_to_verify': payments_to_verify[:5],
        'recent_expenses': recent_expenses,
        'stats': stats,
        'categories': raw_categories,
    })
