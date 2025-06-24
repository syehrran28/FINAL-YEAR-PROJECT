from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
import re

ROLE_CHOICES = [
    ('parent_student', 'Parent/Student'),
    ('tutor_center', 'Tutor/Tuition Center'),
]

# Model for parent/student additional details
class ParentStudentDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_student_details')
    age = models.PositiveIntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    street = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    favorite_subjects = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Details"

# Profile model for role management
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)

    def __str__(self):
        role_display = self.get_role_display() or "No role assigned"
        return f"{self.user.username} - {role_display}"

# Model for reviews
class Review(models.Model):
    student = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'parent_student'},
        related_name='reviews_given'
    )
    tutor = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'tutor_center'},
        related_name='reviews_received'
    )
    rating = models.IntegerField()
    feedback = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.student.user.username} for {self.tutor.user.username}"

# New model for tutor details
from django.db import models
from django.contrib.auth.models import User

class TutorProfile(models.Model):
    SCHOOL_LEVEL_CHOICES = [
        ('kindergarten', 'Kindergarten (4 to 6 years)'),
        ('primary', 'Primary School (Standard 1 to Standard 6)'),
        ('secondary', 'Secondary School (Form 1 to Form 5)'),
        ('preuniversity', 'Pre-University (STPM/Foundation/A-Levels)'),
        ('university', 'University/College'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    qualifications = models.TextField(blank=True, null=True)
    specializations = models.TextField(blank=True, null=True)
    teaching_experience = models.PositiveIntegerField(blank=True, null=True)
    certifications = models.TextField(blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    weekly_hours = models.PositiveIntegerField(blank=True, null=True)
    subjects_offered = models.TextField(blank=True, null=True)
    availability_schedule = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    youtube_link = models.URLField(max_length=500, blank=True, null=True)
       # Update image fields to be editable
    profile_image = models.BinaryField(null=True, blank=True, editable=True)
    image_name = models.CharField(max_length=255, null=True, blank=True)
    image_type = models.CharField(max_length=50, null=True, blank=True)
    
    # Updated school_level field to store multiple selections
    school_level = models.CharField(
        max_length=255,  # Increased max_length to accommodate multiple selections
        blank=True,
        null=True,
        help_text="Comma-separated list of school levels"
    )

    # Location fields
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    def clean_youtube_link(self):
        youtube_link = self.cleaned_data.get('youtube_link')
        pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$'
        if youtube_link and not re.match(pattern, youtube_link):
            raise ValidationError("Please enter a valid YouTube URL.")
        return youtube_link
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

    # Add helper methods for school_level handling
    def get_school_levels(self):
        """Return list of selected school levels"""
        if not self.school_level:
            return []
        return [level.strip() for level in self.school_level.split(',') if level.strip()]

    def set_school_levels(self, levels):
        """Set school levels from a list"""
        if not levels:
            self.school_level = ''
        else:
            self.school_level = ', '.join(levels)


class Rating(models.Model):
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # Values from 1 to 5
    review = models.TextField(blank=True, null=True)  # Optional review text
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tutor', 'user')  # Prevent multiple active ratings for same tutor-user pair
        ordering = ['-created_at']  # Order by most recent first

    def __str__(self):
        return f"Rating by {self.user.username} for {self.tutor.user.username} - {self.rating}/5"
    
    @classmethod
    def can_user_rate_tutor(cls, user, tutor):
        """
        Check if a user can rate a specific tutor based on the 3-month cooldown period.
        Returns True if the user can rate, False otherwise.
        """
        three_months_ago = timezone.now() - timedelta(days=90)
        last_rating = cls.objects.filter(
            user=user,
            tutor=tutor,
            created_at__gt=three_months_ago
        ).exists()
        return not last_rating

    def get_next_available_date(self):
        """
        Returns the date when the user can rate this tutor again.
        """
        return self.created_at + timedelta(days=90)
