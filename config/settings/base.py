import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='django-insecure-secret-key-placeholder')

DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'cloudinary_storage',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.humanize',

    # Third-party
    'rest_framework',
    'corsheaders',
    'django_htmx',
    'ckeditor',
    'django_extensions',
    'storages',
    'anymail',

    # Local apps
    'apps.core',
    'apps.jobs',
    'apps.blog',
    'apps.accounts',
    'apps.services',
    'apps.newsletter',
    'apps.seo',
    'cloudinary',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'config.urls'

SITE_ID = 1

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ── Database ──────────────────────────────────────────────────
import dj_database_url

TURSO_DATABASE_URL = env('TURSO_DATABASE_URL', default='')
TURSO_AUTH_TOKEN = env('TURSO_AUTH_TOKEN', default='')
DATABASE_URL = env('DATABASE_URL', default='')

if TURSO_DATABASE_URL:
    DATABASES = {
        'default': {
            'ENGINE': 'libsql.db.backends.sqlite3',
            'NAME': TURSO_DATABASE_URL,
            'OPTIONS': {
                'auth_token': TURSO_AUTH_TOKEN,
            },
        }
    }
elif DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

AUTHENTICATION_BACKENDS = [
    'apps.accounts.backends.BypassAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
# Compat shim: django-cloudinary-storage 0.3.0 reads this directly
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ── Cloudinary Media Storage ───────────────────────────────────
CLOUDINARY_CLOUD_NAME = env('CLOUDINARY_CLOUD_NAME', default='')
CLOUDINARY_API_KEY = env('CLOUDINARY_API_KEY', default='')
CLOUDINARY_API_SECRET = env('CLOUDINARY_API_SECRET', default='')

if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
        'API_KEY': CLOUDINARY_API_KEY,
        'API_SECRET': CLOUDINARY_API_SECRET,
    }
    import cloudinary
    cloudinary.config(
        cloud_name = CLOUDINARY_STORAGE['CLOUD_NAME'],
        api_key    = CLOUDINARY_STORAGE['API_KEY'],
        api_secret = CLOUDINARY_STORAGE['API_SECRET'],
        secure     = True,
    )
    # Tell Django to use Cloudinary for all media uploads
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    # Use local media storage safely if keys are missing
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Local development fallback
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


CKEDITOR_UPLOAD_PATH = "uploads/"

SITE_NAME    = env('SITE_NAME', default='Job Foundry Hub')
SITE_TAGLINE = env('SITE_TAGLINE', default='Entry-Level Jobs for Recent Graduates')
SITE_URL     = env('SITE_URL', default='https://jobfoundryhub.com')

GA_MEASUREMENT_ID    = env('GA_MEASUREMENT_ID', default='')
ADSENSE_PUBLISHER_ID = env('ADSENSE_PUBLISHER_ID', default='')
SOCIAL_LINKEDIN      = env('SOCIAL_LINKEDIN', default='')
SOCIAL_TWITTER       = env('SOCIAL_TWITTER', default='')
SOCIAL_INSTAGRAM     = env('SOCIAL_INSTAGRAM', default='')

EMAIL_HOST           = env('EMAIL_HOST', default='smtp.hostinger.com')
EMAIL_PORT           = env.int('EMAIL_PORT', default=465)
EMAIL_USE_TLS        = env.bool('EMAIL_USE_TLS', default=False)
EMAIL_USE_SSL        = env.bool('EMAIL_USE_SSL', default=True)
EMAIL_HOST_USER      = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD  = env('EMAIL_HOST_PASSWORD', default='')

# ── Anymail (MailerSend/Brevo/SendGrid) ────────────────────────
MAILERSEND_API_KEY = env('MAILERSEND_API_KEY', default='')
BREVO_API_KEY      = env('BREVO_API_KEY', default='')
SENDGRID_API_KEY   = env('SENDGRID_API_KEY', default='')

if MAILERSEND_API_KEY:
    EMAIL_BACKEND = "anymail.backends.mailersend.EmailBackend"
    ANYMAIL = {
        "MAILERSEND_API_KEY": MAILERSEND_API_KEY,
    }
elif BREVO_API_KEY:
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
    ANYMAIL = {
        "BREVO_API_KEY": BREVO_API_KEY,
    }
elif SENDGRID_API_KEY:
    EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
    ANYMAIL = {
        "SENDGRID_API_KEY": SENDGRID_API_KEY,
    }
else:
    EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

EMAIL_TIMEOUT = 5  # Give up after 5 seconds to prevent site crash

DEFAULT_FROM_EMAIL   = env('DEFAULT_FROM_EMAIL', default='support@jobfoundryhub.com')
SUPPORT_EMAIL        = env('SUPPORT_EMAIL', default='support@jobfoundryhub.com')
