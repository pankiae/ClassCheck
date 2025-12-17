from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('invite-teacher/', views.invite_teacher, name='invite_teacher'),
    path('invite-student/', views.invite_student, name='invite_student'),
    path('register/<uuid:token>/', views.register, name='register'),
    path('signup/teacher/', views.TeacherSignUpView.as_view(), name='signup_teacher'),
    path('signup/student/', views.StudentSignUpView.as_view(), name='signup_student'),
    path('role_redirect/', views.role_based_redirect, name='role_based_redirect'),
    path('dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
]
