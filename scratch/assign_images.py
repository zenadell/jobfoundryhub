import sys
import os
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from apps.blog.models import Post

posts = Post.objects.filter(featured_image="")
placeholders = ["blog/images/placeholder_1.png", "blog/images/placeholder_2.png", "blog/images/placeholder_3.png"]

for i, p in enumerate(posts):
    p.featured_image = placeholders[i % 3]
    p.save()
    print(f'Assigned {p.featured_image} to {p.title}')
