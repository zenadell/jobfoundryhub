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
    
    monetag_head_script  = models.TextField(blank=True, help_text='Paste the Monetag JS snippet here (Vignette or In-Page Push)')
    monetag_enabled      = models.BooleanField(default=False, help_text='Enable Monetag ads on the site')
    
    # How It Works Video Embeds (YouTube, Vimeo, etc.)
    hiw_video_embed_seekers = models.TextField(blank=True, help_text='YouTube iframe embed code for Job Seekers')
    hiw_video_embed_employers = models.TextField(blank=True, help_text='YouTube iframe embed code for Employers')
    
    # How It Works Video Uploads (Local/Cloudinary)
    # We use VideoMediaCloudinaryStorage to ensure Cloudinary treats it as a video (resource_type='video')
    from django.conf import settings
    
    if getattr(settings, 'CLOUDINARY_STORAGE', {}).get('CLOUD_NAME'):
        from cloudinary_storage.storage import VideoMediaCloudinaryStorage
        storage_backend = VideoMediaCloudinaryStorage()
    else:
        storage_backend = None

    hiw_video_file_seekers = models.FileField(upload_to='videos/hiw/', storage=storage_backend, blank=True, null=True, help_text='Upload a video file for Job Seekers')
    hiw_video_file_employers = models.FileField(upload_to='videos/hiw/', storage=storage_backend, blank=True, null=True, help_text='Upload a video file for Employers')
    
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

    def get_seeker_video_html(self):
        return self._process_video_html(self.hiw_video_embed_seekers)

    def get_employer_video_html(self):
        return self._process_video_html(self.hiw_video_embed_employers)

    def _process_video_html(self, raw_input):
        if not raw_input:
            return ""
        
        # If it's already an iframe, just return it
        if '<iframe' in raw_input.lower():
            return raw_input

        # If it's a raw YouTube URL, convert to iframe
        import re
        yt_regex = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})'
        match = re.search(yt_regex, raw_input)
        
        if match:
            video_id = match.group(4)
            return (
                f'<iframe src="https://www.youtube-nocookie.com/embed/{video_id}?enablejsapi=1" '
                f'frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
                f'allowfullscreen referrerpolicy="strict-origin-when-cross-origin" '
                f'style="width:100%;height:100%;"></iframe>'
            )
            
        # If it's a direct video link (.mp4, .webm), convert to video tag
        if raw_input.strip().lower().endswith(('.mp4', '.webm', '.mov', '.avi')):
            return (
                f'<video muted controls class="hiw-uploaded-video" style="position:absolute;top:0;left:0;width:100%;height:100%;">'
                f'<source src="{raw_input.strip()}" type="video/mp4">'
                f'Your browser does not support the video tag.'
                f'</video>'
            )
            
        return raw_input  # Fallback if it's not a recognized URL but not an iframe


class HowItWorksStep(models.Model):
    CATEGORY_CHOICES = [
        ('seekers', 'For Job Seekers'),
        ('employers', 'For Employers'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'order']
        verbose_name = 'How It Works Step'
        verbose_name_plural = 'How It Works Steps'

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"
