from django.urls import path
from . import views
from django.shortcuts import render


urlpatterns = [
    # Template views
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/create/', views.job_create, name='job_create'),
    path('jobs/<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:pk>/delete/', views.job_delete, name='job_delete'),

    # API endpoints will go here in Phase 8
    # path('api/jobs/', api_views.JobListCreateAPIView.as_view(), name='api_job_list'),
    # ...
]