from django.db import models
from ckeditor.fields import RichTextField

class ContactMessage(models.Model):
    name       = models.CharField(max_length=100)
    email      = models.EmailField()
    subject    = models.CharField(max_length=200)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{'[READ] ' if self.is_read else '[NEW] '}{self.name} — {self.subject}"


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('job-seekers',  'For Job Seekers'),
        ('employers',    'For Employers'),
        ('platform',     'Platform & Account'),
        ('adsense',      'General'),
    ]
    question   = models.CharField(max_length=500)
    answer     = RichTextField()
    category   = models.CharField(choices=CATEGORY_CHOICES, max_length=30, default='job-seekers')
    order      = models.PositiveIntegerField(default=0)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'order']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question[:80]


class SiteSettings(models.Model):
    """
    Singleton model — only ONE row ever exists.
    Lets admin change hero text, site tagline, social links
    without touching code.
    """
    site_name      = models.CharField(max_length=100, default='Job Foundry Hub')
    site_tagline   = models.CharField(max_length=200, default='Entry-Level Jobs for Recent Graduates')
    hero_heading   = models.CharField(max_length=200, default='Launch Your Career with Confidence')
    hero_subtext   = models.TextField(default='Browse verified entry-level jobs curated for recent graduates.')
    hero_cta_text  = models.CharField(max_length=100, default='Browse All Jobs')
    about_intro    = RichTextField(blank=True)
    contact_email  = models.EmailField(default='support@jobfoundryhub.com')
    linkedin_url   = models.URLField(blank=True)
    twitter_url    = models.URLField(blank=True)
    instagram_url  = models.URLField(blank=True)
    ga_measurement_id    = models.CharField(max_length=50, blank=True, help_text='Google Analytics 4 Measurement ID, e.g. G-XXXXXXXXXX')
    adsense_publisher_id = models.CharField(max_length=50, blank=True, help_text='AdSense Publisher ID, e.g. pub-XXXXXXXXXXXXXXXX — only fill after approval')
    adsense_enabled      = models.BooleanField(default=False, help_text='ONLY enable after AdSense application is approved')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'

    def save(self, *args, **kwargs):
        # Enforce singleton — only one row allowed
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
