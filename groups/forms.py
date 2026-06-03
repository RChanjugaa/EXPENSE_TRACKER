from django import forms
from django.contrib.auth import get_user_model

from accounts.validators import validate_gmail_address

from .models import ExpenseGroup


class ExpenseGroupForm(forms.ModelForm):
    class Meta:
        model = ExpenseGroup
        fields = ['name', 'description']
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}


class AddMemberForm(forms.Form):
    user = forms.ModelChoiceField(queryset=get_user_model().objects.none())

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        users = get_user_model().objects.order_by('username')
        if group:
            users = users.exclude(expense_memberships__group=group)
        self.fields['user'].queryset = users


class GroupInvitationForm(forms.Form):
    email = forms.EmailField(label='Gmail address', help_text='The invitation link will be sent to this Gmail inbox.')

    def clean_email(self):
        return validate_gmail_address(self.cleaned_data['email'])
