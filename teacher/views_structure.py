import uuid
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

from user.models import Invitation

from .models import AcademicSession, Department, StudentClass, Subject


def is_admin(user):
    return user.is_authenticated and user.is_admin()


@user_passes_test(is_admin)
def manage_structure(request):
    sessions = AcademicSession.objects.prefetch_related(
        Prefetch(
            "departments",
            queryset=Department.objects.filter(is_dead=False).prefetch_related(
                Prefetch(
                    "classes",
                    queryset=StudentClass.objects.filter(
                        is_dead=False
                    ).prefetch_related(
                        Prefetch(
                            "subjects", queryset=Subject.objects.filter(is_dead=False)
                        )
                    ),
                )
            ),
        )
    ).order_by("-created_at")

    current_year = datetime.now().year
    next_year = current_year + 1
    default_session_name = f"{current_year}-{next_year}"

    days_of_week = [
        ("Mon", "Monday"),
        ("Tue", "Tuesday"),
        ("Wed", "Wednesday"),
        ("Thu", "Thursday"),
        ("Fri", "Friday"),
        ("Sat", "Saturday"),
        ("Sun", "Sunday"),
    ]

    context = {
        "sessions": sessions,
        "default_session_name": default_session_name,
        "days_of_week": days_of_week,
    }
    return render(request, "teacher/manage_structure.html", context)


@user_passes_test(is_admin)
def add_department(request):
    if request.method == "POST":
        dept_name = request.POST.get("name")
        session_id = request.POST.get("session_id")

        if not dept_name:
            messages.error(request, "Department name is required.")
            return redirect("manage_structure")

        session = None
        if session_id:
            try:
                session = AcademicSession.objects.get(id=session_id)
            except AcademicSession.DoesNotExist:
                pass

        if not session:
            # Auto-create session logic
            current_year = datetime.now().year
            next_year = current_year + 1
            session_name = f"{current_year}-{next_year}"
            session, created = AcademicSession.objects.get_or_create(
                year_range=session_name
            )
            if created:
                messages.info(request, f"Created new session: {session.year_range}")
                # Set as active if it's the first one or logic dictates; keeping simple for now.
                session.is_active = True
                session.save()

        if Department.objects.filter(name=dept_name, session=session).exists():
            messages.error(
                request, f"Department '{dept_name}' already exists in this session."
            )
        else:
            Department.objects.create(name=dept_name, session=session)
            messages.success(
                request,
                f"Department '{dept_name}' added to session '{session.year_range}'.",
            )

    return redirect("manage_structure")


@user_passes_test(is_admin)
def add_class(request):
    if request.method == "POST":
        class_name = request.POST.get("name")
        dept_id = request.POST.get("department_id")

        department = get_object_or_404(Department, id=dept_id)
        StudentClass.objects.create(name=class_name, department=department)
        messages.success(request, f"Class '{class_name}' added to '{department.name}'.")

    return redirect("manage_structure")


@user_passes_test(is_admin)
def add_subject(request):
    if request.method == "POST":
        subject_name = request.POST.get("name")
        class_id = request.POST.get("class_id")
        days_str = request.POST.get("days")
        days = days_str.split(",") if days_str else []
        timing = request.POST.get("timing")
        teacher_email = request.POST.get("teacher_email")

        if not teacher_email:
            messages.error(request, "Teacher email is required.")
            return redirect("manage_structure")

        # Conflict Detection
        conflicting_subjects = Subject.objects.filter(
            teacher_email=teacher_email, timing=timing, is_active=True, is_dead=False
        )

        for subj in conflicting_subjects:
            # Check for intersection in days
            # days is a list like ['Mon', 'Wed']
            if any(day in subj.days for day in days):
                messages.error(
                    request,
                    f"Conflict: Teacher is already assigned to '{subj.name}' ({subj.student_class.name}) at {timing} on overlapping days.",
                )
                return redirect("manage_structure")

        student_class = get_object_or_404(StudentClass, id=class_id)
        
        User = get_user_model()
        try:
            user = User.objects.get(email=teacher_email)
            # User exists, proceed directly
            subject = Subject.objects.create(
                name=subject_name,
                student_class=student_class,
                days=days,
                timing=timing,
                teacher_email=teacher_email,
                teacher=user
            )
            messages.success(
                request, f"Subject '{subject_name}' added to '{student_class.name}' and assigned to {user.email}."
            )
            
        except User.DoesNotExist:
            # User does not exist, try to invite
            token = uuid.uuid4()
            invite_link = request.build_absolute_uri(f"/register/{token}/")
            
            subject_email = "Invitation to join ClassCheck as a Teacher"
            message = f"Hi,\n\nYou have been invited to join ClassCheck as a Teacher for the subject '{subject_name}' in class '{student_class.name}'. Please click the link below to set your password and activate your account:\n\n{invite_link}\n\nThis link is valid for 72 hours.\n\nBest regards,\nClassCheck Team"

            try:
                send_mail(
                    subject_email,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [teacher_email],
                    fail_silently=False,
                )
                
                # Email sent successfully, now save data
                Invitation.objects.get_or_create(
                    email=teacher_email,
                    defaults={
                        "token": token,
                        "role": User.Role.TEACHER,
                    },
                )
                
                Subject.objects.create(
                    name=subject_name,
                    student_class=student_class,
                    days=days,
                    timing=timing,
                    teacher_email=teacher_email,
                )
                
                messages.success(
                    request, f"Subject '{subject_name}' added. Invitation sent to {teacher_email}."
                )
                
            except Exception as e:
                # Email failed, do not save anything
                messages.error(request, f"Error sending invitation email: {e}. Subject was NOT created.")
                return redirect("manage_structure")

    return redirect("manage_structure")


@user_passes_test(is_admin)
def delete_department(request, dept_id):
    dept = get_object_or_404(Department, id=dept_id)
    if "restore" in request.POST:
        dept.is_active = True
        dept.save()
        messages.success(request, f"Department '{dept.name}' restored.")
    elif "hard_delete" in request.POST:
        dept_name = dept.name
        dept.delete()
        messages.success(request, f"Department '{dept_name}' permanently deleted.")
    else:
        dept.is_active = False
        dept.save()
        # Cascading deactivation
        for student_class in dept.classes.all():
            student_class.is_active = False
            student_class.save()
            for subject in student_class.subjects.all():
                subject.is_active = False
                subject.save()
        messages.warning(
            request, f"Department '{dept.name}' and its contents deactivated."
        )
    return redirect("manage_structure")


@user_passes_test(is_admin)
def delete_class(request, class_id):
    student_class = get_object_or_404(StudentClass, id=class_id)
    if "restore" in request.POST:
        student_class.is_active = True
        student_class.save()
        messages.success(request, f"Class '{student_class.name}' restored.")
    elif "hard_delete" in request.POST:
        class_name = student_class.name
        student_class.delete()
        messages.success(request, f"Class '{class_name}' permanently deleted.")
    else:
        student_class.is_active = False
        student_class.save()
        # Cascading deactivation
        for subject in student_class.subjects.all():
            subject.is_active = False
            subject.save()
        messages.warning(
            request, f"Class '{student_class.name}' and its subjects deactivated."
        )
    return redirect("manage_structure")


@user_passes_test(is_admin)
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if "restore" in request.POST:
        subject.is_active = True
        subject.save()
        messages.success(request, f"Subject '{subject.name}' restored.")
    elif "hard_delete" in request.POST:
        subject_name = subject.name
        subject.delete()
        messages.success(request, f"Subject '{subject_name}' permanently deleted.")
    else:
        subject.is_active = False
        subject.save()
        messages.warning(request, f"Subject '{subject.name}' deactivated.")
    return redirect("manage_structure")
