from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ContactMessage, FAQ, SiteSettings, HowItWorksStep


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
#  HOW IT WORKS STEPS
# ─────────────────────────────────────────

@admin.register(HowItWorksStep)
class HowItWorksStepAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'description')
    ordering = ('category', 'order')


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
        ('📹 How It Works Videos', {
            'fields': (
                'hiw_video_embed_seekers',
                'hiw_video_embed_employers'
            ),
            'description': 'Use the "Upload Video" button below to upload directly to the cloud, or paste a YouTube link.'
        }),
    )

    def has_add_permission(self, request):
        # Only one SiteSettings row is allowed
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False  # Never delete the settings row

    list_display = ('site_name', 'view_site_link', 'data_vault_link')

    def view_site_link(self, obj):
        url = reverse('core:home')
        return format_html('<a href="{}" target="_blank" style="font-weight:bold;color:#3498db;">🔗 View Homepage</a>', url)
    view_site_link.short_description = 'Public Site'

    def data_vault_link(self, obj):
        url = reverse('core:data_vault')
        return format_html('<a href="{}" style="font-weight:bold;color:#10b981;">🗄️ Open Data Vault</a>', url)
    data_vault_link.short_description = 'Database Backup'
