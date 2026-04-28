from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

# For local development, we can use sqlite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Optional: Disable password validation in dev for easier testing
AUTH_PASSWORD_VALIDATORS = []

# Optional: Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
