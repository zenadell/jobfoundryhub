import os
import django
import traceback
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

c = Client()
try:
    response = c.get('/blog/')
    print('Status:', response.status_code)
    if response.status_code == 500:
        print("Server returned 500. Traceback might not be captured by test client directly without setting DEBUG=True.")
except Exception as e:
    traceback.print_exc()
