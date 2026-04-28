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
