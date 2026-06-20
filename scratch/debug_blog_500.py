import os
import django
import traceback
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
os.environ['ALLOWED_HOSTS'] = '*'
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_2lzWmf5RvypB@ep-crimson-lab-a4562j2e.us-east-1.aws.neon.tech/neondb?sslmode=require'
django.setup()

c = Client()
try:
    response = c.get('/blog/')
    print('Status:', response.status_code)
except Exception as e:
    traceback.print_exc()
