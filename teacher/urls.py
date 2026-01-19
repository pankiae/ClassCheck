from django.urls import path

from . import views, views_structure

urlpatterns = [
    path("dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("class/<int:class_id>/invite/", views.invite_student, name="invite_student"),
    path(
        "class/<int:class_id>/attendance/",
        views.mark_attendance,
        name="mark_attendance",
    ),
    path("class/<int:class_id>/details/", views.class_details, name="class_details"),
    # Structure Management
    path("structure/", views_structure.manage_structure, name="manage_structure"),
    path(
        "structure/department/add/",
        views_structure.add_department,
        name="add_department",
    ),
    path("structure/class/add/", views_structure.add_class, name="add_class"),
    path("structure/subject/add/", views_structure.add_subject, name="add_subject"),
    # Delete Routes
    path(
        "structure/department/<int:dept_id>/delete/",
        views_structure.delete_department,
        name="delete_department",
    ),
    path(
        "structure/class/<int:class_id>/delete/",
        views_structure.delete_class,
        name="delete_class",
    ),
    path(
        "structure/subject/<int:subject_id>/delete/",
        views_structure.delete_subject,
        name="delete_subject",
    ),
]
