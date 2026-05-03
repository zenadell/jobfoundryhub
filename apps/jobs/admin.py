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

class JobInline(admin.StackedInline):
    model = Job
    extra = 0
    fields = (
        ('title', 'job_type'),
        ('is_active', 'is_featured', 'expires_at'),
        'description', 'requirements'
    )
    show_change_link = True
    can_delete = True


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display  = ('logo_preview', 'name', 'industry', 'size',
                     'location', 'is_verified', 'is_partner', 'is_active', 'active_jobs_badge', 'view_on_site_link')
    list_display_links = ('name',)
    list_editable = ('is_verified', 'is_partner', 'is_active')
    list_filter   = ('is_verified', 'is_partner', 'is_active', 'industry', 'size')
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
            'fields': ('is_verified', 'is_partner', 'is_active'),
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

    def view_on_site_link(self, obj):
        url = obj.get_absolute_url()
        return format_html('<a href="{}" target="_blank" style="font-weight:bold;color:#3498db;">🔗 View Live</a>', url)
    view_on_site_link.short_description = 'Live Site'


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
                     'location_or_remote', 'status_badge', 'is_featured', 'view_on_site_link', 'posted_at')
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

    def view_on_site_link(self, obj):
        url = obj.get_absolute_url()
        return format_html('<a href="{}" target="_blank" style="font-weight:bold;color:#3498db;">🔗 View Live</a>', url)
    view_on_site_link.short_description = 'Live Site'


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
