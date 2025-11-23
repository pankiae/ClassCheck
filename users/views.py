import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .models import Invitation, User
from .forms import InviteTeacherForm, RegisterForm
from .decorators import admin_required
from student.models import Enrollment
from teacher.models import Class

def logout_view(request):
    logout(request)
    return redirect('login')

@admin_required
def invite_teacher(request):
    if request.method == 'POST':
        form = InviteTeacherForm(request.POST)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.token = uuid.uuid4()
            invitation.role = User.Role.TEACHER
            invitation.save()
            # In a real app, send email here. For now, just show the link.
            invite_link = request.build_absolute_uri(f'/register/{invitation.token}/')
            return render(request, 'users/invite_success.html', {'invite_link': invite_link})
    else:
        form = InviteTeacherForm()
    return render(request, 'users/invite_teacher.html', {'form': form})

def register(request, token):
    invitation = get_object_or_404(Invitation, token=token, is_used=False)
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = invitation.role
            user.email = invitation.email
            user.save()
            invitation.is_used = True
            invitation.save()
            
            # Handle Enrollment if class_id is present
            if invitation.class_id:
                try:
                    class_obj = Class.objects.get(id=invitation.class_id)
                    Enrollment.objects.create(student=user, class_obj=class_obj)
                except Class.DoesNotExist:
                    pass # Should not happen ideally
            
            login(request, user)
            if user.is_teacher():
                return redirect('teacher_dashboard')
            elif user.is_student():
                return redirect('student_dashboard')
            elif user.is_admin():
                return redirect('superuser_dashboard')
            return redirect('dashboard') # Fallback
    else:
        form = RegisterForm(initial={'email': invitation.email})
    return render(request, 'users/register.html', {'form': form})

@admin_required
def superuser_dashboard(request):
    teachers = User.objects.filter(role=User.Role.TEACHER)
    students = User.objects.filter(role=User.Role.STUDENT)
    classes = Class.objects.all()
    return render(request, 'users/dashboard.html', {
        'teachers': teachers,
        'students': students,
        'classes': classes
    })
