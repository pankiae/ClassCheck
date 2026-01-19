from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from teacher.models import Department, StudentClass, Subject, AcademicSession
from users.models import Invitation

User = get_user_model()

class BulkInviteTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            email="teacher@example.com", password="password", role=User.Role.TEACHER
        )
        self.client.force_login(self.teacher)
        
        # Setup Hierarchy
        self.session = AcademicSession.objects.create(year_range="2090-2091")
        self.dept = Department.objects.create(name="Science", session=self.session)
        self.cls = StudentClass.objects.create(name="science-1", department=self.dept)
        self.subject = Subject.objects.create(
            name="Physics", 
            student_class=self.cls, 
            teacher=self.teacher
        )

    def test_bulk_invite_success(self):
        # Prepare comma separated emails (mimicking the hidden input populated by JS)
        email_string = "student1@example.com,student2@example.com, student3@example.com "
        
        response = self.client.post(
            f"/teacher/class/{self.subject.id}/invite/",
            {"emails": email_string}  # Matches form field name
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "teacher/invite_bulk_success.html")
        self.assertContains(response, "3") # Expecting "processed 3 invitations" or similar count
        
        # Verify DB
        self.assertEqual(Invitation.objects.count(), 3)
        self.assertTrue(Invitation.objects.filter(email="student1@example.com").exists())
        self.assertTrue(Invitation.objects.filter(email="student2@example.com").exists())

    def test_bulk_invite_partial_failure(self):
        # One valid, one invalid, one duplicate
        import uuid
        Invitation.objects.create(
            email="existing@example.com", 
            class_id=self.subject.id, 
            role=User.Role.STUDENT,
            token=uuid.uuid4()
        )
        
        email_string = "new@example.com, invalid-email, existing@example.com"
        
        response = self.client.post(
            f"/teacher/class/{self.subject.id}/invite/",
            {"emails": email_string}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check success count in context/html
        # "total_success" should be 1 (for new@example.com)
        self.assertIn("1", str(response.content)) 
        
        # Check failures
        self.assertContains(response, "invalid-email")
        self.assertContains(response, "existing@example.com")
        
        # DB check: 1 existing + 1 new = 2 total
        self.assertEqual(Invitation.objects.count(), 2)
