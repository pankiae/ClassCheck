from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from .models import AcademicSession, Department, StudentClass, Subject


def is_admin(user):
    return user.is_authenticated and user.is_admin()


@user_passes_test(is_admin)
def manage_structure(request):
    sessions = AcademicSession.objects.all().order_by("-created_at")
    # If no session exists, we might want to prompt or show empty state.
    # The requirement says "present session will automatically create if any department is added".

    current_year = datetime.now().year
    next_year = current_year + 1
    default_session_name = f"{current_year}-{next_year}"

    context = {"sessions": sessions, "default_session_name": default_session_name}
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

        student_class = get_object_or_404(StudentClass, id=class_id)
        Subject.objects.create(name=subject_name, student_class=student_class)
        messages.success(
            request, f"Subject '{subject_name}' added to '{student_class.name}'."
        )

    return redirect("manage_structure")
