from django import forms
from .models import Job


class JobForm(forms.ModelForm):
    """
    ModelForm for creating and updating Job instances.

    Excludes fields that are set programmatically (client, status, timestamps).
    """
    class Meta:
        model = Job
        exclude = ['client', 'status', 'created_at', 'updated_at']
        # Fields included: title, description, budget, category, attachment
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Describe the project in detail...'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Build a REST API for mobile app'}),
            'budget': forms.NumberInput(attrs={'placeholder': 'e.g. 500.00', 'step': '0.01'}),
        }

    def clean_budget(self):
        """
        Ensure the budget is a positive number.
        The method name clean_<fieldname> tells Django to call this
        after the field's built-in validation.
        """
        budget = self.cleaned_data.get('budget')
        if budget is not None and budget <= 0:
            raise forms.ValidationError('Budget must be a positive number.')
        return budget

    def clean_title(self):
        """
        Ensure the title is not too short.
        """
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 5:
            raise forms.ValidationError('Title must be at least 5 characters long.')
        return title