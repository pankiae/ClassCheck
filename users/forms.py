from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Invitation

class InviteTeacherForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ['email']

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email']
