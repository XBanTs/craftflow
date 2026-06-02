from django.db import models
from django.contrib.auth.models import User


# JOB
class Job(models.Model):
    """
    Represents a work opportunity posted by a client.

    Each job has a lifecycle governed by its status field:
    open → in_progress → completed (or cancelled).
    """
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        # TextChoices is a Django 3.0+ feature.
        # The first value is stored in the database (shorter).
        # The second value is the human-readable label.

    class Category(models.TextChoices):
        WEB_DEV = 'web_dev', 'Web Development'
        MOBILE_DEV = 'mobile_dev', 'Mobile Development'
        UI_UX = 'ui_ux', 'UI/UX Design'
        DATA_SCIENCE = 'data_science', 'Data Science & Analytics'
        WRITING = 'writing', 'Content & Writing'
        MARKETING = 'marketing', 'Digital Marketing'
        OTHER = 'other', 'Other'

    title = models.CharField(
        max_length=200,
        help_text="A concise, descriptive title for your job posting."
        # CharField: short text with a max_length.
        # max_length=200 is generous enough for a good title.
    )

    description = models.TextField(
        help_text="Detailed description of the work, requirements, and deliverables."
        # TextField: unlimited-length text.
    )

    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total budget in USD (e.g., 500.00)"
        # max_digits=10 allows up to 99,999,999.99 — plenty of room.
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
        # choices restricts the field to the predefined set.
        # In forms, this renders as a dropdown.
        # In the database, it's still stored as a string.
    )

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.WEB_DEV
    )

    client = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='jobs_posted'
        # PROTECT: if a client has posted jobs, their User account cannot be deleted
        # until all their jobs are reassigned or deleted.
        # This prevents accidentally orphaning job records.
        # CASCADE would mean deleting a client deletes all their jobs,
        # which might not be desirable for a marketplace history.
        # related_name='jobs_posted' lets us do user.jobs_posted.all().
    )

    attachment = models.FileField(
        upload_to='job_attachments/',
        null=True,
        blank=True,
        help_text="Optional: attach a brief, spec, or reference file."
        # FileField is more generic than ImageField — accepts any file type.
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # auto_now: updates the field automatically on every .save() call.
    # Together with created_at, we can track how recently a job was modified.

    def __str__(self):
        return self.title
        # In admin list: shows the job title directly.

    class Meta:
        ordering = ['-created_at']
        # Orders jobs newest-first by default across queries.
        # This saves us writing .order_by('-created_at') in every view.
        verbose_name = "Job"
        verbose_name_plural = "Jobs"


# BID
class Bid(models.Model):
    """
    Represents a freelancer's proposal for a job.

    Each bid is tied to exactly one job and one freelancer.
    If the job is deleted, the bid is automatically deleted (CASCADE).
    """
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='bids'
        # CASCADE: if the job is deleted, its bids are meaningless.
        # related_name='bids' lets us do job.bids.all() in views.
        # This is the required CASCADE ForeignKey for the Brief.
    )

    freelancer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='bids_submitted'
        # PROTECT: if a freelancer's account is deleted, we might want to keep
        # their bids for the job poster's reference.
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Your proposed amount in USD for this project."
    )

    proposal = models.TextField(
        help_text="Explain why you're the best fit for this job — your approach, timeline, and relevant experience."
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid by {self.freelancer.username} on '{self.job.title}' — {self.status}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Bid"
        verbose_name_plural = "Bids"        


# REVIEW
class Review(models.Model):
    """
    A rating and comment left after a job is completed.

    The reviewer is typically the client reviewing the freelancer.
    For simplicity, we store both parties but design primarily for client→freelancer reviews.
    """
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='reviews'
        # CASCADE: if the job is deleted, the review is deleted.
        # Each job should have at most one review (we enforce this in logic, not schema).
    )

    reviewer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='reviews_given'
        # The person who wrote the review.
    )

    reviewee = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='reviews_received'
        # The person being reviewed (usually the freelancer).
    )

    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text="Rating from 1 (poor) to 5 (excellent)."
        # PositiveSmallIntegerField stores integers 0–32767.
        # We restrict to 1–5 via choices.
    )

        # Multi‑facet ratings (1‑5)
    communication_rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        default=0,
        help_text="Rate the freelancer's communication."
    )
    quality_rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        default=0,
        help_text="Rate the quality of the work delivered."
    )
    timeliness_rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        default=0,
        help_text="Rate the freelancer's timeliness."
    )

    comment = models.TextField(
        blank=True,
        help_text="Share your experience working on this project."
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # If overall rating not manually set, compute average of sub‑ratings
        if self.pk is None and self.rating == 0:  # new review and rating not set
            ratings = [self.communication_rating, self.quality_rating, self.timeliness_rating]
            if all(r > 0 for r in ratings):
                self.rating = round(sum(ratings) / 3, 1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review for {self.reviewee.username} on '{self.job.title}' — {self.rating}★"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Review"
        verbose_name_plural = "Reviews"        


# SERVICE
class Service(models.Model):
    """
    Represents a service offered by a freelancer.

    Freelancers can list multiple services (e.g., "Python Backend Development",
    "API Integration"), each with a title, description, price, and category.
    """
    class Category(models.TextChoices):
        WEB_DEV = 'web_dev', 'Web Development'
        MOBILE_DEV = 'mobile_dev', 'Mobile Development'
        UI_UX = 'ui_ux', 'UI/UX Design'
        DATA_SCIENCE = 'data_science', 'Data Science & Analytics'
        WRITING = 'writing', 'Content & Writing'
        MARKETING = 'marketing', 'Digital Marketing'
        OTHER = 'other', 'Other'

    freelancer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='services'
        # CASCADE: if the freelancer's account is deleted, their services are removed.
        # This makes sense because a service without a provider is invalid.
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Starting price for this service in USD."
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.WEB_DEV
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.freelancer.username}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Service"
        verbose_name_plural = "Services"        


class SavedJob(models.Model):
    """
    Represents a user bookmarking a job for later viewing.
    Unique together constraint prevents duplicate saves.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_jobs'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='saved_by_users'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'job']
        ordering = ['-created_at']
        verbose_name = "Saved Job"
        verbose_name_plural = "Saved Jobs"

    def __str__(self):
        return f"{self.user.username} saved '{self.job.title}'"  


class BidDraft(models.Model):
    """
    Stores an in‑progress bid proposal that a freelancer hasn't submitted yet.
    Unique per user and job – only one draft per freelancer per job.   
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bid_drafts'
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name='bid_drafts'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    proposal = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'job']
        ordering = ['-updated_at']
        verbose_name = "Bid Draft"
        verbose_name_plural = "Bid Drafts"

    def __str__(self):
        return f"Draft by {self.user.username} for '{self.job.title}'"


class Notification(models.Model):
    """
    Stores a notification for a user.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255, blank=True)   # e.g., /jobs/5/
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"        