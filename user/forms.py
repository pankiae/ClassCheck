from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Invitation, User


class InviteTeacherForm(forms.Form):
    emails = forms.CharField(widget=forms.HiddenInput(), required=False)


class InviteStudentForm(forms.Form):
    emails = forms.CharField(widget=forms.HiddenInput(), required=False)


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email"]


