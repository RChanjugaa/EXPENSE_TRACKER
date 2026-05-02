from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class ResendVerificationForm(forms.Form):
    email = forms.EmailField()


class RequestOTPForm(forms.Form):
    email = forms.EmailField(label='Email address')


class VerifyOTPForm(forms.Form):
    code = forms.CharField(
        label='One-time password',
        min_length=6,
        max_length=6,
        widget=forms.TextInput(attrs={'inputmode': 'numeric', 'autocomplete': 'one-time-code'}),
    )


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Email or username')

    def clean(self):
        username = self.cleaned_data.get('username')
        if username and '@' in username:
            user = get_user_model().objects.filter(email__iexact=username).first()
            if user:
                self.cleaned_data['username'] = user.get_username()
        return super().clean()
