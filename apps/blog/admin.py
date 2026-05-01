from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from .models import BlogCategory, Tag, Post, TrashedPost


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


# ─────────────────────────────────────────────────────────────
#  POSTS — only Draft + Published (trashed posts hidden here)
# ─────────────────────────────────────────────────────────────
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
    readonly_fields     = ('views_count', 'seo_preview', 'word_count_display', 'seo_report')
    actions = ['publish_posts', 'unpublish_posts', 'trash_posts']

    fieldsets = (
        ('Content', {
            'fields': (
                'title', 'slug', 'category', 'tags',
                'author', 'featured_image',
                'excerpt', 'content', 'read_time', 'word_count_display'
            )
        }),
        ('SEO — Fill ALL fields before publishing', {
            'fields': ('seo_report', 'meta_title', 'meta_description', 'focus_keyword', 'seo_preview'),
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

    def get_queryset(self, request):
        """Hide trashed posts from the main Posts list."""
        return super().get_queryset(request).exclude(status='trashed')

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
                issues.append(f"Title is {len(obj.meta_title)} chars (aim for 50-60)")
        else:
            issues.append("Missing Meta Title")

        if obj.meta_description:
            if 150 <= len(obj.meta_description) <= 160:
                score += 1
            else:
                issues.append(f"Description is {len(obj.meta_description)} chars (aim for 150-160)")
        else:
            issues.append("Missing Meta Description")

        if obj.focus_keyword:
            score += 1
        else:
            issues.append("Missing Focus Keyword")

        if obj.featured_image:
            score += 1
        else:
            issues.append("Missing Featured Image")

        if obj.excerpt and len(obj.excerpt) >= 100:
            score += 1
        else:
            issues.append("Excerpt is too short (need 100+ chars)")

        colour = {5: '#2ecc71', 4: '#f39c12', 3: '#e67e22'}.get(score, '#e74c3c')
        tip    = ' | '.join(issues) if issues else 'All SEO fields perfect!'
        
        return format_html(
            '<span title="{}" style="background:{};color:white;padding:3px 10px;'
            'border-radius:100px;font-size:11px;font-weight:700;cursor:help;display:inline-block;">{}</span>',
            tip, colour, f"{score}/5"
        )
    seo_health.short_description = 'SEO Score'

    def seo_report(self, obj):
        """A detailed checklist shown inside the post edit page."""
        checks = [
            (obj.meta_title and 50 <= len(obj.meta_title) <= 60, 
             f"Meta Title (50-60 chars): Currently {len(obj.meta_title) if obj.meta_title else 0}"),
            (obj.meta_description and 150 <= len(obj.meta_description) <= 160, 
             f"Meta Description (150-160 chars): Currently {len(obj.meta_description) if obj.meta_description else 0}"),
            (bool(obj.focus_keyword), "Focus Keyword set"),
            (bool(obj.featured_image), "Featured Image uploaded"),
            (obj.excerpt and len(obj.excerpt) >= 100, "Excerpt length (100+ chars)"),
        ]
        
        html = '<ul style="margin:0; padding:0; list-style:none;">'
        for passed, label in checks:
            icon = '✅' if passed else '❌'
            color = '#2ecc71' if passed else '#e74c3c'
            html += f'<li style="color:{color}; margin-bottom:5px;">{icon} {label}</li>'
        html += '</ul>'
        return format_html(html)
    seo_report.short_description = 'SEO Checklist'

    def word_count_display(self, obj):
        if obj.content:
            # Strip HTML tags for word count
            import re
            text  = re.sub('<[^<]+?>', '', obj.content)
            count = len(text.split())
            colour = '#2ecc71' if count >= 800 else '#e74c3c'
            note   = '✅ Good length' if count >= 800 else '⚠️ Too short for AdSense (need 800+)'
            return format_html(
                '<span style="color:{};font-weight:bold;">{} words — {}</span>',
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
            'border:1px solid #ddd;padding:16px;border-radius:8px;background:#f9f9f9;margin-top:10px;">'
            '<div style="color:#1a0dab;font-size:18px;margin-bottom:4px;text-decoration:none;">{}</div>'
            '<div style="color:#006621;font-size:13px;margin-bottom:4px;">'
            'jobfoundryhub.com{}</div>'
            '<div style="color:#545454;font-size:13px;line-height:1.4;">{}</div>'
            '</div>',
            title, url, desc[:160]
        )
    seo_preview.short_description = 'Google Search Preview'

    def save_model(self, request, obj, form, change):
        # Auto-set published_at when status changes to published
        if obj.status == 'published' and not obj.published_at:
            obj.published_at = timezone.now()
        # Auto-calculate read_time if not set
        if obj.content and not obj.read_time:
            import re
            text = re.sub('<[^<]+?>', '', obj.content)
            obj.read_time = max(1, len(text.split()) // 200)

        # Check if a new image was uploaded in this save
        has_new_image = 'featured_image' in form.changed_data

        if has_new_image:
            # Strategy: save the post WITHOUT the new image first,
            # then try to attach the image in a second step.
            # This ensures the post content is never lost.
            uploaded_image = obj.featured_image  # hold the new file
            
            # Keep the old image (or None) for the initial safe save
            if change and obj.pk:
                try:
                    old_obj = Post.objects.get(pk=obj.pk)
                    obj.featured_image = old_obj.featured_image
                except Post.DoesNotExist:
                    obj.featured_image = None
            else:
                obj.featured_image = None
            
            # Save the post content safely (no image upload involved)
            try:
                super().save_model(request, obj, form, change)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to save post content: {e}")
                from django.contrib import messages
                messages.error(request, f"⚠️ Failed to save post: {e}")
                return
            
            # Now try to attach the uploaded image
            try:
                obj.featured_image = uploaded_image
                obj.save(update_fields=['featured_image'])
                from django.contrib import messages
                messages.success(request, "✅ Post and image saved successfully.")
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Image upload failed: {e}")
                from django.contrib import messages
                messages.warning(
                    request,
                    f"⚠️ Your post was saved, but the image upload failed: {e}. "
                    "Please check your Cloudinary credentials on Render, or try re-uploading."
                )
        else:
            # No new image — standard save, still protected
            try:
                super().save_model(request, obj, form, change)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to save post: {e}")
                from django.contrib import messages
                messages.error(request, f"⚠️ Error saving post: {e}")

    # ── Bulk Actions ─────────────────────────────────────────────

    @admin.action(description='🚀 Publish selected posts')
    def publish_posts(self, request, queryset):
        updated = 0
        for post in queryset:
            if not post.published_at:
                post.published_at = timezone.now()
            post.status = 'published'
            post.save(update_fields=['status', 'published_at'])
            updated += 1
        self.message_user(request, f'✅ {updated} post(s) published.')

    @admin.action(description='📥 Unpublish (return to draft)')
    def unpublish_posts(self, request, queryset):
        queryset.update(status='draft')
        self.message_user(request, f'📥 {queryset.count()} post(s) returned to draft.')

    @admin.action(description='🗑️ Move to Trash')
    def trash_posts(self, request, queryset):
        count = queryset.count()
        queryset.update(status='trashed', deleted_at=timezone.now())
        self.message_user(
            request,
            f'🗑️ {count} post(s) moved to Trash. '
            f'They will be permanently deleted after 30 days. '
            f'Go to 🗑️ Trash to restore or permanently delete them.'
        )


# ─────────────────────────────────────────────────────────────
#  🗑️ TRASH — separate section, only trashed posts
# ─────────────────────────────────────────────────────────────
@admin.register(TrashedPost)
class TrashedPostAdmin(admin.ModelAdmin):
    list_display  = ('title', 'category', 'author', 'trash_timer',
                     'deleted_at')
    list_display_links = ('title',)
    list_filter   = ('category',)
    search_fields = ('title',)
    readonly_fields = ('title', 'slug', 'category', 'author', 'excerpt',
                       'content', 'featured_image', 'read_time',
                       'meta_title', 'meta_description', 'focus_keyword',
                       'status', 'published_at', 'views_count', 'deleted_at')
    actions = ['restore_to_draft', 'restore_and_publish', 'permanently_delete']

    fieldsets = (
        ('⚠️ This post is in the Trash', {
            'description': (
                'Posts in the Trash are automatically deleted after 30 days. '
                'Use the actions above to restore or permanently delete.'
            ),
            'fields': ('title', 'slug', 'category', 'author', 'deleted_at')
        }),
        ('Content Preview', {
            'fields': ('excerpt', 'featured_image'),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        """Only show trashed posts here."""
        return super().get_queryset(request).filter(status='trashed')

    def has_add_permission(self, request):
        """Can't create posts directly in trash."""
        return False

    def trash_timer(self, obj):
        """Shows how many days left before permanent deletion."""
        if not obj.deleted_at:
            return '—'
        days_in_trash = (timezone.now() - obj.deleted_at).days
        days_left = max(0, 30 - days_in_trash)
        if days_left == 0:
            return format_html(
                '<span style="color:#e74c3c;font-weight:600;">⏰ EXPIRED</span>'
            )
        colour = '#e74c3c' if days_left <= 7 else '#f39c12'
        return format_html(
            '<span style="color:{};font-weight:600;">⏳ {} days left</span>',
            colour, days_left
        )
    trash_timer.short_description = 'Auto-Delete In'

    # ── Trash Actions ────────────────────────────────────────

    @admin.action(description='♻️ Restore to Draft')
    def restore_to_draft(self, request, queryset):
        count = queryset.count()
        queryset.update(status='draft', deleted_at=None)
        self.message_user(request, f'♻️ {count} post(s) restored to Draft. Find them under Posts.')

    @admin.action(description='🚀 Restore & Publish immediately')
    def restore_and_publish(self, request, queryset):
        count = 0
        for post in queryset:
            post.status = 'published'
            post.deleted_at = None
            if not post.published_at:
                post.published_at = timezone.now()
            post.save(update_fields=['status', 'deleted_at', 'published_at'])
            count += 1
        self.message_user(request, f'🚀 {count} post(s) restored and published live!')

    @admin.action(description='❌ Permanently delete (CANNOT be undone!)')
    def permanently_delete(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f'❌ {count} post(s) permanently deleted. This cannot be undone.',
            level='warning'
        )
