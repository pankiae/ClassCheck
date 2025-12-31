from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from teacher.models import AcademicSession, Department, StudentClass, Subject

User = get_user_model()


class DashboardHierarchyTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            email="teacher@example.com", password="password", role=User.Role.TEACHER
        )
        self.client.force_login(self.teacher)

        # Setup Hierarchy
        self.session = AcademicSession.objects.create(year_range="2090-2091")
        self.dept = Department.objects.create(name="Science", session=self.session)
        self.cls1 = StudentClass.objects.create(name="science-1", department=self.dept)

        # Create Subjects
        self.subj1 = Subject.objects.create(
            name="Physics",
            student_class=self.cls1,
            teacher=self.teacher,
            days=["Mon"],
            timing="10:00",
        )
        self.subj2 = Subject.objects.create(
            name="Chemistry",
            student_class=self.cls1,
            teacher=self.teacher,
            days=["Tue"],
            timing="11:00",
        )

        # Create another class
        self.cls2 = StudentClass.objects.create(name="science-2", department=self.dept)
        self.subj3 = Subject.objects.create(
            name="Math",
            student_class=self.cls2,
            teacher=self.teacher,
            days=["Wed"],
            timing="09:00",
        )

    def test_dashboard_grouping(self):
        response = self.client.get("/teacher/dashboard/")
        self.assertEqual(response.status_code, 200)

        # Check Department Header appears (only once preferably, but assertContains checks existence)
        self.assertContains(response, "Science")

        # Check Class Headers
        self.assertContains(response, "Science-1")
        self.assertContains(response, "Science-2")

        # Check Subjects
        self.assertContains(response, "Physics")
        self.assertContains(response, "Chemistry")
        self.assertContains(response, "Math")

        # Check Context Ordering
        # View should return queryset ordered by dept name, class name, subject name.
        ordered_classes = list(response.context["classes"])
        # Expected order: Math (science-2) > Chemistry (science-1) > Physics (science-1) ?
        # No: Order is Dept Name -> Class Name -> Name
        # science-1 < science-2
        # Inside science-1: Chemistry < Physics
        # So: Chemistry, Physics, Math

        self.assertEqual(ordered_classes[0], self.subj2)  # Chemistry (science-1)
        self.assertEqual(ordered_classes[1], self.subj1)  # Physics (science-1)
        self.assertEqual(ordered_classes[2], self.subj3)  # Math (science-2)

    def test_dashboard_inactive_filtering(self):
        # 1. Inactive Subject
        inactive_subj = Subject.objects.create(
            name="Inactive Subject",
            student_class=self.cls1,
            teacher=self.teacher,
            days=["Mon"],
            timing="12:00",
            is_active=False,
        )

        # 2. Inactive Class
        inactive_class = StudentClass.objects.create(
            name="Inactive Class", department=self.dept, is_active=False
        )
        subj_in_inactive_class = Subject.objects.create(
            name="Subj in Inactive Class",
            student_class=inactive_class,
            teacher=self.teacher,
            days=["Mon"],
            timing="13:00",
        )

        # 3. Inactive Department
        inactive_dept = Department.objects.create(
            name="Inactive Dept", session=self.session, is_active=False
        )
        cls_in_inactive_dept = StudentClass.objects.create(
            name="Class inside Inactive Dept", department=inactive_dept
        )
        subj_in_inactive_dept = Subject.objects.create(
            name="Subj in Inactive Dept",
            student_class=cls_in_inactive_dept,
            teacher=self.teacher,
            days=["Mon"],
            timing="14:00",
        )

        # 4. Inactive Session
        inactive_session = AcademicSession.objects.create(
            year_range="1990-1991", is_active=False
        )
        dept_in_inactive_session = Department.objects.create(
            name="Dept in Inactive Session", session=inactive_session
        )
        cls_in_inactive_session = StudentClass.objects.create(
            name="Class in Inactive Session", department=dept_in_inactive_session
        )
        subj_in_inactive_session = Subject.objects.create(
            name="Subj in Inactive Session",
            student_class=cls_in_inactive_session,
            teacher=self.teacher,
            days=["Mon"],
            timing="15:00",
        )

        response = self.client.get("/teacher/dashboard/")
        self.assertEqual(response.status_code, 200)

        # Verify ONLY active stuff is there
        # We expect subj1, subj2, subj3 from setUp (they are active)
        # We expect NONE of the new ones

        content = response.content.decode()
        self.assertIn("Physics", content)
        self.assertIn("Chemistry", content)

        self.assertNotIn("Inactive Subject", content)
        self.assertNotIn("Subj in Inactive Class", content)
        self.assertNotIn("Subj in Inactive Dept", content)
        self.assertNotIn("Subj in Inactive Session", content)
