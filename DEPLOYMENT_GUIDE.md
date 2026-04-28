# 🚀 DEPLOYMENT GUIDE — Render + Turso + Cloudinary
### Career Builders Hub | jobfoundryhub.com
### Lead Manager: Claude | Status: READY TO DEPLOY

---

## WHAT THE AUDIT FOUND

The code is complete. But the project has NEVER been configured for 
Render + Turso + Cloudinary. The current setup still assumes:
- PostgreSQL (psycopg2 in requirements)
- Local file storage (media/ folder)
- VPS/Ubuntu deployment (nginx + gunicorn configs)
- No .gitignore (db.sqlite3 and real user PDFs are committed!)

Also: site_name in the DB is "Career linker Hub" — wrong name.
Must be fixed before launch.

Before you touch Render, Turso, or Cloudinary — do these fixes first.

---

## ⚠️ CRITICAL PRE-DEPLOYMENT FIXES

### FIX 1: Create .gitignore IMMEDIATELY
Real user resume PDFs are committed to your repo right now.
This is a data privacy violation. Fix this before pushing to GitHub.

Create `.gitignore` in the project root:
```
# Python
__pycache__/
*.py[cod]
*.pyo
.Python
*.pyc

# Environment
.env
.env.*
!.env.example

# Database — never commit SQLite
db.sqlite3
*.sqlite3

# Media files — served from Cloudinary in production
media/

# Static collected
staticfiles/

# Django
local_settings.py

# macOS
.DS_Store

# IDE
.vscode/
.idea/

# Logs
*.log

# Backup files
*.bak
*.css.bak
```

Then run:
```bash
git rm -r --cached media/
git rm --cached db.sqlite3
git add .gitignore
git commit -m "Remove committed media files and db, add gitignore"
```

---

### FIX 2: Fix site_name in SiteSettings
The DB has "Career linker Hub" — this will show on the live site.

After deployment, go to Django admin → Site Settings → change to
"Career Builders Hub" → save.

OR fix it now in the seed_data command before deploying:
```python
# In seed_data.py, find the SiteSettings.objects.get_or_create line
# and make sure defaults has:
'site_name': 'Career Builders Hub',
```

---

## STEP 1: ADD TURSO + CLOUDINARY TO REQUIREMENTS

Replace `requirements/base.txt` entirely:

```
Django==5.2
django-environ==0.11.2
Pillow==10.3.0
whitenoise==6.7.0
gunicorn==22.0.0
django-htmx==1.19.0
django-ckeditor==6.7.0
django-extensions==3.2.3
djangorestframework==3.15.2
django-cors-headers==4.4.0
django-storages==1.14.3
django-crispy-forms==2.3

# Turso / libSQL database
libsql-client==0.3.0

# Cloudinary media storage
cloudinary==1.40.0
django-cloudinary-storage==0.3.0
```

Note: `psycopg2-binary`, `boto3`, `celery`, `redis` all REMOVED.
We don't need PostgreSQL, S3, or Celery for this stack.

Also update `requirements/production.txt`:
```
-r base.txt
```

---

## STEP 2: UPDATE DATABASE SETTINGS FOR TURSO

Turso uses libSQL — not PostgreSQL. The current `env.db()` call
expects a Postgres URL format and will crash with a Turso URL.

### Update `config/settings/base.py`

Find the DATABASES block and replace it:

```python
# ── Database ──────────────────────────────────────────────────
# Uses Turso (libSQL) in production, SQLite in development
TURSO_DATABASE_URL = env('TURSO_DATABASE_URL', default='')
TURSO_AUTH_TOKEN   = env('TURSO_AUTH_TOKEN', default='')

if TURSO_DATABASE_URL:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'OPTIONS': {
                'uri': True,
            },
            # libsql-client handles the Turso connection
            'TURSO_DATABASE_URL': TURSO_DATABASE_URL,
            'TURSO_AUTH_TOKEN':   TURSO_AUTH_TOKEN,
        }
    }
else:
    # Local development — use SQLite file
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

**WAIT** — important note on Turso + Django:

Turso uses the `libsql` protocol. The cleanest way to connect Django 
to Turso is via the `libsql-django` backend. Update the DB block to:

```python
if TURSO_DATABASE_URL:
    DATABASES = {
        'default': {
            'ENGINE': 'libsql',
            'NAME': TURSO_DATABASE_URL,
            'OPTIONS': {
                'authToken': TURSO_AUTH_TOKEN,
                'tls': True,
            },
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

And update requirements to use the correct package:
```
# Replace libsql-client with:
libsql-django==0.1.6
```

---

## STEP 3: ADD CLOUDINARY STORAGE SETTINGS

Add this block to `config/settings/base.py`:

```python
# ── Cloudinary Media Storage ───────────────────────────────────
CLOUDINARY_CLOUD_NAME = env('CLOUDINARY_CLOUD_NAME', default='')
CLOUDINARY_API_KEY    = env('CLOUDINARY_API_KEY', default='')
CLOUDINARY_API_SECRET = env('CLOUDINARY_API_SECRET', default='')

if CLOUDINARY_CLOUD_NAME:
    import cloudinary
    cloudinary.config(
        cloud_name = CLOUDINARY_CLOUD_NAME,
        api_key    = CLOUDINARY_API_KEY,
        api_secret = CLOUDINARY_API_SECRET,
        secure     = True,
    )

    INSTALLED_APPS += ['cloudinary_storage', 'cloudinary']

    # All uploaded media goes to Cloudinary
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    
    # Static files — still served by WhiteNoise
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    # Local development — use local media folder
    MEDIA_URL  = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
```

Also add `cloudinary_storage` to INSTALLED_APPS in base.py.
Order matters — it must come before `django.contrib.staticfiles`:

```python
INSTALLED_APPS = [
    'cloudinary_storage',          # ADD — before staticfiles
    'django.contrib.staticfiles',
    # ... rest of apps
    'cloudinary',                  # ADD — at the end
]
```

---

## STEP 4: ADD HEALTH CHECK ENDPOINT (for UptimeRobot)

This is what keeps Render awake. Add a dead-simple view.

**Add to `apps/core/views.py`:**
```python
from django.http import JsonResponse

def health_check(request):
    """
    UptimeRobot pings this every 5 minutes.
    Keeps Render free tier from spinning down.
    Also verifies DB is reachable.
    """
    from apps.jobs.models import Job
    try:
        job_count = Job.objects.filter(is_active=True).count()
        return JsonResponse({
            'status': 'ok',
            'active_jobs': job_count,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'detail': str(e)}, status=500)
```

**Add to `apps/core/urls.py`:**
```python
path('health/', views.health_check, name='health_check'),
```

Test it locally: `http://localhost:8000/health/` should return:
```json
{"status": "ok", "active_jobs": 31}
```

---

## STEP 5: UPDATE .env.example

Replace with the Turso + Cloudinary version:

```env
# ── Django ────────────────────────────────────────────────────
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=jobfoundryhub.com,www.jobfoundryhub.com,your-app.onrender.com
DJANGO_SETTINGS_MODULE=config.settings.production

# ── Turso Database ────────────────────────────────────────────
# Get these from: turso auth login → turso db create jobfoundryhub
# → turso db show jobfoundryhub --url → turso db tokens create jobfoundryhub
TURSO_DATABASE_URL=libsql://jobfoundryhub-YOURNAME.turso.io
TURSO_AUTH_TOKEN=your-turso-jwt-token-here

# ── Cloudinary Media ─────────────────────────────────────────
# Get these from: cloudinary.com → Dashboard
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# ── Site ─────────────────────────────────────────────────────
SITE_NAME=Career Builders Hub
SITE_TAGLINE=Entry-Level Jobs for Recent Graduates
SITE_URL=https://jobfoundryhub.com

# ── Google ───────────────────────────────────────────────────
GA_MEASUREMENT_ID=G-XXXXXXXXXX
ADSENSE_PUBLISHER_ID=pub-XXXXXXXXXXXXXXXX

# ── Email ────────────────────────────────────────────────────
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=hello@jobfoundryhub.com

# ── Social ───────────────────────────────────────────────────
SOCIAL_LINKEDIN=
SOCIAL_TWITTER=
SOCIAL_INSTAGRAM=
```

---

## STEP 6: UPDATE PRODUCTION SETTINGS

Replace `config/settings/production.py` entirely:

```python
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
```

The `SECURE_PROXY_SSL_HEADER` line is critical for Render.
Without it, `SECURE_SSL_REDIRECT = True` will cause infinite redirect 
loops because Render terminates SSL at their load balancer, not at 
your app. This is the #1 Render deployment mistake.

---

## STEP 7: CREATE render.yaml

Create this file in the project root:

```yaml
services:
  - type: web
    name: jobfoundryhub
    env: python
    region: oregon
    plan: free
    buildCommand: |
      pip install -r requirements/base.txt &&
      python manage.py collectstatic --noinput &&
      python manage.py migrate &&
      python manage.py seed_data &&
      python manage.py load_initial_blog_posts
    startCommand: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
    envVars:
      - key: DJANGO_SETTINGS_MODULE
        value: config.settings.production
      - key: SECRET_KEY
        generateValue: true
      - key: ALLOWED_HOSTS
        value: jobfoundryhub.onrender.com,jobfoundryhub.com,www.jobfoundryhub.com
      - key: TURSO_DATABASE_URL
        sync: false
      - key: TURSO_AUTH_TOKEN
        sync: false
      - key: CLOUDINARY_CLOUD_NAME
        sync: false
      - key: CLOUDINARY_API_KEY
        sync: false
      - key: CLOUDINARY_API_SECRET
        sync: false
      - key: SITE_NAME
        value: Career Builders Hub
      - key: SITE_TAGLINE
        value: Entry-Level Jobs for Recent Graduates
      - key: SITE_URL
        value: https://jobfoundryhub.com
      - key: DEFAULT_FROM_EMAIL
        value: hello@jobfoundryhub.com
```

Variables marked `sync: false` are secrets — you'll fill them 
manually in Render dashboard, not in this file. Never commit 
real tokens to render.yaml.

---

## STEP 8: THE FULL DEPLOYMENT SEQUENCE

Do these in this exact order. Don't skip.

---

### 8A — Turso Setup (Terminal on your Mac)

```bash
# Install Turso CLI
brew install tursodatabase/tap/turso

# Login (opens browser)
turso auth login

# Create the database
turso db create jobfoundryhub

# Get your database URL — copy this
turso db show jobfoundryhub --url

# Create auth token — copy this  
turso db tokens create jobfoundryhub
```

Save both values. You need them in step 8D.

---

### 8B — Cloudinary Setup (Browser)

1. Go to cloudinary.com → Sign Up Free
2. Choose "Developer" account type
3. Dashboard → copy these three values:
   - Cloud name (e.g. `dxxxxxx`)
   - API Key (numbers)
   - API Secret (letters+numbers)

Save all three. You need them in step 8D.

---

### 8C — Push to GitHub

```bash
# Make sure you're in the project root
cd /path/to/your/project

# Initialize git if not already done
git init

# Make sure .gitignore exists (Step FIX 1 above)
# Then stage everything
git add .
git status  # verify media/ and db.sqlite3 are NOT listed

# Commit
git commit -m "feat: Career Builders Hub — ready for deployment"

# Create repo on github.com then:
git remote add origin https://github.com/YOURUSERNAME/jobfoundryhub.git
git branch -M main
git push -u origin main
```

---

### 8D — Render Setup (Browser)

1. Go to render.com → Sign Up with GitHub
2. New → Web Service → Connect your GitHub repo
3. Render will detect `render.yaml` automatically
4. Fill in the secret environment variables manually:
   - `TURSO_DATABASE_URL` → paste your Turso URL
   - `TURSO_AUTH_TOKEN`   → paste your Turso token
   - `CLOUDINARY_CLOUD_NAME` → paste cloud name
   - `CLOUDINARY_API_KEY`    → paste API key
   - `CLOUDINARY_API_SECRET` → paste API secret
5. Click **Create Web Service**
6. Watch the build logs — first deploy takes 3-5 minutes

**Watch for these in the build logs:**
```
✅ pip install — all packages installed
✅ collectstatic — X files copied
✅ migrate — all migrations applied
✅ seed_data — SiteSettings and FAQs created
✅ load_initial_blog_posts — 24 posts loaded
```

If you see an error → paste it here, I'll fix it immediately.

---

### 8E — Connect Custom Domain

1. Render dashboard → your service → Settings → Custom Domains
2. Add `jobfoundryhub.com` and `www.jobfoundryhub.com`
3. Render gives you a CNAME value, e.g. `jobfoundryhub.onrender.com`
4. Go to your domain registrar (where you bought jobfoundryhub.com)
5. DNS settings → add these records:

```
Type    Name    Value
CNAME   www     jobfoundryhub.onrender.com
CNAME   @       jobfoundryhub.onrender.com
```

(Some registrars use ALIAS or ANAME for the @ record if CNAME 
doesn't work on root domain)

6. SSL is automatic — Render issues the certificate within minutes
7. DNS propagation takes 10-30 minutes

---

### 8F — UptimeRobot Setup (keeps Render alive)

1. Go to uptimerobot.com → Sign Up Free
2. Add New Monitor:
   - Monitor Type: HTTP(s)
   - Friendly Name: JobFoundryHub Keep-Alive
   - URL: `https://jobfoundryhub.com/health/`
   - Monitoring Interval: Every 5 minutes
3. Click Create Monitor

That's it. UptimeRobot pings `/health/` every 5 minutes.
Render never sleeps. Your client never sees a cold start.

---

### 8G — Fix Site Name in Admin

1. Go to `https://jobfoundryhub.com/admin/`
2. Login with your superuser credentials
3. Core → Site Settings → click the row
4. Change Site Name from "Career linker Hub" to "Career Builders Hub"
5. Fill in Contact Email, social links if you have them
6. Save

---

### 8H — Upload Featured Images for 15 Blog Posts

1. Admin → Blog → Posts
2. Filter by: featured image is blank
3. For each post, click edit → upload a relevant image
   - Source: unsplash.com (free, no attribution needed)
   - Search: "job interview", "resume", "career", "office", "laptop"
   - Download → upload directly to that post
4. Images go to Cloudinary automatically — never lost on redeploy

---

### 8I — Google Search Console

1. Go to search.google.com/search-console
2. Add property → URL prefix → `https://jobfoundryhub.com`
3. Verify via HTML tag method:
   - Copy the meta tag Google gives you
   - In Django admin → Site Settings → paste it into 
     the `about_intro` field temporarily (or better — 
     add a `google_verification` field to SiteSettings)
   - OR: add it directly to base.html `<head>` block
4. Once verified → Sitemaps → submit:
   `https://jobfoundryhub.com/sitemap.xml`
5. URL Inspection → test homepage → Request Indexing

---

### 8J — Google Analytics 4

1. analytics.google.com → Create Account → Create Property
2. Choose Web → enter `jobfoundryhub.com`
3. Get Measurement ID (format: G-XXXXXXXXXX)
4. Django admin → Site Settings → paste into GA Measurement ID field
5. Analytics starts tracking immediately — no code deploy needed

---

## STEP 9: ADSENSE APPLICATION

Do NOT do this until:
- ✅ Site is live on jobfoundryhub.com with HTTPS
- ✅ All 24 blog posts are published with images
- ✅ Google Search Console verified and sitemap submitted
- ✅ Site has been live for at least 2 weeks (let Google index it)
- ✅ robots.txt and ads.txt are accessible
- ✅ Privacy Policy, Terms, About, Contact pages all working
- ✅ Lighthouse Performance score > 90

**When ready:**

1. Create a brand new Google account for your client
   - This account must have ZERO connection to careerbuilders.agency
   - New Gmail, new everything
   
2. Go to adsense.google.com → Sign in with new account
3. Enter website URL: `https://jobfoundryhub.com`
4. Get your Publisher ID (pub-XXXXXXXXXXXXXXXX)
5. Update `templates/ads.txt`:
   ```
   google.com, pub-YOURREALPUBLISHERID, DIRECT, f08c47fec0942fa0
   ```
6. Redeploy (just push to GitHub — Render auto-deploys)
7. In Django admin → Site Settings → paste publisher ID → 
   leave `adsense_enabled = False` ← DO NOT TURN THIS ON YET
8. Submit the AdSense application
9. Wait for approval email (typically 1-4 weeks)
10. Once approved → admin → Site Settings → adsense_enabled = True
    Ads go live automatically. No code change needed.

---

## CHECKLIST — Before You Tell Client Site is Live

```
Infrastructure:
□ Site loads on https://jobfoundryhub.com
□ www.jobfoundryhub.com redirects correctly
□ SSL certificate is valid (green padlock)
□ /health/ returns {"status": "ok"}
□ UptimeRobot is pinging /health/ every 5 minutes
□ Cloudinary dashboard shows uploaded images

Content:
□ All 24 blog posts published with images
□ 31 active jobs showing on /jobs/
□ 5 companies showing on /companies/
□ Site name shows "Career Builders Hub" everywhere
□ About, Contact, Privacy, Terms, FAQ all working

SEO:
□ /sitemap.xml loads and has all posts + jobs
□ /robots.txt loads correctly
□ /ads.txt loads (with placeholder pub ID for now)
□ Job detail page source has JobPosting JSON-LD
□ Blog post source has BlogPosting JSON-LD
□ Google Search Console verified + sitemap submitted

Admin:
□ /admin/ loads and is branded "Career Builders Hub"
□ Can create a test job → appears on /jobs/
□ Can create a test blog post → appears on /blog/
□ Site Settings shows correct site name + contact email

Adsense (separate timeline):
□ Wait 2 weeks after go-live before applying
□ New Google account created (fresh, no history)
□ Lighthouse Performance > 90
□ Apply when all above content checks pass
```

---

## COMMON RENDER ERRORS AND FIXES

**Error: `ModuleNotFoundError: No module named 'libsql'`**
Fix: Make sure `libsql-django` is in requirements/base.txt and 
Render has rebuilt since you added it. Clear build cache in 
Render settings and redeploy.

**Error: `SECURE_SSL_REDIRECT infinite loop`**
Fix: Make sure `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`
is in production.py. This is already in Step 6 above.

**Error: `DisallowedHost at /`**
Fix: Add your Render URL to ALLOWED_HOSTS in render.yaml:
`jobfoundryhub.onrender.com,jobfoundryhub.com,www.jobfoundryhub.com`

**Error: `cloudinary.exceptions.AuthorizationRequired`**
Fix: Check your CLOUDINARY_API_SECRET is correct in Render env vars.
Secrets are case-sensitive.

**Error: collectstatic fails**
Fix: Make sure `STATICFILES_DIRS` doesn't include a directory that 
doesn't exist. Check that `static/` folder is committed to git.

---

*Deployment Guide v1.0 | Career Builders Hub*
*Stack: Render + Turso + Cloudinary | Domain: jobfoundryhub.com*
