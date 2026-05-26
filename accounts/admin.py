from django.contrib import admin
from .models import FreelancerProfile


@admin.register(FreelancerProfile)
class FreelancerProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for FreelancerProfile.

    list_display: shows the user, hourly rate, and creation date in the list.
    search_fields: allows searching by username (via the related User model)
                   and by skills text.
    list_filter: adds a date-based filter on the creation date.
    raw_id_fields: for the user ForeignKey — prevents loading all users into a dropdown.
    """
    list_display = ('user', 'hourly_rate', 'is_verified', 'created_at')
    search_fields = ('user__username', 'skills')
    list_filter = ('is_verified', 'created_at',)
    raw_id_fields = ('user',)