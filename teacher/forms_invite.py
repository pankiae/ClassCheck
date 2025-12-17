from django import forms
from users.models import Invitation

class InviteStudentForm(forms.Form):
    emails = forms.CharField(widget=forms.HiddenInput(), required=False)
