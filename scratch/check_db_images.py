import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.blog.models import Post

for post in Post.objects.all():
    print(f"Title: {post.title}")
    print(f"Featured Image Field: {post.featured_image}")
    if post.featured_image:
        try:
            print(f"Featured Image URL: {post.featured_image.url}")
        except Exception as e:
            print(f"Error getting URL: {e}")
    print("-" * 20)
