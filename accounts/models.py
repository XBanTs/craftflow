from django.db import models
from django.contrib.auth.models import User
import uuid


class FreelancerProfile(models.Model):
    """
    Extends Django's built-in User model with freelancer-specific data.

    Why a OneToOneField, not AbstractBaseUser?
    - Django's User model already handles authentication, permissions, sessions.
    - A profile extension adds domain data (skills, bio, rate) without breaking anything.
    - This is the standard "profile model" pattern used in production Django apps.

    If we needed a completely custom user from scratch, we'd subclass AbstractBaseUser.
    For this project, the profile extension is cleaner and faster.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='freelancer_profile'
        # CASCADE: If the User is deleted, the profile is meaningless.
        # related_name='freelancer_profile' lets us do user.freelancer_profile
        # instead of user.freelancerprofile (Django's default lowercase model name).
    )

    bio = models.TextField(
        blank=True,
        help_text="A short introduction about yourself and your expertise."
        # TextField for multi-line text, no max_length constraint.
        # blank=True allows the field to be submitted empty in forms.
        # null is not needed for string-based fields (Django convention).
    )

    skills = models.TextField(
        blank=True,
        help_text="Comma-separated list of skills, e.g. Python, React, UI Design"
        # Storing skills as a comma-separated string is simple.
        # In a scalable system, you'd use a ManyToManyField to a Skill model
        # for better querying ("find all freelancers with Python").
        # We keep it simple for now.
    )

    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
        # DecimalField is the correct type for money — never use FloatField.
        # FloatField introduces rounding errors.
        # max_digits=8 means the total number of digits is 8.
        # decimal_places=2 means 2 digits after the decimal point.
        # Example max: 999999.99
        # null=True allows the database to store NULL.
        # blank=True allows the form to submit an empty field.
        # Both are needed for an optional numeric field.
    )

    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True
        # ImageField requires Pillow to be installed
        # upload_to defines the subdirectory under MEDIA_ROOT where files are stored.
        # The final path: MEDIA_ROOT/avatars/somefile.jpg
        # This satisfies the Brief's requirement for at least one model with ImageField.
    )

    is_verified = models.BooleanField(
        default=False,
        help_text="Designates whether the freelancer has been verified by an admin."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now_add: sets the field to the current timestamp when the object is first created.
    # It is not modified on subsequent saves.
    # Compare with auto_now: updates every time .save() is called.
    # Use auto_now_add for creation timestamps, auto_now for modification timestamps.

    def __str__(self):
        return f"{self.user.username}'s Profile"
        # In the admin list view, this shows as "alice's Profile" — human-readable.

    class Meta:
        verbose_name = "Freelancer Profile"
        verbose_name_plural = "Freelancer Profiles"
        # These control the display name in the Django admin sidebar.
        # Without them, Django shows "Freelancer profiles" (lowercase 'p').

class PortfolioItem(models.Model):
    """
    A showcase item in a freelancer's portfolio.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='portfolio_items'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='portfolio/',
        null=True,
        blank=True
    )
    link = models.URLField(
        blank=True,
        help_text="Optional external link to live project or case study."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Portfolio Item"
        verbose_name_plural = "Portfolio Items"

    def __str__(self):
        return f"{self.user.username} – {self.title}"


class UserVerification(models.Model):
    """
    Tracks email verification status for any user.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='verification'
    )
    email_verified = models.BooleanField(default=False)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} – {'Verified' if self.email_verified else 'Unverified'}"