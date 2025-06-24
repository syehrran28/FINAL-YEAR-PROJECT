from django import forms
from dal import autocomplete
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from .models import Profile, ParentStudentDetails, TutorProfile, ROLE_CHOICES
from .models import Rating


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required. Only letters, spaces, or hyphens are allowed.',
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s-]+$',
                message="First name should only contain letters, spaces, or hyphens."
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': 'Enter First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        help_text='Required. Only letters, spaces, or hyphens are allowed.',
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\s-]+$',
                message="Last name should only contain letters, spaces, or hyphens."
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': 'Enter Last Name'})
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text='Enter a valid email address.',
        widget=forms.EmailInput(attrs={'placeholder': 'Enter Email'})
    )
    username = forms.CharField(
        max_length=30,
        required=True,
        help_text="Required. Alphanumeric characters or underscores only.",
        validators=[
            RegexValidator(
                regex=r'^\w+$',
                message="Username must be alphanumeric and may include underscores."
            )
        ],
        widget=forms.TextInput(attrs={'placeholder': 'Enter Username'})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}),
        help_text="Must be at least 8 characters long, including uppercase, lowercase, numbers, and special characters.",
        validators=[
            MinLengthValidator(8, 'Password must be at least 8 characters long.'),
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])',
                message="Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character."
            )
        ]
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        help_text="Enter the same password as above."
    )

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        required=True,
        help_text="Select your role",
        widget=forms.Select(attrs={'placeholder': 'Select your role'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return password2

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if not role or role not in dict(ROLE_CHOICES):
            raise ValidationError("Please select a valid role.")
        return role

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        # Create or update the Profile with the role
        role = self.cleaned_data.get('role')
        Profile.objects.update_or_create(user=user, defaults={'role': role})

        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
        help_text="Enter your username."
    )
    password = forms.CharField(
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        help_text="Enter your password."
    )

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise ValidationError("This account is inactive.", code='inactive')


class ParentStudentDetailsForm(forms.ModelForm):
    favorite_subjects = forms.MultipleChoiceField(
        choices=[('BM', 'Bahasa Melayu'),
    ('English', 'English'),
    ('Mathematics', 'Mathematics'),
    ('Science', 'Science'),
    ('History', 'History'),
    ('Geography', 'Geography'),
    ('Moral', 'Moral Studies'),
    ('Islamic_Studies', 'Islamic Studies'),
    ('Art', 'Art'),
    ('Economics', 'Economics'),
    ('Physics', 'Physics'),
    ('Chemistry', 'Chemistry'),
    ('Biology', 'Biology'),
    ('Additional_Math', 'Additional Mathematics'),
    ('Accounts', 'Accounting'),
    ('Business', 'Business Studies'),
    ('Literature', 'Literature in English'),
    ('ICT', 'Information and Communication Technology'),
    ('STPM_Math', 'STPM Mathematics'),
    ('STPM_Physics', 'STPM Physics'),], 
         widget=forms.SelectMultiple(attrs={
            'placeholder': 'Select your favorite subjects',
            'class': 'form-control',
            'style': 'height: 150px; overflow-y: auto;',  
        }),
        required=False,
        label="Favorite Subjects"
    )

    class Meta:
        model = ParentStudentDetails
        fields = ['age', 'phone_number', 'street', 'city', 'state', 'postcode', 'country', 'favorite_subjects']
        widgets = {
            'age': forms.NumberInput(attrs={'placeholder': 'Enter your age'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
            'street': forms.TextInput(attrs={'placeholder': 'Enter your street address'}),
            'city': forms.TextInput(attrs={'placeholder': 'Enter your city'}),
            'state': forms.TextInput(attrs={'placeholder': 'Enter your state'}),
            'postcode': forms.TextInput(attrs={'placeholder': 'Enter your postcode'}),
            'country': forms.TextInput(attrs={'placeholder': 'Enter your country'}),
        }
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Join multiple selections into a comma-separated string for storage
        instance.favorite_subjects = ', '.join(self.cleaned_data['favorite_subjects'])
        if commit:
            instance.save()
        return instance


class TutorProfileForm(forms.ModelForm):
    SCHOOL_LEVEL_CHOICES = [
        ('kindergarten', 'Kindergarten (4 to 6 years)'),
        ('primary', 'Primary School (Standard 1 to Standard 6)'),
        ('secondary', 'Secondary School (Form 1 to Form 5)'),
        ('preuniversity', 'Pre-University (STPM/Foundation/A-Levels)'),
        ('university', 'University/College'),
    ]
    
    profile_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control',
        'accept': 'image/*'
    }))

    school_level = forms.MultipleChoiceField(
        choices=SCHOOL_LEVEL_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'checkbox-group',
        }),
        required=False,
        label="School Level",
        help_text="Select the school levels you are comfortable teaching."
    )

    class Meta:
        model = TutorProfile
        fields = [
            'qualifications', 'specializations', 'teaching_experience', 'school_level', 
            'certifications', 'hourly_rate', 'weekly_hours', 'subjects_offered', 
            'availability_schedule', 'bio', 'phone_number', 'street', 'city', 
            'state', 'postcode', 'country', 'youtube_link', 'profile_image'
        ]
        widgets = {
            'subjects_offered': forms.Textarea(attrs={'placeholder': 'e.g., Math, Science, English'}),
            'availability_schedule': forms.Textarea(attrs={'placeholder': 'Describe your availability'}),
            'bio': forms.Textarea(attrs={'placeholder': 'A short introduction about yourself'}),
            'weekly_hours': forms.NumberInput(attrs={'placeholder': 'Enter your weekly teaching hours'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
            'youtube_link': forms.URLInput(attrs={'placeholder': 'Enter YouTube video link'}),
        }

    def clean_school_level(self):
        """Clean and validate school_level data"""
        school_levels = self.cleaned_data.get('school_level', [])
        if not school_levels:
            return ''
        # Validate that all selected values are in choices
        valid_levels = [choice[0] for choice in self.SCHOOL_LEVEL_CHOICES]
        for level in school_levels:
            if level not in valid_levels:
                raise forms.ValidationError(f"Invalid school level selection: {level}")
        return school_levels
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Handle image upload
        image_file = self.cleaned_data.get('profile_image')
        if image_file and hasattr(image_file, 'read'):  # Check if it's a new file upload
            try:
                image_file.seek(0)
                instance.profile_image = image_file.read()
                instance.image_name = image_file.name
                instance.image_type = image_file.content_type
            except Exception as e:
                print(f"Error processing image: {str(e)}")
        
        # Join the selected school levels into a comma-separated string
        school_levels = self.cleaned_data.get('school_level', [])
        instance.school_level = ', '.join(school_levels)
        
        if commit:
            instance.save()
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Handle initial values for school_level
        if self.instance and self.instance.school_level:
            try:
                # Split the stored string and clean whitespace
                initial_levels = [
                    level.strip() 
                    for level in self.instance.school_level.split(',')
                    if level.strip()
                ]
                self.fields['school_level'].initial = initial_levels
            except Exception as e:
                # Handle any potential errors gracefully
                print(f"Error setting initial school levels: {e}")
                self.fields['school_level'].initial = []
    
class TutorSearchForm(forms.Form):
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your city', 'class': 'form-control'}),
    )
    subjects_offered = forms.ChoiceField(
        required=False,
        choices=[
            ('BM', 'Bahasa Melayu'),
            ('English', 'English'),
            ('Mathematics', 'Mathematics'),
            ('Science', 'Science'),
            ('History', 'History'),
            ('Geography', 'Geography'),
            ('Moral', 'Moral Studies'),
            ('Islamic_Studies', 'Islamic Studies'),
            ('Art', 'Art'),
            ('Economics', 'Economics'),
            ('Physics', 'Physics'),
            ('Chemistry', 'Chemistry'),
            ('Biology', 'Biology'),
            ('Additional_Math', 'Additional Mathematics'),
            ('Accounts', 'Accounting'),
            ('Business', 'Business Studies'),
            ('Literature', 'Literature in English'),
            ('ICT', 'Information and Communication Technology'),
            ('STPM_Math', 'STPM Mathematics'),
            ('STPM_Physics', 'STPM Physics'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    custom_subject = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Or type your subject here', 'class': 'form-control'}),
    )
    hourly_rate_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Min Rate', 'class': 'form-control'}),
    )
    hourly_rate_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Max Rate', 'class': 'form-control'}),
    )
    teaching_experience = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Experience (Years)', 'class': 'form-control'}),
    )
    specializations = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter specialization', 'class': 'form-control'}),
    )
    school_level = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter school level', 'class': 'form-control'}),
    )

    
    
class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'review': forms.Textarea(attrs={'placeholder': 'Write your review (optional)...'}),
        }
