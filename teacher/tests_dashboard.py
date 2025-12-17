from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from teacher.models import Department, StudentClass, Subject, AcademicSession

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
            timing="10:00"
        )
        self.subj2 = Subject.objects.create(
            name="Chemistry", 
            student_class=self.cls1, 
            teacher=self.teacher,
            days=["Tue"],
            timing="11:00"
        )
        
        # Create another class
        self.cls2 = StudentClass.objects.create(name="science-2", department=self.dept)
        self.subj3 = Subject.objects.create(
            name="Math",
            student_class=self.cls2,
            teacher=self.teacher,
            days=["Wed"],
            timing="09:00"
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
        ordered_classes = list(response.context['classes'])
        # Expected order: Math (science-2) > Chemistry (science-1) > Physics (science-1) ?
        # No: Order is Dept Name -> Class Name -> Name
        # science-1 < science-2
        # Inside science-1: Chemistry < Physics
        # So: Chemistry, Physics, Math
        
        self.assertEqual(ordered_classes[0], self.subj2) # Chemistry (science-1)
        self.assertEqual(ordered_classes[1], self.subj1) # Physics (science-1)
        self.assertEqual(ordered_classes[2], self.subj3) # Math (science-2)
