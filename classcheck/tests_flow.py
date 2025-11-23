from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from users.models import Invitation
from teacher.models import ClassProposal, Class, ClassSchedule, ClassSession, Attendance
from student.models import Enrollment
import datetime
import uuid

User = get_user_model()

class EndToEndFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser('admin@example.com', 'password')

    def test_flow(self):
        # 1. Superuser invites Teacher
        self.client.force_login(self.superuser)
        response = self.client.post('/invite-teacher/', {'email': 'teacher@example.com'})
        self.assertEqual(response.status_code, 200)
        invitation = Invitation.objects.get(email='teacher@example.com')
        self.assertEqual(invitation.role, User.Role.TEACHER)
        self.client.logout()

        # 2. Teacher registers
        register_url = f'/register/{invitation.token}/'
        response = self.client.post(register_url, {'email': 'teacher@example.com', 'password': 'password', 'password_confirmation': 'password'})
        
        # Simulating registration by creating user directly as if view did it
        teacher = User.objects.create_user(email='teacher@example.com', password='password', role=User.Role.TEACHER)
        invitation.is_used = True
        invitation.save()
        
        # 3. Teacher proposes Class
        self.client.force_login(teacher)
        response = self.client.post('/teacher/proposal/create/', {
            'subject': 'Math 101',
            'timing': '10:00',
            'days': 'Mon,Wed,Fri'
        })
        self.assertEqual(response.status_code, 302) # Redirect to dashboard
        proposal = ClassProposal.objects.get(subject='Math 101')
        self.assertEqual(proposal.status, 'PENDING')
        self.client.logout()

        # 4. Superuser approves Class
        self.client.force_login(self.superuser)
        response = self.client.post(f'/teacher/proposal/{proposal.id}/approve/', {'action': 'approve'})
        self.assertEqual(response.status_code, 302)
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'APPROVED')
        class_obj = Class.objects.get(subject='Math 101')
        self.assertTrue(ClassSchedule.objects.filter(class_obj=class_obj).exists())
        self.client.logout()

        # 5. Teacher invites Student
        self.client.force_login(teacher)
        response = self.client.post(f'/teacher/class/{class_obj.id}/invite/', {'email': 'student@example.com'})
        self.assertEqual(response.status_code, 200)
        student_invite = Invitation.objects.get(email='student@example.com')
        self.assertEqual(student_invite.role, User.Role.STUDENT)
        self.assertEqual(student_invite.class_id, class_obj.id)
        self.client.logout()

        # 6. Student registers
        student = User.objects.create_user(email='student@example.com', password='password', role=User.Role.STUDENT)
        student_invite.is_used = True
        student_invite.save()
        Enrollment.objects.create(student=student, class_obj=class_obj)

        # 7. Teacher marks attendance
        # We need to mock time or ensure schedule matches.
        # Let's create a schedule for TODAY at CURRENT TIME for testing purposes
        now = datetime.datetime.now()
        current_day = now.strftime("%a")
        start_time = (now - datetime.timedelta(minutes=45)).time() # Started 45 mins ago
        end_time = (now + datetime.timedelta(minutes=15)).time() # Ends in 15 mins (Window active)
        
        # Create a specific schedule for this test
        schedule = ClassSchedule.objects.create(
            class_obj=class_obj,
            day_of_week=current_day,
            start_time=start_time,
            end_time=end_time
        )
        
        self.client.force_login(teacher)
        response = self.client.post(f'/teacher/class/{class_obj.id}/attendance/', {
            f'student_{student.id}': 'on'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify Attendance
        self.assertTrue(ClassSession.objects.filter(class_obj=class_obj, date=now.date()).exists())
        session = ClassSession.objects.get(class_obj=class_obj, date=now.date())
        self.assertTrue(Attendance.objects.filter(session=session, student=student, is_present=True).exists())
