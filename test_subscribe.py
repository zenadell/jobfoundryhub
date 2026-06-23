import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")
django.setup()

from django.test import Client
c = Client(SERVER_NAME='localhost')
response = c.post('/newsletter/subscribe/', {'email': 'test2@example.com'})
print(f"Status Code: {response.status_code}")
if response.status_code >= 400:
    print(response.content)
