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

from .decorators import admin_required
from .forms import InviteStudentForm, InviteTeacherForm, RegisterForm
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
            email_string = form.cleaned_data["emails"]
            emails = [e.strip() for e in email_string.split(",") if e.strip()]

            success_count = 0
            failures = []

            for email in emails:
                if "@" not in email:
                    failures.append({"email": email, "reason": "Invalid format"})
                    continue

                if Invitation.objects.filter(email=email).exists():
                    failures.append({"email": email, "reason": "Already invited"})
                    continue

                try:
                    invitation = Invitation(
                        email=email, token=uuid.uuid4(), role=User.Role.TEACHER
                    )

                    invite_link = request.build_absolute_uri(
                        f"/register/{invitation.token}/"
                    )
                    subject = "Invitation to join ClassCheck as a Teacher"
                    message = f"Hi,\n\nYou have been invited to join ClassCheck. Please click the link below to set your password and activate your account:\n\n{invite_link}\n\nThis link is valid for 72 hours.\n\nBest regards,\nClassCheck Team"

                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    invitation.save()
                    success_count += 1
                except Exception as e:
                    failures.append({"email": email, "reason": str(e)})

            context = {
                "title": "Teachers",
                "total_success": success_count,
                "failures": failures,
                "dashboard_url": "invite_teacher",  # Redirect back to same page logic or dashboard
            }
            return render(request, "user/invite_success.html", context)
    else:
        form = InviteTeacherForm()
    return render(request, "user/invite_teacher.html", {"form": form})


@admin_required
def invite_student(request):
    if request.method == "POST":
        form = InviteStudentForm(request.POST)
        if form.is_valid():
            email_string = form.cleaned_data["emails"]
            emails = [e.strip() for e in email_string.split(",") if e.strip()]

            success_count = 0
            failures = []

            for email in emails:
                if "@" not in email:
                    failures.append({"email": email, "reason": "Invalid format"})
                    continue

                if Invitation.objects.filter(email=email).exists():
                    failures.append({"email": email, "reason": "Already invited"})
                    continue

                try:
                    invitation = Invitation(
                        email=email, token=uuid.uuid4(), role=User.Role.STUDENT
                    )

                    invite_link = request.build_absolute_uri(
                        f"/register/{invitation.token}/"
                    )
                    subject = "Invitation to join ClassCheck as a Student"
                    message = f"Hi,\n\nYou have been invited to join ClassCheck as a Student. Please click the link below to set your password and activate your account:\n\n{invite_link}\n\nThis link is valid for 72 hours.\n\nBest regards,\nClassCheck Team"

                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                    invitation.save()
                    success_count += 1
                except Exception as e:
                    failures.append({"email": email, "reason": str(e)})

            context = {
                "title": "Students",
                "total_success": success_count,
                "failures": failures,
                "dashboard_url": "invite_student",
            }
            return render(request, "user/invite_success.html", context)
    else:
        form = InviteStudentForm()
    return render(request, "user/invite_student.html", {"form": form})


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

            # Assign pre-created subjects to the new teacher
            if user.is_teacher():
                from teacher.models import Subject

                Subject.objects.filter(
                    teacher_email=user.email, teacher__isnull=True
                ).update(teacher=user)

            # Handle Enrollment if class_id is present
            if invitation.class_id:
                try:
                    from teacher.models import Subject

                    subject = Subject.objects.get(id=invitation.class_id)
                    Enrollment.objects.create(student=user, subject=subject)
                except Subject.DoesNotExist:
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
    return render(request, "user/register.html", {"form": form})


@admin_required
def superuser_dashboard(request):
    teachers = User.objects.filter(role=User.Role.TEACHER)
    students = User.objects.filter(role=User.Role.STUDENT)

    from teacher.models import Subject

    classes = Subject.objects.all()
    return render(
        request,
        "user/dashboard.html",
        {"teachers": teachers, "students": students, "classes": classes},
    )


def landing_page(request):
    if request.user.is_authenticated:
        return redirect("role_based_redirect")
    return render(request, "user/landing.html")


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
