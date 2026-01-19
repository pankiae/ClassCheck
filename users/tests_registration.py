import uuid

from django.test import Client, TestCase
from django.urls import reverse

from teacher.models import AcademicSession, Department, StudentClass, Subject
from users.models import Invitation, User


class TeacherRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = "newteacher@example.com"

        # Setup Hierarchy for Subject
        self.session = AcademicSession.objects.create(year_range="2025-2026")
        self.dept = Department.objects.create(name="Science", session=self.session)
        self.cls = StudentClass.objects.create(name="Science-1", department=self.dept)

        # Create Subject assigned to email but no User yet
        self.subject = Subject.objects.create(
            name="Physics",
            student_class=self.cls,
            teacher_email=self.email,
            teacher=None,
            is_active=True,
        )

        # Create Invitation
        self.token = uuid.uuid4()
        self.invitation = Invitation.objects.create(
            email=self.email, token=self.token, role=User.Role.TEACHER
        )

    def test_registration_assigns_subject(self):
        # Verify initial state
        self.subject.refresh_from_db()
        self.assertIsNone(self.subject.teacher)

        # Register
        url = reverse("register", args=[self.token])
        data = {
            "email": self.email,
            "password": "password123",
            "confirm_password": "password123",
            "first_name": "New",
            "last_name": "Teacher",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Should redirect

        # Verify User created
        user = User.objects.get(email=self.email)
        self.assertTrue(user.is_teacher())

        # Verify Subject assigned
        self.subject.refresh_from_db()
        self.assertEqual(self.subject.teacher, user)

    def test_registration_assigns_multiple_subjects(self):
        # Create another subject for the same email
        subject2 = Subject.objects.create(
            name="Chemistry",
            student_class=self.cls,
            teacher_email=self.email,
            teacher=None,
            is_active=True,
        )

        # Register
        url = reverse("register", args=[self.token])
        data = {
            "email": self.email,
            "password": "password123",
            "confirm_password": "password123",
            "first_name": "New",
            "last_name": "Teacher",
        }
        self.client.post(url, data)

        user = User.objects.get(email=self.email)

        # Verify BOTH subjects are assigned
        self.subject.refresh_from_db()
        subject2.refresh_from_db()

        self.assertEqual(self.subject.teacher, user)
        self.assertEqual(subject2.teacher, user)
