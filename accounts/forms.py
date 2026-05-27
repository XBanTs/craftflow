from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import FreelancerProfile, PortfolioItem


class CustomUserRegistrationForm(UserCreationForm):
    """
    Extends Django's built-in UserCreationForm.

    UserCreationForm already handles:
    - Username uniqueness validation.
    - Password strength validation (must not be too common, entirely numeric,
      or similar to the username).
    - Password confirmation (password1 and password2 must match).
    - Automatic password hashing on save (PBKDF2 by default).

    We extend it to require email, which is optional in the default form
    but important for a professional marketplace (password resets, notifications).
    """
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        # We explicitly list the fields we want in the form.
        # 'password1' is the password field, 'password2' is the confirmation field.
        # They are automatically validated to match.

    def save(self, commit=True):
        """
        Override save() to set the email field on the User model
        before saving to the database.
        """
        user = super().save(commit=False)
        # commit=False creates the User instance in memory without hitting the DB.
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class FreelancerProfileEditForm(forms.ModelForm):
    """
    Form for editing a freelancer's profile (bio, skills, hourly rate, avatar).
    """
    class Meta:
        model = FreelancerProfile
        fields = ['bio', 'skills', 'hourly_rate', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Introduce yourself and your expertise…'}),
            'skills': forms.TextInput(attrs={'placeholder': 'e.g. Python, React, UI Design'}),
        }


class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ['title', 'description', 'image', 'link']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. E‑commerce website redesign'}),
            'link': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }        