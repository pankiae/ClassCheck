from django import forms
from user.models import Invitation

class InviteStudentForm(forms.Form):
    emails = forms.CharField(widget=forms.HiddenInput(), required=False)
