# 📋 LEAD MANAGER AUDIT REPORT
### Career Builders Hub — Full Review
### Date: April 2026 | Status: NEEDS FIXES BEFORE LAUNCH

---

## OVERALL VERDICT

The project has a **solid foundation** — architecture is correct, Django 
structure is clean, settings are well-organised, and the right apps exist.
However there are **critical bugs that will crash the site**, templates still 
containing Webflow CDN URLs, and several planned features that are completely 
missing. None of these are hard to fix. Work through this list top to bottom.

---

## 🔴 CRITICAL — FIX THESE FIRST (will crash or break the site)

---

### CRIT-1: requirements/base.txt IS EMPTY
**File:** `requirements/base.txt`  
**Problem:** The file has zero content. No dependencies are listed. 
Anyone who clones this project and runs `pip install -r requirements/base.txt` 
installs nothing. The project won't even start.

**Fix — add this to requirements/base.txt:**
```
Django==5.2
django-environ==0.11.2
psycopg2-binary==2.9.9
Pillow==10.3.0
whitenoise==6.7.0
gunicorn==22.0.0
django-htmx==1.19.0
django-ckeditor==6.7.0
django-extensions==3.2.3
djangorestframework==3.15.2
django-cors-headers==4.4.0
django-storages==1.14.3
boto3==1.34.100
celery==5.4.0
redis==5.0.4
django-crispy-forms==2.3
```

---

### CRIT-2: get_absolute_url MISSING on Job, Post, and Company
**Files:** `apps/jobs/models.py`, `apps/blog/models.py`  
**Problem:** The sitemap classes call `get_absolute_url()` on every Job and Post 
object. Without it, `sitemap.xml` will throw a `AttributeError` and crash.
Templates that use `{{ job.get_absolute_url }}` will also fail silently.

**Fix — add to Job model:**
```python
from django.urls import reverse

def get_absolute_url(self):
    return reverse('jobs:job_detail', kwargs={'slug': self.slug})
```

**Fix — add to Company model:**
```python
def get_absolute_url(self):
    return reverse('jobs:company_detail', kwargs={'slug': self.slug})
```

**Fix — add to Post model:**
```python
def get_absolute_url(self):
    return reverse('blog:post_detail', kwargs={'slug': self.slug})
```

---

### CRIT-3: Company model missing is_active field
**File:** `apps/jobs/models.py`  
**Problem:** `core/views.py` home view calls 
`Company.objects.filter(is_active=True).count()` for the stats. 
The Company model has no `is_active` field. This will crash the homepage.

**Fix — add to Company model:**
```python
is_active = models.BooleanField(default=True)
```
Then run `python manage.py makemigrations && python manage.py migrate`.

---

### CRIT-4: Job fields missing blank=True — will break forms
**File:** `apps/jobs/models.py`  
**Problem:** `remote_type` and `salary_period` have no `blank=True`. 
These are not always required (a remote job doesn't need remote_type, 
salary fields can be empty). Without `blank=True`, any form submission 
or admin save without these fields will fail validation.

**Fix:**
```python
remote_type  = models.CharField(choices=REMOTE_CHOICES, max_length=20, blank=True)
salary_period = models.CharField(choices=SALARY_PERIOD_CHOICES, max_length=20, blank=True)
```

---

### CRIT-5: accounts/views.py is completely empty
**File:** `apps/accounts/views.py`  
**Problem:** The file only has `from django.shortcuts import render` and nothing 
else. No login, no register, no logout, no dashboard. The navbar in base.html 
references `{% url 'accounts:login' %}`, `{% url 'accounts:register' %}`, and 
`{% url 'accounts:dashboard' %}` — these will all throw `NoReverseMatch` errors 
and crash every single page that uses base.html (which is all of them).

**Fix — minimum required views for the site to not crash:**
```python
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def register(request):
    if request.method == 'POST':
        username  = request.POST.get('username')
        email     = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'accounts/register.html')
        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, 'Welcome! Your account has been created.')
        return redirect('core:home')
    return render(request, 'accounts/register.html')

def user_login(request):
    if request.method == 'POST':
        email    = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'accounts:dashboard'))
        messages.error(request, 'Invalid email or password.')
    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)
    return redirect('core:home')

@login_required
def dashboard(request):
    from apps.accounts.models import UserProfile
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    saved_jobs  = profile.saved_jobs.filter(is_active=True).select_related('company')[:6]
    return render(request, 'accounts/dashboard.html', {
        'profile': profile,
        'saved_jobs': saved_jobs,
    })
```

**Also add accounts/urls.py if not already complete:**
```python
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/',  views.register,   name='register'),
    path('login/',     views.user_login,  name='login'),
    path('logout/',    views.user_logout, name='logout'),
    path('dashboard/', views.dashboard,   name='dashboard'),
]
```

**Register in config/urls.py:**
```python
path('accounts/', include('apps.accounts.urls')),
```

**Create these templates (minimum):**
- `templates/accounts/register.html`
- `templates/accounts/login.html`
- `templates/accounts/dashboard.html`

---

### CRIT-6: Post model missing updated_at field
**File:** `apps/blog/models.py`  
**Problem:** The blog detail template's structured data (JSON-LD) references 
`{{ post.updated_at }}`. The field does not exist. This will cause a template 
error on every blog post page.

**Fix — add to Post model:**
```python
updated_at = models.DateTimeField(auto_now=True)
```
Then run migrations.

---

## 🟠 BROKEN TEMPLATES — 15 pages still have Webflow CDN URLs

These pages are not clean. Every CDN URL is a broken image link in production 
AND a signal to Google that this is not original content.

Run the fix command, then manually verify each page:

```bash
# See exactly which lines still have CDN URLs in each file
grep -n "cdn.prod.website-files.com" templates/pages/about.html
grep -n "cdn.prod.website-files.com" templates/pages/contact.html
grep -n "cdn.prod.website-files.com" templates/pages/confirmation.html
grep -n "cdn.prod.website-files.com" templates/jobs/detail.html
grep -n "cdn.prod.website-files.com" templates/jobs/post_job.html
grep -n "cdn.prod.website-files.com" templates/jobs/submit_resume.html
grep -n "cdn.prod.website-files.com" templates/jobs/company_detail.html
grep -n "cdn.prod.website-files.com" templates/blog/list.html
grep -n "cdn.prod.website-files.com" templates/blog/detail.html
grep -n "cdn.prod.website-files.com" templates/components/job_card.html
grep -n "cdn.prod.website-files.com" templates/components/cta_newsletter.html
grep -n "cdn.prod.website-files.com" templates/404.html
grep -n "cdn.prod.website-files.com" templates/pages/coming_soon.html
grep -n "cdn.prod.website-files.com" templates/pages/licenses.html
grep -n "cdn.prod.website-files.com" templates/pages/changelog.html
```

For each CDN URL found, replace with the correct `{% static 'images/...' %}` 
reference. The image files are already downloaded in `static/images/`.

---

### Remaining "Better Talent" Branding
**Files:** `templates/pages/home.html`, `templates/jobs/list.html`, 
`templates/pages/coming_soon.html`

```bash
grep -n "Better Talent" templates/pages/home.html
grep -n "Better Talent" templates/jobs/list.html
grep -n "Better Talent" templates/pages/coming_soon.html
```

Replace every occurrence with `{{ site_name }}` or remove entirely.

---

## 🟡 MISSING FEATURES FROM THE PLAN

These are items in MASTER_PROJECT.md that are not yet built:

---

### MISS-1: Newsletter model is empty
**File:** `apps/newsletter/models.py`  
The model file only has a comment. The newsletter signup CTA appears on 
multiple pages and the footer. Without a model, submissions go nowhere.

**Fix:**
```python
from django.db import models

class NewsletterSubscriber(models.Model):
    email      = models.EmailField(unique=True)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-created_at']
```

Then add a view in `apps/newsletter/views.py`:
```python
from django.shortcuts import redirect
from django.contrib import messages
from .models import NewsletterSubscriber

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            NewsletterSubscriber.objects.get_or_create(email=email)
            messages.success(request, 'You are now subscribed!')
    return redirect(request.META.get('HTTP_REFERER', '/'))
```

Add URL in `apps/newsletter/urls.py` and wire it up in `config/urls.py`.

---

### MISS-2: ResumeSubmission model missing
**File:** `apps/jobs/views.py` — submit_resume has a `# TODO` comment  
Resume submissions currently save nowhere. Create a model:

```python
class ResumeSubmission(models.Model):
    full_name  = models.CharField(max_length=200)
    email      = models.EmailField()
    position   = models.CharField(max_length=200, blank=True)
    resume     = models.FileField(upload_to='resumes/')
    cover_note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_reviewed  = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.full_name} — {self.submitted_at.date()}"
```

Update `submit_resume` view to save the submission properly.

---

### MISS-3: JobPostingRequest model missing
**File:** `apps/jobs/views.py` — post_job has a `# TODO` comment  
Job posting requests save nowhere. Create a model:

```python
class JobPostingRequest(models.Model):
    company_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=200)
    contact_email = models.EmailField()
    job_title    = models.CharField(max_length=300)
    job_description = models.TextField()
    job_location = models.CharField(max_length=200)
    job_type     = models.CharField(choices=JOB_TYPE_CHOICES, max_length=20)
    salary_range = models.CharField(max_length=100, blank=True)
    apply_url    = models.URLField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        choices=[('pending','Pending'),('approved','Approved'),('rejected','Rejected')],
        default='pending', max_length=20
    )
    
    def __str__(self):
        return f"{self.job_title} @ {self.company_name}"
```

---

### MISS-4: active_jobs_count missing on Company
**File:** `apps/jobs/models.py`  
Templates reference `{{ company.active_jobs_count }}` but this property 
does not exist on the model.

**Fix — add property to Company model:**
```python
@property
def active_jobs_count(self):
    return self.job_set.filter(is_active=True).count()
```

---

### MISS-5: Missing settings variables
**File:** `config/settings/base.py`  
These are referenced in `context_processors.py` and templates but not 
defined in settings:

```python
GA_MEASUREMENT_ID    = env('GA_MEASUREMENT_ID', default='')
ADSENSE_PUBLISHER_ID = env('ADSENSE_PUBLISHER_ID', default='')
SOCIAL_LINKEDIN      = env('SOCIAL_LINKEDIN', default='')
SOCIAL_TWITTER       = env('SOCIAL_TWITTER', default='')
SOCIAL_INSTAGRAM     = env('SOCIAL_INSTAGRAM', default='')
EMAIL_BACKEND        = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
DEFAULT_FROM_EMAIL   = env('DEFAULT_FROM_EMAIL', default='hello@careerbuildershub.com')
```

---

### MISS-6: ads.txt publisher ID not set
**File:** `templates/ads.txt`  
The ads.txt file exists (good) but the publisher ID is still a placeholder.
This must be updated with the real AdSense publisher ID before applying.
Leave it as a placeholder for now but add a comment so it's not forgotten:

```
# IMPORTANT: Replace XXXXXXXXXXXXXXXXX with your actual AdSense Publisher ID
# Get this from: adsense.google.com → Account → Account information
google.com, pub-XXXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0
```

---

### MISS-7: Sitemap priority for blog posts is too low
**File:** `apps/core/sitemaps.py`  
`PostSitemap` has `priority = 0.7`. Blog posts are the most important 
content for AdSense approval — they should have the highest priority.

**Fix:**
```python
class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9  # was 0.7 — blog posts are primary AdSense content
```

---

### MISS-8: Blog posts from MASTER_PROJECT.md not yet loaded
**Status:** The `load_initial_blog_posts` management command exists 
but the 20 articles have not been confirmed as loaded.

**Action:** After fixing CRIT issues, run:
```bash
python manage.py load_initial_blog_posts
```
Verify in Django admin that all 20 posts are published with correct 
categories, slugs, and meta descriptions.

---

### MISS-9: Utility pages that should not be in a live site
**Files to DELETE or restrict to admin only:**
- `templates/pages/style_guide.html` — Webflow design utility, has Lorem ipsum
- `templates/pages/licenses.html` — Webflow license page, has CDN URLs  
- `templates/pages/changelog.html` — Webflow changelog

These pages are currently routed and publicly accessible. They will hurt 
AdSense review if a Google reviewer lands on them. Either delete them and 
remove their URL routes, or protect them with `@staff_member_required`.

---

## 🟢 WHAT IS WORKING WELL

These are done correctly — do not change:

- ✅ Django project structure matches MASTER_PROJECT.md exactly
- ✅ All 6 apps created and registered correctly
- ✅ Settings split into base/development/production correctly
- ✅ Production security settings all in place (HSTS, SSL redirect, etc.)
- ✅ WhiteNoise configured correctly
- ✅ Context processor wired up and returning correct variables
- ✅ Sitemap classes exist for all content types
- ✅ robots.txt and ads.txt served as template views (correct approach)
- ✅ All service page templates clean (0 CDN URLs, 0 Lorem ipsum)
- ✅ FAQ page clean ✅
- ✅ Privacy policy clean ✅
- ✅ Terms of service clean ✅
- ✅ Skeleton CSS file exists and is complete
- ✅ Blog management command (`load_initial_blog_posts`) exists
- ✅ Seed data command exists for development
- ✅ CORS, HTMX, CKEditor, django-humanize all in INSTALLED_APPS
- ✅ ContactMessage model exists and contact view saves to DB
- ✅ Google Analytics placeholder in base.html
- ✅ AdSense placeholder commented out (correct — leave until approval)
- ✅ FBV used throughout (as instructed — consistent and readable)

---

## 📋 PRIORITY FIX ORDER

Work through in this exact order:

**Today — stops the crashes:**
1. CRIT-1: Fill requirements/base.txt
2. CRIT-3: Add `is_active` to Company model + migrate
3. CRIT-6: Add `updated_at` to Post model + migrate
4. CRIT-4: Add `blank=True` to Job remote_type + salary_period + migrate
5. CRIT-2: Add `get_absolute_url` to Job, Post, Company models
6. CRIT-5: Build accounts views + templates (login, register, dashboard)

**Next — cleans the content:**
7. Fix all 15 templates with remaining CDN URLs
8. Remove "Better Talent" from home.html, jobs/list.html, coming_soon.html
9. Delete or restrict style_guide, licenses, changelog pages

**Then — completes the features:**
10. MISS-1: Newsletter model + view + URL
11. MISS-2: ResumeSubmission model + update submit_resume view
12. MISS-3: JobPostingRequest model + update post_job view
13. MISS-4: active_jobs_count property on Company
14. MISS-5: Add missing settings variables
15. MISS-7: Fix PostSitemap priority to 0.9
16. MISS-8: Run load_initial_blog_posts, verify all 20 posts in admin

**Before AdSense submission:**
17. MISS-6: Set real publisher ID in ads.txt
18. Run the full AdSense checklist from MASTER_PROJECT.md Section 11
19. Lighthouse audit — fix anything below 90

---

## FINAL STAT

| Category | Count |
|----------|-------|
| Critical bugs (will crash) | 6 |
| Dirty templates (CDN URLs remain) | 15 |
| Missing features from plan | 9 |
| Pages clean and passing | 11 |
| Overall completion estimate | ~55% |

Target to be AdSense-ready: fix all critical bugs + clean templates + 
load 20 blog posts. That gets you to ~85%. The remaining missing features 
(newsletter, resume model, job request model) can ship after AdSense 
approval as they don't affect the review.

---

*Audit by: Claude (Lead Manager) | Career Builders Hub Project*
