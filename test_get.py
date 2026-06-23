import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from apps.blog.models import Post
print(f"Posts count: {Post.objects.count()}")
