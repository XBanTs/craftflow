from django.urls import path
from . import views, api_views
from django.shortcuts import render


urlpatterns = [
    # Template views
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/create/', views.job_create, name='job_create'),
    path('jobs/<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:pk>/delete/', views.job_delete, name='job_delete'),

    # API endpoints
    path('api/jobs/', api_views.JobListCreateAPIView.as_view(), name='api_job_list'),
    path('api/jobs/<int:pk>/', api_views.JobDetailAPIView.as_view(), name='api_job_detail'),
    path('api/bids/', api_views.BidCreateAPIView.as_view(), name='api_bid_create'),
    path('api/services/', api_views.ServiceListAPIView.as_view(), name='api_service_list'),
    path('api/services/<int:pk>/', api_views.ServiceDetailAPIView.as_view(), name='api_service_detail'),
]