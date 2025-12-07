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

class TeacherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.TEACHER
        if commit:
            user.save()
        return user

class StudentSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        if commit:
            user.save()
        return user
