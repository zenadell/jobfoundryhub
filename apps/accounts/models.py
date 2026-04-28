from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Career details
    current_title = models.CharField(max_length=200, blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    degree = models.CharField(max_length=200, blank=True)
    university = models.CharField(max_length=200, blank=True)
    skills = models.TextField(blank=True)  # Comma-separated
    
    # Resume
    resume = models.FileField(upload_to='resumes/', blank=True)
    resume_public = models.BooleanField(default=False)
    
    # Social
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    
    # Saved jobs
    saved_jobs = models.ManyToManyField('jobs.Job', blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
