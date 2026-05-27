from django.contrib import admin
from .models import Job, Bid, Review, Service, SavedJob, BidDraft


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """
    Admin configuration for Job.
    """
    list_display = ('title', 'client', 'budget', 'status', 'category', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'description', 'client__username')
    raw_id_fields = ('client',)
    # readonly_fields: fields that should be visible but not editable.
    # created_at and updated_at are auto-managed, so we don't want admin to change them.
    readonly_fields = ('created_at', 'updated_at')

    # We can also define fieldsets to group fields on the detail page.
    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'description', 'category', 'budget', 'attachment')
        }),
        ('Status & Owner', {
            'fields': ('status', 'client')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Hides this section by default (click to expand)
        }),
    )


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('job', 'freelancer', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('job__title', 'freelancer__username', 'proposal')
    raw_id_fields = ('job', 'freelancer')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('job', 'reviewer', 'reviewee', 'rating', 'communication_rating', 'quality_rating', 'timeliness_rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('job__title', 'reviewer__username', 'reviewee__username')
    raw_id_fields = ('job', 'reviewer', 'reviewee')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'freelancer', 'price', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description', 'freelancer__username')
    raw_id_fields = ('freelancer',)


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'created_at')
    search_fields = ('user__username', 'job__title')
    raw_id_fields = ('user', 'job')    


@admin.register(BidDraft)
class BidDraftAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'amount', 'updated_at')
    search_fields = ('user__username', 'job__title')
    raw_id_fields = ('user', 'job')    