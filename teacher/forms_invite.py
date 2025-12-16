from django import forms
from users.models import Invitation

class InviteStudentForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['email']
