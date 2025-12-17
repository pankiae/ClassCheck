from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Invitation, User


class InviteTeacherForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ["first_name", "last_name", "email"]


class InviteStudentForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ["first_name", "last_name", "email"]


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email"]


