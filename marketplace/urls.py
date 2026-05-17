from django.urls import path
from django.shortcuts import render

# Temporary home view until Phase 7
def home(request):
    return render(request, 'base.html')

urlpatterns = [
    path('', home, name='home'),
]