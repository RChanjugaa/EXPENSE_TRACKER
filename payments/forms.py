from pathlib import Path

from django import forms

from .models import Payment


class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['proof_file']

    def clean_proof_file(self):
        proof_file = self.cleaned_data['proof_file']
        extension = Path(proof_file.name).suffix.lower()
        if extension not in {'.jpg', '.jpeg', '.png', '.pdf'}:
            raise forms.ValidationError('Upload a JPG, PNG, or PDF proof file.')
        if proof_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('File is too large. Maximum size is 5 MB.')
        return proof_file


class PaymentRejectForm(forms.Form):
    rejection_reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=True)
