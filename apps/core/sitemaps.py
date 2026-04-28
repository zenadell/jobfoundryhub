from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.jobs.models import Job
from apps.blog.models import Post

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['core:home', 'core:about', 'core:contact', 'core:faq', 'core:pricing', 'core:privacy', 'core:terms']

    def location(self, item):
        return reverse(item)

class ServiceViewSitemap(Sitemap):
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        return [
            'services:overview',
            'services:curated_jobs',
            'services:career_launch',
            'services:resume_review',
            'services:interview_coaching',
            'services:salary_negotiation'
        ]

    def location(self, item):
        return reverse(item)

class JobSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Job.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.posted_at

class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.published_at
