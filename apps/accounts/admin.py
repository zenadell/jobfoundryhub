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
