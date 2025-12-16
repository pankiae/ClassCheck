import os
import uuid

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "classcheck.settings")
django.setup()

from django.contrib.auth import get_user_model

from teacher.models import AcademicSession, Department, StudentClass, Subject

User = get_user_model()

# Create Superuser
email = "admin@test.com"
password = "password123"
try:
    user = User.objects.get(email=email)
    user.set_password(password)
    user.save()
    print(f"Updated user {email}")
except User.DoesNotExist:
    User.objects.create_superuser(
        email=email, password=password, first_name="Admin", last_name="Test"
    )
    print(f"Created user {email}")

# Create Structure Data
session, _ = AcademicSession.objects.get_or_create(
    year_range="2024-2025", defaults={"is_active": True}
)
dept, _ = Department.objects.get_or_create(name="Computer Science", session=session)
cls1, _ = StudentClass.objects.get_or_create(name="CS-A", department=dept)
cls2, _ = StudentClass.objects.get_or_create(name="CS-B", department=dept)
cls3, _ = StudentClass.objects.get_or_create(name="CS-C", department=dept)

# Add some subjects
Subject.objects.get_or_create(
    name="Python",
    student_class=cls1,
    defaults={
        "days": ["Mon", "Wed"],
        "timing": "10:00",
        "teacher_email": "t1@test.com",
    },
)
Subject.objects.get_or_create(
    name="Web Dev",
    student_class=cls1,
    defaults={"days": ["Tue"], "timing": "12:00", "teacher_email": "t2@test.com"},
)
Subject.objects.get_or_create(
    name="Data Structures",
    student_class=cls2,
    defaults={"days": ["Fri"], "timing": "09:00", "teacher_email": "t1@test.com"},
)

print("Test data setup complete.")
