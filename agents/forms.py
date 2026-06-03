from django import forms

from groups.models import ExpenseGroup


class GroupScopedForm(forms.Form):
    group = forms.ModelChoiceField(queryset=ExpenseGroup.objects.none())

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['group'].queryset = ExpenseGroup.objects.filter(memberships__user=user).distinct()


class ExpenseAssistantForm(GroupScopedForm):
    prompt = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        help_text='Example: I paid 4500 for dinner with amal and sara',
    )
    create_expense = forms.BooleanField(required=False, initial=False, label='Create this expense immediately')


class SettlementAgentForm(GroupScopedForm):
    send_reminders = forms.BooleanField(required=False, initial=False, label='Email reminders for pending payments')
