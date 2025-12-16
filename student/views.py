from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.decorators import student_required
from .models import Enrollment
from teacher.models import ClassSession, Attendance
import datetime

@student_required
def student_dashboard(request):
    date_str = request.GET.get('date')
    if date_str:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        date = datetime.date.today()

    enrollments = Enrollment.objects.filter(student=request.user)
    class_ids = enrollments.values_list('class_obj_id', flat=True)
    
    sessions = ClassSession.objects.filter(class_obj_id__in=class_ids, date=date).select_related('class_obj', 'schedule').order_by('schedule__start_time')
    
    attendance_map = {}
    for session in sessions:
        try:
            att = Attendance.objects.get(session=session, student=request.user)
            attendance_map[session.id] = 'Present' if att.is_present else 'Absent'
        except Attendance.DoesNotExist:
            attendance_map[session.id] = 'Not Marked'

    return render(request, 'student/dashboard.html', {
        'date': date,
        'sessions': sessions,
        'attendance_map': attendance_map
    })
