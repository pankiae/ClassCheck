from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from users.models import Invitation
from unittest.mock import patch

User = get_user_model()

class InvitationTransactionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            email="admin@example.com", password="password", role=User.Role.ADMIN
        )
        self.client.force_login(self.admin)

    def test_invite_teacher_email_failure_no_save(self):
        # Mock send_mail to raise an exception
        # Patch where it is used (users.views)
        with patch('users.views.send_mail', side_effect=Exception("SMTP Error")):
            email_string = "fail@example.com"
            response = self.client.post(
                "/invite-teacher/",
                {"emails": email_string}
            )
            
            self.assertEqual(response.status_code, 200)
            # Should show error in context
            self.assertContains(response, "SMTP Error")
            # Should NOT create record
            self.assertFalse(Invitation.objects.filter(email="fail@example.com").exists())

    def test_invite_teacher_email_success_saves(self):
        # Mock send_mail to succeed
        with patch('users.views.send_mail') as mock_send:
            email_string = "success@example.com"
            response = self.client.post(
                "/invite-teacher/",
                {"emails": email_string}
            )
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(Invitation.objects.filter(email="success@example.com").exists())
            self.assertTrue(mock_send.called)
