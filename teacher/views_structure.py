from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render

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


@user_passes_test(is_admin)
def delete_department(request, dept_id):
    dept = get_object_or_404(Department, id=dept_id)
    if "restore" in request.POST:
        dept.is_active = True
        dept.save()
        messages.success(request, f"Department '{dept.name}' restored.")
    elif "dead" in request.POST:
        dept.is_dead = True
        dept.save()
        messages.success(request, f"Department '{dept.name}' marked as dead.")
    else:
        dept.is_active = False
        dept.save()
        messages.warning(request, f"Department '{dept.name}' deactivated.")
    return redirect("manage_structure")


@user_passes_test(is_admin)
def delete_class(request, class_id):
    student_class = get_object_or_404(StudentClass, id=class_id)
    if "restore" in request.POST:
        student_class.is_active = True
        student_class.save()
        messages.success(request, f"Class '{student_class.name}' restored.")
    elif "dead" in request.POST:
        student_class.is_dead = True
        student_class.save()
        messages.success(request, f"Class '{student_class.name}' marked as dead.")
    else:
        student_class.is_active = False
        student_class.save()
        messages.warning(request, f"Class '{student_class.name}' deactivated.")
    return redirect("manage_structure")


@user_passes_test(is_admin)
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    if "restore" in request.POST:
        subject.is_active = True
        subject.save()
        messages.success(request, f"Subject '{subject.name}' restored.")
    elif "dead" in request.POST:
        subject.is_dead = True
        subject.save()
        messages.success(request, f"Subject '{subject.name}' marked as dead.")
    else:
        subject.is_active = False
        subject.save()
        messages.warning(request, f"Subject '{subject.name}' deactivated.")
    return redirect("manage_structure")
