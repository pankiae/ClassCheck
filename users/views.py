import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from student.models import Enrollment
from teacher.models import Class

from .decorators import admin_required
from .forms import InviteStudentForm, InviteTeacherForm, RegisterForm, StudentSignUpForm, TeacherSignUpForm
from .models import Invitation, User


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("login")


@admin_required
def invite_teacher(request):
    if request.method == "POST":
        form = InviteTeacherForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.token = uuid.uuid4()
            invitation.role = User.Role.TEACHER
            # Remove early save

            invite_link = request.build_absolute_uri(f"/register/{invitation.token}/")

            # Send email
            subject = "Invitation to join ClassCheck as a Teacher"
            message = f"Hi {invitation.first_name},\n\nYou have been invited to join ClassCheck. Please click the link below to set your password and activate your account:\n\n{invite_link}\n\nThis link is valid for 72 hours.\n\nBest regards,\nClassCheck Team"

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [invitation.email],
                    fail_silently=False,
                )
                invitation.save()  # Save only after successful email
                messages.success(request, f"Invitation sent to {invitation.email}")
            except Exception as e:
                messages.error(request, f"Error sending email: {e}")

            return redirect("invite_teacher")
    else:
        form = InviteTeacherForm()
    return render(request, "users/invite_teacher.html", {"form": form})


@admin_required
def invite_student(request):
    if request.method == "POST":
        form = InviteStudentForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.token = uuid.uuid4()
            invitation.role = User.Role.STUDENT
            # Remove early save

            invite_link = request.build_absolute_uri(f"/register/{invitation.token}/")

            # Send email
            subject = "Invitation to join ClassCheck as a Student"
            message = f"Hi {invitation.first_name},\n\nYou have been invited to join ClassCheck as a Student. Please click the link below to set your password and activate your account:\n\n{invite_link}\n\nThis link is valid for 72 hours.\n\nBest regards,\nClassCheck Team"

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [invitation.email],
                    fail_silently=False,
                )
                invitation.save()  # Save only after successful email
                messages.success(request, f"Invitation sent to {invitation.email}")
            except Exception as e:
                messages.error(request, f"Error sending email: {e}")

            return redirect("invite_student")
    else:
        form = InviteStudentForm()
    return render(request, "users/invite_student.html", {"form": form})


def register(request, token):
    invitation = get_object_or_404(Invitation, token=token, is_used=False)

    if not invitation.is_valid():
        messages.error(request, "This invitation has expired or is invalid.")
        return redirect("landing")  # Or a specific error page

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = invitation.role
            user.email = invitation.email
            user.first_name = invitation.first_name
            user.last_name = invitation.last_name
            user.save()
            invitation.is_used = True
            invitation.save()

            # Handle Enrollment if class_id is present
            if invitation.class_id:
                try:
                    class_obj = Class.objects.get(id=invitation.class_id)
                    Enrollment.objects.create(student=user, class_obj=class_obj)
                except Class.DoesNotExist:
                    pass  # Should not happen ideally

            login(request, user)
            messages.success(
                request, f"Welcome {user.email}! You have successfully registered."
            )
            if user.is_teacher():
                return redirect("teacher_dashboard")
            elif user.is_student():
                return redirect("student_dashboard")
            elif user.is_admin():
                return redirect("superuser_dashboard")
            return redirect("dashboard")  # Fallback
    else:
        form = RegisterForm(initial={"email": invitation.email})
    return render(request, "users/register.html", {"form": form})


@admin_required
def superuser_dashboard(request):
    teachers = User.objects.filter(role=User.Role.TEACHER)
    students = User.objects.filter(role=User.Role.STUDENT)
    classes = Class.objects.all()
    return render(
        request,
        "users/dashboard.html",
        {"teachers": teachers, "students": students, "classes": classes},
    )


def landing_page(request):
    if request.user.is_authenticated:
        return redirect("role_based_redirect")
    return render(request, "users/landing.html")


class TeacherSignUpView(CreateView):
    model = User
    form_class = TeacherSignUpForm
    template_name = "users/register.html"

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "Teacher"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Teacher account created successfully!")
        return redirect("teacher_dashboard")


class StudentSignUpView(CreateView):
    model = User
    form_class = StudentSignUpForm
    template_name = "users/register.html"

    def get_context_data(self, **kwargs):
        kwargs["user_type"] = "Student"
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Student account created successfully!")
        return redirect("student_dashboard")


@login_required
def role_based_redirect(request):
    user = request.user
    if user.is_teacher():
        return redirect("teacher_dashboard")
    elif user.is_student():
        return redirect("student_dashboard")
    elif user.is_admin():
        return redirect("superuser_dashboard")
    return redirect("landing")
