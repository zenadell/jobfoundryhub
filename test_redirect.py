import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from django.shortcuts import redirect
try:
    redirect(None)
except Exception as e:
    print(f"Error: {e}")
