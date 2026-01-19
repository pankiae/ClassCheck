import uuid

from django.test import Client, TestCase
from django.urls import reverse

from student.models import Enrollment
from teacher.models import AcademicSession, Class, Department, StudentClass, Subject
from users.models import Invitation, User


class StudentRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.email = "student@example.com"

        # Setup Hierarchy for Subject
        self.session = AcademicSession.objects.create(year_range="2025-2026")
        self.dept = Department.objects.create(name="Science", session=self.session)
        self.cls = StudentClass.objects.create(name="Science-1", department=self.dept)

        # Create Subject
        self.subject = Subject.objects.create(
            name="Physics", student_class=self.cls, is_active=True
        )

        # Create Invitation linked to Subject (teacher invite logic uses subject.id as class_id)
        self.token = uuid.uuid4()
        self.invitation = Invitation.objects.create(
            email=self.email,
            token=self.token,
            role=User.Role.STUDENT,
            class_id=self.subject.id,
        )

    def test_student_registration_success(self):
        # Register
        url = reverse("register", args=[self.token])
        data = {
            "email": self.email,
            "password": "password123",
            "confirm_password": "password123",
            "first_name": "New",
            "last_name": "Student",
        }

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        # Verify Enrollment
        user = User.objects.get(email=self.email)
        self.assertTrue(
            Enrollment.objects.filter(student=user, subject=self.subject).exists()
        )
