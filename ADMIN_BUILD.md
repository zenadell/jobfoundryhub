# 🛠️ ADMIN BUILD INSTRUCTIONS
### Career Builders Hub — Complete Admin System
### Lead Manager: Claude | Priority: HIGH

---

## THE GOAL OF THIS DOCUMENT

Build a complete Django admin system that lets the client:
- Post and manage jobs, companies, blog posts
- Control FAQs, site settings, and hero text from admin
- Review contact messages and resume submissions
- Manage newsletter subscribers
- See at a glance what's hurting or helping AdSense approval

**AdSense is the #1 business goal.** Every admin tool we build should
make it easier to publish quality content and harder to accidentally
publish thin or incomplete content that would get rejected.

---

## STEP 1: NEW MODELS TO CREATE

Create these models BEFORE touching any admin files.
Run `makemigrations` and `migrate` after each app's models are complete.

---

### 1A. apps/core/models.py — ADD these models

```python
from django.db import models

class ContactMessage(models.Model):
    # already exists — do not change
    name       = models.CharField(max_length=100)
    email      = models.EmailField()
    subject    = models.CharField(max_length=200)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)   # ADD THIS
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{'[READ] ' if self.is_read else '[NEW] '}{self.name} — {self.subject}"


class FAQ(models.Model):
    CATEGORY_CHOICES = [
        ('job-seekers',  'For Job Seekers'),
        ('employers',    'For Employers'),
        ('platform',     'Platform & Account'),
        ('adsense',      'General'),
    ]
    question   = models.CharField(max_length=500)
    answer     = models.TextField()
    category   = models.CharField(choices=CATEGORY_CHOICES, max_length=30, default='job-seekers')
    order      = models.PositiveIntegerField(default=0)
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'order']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question[:80]


class SiteSettings(models.Model):
    """
    Singleton model — only ONE row ever exists.
    Lets admin change hero text, site tagline, social links
    without touching code.
    """
    site_name      = models.CharField(max_length=100, default='Career Builders Hub')
    site_tagline   = models.CharField(max_length=200, default='Entry-Level Jobs for Recent Graduates')
    hero_heading   = models.CharField(max_length=200, default='Launch Your Career with Confidence')
    hero_subtext   = models.TextField(default='Browse verified entry-level jobs curated for recent graduates.')
    hero_cta_text  = models.CharField(max_length=100, default='Browse All Jobs')
    about_intro    = models.TextField(blank=True)
    contact_email  = models.EmailField(default='hello@careerbuildershub.com')
    linkedin_url   = models.URLField(blank=True)
    twitter_url    = models.URLField(blank=True)
    instagram_url  = models.URLField(blank=True)
    ga_measurement_id    = models.CharField(max_length=50, blank=True, help_text='Google Analytics 4 Measurement ID, e.g. G-XXXXXXXXXX')
    adsense_publisher_id = models.CharField(max_length=50, blank=True, help_text='AdSense Publisher ID, e.g. pub-XXXXXXXXXXXXXXXX — only fill after approval')
    adsense_enabled      = models.BooleanField(default=False, help_text='ONLY enable after AdSense application is approved')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return 'Site Settings'

    def save(self, *args, **kwargs):
        # Enforce singleton — only one row allowed
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
```

---

### 1B. apps/newsletter/models.py — REPLACE empty file

```python
from django.db import models

class NewsletterSubscriber(models.Model):
    email      = models.EmailField(unique=True)
    is_active  = models.BooleanField(default=True)
    source     = models.CharField(max_length=100, blank=True,
                     help_text='Where they subscribed from: homepage, blog, footer, etc.')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email
```

---

### 1C. apps/jobs/models.py — ADD these two models at the bottom

```python
class ResumeSubmission(models.Model):
    full_name    = models.CharField(max_length=200)
    email        = models.EmailField()
    position     = models.CharField(max_length=200, blank=True,
                       help_text='Job title or position they are applying for')
    resume       = models.FileField(upload_to='resumes/%Y/%m/')
    cover_note   = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_reviewed  = models.BooleanField(default=False)
    notes        = models.TextField(blank=True, help_text='Internal admin notes')

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.full_name} — {self.submitted_at.strftime('%Y-%m-%d')}"


class JobPostingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending Review'),
        ('approved', 'Approved — Published'),
        ('rejected', 'Rejected'),
    ]
    # Submitter info
    company_name   = models.CharField(max_length=200)
    contact_name   = models.CharField(max_length=200)
    contact_email  = models.EmailField()
    contact_phone  = models.CharField(max_length=30, blank=True)
    company_website = models.URLField(blank=True)

    # Job details
    job_title       = models.CharField(max_length=300)
    job_description = models.TextField()
    job_requirements = models.TextField(blank=True)
    job_location    = models.CharField(max_length=200)
    job_type        = models.CharField(choices=JOB_TYPE_CHOICES, max_length=20)
    is_remote       = models.BooleanField(default=False)
    salary_range    = models.CharField(max_length=100, blank=True)
    apply_url       = models.URLField(blank=True)

    # Admin workflow
    status     = models.CharField(choices=STATUS_CHOICES, max_length=20, default='pending')
    admin_notes = models.TextField(blank=True, help_text='Internal notes — not visible to submitter')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"[{self.status.upper()}] {self.job_title} @ {self.company_name}"
```

Also update `submit_resume` and `post_job` views to save to these models.

**Update apps/jobs/views.py submit_resume:**
```python
def submit_resume(request):
    if request.method == 'POST':
        from .models import ResumeSubmission
        ResumeSubmission.objects.create(
            full_name  = request.POST.get('full_name', ''),
            email      = request.POST.get('email', ''),
            position   = request.POST.get('position', ''),
            resume     = request.FILES.get('resume'),
            cover_note = request.POST.get('message', ''),
        )
        messages.success(request, 'Your resume has been submitted. We will be in touch soon.')
        return redirect('core:confirmation')
    return render(request, 'jobs/submit_resume.html')
```

**Update apps/jobs/views.py post_job:**
```python
def post_job(request):
    if request.method == 'POST':
        from .models import JobPostingRequest
        JobPostingRequest.objects.create(
            company_name     = request.POST.get('company_name', ''),
            contact_name     = request.POST.get('contact_name', ''),
            contact_email    = request.POST.get('contact_email', ''),
            contact_phone    = request.POST.get('contact_phone', ''),
            company_website  = request.POST.get('company_website', ''),
            job_title        = request.POST.get('job_title', ''),
            job_description  = request.POST.get('job_description', ''),
            job_requirements = request.POST.get('job_requirements', ''),
            job_location     = request.POST.get('job_location', ''),
            job_type         = request.POST.get('job_type', 'full-time'),
            is_remote        = request.POST.get('is_remote') == 'on',
            salary_range     = request.POST.get('salary_range', ''),
            apply_url        = request.POST.get('apply_url', ''),
        )
        messages.success(request, 'Your job posting has been submitted. Our team will review it within 24 hours.')
        return redirect('core:confirmation')
    return render(request, 'jobs/post_job.html')
```

---

## STEP 2: UPDATE CONTEXT PROCESSOR

The context processor must pull SiteSettings from DB, not from settings.py.
This means the admin can change hero text, site name, social links without
a code deploy.

**Replace apps/core/context_processors.py entirely:**

```python
from apps.jobs.models import JobCategory

def site_context(request):
    from apps.core.models import SiteSettings
    settings_obj = SiteSettings.get()

    return {
        # From DB — admin-controlled
        'site_name':             settings_obj.site_name,
        'site_tagline':          settings_obj.site_tagline,
        'hero_heading':          settings_obj.hero_heading,
        'hero_subtext':          settings_obj.hero_subtext,
        'hero_cta_text':         settings_obj.hero_cta_text,
        'contact_email':         settings_obj.contact_email,
        'GA_MEASUREMENT_ID':     settings_obj.ga_measurement_id,
        'ADSENSE_PUBLISHER_ID':  settings_obj.adsense_publisher_id,
        'ADSENSE_ENABLED':       settings_obj.adsense_enabled,
        'social': {
            'linkedin':  settings_obj.linkedin_url,
            'twitter':   settings_obj.twitter_url,
            'instagram': settings_obj.instagram_url,
        },
        # From DB — navigation
        'footer_categories': JobCategory.objects.all()[:6],
    }
```

**Update base.html AdSense block to use ADSENSE_ENABLED:**
```html
{% if ADSENSE_ENABLED and ADSENSE_PUBLISHER_ID %}
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={{ ADSENSE_PUBLISHER_ID }}"
     crossorigin="anonymous"></script>
{% endif %}
```

---

## STEP 3: BUILD ALL ADMIN FILES

---

### apps/jobs/admin.py — REPLACE entirely

```python
import json
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.http import HttpResponseRedirect
from .models import (
    Company, JobCategory, Job, JobAlert,
    ResumeSubmission, JobPostingRequest
)


# ─────────────────────────────────────────
#  COMPANY
# ─────────────────────────────────────────

class JobInline(admin.TabularInline):
    model = Job
    extra = 0
    fields = ('title', 'job_type', 'is_active', 'is_featured', 'expires_at')
    readonly_fields = ('title',)
    show_change_link = True
    can_delete = False


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display  = ('logo_preview', 'name', 'industry', 'size',
                     'location', 'is_verified', 'is_active', 'active_jobs_badge', 'created_at')
    list_display_links = ('name',)
    list_editable = ('is_verified', 'is_active')
    list_filter   = ('is_verified', 'is_active', 'industry', 'size')
    search_fields = ('name', 'description', 'location', 'industry')
    prepopulated_fields = {'slug': ('name',)}
    inlines       = [JobInline]
    actions       = ['verify_companies', 'unverify_companies',
                     'activate_companies', 'deactivate_companies']

    fieldsets = (
        ('Company Information', {
            'fields': ('name', 'slug', 'logo', 'website', 'industry', 'size', 'location')
        }),
        ('About', {
            'fields': ('description',)
        }),
        ('Status', {
            'fields': ('is_verified', 'is_active'),
            'classes': ('collapse',)
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="width:36px;height:36px;object-fit:contain;border-radius:4px;">',
                obj.logo.url
            )
        return format_html('<span style="color:#ccc;">No logo</span>')
    logo_preview.short_description = 'Logo'

    def active_jobs_badge(self, obj):
        count = obj.job_set.filter(is_active=True).count()
        colour = '#2ecc71' if count > 0 else '#e74c3c'
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:100px;font-size:11px;font-weight:600;">{} jobs</span>',
            colour, count
        )
    active_jobs_badge.short_description = 'Active Jobs'

    @admin.action(description='✅ Mark selected companies as Verified')
    def verify_companies(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f'{updated} companies marked as verified.')

    @admin.action(description='❌ Remove Verified status')
    def unverify_companies(self, request, queryset):
        queryset.update(is_verified=False)

    @admin.action(description='👁️ Activate companies')
    def activate_companies(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='🚫 Deactivate companies')
    def deactivate_companies(self, request, queryset):
        queryset.update(is_active=False)


# ─────────────────────────────────────────
#  JOB CATEGORY
# ─────────────────────────────────────────

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'slug', 'live_job_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def live_job_count(self, obj):
        count = Job.objects.filter(category=obj, is_active=True).count()
        return format_html(
            '<a href="{}?category__id__exact={}">{} live jobs</a>',
            reverse('admin:jobs_job_changelist'), obj.pk, count
        )
    live_job_count.short_description = 'Live Jobs'


# ─────────────────────────────────────────
#  JOB
# ─────────────────────────────────────────

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display  = ('title', 'company_link', 'category', 'job_type',
                     'location_or_remote', 'salary_display',
                     'status_badge', 'is_featured', 'expires_badge', 'posted_at')
    list_display_links = ('title',)
    list_editable = ('is_featured',)
    list_filter   = ('is_active', 'is_featured', 'job_type',
                     'experience_level', 'is_remote', 'category')
    search_fields = ('title', 'company__name', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'posted_at'
    actions = ['activate_jobs', 'deactivate_jobs',
               'feature_jobs', 'unfeature_jobs', 'extend_30_days']

    fieldsets = (
        ('Job Details', {
            'fields': (
                'title', 'slug', 'company', 'category',
                'description', 'requirements'
            )
        }),
        ('Location & Type', {
            'fields': (
                'location', 'region', 'country',
                'is_remote', 'remote_type',
                'job_type', 'experience_level'
            )
        }),
        ('Salary', {
            'fields': ('salary_min', 'salary_max', 'salary_currency', 'salary_period'),
            'classes': ('collapse',)
        }),
        ('Application', {
            'fields': ('apply_url',)
        }),
        ('Status & Visibility', {
            'fields': ('is_active', 'is_featured', 'expires_at'),
            'description': (
                '⚠️ AdSense note: only keep high-quality, complete job listings '
                'active. Thin or expired listings hurt content quality score.'
            )
        }),
        ('Stats (read-only)', {
            'fields': ('views_count', 'applications_count'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('views_count', 'applications_count', 'posted_at')

    # ── Google for Jobs schema preview ──────────────
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('posted_at',)
        return self.readonly_fields

    def company_link(self, obj):
        url = reverse('admin:jobs_company_change', args=[obj.company.pk])
        return format_html('<a href="{}">{}</a>', url, obj.company.name)
    company_link.short_description = 'Company'

    def location_or_remote(self, obj):
        if obj.is_remote:
            return format_html(
                '<span style="background:#e8f5e9;color:#2e7d32;padding:2px 8px;'
                'border-radius:100px;font-size:11px;">🌐 Remote</span>'
            )
        return obj.location
    location_or_remote.short_description = 'Location'

    def salary_display(self, obj):
        if obj.salary_min:
            return f'${int(obj.salary_min):,}' + (f' – ${int(obj.salary_max):,}' if obj.salary_max else '')
        return format_html('<span style="color:#ccc;">—</span>')
    salary_display.short_description = 'Salary'

    def status_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background:#2ecc71;color:white;padding:2px 8px;'
                'border-radius:100px;font-size:11px;font-weight:600;">LIVE</span>'
            )
        return format_html(
            '<span style="background:#e74c3c;color:white;padding:2px 8px;'
            'border-radius:100px;font-size:11px;font-weight:600;">OFF</span>'
        )
    status_badge.short_description = 'Status'

    def expires_badge(self, obj):
        now = timezone.now()
        diff = obj.expires_at - now
        days = diff.days
        if days < 0:
            return format_html(
                '<span style="color:#e74c3c;font-weight:600;">Expired {}</span>',
                obj.expires_at.strftime('%b %d')
            )
        elif days <= 7:
            return format_html(
                '<span style="color:#f39c12;font-weight:600;">⚠️ {} days left</span>',
                days
            )
        return format_html('<span style="color:#27ae60;">{} days</span>', days)
    expires_badge.short_description = 'Expires'

    @admin.action(description='✅ Activate selected jobs')
    def activate_jobs(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} jobs activated.')

    @admin.action(description='🚫 Deactivate selected jobs')
    def deactivate_jobs(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} jobs deactivated.')

    @admin.action(description='⭐ Feature selected jobs')
    def feature_jobs(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} jobs featured.')

    @admin.action(description='Remove featured status')
    def unfeature_jobs(self, request, queryset):
        queryset.update(is_featured=False)

    @admin.action(description='📅 Extend expiry by 30 days')
    def extend_30_days(self, request, queryset):
        for job in queryset:
            job.expires_at = max(job.expires_at, timezone.now()) + timezone.timedelta(days=30)
            job.save(update_fields=['expires_at'])
        self.message_user(request, f'{queryset.count()} job expiry dates extended.')


# ─────────────────────────────────────────
#  JOB ALERT
# ─────────────────────────────────────────

@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    list_display  = ('email', 'keywords', 'location', 'job_type', 'is_active', 'created_at')
    list_filter   = ('is_active', 'job_type')
    search_fields = ('email', 'keywords', 'location')
    actions       = ['activate_alerts', 'deactivate_alerts']

    @admin.action(description='✅ Activate selected alerts')
    def activate_alerts(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='🚫 Deactivate selected alerts')
    def deactivate_alerts(self, request, queryset):
        queryset.update(is_active=False)


# ─────────────────────────────────────────
#  RESUME SUBMISSION
# ─────────────────────────────────────────

@admin.register(ResumeSubmission)
class ResumeSubmissionAdmin(admin.ModelAdmin):
    list_display  = ('full_name', 'email', 'position', 'resume_link',
                     'reviewed_badge', 'submitted_at')
    list_filter   = ('is_reviewed',)
    search_fields = ('full_name', 'email', 'position')
    readonly_fields = ('full_name', 'email', 'position',
                       'resume', 'cover_note', 'submitted_at')
    actions = ['mark_reviewed']

    fieldsets = (
        ('Submission', {
            'fields': ('full_name', 'email', 'position', 'resume', 'cover_note', 'submitted_at')
        }),
        ('Admin', {
            'fields': ('is_reviewed', 'notes')
        }),
    )

    def resume_link(self, obj):
        if obj.resume:
            return format_html('<a href="{}" target="_blank">📄 Download</a>', obj.resume.url)
        return '—'
    resume_link.short_description = 'Resume'

    def reviewed_badge(self, obj):
        if obj.is_reviewed:
            return format_html(
                '<span style="background:#2ecc71;color:white;padding:2px 8px;'
                'border-radius:100px;font-size:11px;">Reviewed</span>'
            )
        return format_html(
            '<span style="background:#f39c12;color:white;padding:2px 8px;'
            'border-radius:100px;font-size:11px;">Pending</span>'
        )
    reviewed_badge.short_description = 'Status'

    @admin.action(description='✅ Mark selected as reviewed')
    def mark_reviewed(self, request, queryset):
        queryset.update(is_reviewed=True)


# ─────────────────────────────────────────
#  JOB POSTING REQUEST
# ─────────────────────────────────────────

@admin.register(JobPostingRequest)
class JobPostingRequestAdmin(admin.ModelAdmin):
    list_display  = ('job_title', 'company_name', 'contact_email',
                     'job_type', 'status_badge', 'submitted_at', 'publish_action')
    list_filter   = ('status', 'job_type', 'is_remote')
    search_fields = ('job_title', 'company_name', 'contact_email')
    readonly_fields = ('submitted_at', 'reviewed_at', 'company_name', 'contact_name',
                       'contact_email', 'contact_phone', 'company_website',
                       'job_title', 'job_description', 'job_requirements',
                       'job_location', 'job_type', 'is_remote', 'salary_range', 'apply_url')
    actions = ['approve_requests', 'reject_requests']

    fieldsets = (
        ('Submitted Job Info', {
            'fields': (
                'company_name', 'contact_name', 'contact_email',
                'contact_phone', 'company_website',
                'job_title', 'job_description', 'job_requirements',
                'job_location', 'job_type', 'is_remote',
                'salary_range', 'apply_url'
            )
        }),
        ('Review', {
            'fields': ('status', 'admin_notes', 'submitted_at', 'reviewed_at')
        }),
    )

    def status_badge(self, obj):
        colours = {
            'pending':  ('#f39c12', 'PENDING'),
            'approved': ('#2ecc71', 'APPROVED'),
            'rejected': ('#e74c3c', 'REJECTED'),
        }
        colour, label = colours.get(obj.status, ('#aaa', obj.status.upper()))
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:100px;font-size:11px;font-weight:600;">{}</span>',
            colour, label
        )
    status_badge.short_description = 'Status'

    def publish_action(self, obj):
        if obj.status == 'pending':
            url = reverse('admin:jobs_jobpostingrequest_change', args=[obj.pk])
            return format_html('<a href="{}">Review →</a>', url)
        return '—'
    publish_action.short_description = 'Action'

    @admin.action(description='✅ Approve selected requests')
    def approve_requests(self, request, queryset):
        queryset.update(status='approved', reviewed_at=timezone.now())
        self.message_user(request, f'{queryset.count()} requests approved.')

    @admin.action(description='❌ Reject selected requests')
    def reject_requests(self, request, queryset):
        queryset.update(status='rejected', reviewed_at=timezone.now())
```

---

### apps/blog/admin.py — REPLACE entirely

```python
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import BlogCategory, Tag, Post


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display       = ('name', 'slug', 'post_count', 'seo_status')
    search_fields      = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def post_count(self, obj):
        count = obj.post_set.filter(status='published').count()
        return format_html(
            '<a href="{}?category__id__exact={}">{} posts</a>',
            '/admin/blog/post/', obj.pk, count
        )
    post_count.short_description = 'Published Posts'

    def seo_status(self, obj):
        # Check if category has meta fields filled
        if obj.meta_title and obj.meta_description:
            return format_html(
                '<span style="color:#2ecc71;font-weight:600;">✅ SEO OK</span>'
            )
        return format_html(
            '<span style="color:#e74c3c;font-weight:600;">⚠️ Missing SEO</span>'
        )
    seo_status.short_description = 'SEO'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display        = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields       = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display  = ('title', 'category', 'author', 'status_badge',
                     'seo_health', 'read_time', 'views_count', 'published_at')
    list_display_links = ('title',)
    list_filter   = ('status', 'category', 'author', 'tags')
    search_fields = ('title', 'content', 'excerpt', 'focus_keyword')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal   = ('tags',)
    date_hierarchy      = 'published_at'
    readonly_fields     = ('views_count', 'seo_preview', 'word_count_display')
    actions = ['publish_posts', 'unpublish_posts']

    fieldsets = (
        ('Content', {
            'fields': (
                'title', 'slug', 'category', 'tags',
                'author', 'featured_image',
                'excerpt', 'content', 'read_time', 'word_count_display'
            )
        }),
        ('SEO — Fill ALL fields before publishing', {
            'fields': ('meta_title', 'meta_description', 'focus_keyword', 'seo_preview'),
            'description': (
                '🎯 AdSense Requirement: Every published post MUST have a unique '
                'meta_title (50–60 chars), meta_description (150–160 chars), '
                'and focus_keyword. Missing these reduces AdSense approval chances.'
            )
        }),
        ('Publishing', {
            'fields': ('status', 'published_at')
        }),
        ('Stats', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
    )

    def status_badge(self, obj):
        if obj.status == 'published':
            return format_html(
                '<span style="background:#2ecc71;color:white;padding:2px 8px;'
                'border-radius:100px;font-size:11px;font-weight:600;">LIVE</span>'
            )
        return format_html(
            '<span style="background:#95a5a6;color:white;padding:2px 8px;'
            'border-radius:100px;font-size:11px;font-weight:600;">DRAFT</span>'
        )
    status_badge.short_description = 'Status'

    def seo_health(self, obj):
        """
        Checks 5 AdSense-critical SEO fields.
        Shows a red/amber/green score so admin can see at a glance
        which posts are hurting the AdSense application.
        """
        score  = 0
        issues = []
        if obj.meta_title:
            if 50 <= len(obj.meta_title) <= 60:
                score += 1
            else:
                issues.append(f'title {len(obj.meta_title)} chars (want 50–60)')
        else:
            issues.append('no meta title')

        if obj.meta_description:
            if 150 <= len(obj.meta_description) <= 160:
                score += 1
            else:
                issues.append(f'desc {len(obj.meta_description)} chars (want 150–160)')
        else:
            issues.append('no meta description')

        if obj.focus_keyword:
            score += 1
        else:
            issues.append('no focus keyword')

        if obj.featured_image:
            score += 1
        else:
            issues.append('no featured image')

        if obj.excerpt and len(obj.excerpt) >= 100:
            score += 1
        else:
            issues.append('excerpt too short')

        colour = {5: '#2ecc71', 4: '#f39c12', 3: '#e67e22'}.get(score, '#e74c3c')
        tip    = ' | '.join(issues) if issues else 'All SEO fields complete'
        label  = f'{score}/5'

        return format_html(
            '<span title="{}" style="background:{};color:white;padding:2px 8px;'
            'border-radius:100px;font-size:11px;font-weight:600;cursor:help;">{}</span>',
            tip, colour, label
        )
    seo_health.short_description = 'SEO Score'

    def word_count_display(self, obj):
        if obj.content:
            # Strip HTML tags for word count
            import re
            text  = re.sub('<[^<]+?>', '', obj.content)
            count = len(text.split())
            colour = '#2ecc71' if count >= 800 else '#e74c3c'
            note   = '✅ Good length' if count >= 800 else '⚠️ Too short for AdSense (need 800+)'
            return format_html(
                '<span style="color:{};">{} words — {}</span>',
                colour, count, note
            )
        return '0 words'
    word_count_display.short_description = 'Word Count'

    def seo_preview(self, obj):
        """Shows exactly how the post will appear in Google search results."""
        title = obj.meta_title or obj.title
        desc  = obj.meta_description or obj.excerpt or ''
        url   = f'/blog/{obj.slug}/'
        return format_html(
            '<div style="max-width:600px;font-family:Arial,sans-serif;'
            'border:1px solid #ddd;padding:16px;border-radius:8px;background:#fff;">'
            '<div style="color:#1a0dab;font-size:18px;margin-bottom:4px;">{}</div>'
            '<div style="color:#006621;font-size:13px;margin-bottom:4px;">'
            'careerbuildershub.com{}</div>'
            '<div style="color:#545454;font-size:13px;">{}</div>'
            '</div>',
            title, url, desc[:160]
        )
    seo_preview.short_description = 'Google Preview'

    def save_model(self, request, obj, form, change):
        # Auto-set published_at when status changes to published
        if obj.status == 'published' and not obj.published_at:
            obj.published_at = timezone.now()
        # Auto-calculate read_time if not set
        if obj.content and not obj.read_time:
            import re
            text = re.sub('<[^<]+?>', '', obj.content)
            obj.read_time = max(1, len(text.split()) // 200)
        super().save_model(request, obj, form, change)

    @admin.action(description='🚀 Publish selected posts')
    def publish_posts(self, request, queryset):
        updated = 0
        for post in queryset:
            if not post.published_at:
                post.published_at = timezone.now()
            post.status = 'published'
            post.save(update_fields=['status', 'published_at'])
            updated += 1
        self.message_user(request, f'{updated} posts published.')

    @admin.action(description='📥 Unpublish (return to draft)')
    def unpublish_posts(self, request, queryset):
        queryset.update(status='draft')
```

---

### apps/core/admin.py — REPLACE entirely

```python
from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage, FAQ, SiteSettings


# ─────────────────────────────────────────
#  CONTACT MESSAGES
# ─────────────────────────────────────────

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display  = ('status_badge', 'name', 'email', 'subject', 'created_at')
    list_filter   = ('is_read',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    actions = ['mark_read', 'mark_unread']

    fieldsets = (
        ('Message', {
            'fields': ('name', 'email', 'subject', 'message', 'created_at')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
    )

    def status_badge(self, obj):
        if not obj.is_read:
            return format_html(
                '<span style="background:#e74c3c;color:white;padding:2px 8px;'
                'border-radius:100px;font-size:11px;font-weight:700;">NEW</span>'
            )
        return format_html(
            '<span style="background:#bdc3c7;color:white;padding:2px 8px;'
            'border-radius:100px;font-size:11px;">Read</span>'
        )
    status_badge.short_description = ''

    def has_add_permission(self, request):
        return False  # Contact messages come from the form, not admin

    @admin.action(description='✅ Mark selected as read')
    def mark_read(self, request, queryset):
        queryset.update(is_read=True)

    @admin.action(description='📩 Mark selected as unread')
    def mark_unread(self, request, queryset):
        queryset.update(is_read=False)


# ─────────────────────────────────────────
#  FAQ
# ─────────────────────────────────────────

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display  = ('question_truncated', 'category', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter   = ('is_active', 'category')
    search_fields = ('question', 'answer')
    ordering      = ('category', 'order')

    fieldsets = (
        (None, {
            'fields': ('question', 'answer', 'category', 'order', 'is_active')
        }),
    )

    def question_truncated(self, obj):
        return obj.question[:80] + ('…' if len(obj.question) > 80 else '')
    question_truncated.short_description = 'Question'


# ─────────────────────────────────────────
#  SITE SETTINGS (Singleton)
# ─────────────────────────────────────────

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('🌐 Site Identity', {
            'fields': ('site_name', 'site_tagline', 'contact_email'),
            'description': 'These values appear in the site header, footer, and meta tags.'
        }),
        ('🏠 Homepage Hero', {
            'fields': ('hero_heading', 'hero_subtext', 'hero_cta_text'),
            'description': 'Edit hero section text without touching code.'
        }),
        ('📱 Social Media', {
            'fields': ('linkedin_url', 'twitter_url', 'instagram_url')
        }),
        ('📊 Analytics', {
            'fields': ('ga_measurement_id',),
            'description': 'Google Analytics 4 Measurement ID — format: G-XXXXXXXXXX'
        }),
        ('💰 AdSense — READ CAREFULLY', {
            'fields': ('adsense_publisher_id', 'adsense_enabled'),
            'description': (
                '⚠️ IMPORTANT: Do NOT enable AdSense until Google has approved '
                'your application. Enabling ads before approval will cause your '
                'application to be rejected. Only turn on adsense_enabled after '
                'you receive the approval email from Google AdSense.'
            )
        }),
    )

    def has_add_permission(self, request):
        # Only one SiteSettings row is allowed
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False  # Never delete the settings row
```

---

### apps/newsletter/admin.py — REPLACE entirely

```python
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import csv
from .models import NewsletterSubscriber


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display  = ('email', 'is_active', 'source', 'created_at')
    list_filter   = ('is_active', 'source')
    search_fields = ('email',)
    actions       = ['activate_subs', 'deactivate_subs', 'export_to_csv']

    def has_add_permission(self, request):
        return False  # Subscribers come from the form only

    @admin.action(description='✅ Activate selected subscribers')
    def activate_subs(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='🚫 Unsubscribe selected')
    def deactivate_subs(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description='📥 Export active emails to CSV')
    def export_to_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers.csv"'
        writer = csv.writer(response)
        writer.writerow(['Email', 'Source', 'Date Subscribed'])
        for sub in queryset.filter(is_active=True):
            writer.writerow([sub.email, sub.source, sub.created_at.strftime('%Y-%m-%d')])
        return response
```

---

### apps/accounts/admin.py — REPLACE entirely

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model  = UserProfile
    extra  = 0
    fields = (
        'avatar', 'current_title', 'university', 'graduation_year',
        'location', 'skills', 'resume', 'resume_public',
        'linkedin_url', 'github_url', 'portfolio_url'
    )
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines      = [UserProfileInline]
    list_display = ('username', 'email', 'full_name', 'is_staff',
                    'is_active', 'date_joined', 'profile_complete')
    list_filter  = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def full_name(self, obj):
        return obj.get_full_name() or '—'
    full_name.short_description = 'Name'

    def profile_complete(self, obj):
        try:
            p = obj.userprofile
            filled = sum([
                bool(p.current_title),
                bool(p.university),
                bool(p.resume),
                bool(p.skills),
                bool(p.linkedin_url),
            ])
            colour = '#2ecc71' if filled >= 4 else '#f39c12' if filled >= 2 else '#e74c3c'
            return format_html(
                '<span style="color:{};">{}/5</span>', colour, filled
            )
        except UserProfile.DoesNotExist:
            return '—'
    profile_complete.short_description = 'Profile'


# Re-register User with our custom admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'current_title', 'university',
                     'graduation_year', 'resume_link', 'resume_public')
    list_filter   = ('resume_public', 'graduation_year')
    search_fields = ('user__username', 'user__email',
                     'current_title', 'university', 'skills')
    raw_id_fields = ('user',)

    def resume_link(self, obj):
        if obj.resume:
            return format_html('<a href="{}" target="_blank">📄 View</a>', obj.resume.url)
        return '—'
    resume_link.short_description = 'Resume'
```

---

## STEP 4: CUSTOMISE THE ADMIN SITE ITSELF

Add this to `config/urls.py` at the top, before urlpatterns:

```python
from django.contrib import admin

# Brand the admin panel
admin.site.site_header  = 'Career Builders Hub'
admin.site.site_title   = 'CBH Admin'
admin.site.index_title  = '⚡ Site Management Dashboard'
```

---

## STEP 5: WIRE FAQ INTO THE FAQ VIEW

The FAQ page currently renders static content. Update `apps/core/views.py`:

```python
def faq(request):
    from .models import FAQ
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')
    grouped = {}
    for faq in faqs:
        grouped.setdefault(faq.get_category_display(), []).append(faq)
    return render(request, 'pages/faq.html', {'faq_groups': grouped})
```

Update `templates/pages/faq.html` to loop over `faq_groups`:
```html
{% for group_name, questions in faq_groups.items %}
  <div class="faq-category">
    <h3>{{ group_name }}</h3>
    {% for item in questions %}
    <div class="faq-item">
      <div class="faq-question">{{ item.question }}</div>
      <div class="faq-answer">{{ item.answer|linebreaks }}</div>
    </div>
    {% endfor %}
  </div>
{% empty %}
  <p>No FAQs published yet.</p>
{% endfor %}
```

---

## STEP 6: SEED INITIAL SITE SETTINGS + FAQs

Add to `apps/core/management/commands/seed_data.py` handle() method:

```python
# Create SiteSettings singleton
from apps.core.models import SiteSettings, FAQ
SiteSettings.objects.get_or_create(pk=1, defaults={
    'site_name':    'Career Builders Hub',
    'site_tagline': 'Entry-Level Jobs for Recent Graduates',
    'hero_heading': 'Launch Your Career with Confidence',
    'hero_subtext': 'Browse 100+ verified entry-level jobs curated for recent graduates. Free to use.',
    'hero_cta_text': 'Browse All Jobs',
    'contact_email': 'hello@careerbuildershub.com',
})

# Seed FAQs
faq_data = [
    ('Is it free to search for jobs?', 'Yes, completely free. Create a profile and apply to any job at no cost.', 'job-seekers', 1),
    ('How do I set up a job alert?', 'Go to Job Listings, set your filters, and click "Set Up Alert". You will receive an email whenever a matching job is posted.', 'job-seekers', 2),
    ('How do I upload my resume?', 'Visit the Submit Resume page or update your profile under Account Settings.', 'job-seekers', 3),
    ('Are all jobs entry-level?', 'Yes. Every job on Career Builders Hub is verified to require 0–2 years of experience.', 'job-seekers', 4),
    ('How do I post a job?', 'Visit the Post a Job page. Submit your details and our team will review and publish within 24 hours.', 'employers', 1),
    ('Is job posting free for employers?', 'We offer free standard listings. Contact us about featured placement options.', 'employers', 2),
    ('How long do job listings stay active?', 'Standard listings are active for 30 days. You can request an extension from our team.', 'employers', 3),
    ('How do I create an account?', 'Click Get Started in the top navigation. Registration takes less than a minute.', 'platform', 1),
    ('Can I save jobs to apply later?', 'Yes. Click the Save button on any job listing. Saved jobs appear in your dashboard.', 'platform', 2),
    ('How do I delete my account?', 'Contact us at hello@careerbuildershub.com and we will process your request within 48 hours.', 'platform', 3),
]
for question, answer, category, order in faq_data:
    FAQ.objects.get_or_create(
        question=question,
        defaults={'answer': answer, 'category': category, 'order': order, 'is_active': True}
    )
self.stdout.write('Created SiteSettings and FAQs.')
```

---

## STEP 7: MIGRATIONS CHECKLIST

Run these in order:
```bash
python manage.py makemigrations core       # FAQ, SiteSettings, is_read on ContactMessage
python manage.py makemigrations newsletter # NewsletterSubscriber
python manage.py makemigrations jobs       # ResumeSubmission, JobPostingRequest, is_active on Company
python manage.py makemigrations blog       # updated_at on Post
python manage.py migrate
python manage.py seed_data
```

---

## ADENSE ADMIN CHECKLIST — what admin now makes easy

| AdSense Requirement | How Admin Handles It |
|---------------------|---------------------|
| 20+ quality blog posts | Post admin with word count + SEO score — can't miss thin content |
| Every post has meta title/desc | SEO Health column shows 0–5 score per post in list view |
| No Lorem ipsum / placeholder | Content comes from DB — never hardcoded |
| Privacy Policy, Terms, FAQ live | FAQ model — admin controls them |
| Contact page works | ContactMessage model — all submissions visible in admin |
| No broken images | Company logo managed through admin, skeleton shown when empty |
| Site stats show real numbers | SiteSettings controls hero; stats come from DB counts |
| ads.txt has correct publisher ID | SiteSettings.adsense_publisher_id + adsense_enabled flag |
| AdSense only enabled after approval | adsense_enabled = False by default, admin flips it after approval |
| Job listings complete and active | Job admin shows expiry warning, activate/deactivate actions |

---

*Admin Build Instructions v1.0 | Career Builders Hub*
*Read alongside: MASTER_PROJECT.md, AUDIT_REPORT.md*
