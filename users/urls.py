from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('invite-teacher/', views.invite_teacher, name='invite_teacher'),
    path('register/<uuid:token>/', views.register, name='register'),
    path('dashboard/', views.superuser_dashboard, name='superuser_dashboard'),
]
