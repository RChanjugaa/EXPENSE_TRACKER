from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django.core.exceptions import ValidationError

from .validators import validate_gmail_address


class RegistrationForm(forms.Form):
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Thamizh', 'autocomplete': 'given-name'}),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Mozhi', 'autocomplete': 'family-name'}),
    )
    email = forms.EmailField(
        label='Gmail address',
        widget=forms.EmailInput(attrs={'placeholder': 'name@gmail.com', 'autocomplete': 'email'}),
    )
    password1 = forms.CharField(
        label='Password',
        min_length=8,
        help_text='Password must be at least 8 characters long.',
        widget=forms.PasswordInput(attrs={'placeholder': 'Create a strong password', 'autocomplete': 'new-password'}),
    )

    def clean_email(self):
        email = validate_gmail_address(self.cleaned_data['email'])
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        User = get_user_model()
        email = self.cleaned_data['email']
        username_base = email.split('@', 1)[0]
        username = username_base
        counter = 1
        while User.objects.filter(username__iexact=username).exists():
            counter += 1
            username = f'{username_base}{counter}'
        user = User(
            username=username,
            email=email,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class ResendVerificationForm(forms.Form):
    email = forms.EmailField(label='Gmail address')

    def clean_email(self):
        return validate_gmail_address(self.cleaned_data['email'])


class RequestOTPForm(forms.Form):
    email = forms.EmailField(label='Gmail address')

    def clean_email(self):
        return validate_gmail_address(self.cleaned_data['email'])


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='Gmail address',
        widget=forms.EmailInput(attrs={'placeholder': 'name@gmail.com', 'autocomplete': 'email'}),
    )

    def clean_email(self):
        return validate_gmail_address(self.cleaned_data['email'])


class ResetPasswordForm(forms.Form):
    code = forms.CharField(
        label='6-digit reset code',
        min_length=6,
        max_length=6,
        widget=forms.TextInput(attrs={'inputmode': 'numeric', 'autocomplete': 'one-time-code'}),
    )
    new_password = forms.CharField(
        label='New password',
        min_length=8,
        help_text='Password must be at least 8 characters long.',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your new password', 'autocomplete': 'new-password'}),
    )
    confirm_password = forms.CharField(
        label='Confirm new password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter the new password', 'autocomplete': 'new-password'}),
    )

    def clean(self):
        cleaned = super().clean()
        new = cleaned.get('new_password')
        confirm = cleaned.get('confirm_password')
        if new and confirm and new != confirm:
            raise forms.ValidationError("Passwords don't match.")
        return cleaned


class VerifyOTPForm(forms.Form):
    code = forms.CharField(
        label='One-time password',
        min_length=6,
        max_length=6,
        widget=forms.TextInput(attrs={'inputmode': 'numeric', 'autocomplete': 'one-time-code'}),
    )


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        label='Email address',
        widget=forms.TextInput(attrs={'placeholder': 'name@gmail.com', 'autocomplete': 'username'}),
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'autocomplete': 'current-password'}),
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and '@' in username:
            user = get_user_model().objects.filter(email__iexact=username).first()
            if user:
                self.cleaned_data['username'] = user.get_username()
                username = user.get_username()
        if username is not None and password:
            inactive_user = get_user_model().objects.filter(username__iexact=username, is_active=False).first()
            if inactive_user and inactive_user.check_password(password):
                raise ValidationError(
                    'This Gmail account is not verified yet. Use "Resend verification code" to activate it.',
                    code='inactive',
                )
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data
