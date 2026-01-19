from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from teacher.models import AcademicSession, Department, StudentClass, Subject

User = get_user_model()


class AcademicStructureTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            "admin@example.com", "password", role=User.Role.ADMIN
        )
        self.client.force_login(self.admin)

    def test_hierarchy_creation(self):
        # 1. Add Department (Auto-creates Session)
        response = self.client.post(
            "/teacher/structure/department/add/", {"name": "Science"}
        )
        self.assertEqual(response.status_code, 302)

        session = AcademicSession.objects.last()
        self.assertIsNotNone(session)
        self.assertTrue(session.year_range.startswith("20"))  # e.g. 2024-2025

        dept = Department.objects.get(name="science")
        self.assertEqual(dept.session, session)

        # 2. Add Class
        response = self.client.post(
            "/teacher/structure/class/add/",
            {"name": "Class 10", "department_id": dept.id},
        )
        self.assertEqual(response.status_code, 302)

        # Class name is auto-generated based on department name
        cls = StudentClass.objects.get(name="science-1")
        self.assertEqual(cls.department, dept)

        # 3. Add Subject
        response = self.client.post(
            "/teacher/structure/subject/add/",
            {"name": "Physics", "class_id": cls.id, "teacher_email": "admin@example.com", "timing": "10:00"},
        )
        self.assertEqual(response.status_code, 302)

        subject = Subject.objects.get(name="physics")
        self.assertEqual(subject.student_class, cls)

        # 4. Verify View Renders
        response = self.client.get("/teacher/structure/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "science")
        self.assertContains(response, "science-1")
        self.assertContains(response, "physics")
