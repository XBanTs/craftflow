from django.contrib import admin
from .models import FreelancerProfile, PortfolioItem, UserVerification


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


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at')
    search_fields = ('user__username', 'title')
    raw_id_fields = ('user',)  


@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_verified', 'created_at')
    list_filter = ('email_verified',)
    search_fields = ('user__username',)      