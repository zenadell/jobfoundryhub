import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from apps.newsletter.models import NewsletterSubscriber
try:
    NewsletterSubscriber.objects.create(email='test3@example.com')
    print("Created successfully!")
except Exception as e:
    print(f"Error: {repr(e)}")
