from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.validators import validate_gmail_address

from .models import Expense, ExpenseCategory


class ExpenseForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        help_text='Select everyone included in this expense, including the payer if they share the cost.',
    )

    class Meta:
        model = Expense
        fields = ['title', 'amount', 'paid_by', 'category', 'expense_date', 'description', 'participants']
        widgets = {
            'expense_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, group=None, **kwargs):
        super().__init__(*args, **kwargs)
        members = group.memberships.select_related('user') if group else []
        users = [membership.user for membership in members]
        self.fields['participants'].queryset = get_user_model().objects.filter(pk__in=[u.pk for u in users]) if users else get_user_model().objects.none()
        self.fields['paid_by'].queryset = self.fields['participants'].queryset
        self.fields['expense_date'].initial = timezone.localdate()
        self.fields['category'].queryset = ExpenseCategory.objects.order_by('name')


class ExpenseInvitationForm(forms.Form):
    email = forms.EmailField(label='Gmail address', help_text='The invitation link will be sent to this Gmail inbox.')

    def clean_email(self):
        return validate_gmail_address(self.cleaned_data['email'])


class AddExpenseParticipantForm(forms.Form):
    user = forms.ModelChoiceField(queryset=get_user_model().objects.none(), label='Group member')

    def __init__(self, *args, expense=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not expense:
            return
        current_participants = expense.participants.values_list('user_id', flat=True)
        self.fields['user'].queryset = (
            get_user_model().objects
            .filter(expense_memberships__group=expense.group)
            .exclude(pk__in=current_participants)
            .order_by('username')
        )
