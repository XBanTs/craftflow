from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:pk>/', views.profile_view, name='profile'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('profile/<int:pk>/edit/', views.profile_edit_view, name='profile_edit'),
    path('portfolio/add/', views.portfolio_create, name='portfolio_create'),
    path('portfolio/<int:pk>/edit/', views.portfolio_edit, name='portfolio_edit'),
    path('portfolio/<int:pk>/delete/', views.portfolio_delete, name='portfolio_delete'),
]