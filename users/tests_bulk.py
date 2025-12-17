from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from users.models import Invitation

User = get_user_model()

class SuperuserBulkInviteTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="password", role=User.Role.ADMIN
        )
        self.client.force_login(self.admin)

    def test_invite_teacher_bulk(self):
        email_string = "teacher1@example.com, teacher2@example.com"
        response = self.client.post(
            "/invite-teacher/",
            {"emails": email_string}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/invite_success.html")
        self.assertContains(response, "2") # Success count
        
        self.assertTrue(Invitation.objects.filter(email="teacher1@example.com", role=User.Role.TEACHER).exists())
        self.assertTrue(Invitation.objects.filter(email="teacher2@example.com", role=User.Role.TEACHER).exists())

    def test_invite_student_bulk(self):
        email_string = "student1@example.com, student2@example.com"
        response = self.client.post(
            "/invite-student/",
            {"emails": email_string}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/invite_success.html")
        
        self.assertTrue(Invitation.objects.filter(email="student1@example.com", role=User.Role.STUDENT).exists())
        self.assertTrue(Invitation.objects.filter(email="student2@example.com", role=User.Role.STUDENT).exists())

    def test_partial_failure(self):
        # Create existing
        import uuid
        Invitation.objects.create(email="existing@example.com", token=uuid.uuid4(), role=User.Role.TEACHER)
        
        email_string = "new@example.com, existing@example.com"
        response = self.client.post(
            "/invite-teacher/",
            {"emails": email_string}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "existing@example.com") # Failure list
        self.assertTrue(Invitation.objects.filter(email="new@example.com").exists())
