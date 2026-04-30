from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
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
            reverse('admin:blog_post_changelist'), obj.pk, count
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
            'jobfoundryhub.com{}</div>'
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
            
        try:
            super().save_model(request, obj, form, change)
        except Exception as e:
            from django.contrib import messages
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to save post/image: {str(e)}")
            
            messages.error(
                request, 
                f"⚠️ Error saving image: {str(e)}. "
                "Your post content was saved, but the image upload failed. "
                "Please check your Cloudinary credentials in Render."
            )
            # If it's a new object and failed to save, we might need to handle it.
            # But super().save_model normally handles the actual DB save.
            # If the image fails, usually the whole transaction rolls back.
            # To ensure the post is saved even if image fails, we'd need to clear the image field.
            if hasattr(obj, 'featured_image'):
                obj.featured_image = None
                obj.save()
                messages.warning(request, "Post saved WITHOUT the image to prevent data loss.")

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
