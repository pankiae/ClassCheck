from django.conf import settings
from django.db import models


class ClassProposal(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="proposals"
    )
    subject = models.CharField(max_length=100)
    timing = models.TimeField()
    days = models.CharField(max_length=100)  # e.g., "Mon,Wed,Fri"
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} by {self.teacher.email} ({self.status})"


class Class(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="classes"
    )
    subject = models.CharField(max_length=100)
    timing = models.TimeField()
    days = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} ({self.teacher.email})"


class ClassSchedule(models.Model):
    class_obj = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="schedules"
    )
    day_of_week = models.CharField(max_length=10)  # Mon, Tue, etc.
    start_time = models.TimeField()
    end_time = (
        models.TimeField()
    )  # Calculated based on duration (assuming 1 hour for now)

    def __str__(self):
        return f"{self.class_obj.subject} on {self.day_of_week} at {self.start_time}"


class ClassSession(models.Model):
    class_obj = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="sessions"
    )
    schedule = models.ForeignKey(
        ClassSchedule, on_delete=models.SET_NULL, null=True, blank=True
    )
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("class_obj", "date", "schedule")

    def __str__(self):
        return f"{self.class_obj.subject} on {self.date}"


class Attendance(models.Model):
    session = models.ForeignKey(
        ClassSession, on_delete=models.CASCADE, related_name="attendances"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendances"
    )
    is_present = models.BooleanField(default=False)

    class Meta:
        unique_together = ("session", "student")

    def __str__(self):
        return f"{self.student.email} - {self.session} - {'Present' if self.is_present else 'Absent'}"


class AcademicSession(models.Model):
    year_range = models.CharField(max_length=20, unique=True)  # e.g., "2025-2026"
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.year_range


class Department(models.Model):
    name = models.CharField(max_length=100)
    session = models.ForeignKey(
        AcademicSession, on_delete=models.CASCADE, related_name="departments"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.session})"


class StudentClass(
    models.Model
):  # Renamed to avoid partial conflict, though Python handles namespacing.
    name = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="classes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.department.name}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    student_class = models.ForeignKey(
        StudentClass, on_delete=models.CASCADE, related_name="subjects"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.student_class.name})"
