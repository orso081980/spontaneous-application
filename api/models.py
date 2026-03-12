"""
Django Models for the Spontaneous Job Board
Compatible with both SQLite and MongoDB backends
"""
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Check if we're using MongoDB backend
try:
    from django_mongodb_backend.fields import ObjectIdAutoField
    USING_MONGODB = True
except ImportError:
    USING_MONGODB = False


class Company(models.Model):
    """
    Company model - represents companies in the job board
    """
    if USING_MONGODB:
        id = ObjectIdAutoField(primary_key=True)
    # For SQLite, use default AutoField
    
    name = models.CharField(max_length=200)
    field = models.CharField(max_length=200)  # e.g., "Software Development"
    website = models.URLField()
    contact = models.EmailField(blank=True, null=True)  # Contact email
    contact_form_url = models.URLField(blank=True, null=True)  # Contact form URL
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=500)  # Full address — format: "Street, City PostalCode, Country"
    city = models.CharField(max_length=200, blank=True, null=True)    # Parsed from address (part 2)
    country = models.CharField(max_length=200, blank=True, null=True) # Parsed from address (part 3)
    vat_number = models.CharField(max_length=50, blank=True, null=True)  # VAT number
    description = models.TextField(blank=True, null=True)  # Brief company description (rich text from Quill)
    potential_improvement = models.TextField(blank=True, null=True)  # Potential improvements
    logo_url = models.URLField()  # Company logo URL
    plus_code = models.CharField(max_length=50, blank=True, null=True)  # Google Plus Code
    latitude = models.CharField(max_length=50, blank=True, null=True)  # Latitude
    longitude = models.CharField(max_length=50, blank=True, null=True)  # Longitude
    technologies = models.TextField(blank=True, null=True)  # Comma-separated list
    
    # Social media fields
    linkedin_url = models.URLField(blank=True, null=True)
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        if USING_MONGODB:
            db_table = 'companies'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.field}"


class UserProfile(models.Model):
    """
    User Profile model - basic user information linked to Django User
    """
    if USING_MONGODB:
        id = ObjectIdAutoField(primary_key=True)
    # For SQLite, use default AutoField
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=200)
    job_position = models.CharField(max_length=200)
    email = models.EmailField()  # Remove unique=True temporarily to avoid conflicts
    bio = models.TextField(blank=True, null=True)  # Rich text from Quill editor
    phone = models.CharField(max_length=50, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        if USING_MONGODB:
            db_table = 'user_profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.job_position}"


class JobApplication(models.Model):
    """
    Model for user applications to companies with project suggestions
    """
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('sent', 'Sent'),
        ('interview', 'Interview State'),
        ('accepted', 'Accepted'),
        ('refused', 'Refused'),
    ]
    
    if USING_MONGODB:
        id = ObjectIdAutoField(primary_key=True)
    # For SQLite, use default AutoField
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='applications')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='applications')
    position = models.CharField(max_length=200, blank=True, null=True)  # Position proposing for
    project_to_suggest = models.TextField()  # Rich text - project description (mandatory)
    link_to_project = models.URLField(blank=True, null=True)  # Link to project or portfolio
    message = models.TextField(blank=True, null=True)  # Letter of introduction
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        if USING_MONGODB:
            db_table = 'job_applications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Application {self.id} - {self.status}"
