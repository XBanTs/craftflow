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
    path('dashboard/', views.dashboard, name='dashboard'),
    path('jobs/<int:job_pk>/bid/', views.bid_create, name='bid_create'),
    path('jobs/<int:job_pk>/save/', views.save_job_toggle, name='save_job_toggle'),
    path('saved-jobs/', views.saved_jobs, name='saved_jobs'),
    path('my-bids/', views.my_bids, name='my_bids'),
    path('bids/<int:pk>/edit/', views.bid_edit, name='bid_edit'),
    path('bids/<int:pk>/delete/', views.bid_delete, name='bid_delete'),
    path('bids/<int:pk>/accept/', views.bid_accept, name='bid_accept'),
    path('bids/<int:pk>/reject/', views.bid_reject, name='bid_reject'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('inbox/', views.inbox, name='inbox'),
    path('messages/<int:job_pk>/<int:user_pk>/', views.conversation, name='conversation'),
    path('messages/<int:job_pk>/<int:user_pk>/send/', views.send_message, name='send_message'),
    path('api/messages/<int:job_pk>/<int:user_pk>/new/', views.fetch_new_messages, name='fetch_new_messages'),

    # API endpoints
    path('api/jobs/', api_views.JobListCreateAPIView.as_view(), name='api_job_list'),
    path('api/jobs/<int:pk>/', api_views.JobDetailAPIView.as_view(), name='api_job_detail'),
    path('api/bids/', api_views.BidCreateAPIView.as_view(), name='api_bid_create'),
    path('api/services/', api_views.ServiceListAPIView.as_view(), name='api_service_list'),
    path('api/services/<int:pk>/', api_views.ServiceDetailAPIView.as_view(), name='api_service_detail'),
    path('api/notifications/unread/', views.unread_notifications, name='unread_notifications'),
]