from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from teacher.models import AcademicSession, Department, StudentClass, Subject

User = get_user_model()


class SoftDeleteTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            "admin@example.com", "password", role=User.Role.ADMIN
        )
        self.client.force_login(self.admin)

        # Setup Data
        self.session = AcademicSession.objects.create(year_range="2090-2091")
        self.dept = Department.objects.create(name="Dept 1", session=self.session)
        self.cls = StudentClass.objects.create(name="Class 1", department=self.dept)
        self.subj = Subject.objects.create(name="Subj 1", student_class=self.cls)

    def test_soft_delete_and_restore(self):
        # 1. Delete Department
        self.client.post(f"/teacher/structure/department/{self.dept.id}/delete/")
        self.dept.refresh_from_db()
        self.assertFalse(self.dept.is_active)
        self.assertFalse(self.dept.is_dead)  # Should be just inactive

        # 2. Restore Department
        self.client.post(
            f"/teacher/structure/department/{self.dept.id}/delete/", {"restore": "true"}
        )
        self.dept.refresh_from_db()
        self.assertTrue(self.dept.is_active)

        # 3. Delete Class
        self.client.post(f"/teacher/structure/class/{self.cls.id}/delete/")
        self.cls.refresh_from_db()
        self.assertFalse(self.cls.is_active)

        # 4. Delete Subject
        self.client.post(f"/teacher/structure/subject/{self.subj.id}/delete/")
        self.subj.refresh_from_db()
        self.assertFalse(self.subj.is_active)

    def test_visibility_logic(self):
        # Ensure dead items are not shown (we check this logic by ensuring view doesn't error,
        # actual filtering is in the Prefetch which we trust Django for, but let's simulate dead item)
        dead_subject = Subject.objects.create(
            name="Dead Subject", student_class=self.cls, is_dead=True
        )
        response = self.client.get("/teacher/structure/")
        self.assertContains(response, "Subj 1")
        self.assertNotContains(response, "Dead Subject")
