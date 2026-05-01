from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone


class PublishedPostManager(models.Manager):
    """Returns only live posts (excludes trashed)."""
    def get_queryset(self):
        return super().get_queryset().exclude(status='trashed')

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    meta_title = models.CharField(max_length=200)
    meta_description = models.TextField(max_length=500)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Blog Categories"

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('trashed', 'Trashed'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Content
    excerpt = models.TextField(max_length=300)
    content = models.TextField()  # HTML content
    featured_image = models.ImageField(upload_to='blog/images/', blank=True, null=True)
    read_time = models.PositiveIntegerField(default=1)  # minutes, auto-calculated
    
    # SEO
    meta_title = models.CharField(max_length=200)
    meta_description = models.TextField(max_length=500)
    focus_keyword = models.CharField(max_length=200)
    
    # Status
    status = models.CharField(choices=STATUS_CHOICES, max_length=20)
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)
    
    # Soft delete
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Managers
    objects = models.Manager()            # default — includes trashed (for admin)
    live    = PublishedPostManager()       # excludes trashed (for public site)
    
    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
