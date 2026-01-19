from django import forms
from .models import ClassProposal

class ClassProposalForm(forms.ModelForm):
    class Meta:
        model = ClassProposal
        fields = ['subject', 'timing', 'days']
        widgets = {
            'timing': forms.TimeInput(attrs={'type': 'time'}),
        }
