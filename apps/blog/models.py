from django.db import models
from django.conf import settings
from django.urls import reverse

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
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Content
    excerpt = models.TextField(max_length=300)
    content = models.TextField()  # HTML content
    featured_image = models.ImageField(upload_to='blog/images/')
    read_time = models.PositiveIntegerField()  # minutes, auto-calculated
    
    # SEO
    meta_title = models.CharField(max_length=200)
    meta_description = models.TextField(max_length=500)
    focus_keyword = models.CharField(max_length=200)
    
    # Status
    status = models.CharField(choices=[('draft','Draft'),('published','Published')], max_length=20)
    published_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
