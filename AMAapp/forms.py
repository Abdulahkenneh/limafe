# forms.py (all needed forms)

from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, AuthenticationForm
from .models import CustomUser, Page, Post, Media, Project, Event, Membership, Booking, Donation, Message, Newsletter, ContactSubmission


# User Forms
class SignupForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number (optional)'
        })
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Address (optional)',
            'rows': 3
        }),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['username', 'email', 'phone_number', 'address']:
                field.widget.attrs.update({'class': 'form-control'})
            if field_name == 'username':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Choose a username'
                })
            if field_name == 'password1':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Enter password'
                })
            if field_name == 'password2':
                field.widget.attrs.update({
                    'class': 'form-control',
                    'placeholder': 'Confirm password'
                })

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'phone_number', 'address')


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class PasswordRecoveryForm(PasswordResetForm):
    pass  # Customize if needed

from django import forms

class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'phone_number',
            'address',
            'is_two_factor_enabled',
            'profile_image',
        )

        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number (optional)'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Address (optional)',
                'rows': 3
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():

            # Checkbox should not use form-control
            if field_name == 'is_two_factor_enabled':
                field.widget.attrs.update({
                    'class': 'form-check-input'
                })

            # File input has its own bootstrap class
            elif field_name == 'profile_image':
                field.widget.attrs.update({
                    'class': 'form-control'
                })

            # Everything else behaves like your signup form
            else:
                field.widget.attrs.update({
                    'class': 'form-control'
                })

# Content Forms
class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ('title', 'content')

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content')

class MediaUploadForm(forms.ModelForm):
    class Meta:
        model = Media
        fields = ('file', 'alt_text')

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('title', 'description', 'images')

# Event Forms
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ('title', 'description', 'start_time', 'end_time', 'location')

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ()  # Auto-filled with event and user

# Donation Form
class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ('amount',)  # Integrate with Stripe/PayPal in views

# Communication Forms
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('receiver', 'content')

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ('subject', 'content')

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ('name', 'email', 'message')

# Admin Forms (for dashboard CRUD) - Use Django admin or ModelForms as above.

# Additional Forms if needed, e.g., for search, filters, etc.
class SearchForm(forms.Form):
    query = forms.CharField(required=False)


from django import forms
from .models import Membership
from django.core.exceptions import ValidationError

from django import forms
from .models import Membership, CustomUser, Chapter


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = [
            'chapter',
            'sex',
            'marital_status',
            'number_of_children',
            'number_of_dependents',
            'household_size',
        ]

    # Make numeric fields optional
    number_of_children = forms.IntegerField(required=False, min_value=0)
    number_of_dependents = forms.IntegerField(required=False, min_value=0)
    household_size = forms.IntegerField(required=False, min_value=1)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control modern-input',
                'autocomplete': 'off'
            })

        self.fields['chapter'].widget.attrs.update({
            'class': 'form-control modern-input select2-style',
            'data-placeholder': 'Choose a chapter...'
        })
        self.fields['chapter'].label = "Select Chapter to Join"
        self.fields['household_size'].help_text = "Total people living in your household"

    def clean(self):
        cleaned_data = super().clean()
        chapter = cleaned_data.get('chapter')

        if self.user and chapter:
            if Membership.objects.filter(user=self.user, chapter=chapter).exists():
                raise forms.ValidationError({
                    'chapter': f"You are already a member of {chapter.name}."
                })

        # Make empty values default to 0 or 1
        children = cleaned_data.get('number_of_children') or 0
        dependents = cleaned_data.get('number_of_dependents') or 0
        household_size = cleaned_data.get('household_size') or 1

        # if household_size < (children + dependents + 1):
        #     raise forms.ValidationError(
        #         "Household size cannot be smaller than dependents plus yourself."
        #     )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user

        if commit:
            instance.save()
        return instance