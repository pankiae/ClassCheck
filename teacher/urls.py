from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('proposal/create/', views.create_proposal, name='create_proposal'),
    path('proposals/', views.list_proposals, name='list_proposals'),
    path('proposal/<int:proposal_id>/approve/', views.approve_proposal, name='approve_proposal'),
    path('class/<int:class_id>/invite/', views.invite_student, name='invite_student'),
    path('class/<int:class_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    path('class/<int:class_id>/details/', views.class_details, name='class_details'),
]
