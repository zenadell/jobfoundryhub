from .base import *

DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['jobfoundryhub.com'])

# Security
SECURE_SSL_REDIRECT          = True
SESSION_COOKIE_SECURE        = True
CSRF_COOKIE_SECURE           = True
SECURE_BROWSER_XSS_FILTER    = True
SECURE_CONTENT_TYPE_NOSNIFF  = True
SECURE_HSTS_SECONDS          = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD          = True

# Trust Render's proxy for HTTPS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Static files via WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
