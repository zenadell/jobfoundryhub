from django.core.cache import cache

def site_context(request):
    from apps.core.models import SiteSettings
    from apps.jobs.models import JobCategory

    # Cache SiteSettings for 10 minutes — it barely changes
    settings_obj = cache.get('site_settings')
    if not settings_obj:
        settings_obj = SiteSettings.get()
        cache.set('site_settings', settings_obj, 600)

    # Cache footer categories for 1 hour
    footer_cats = cache.get('footer_categories')
    if not footer_cats:
        footer_cats = list(JobCategory.objects.all()[:6])
        cache.set('footer_categories', footer_cats, 3600)

    return {
        'site_name':            settings_obj.site_name,
        'site_tagline':         settings_obj.site_tagline,
        'hero_heading':         settings_obj.hero_heading,
        'hero_subtext':         settings_obj.hero_subtext,
        'hero_cta_text':        settings_obj.hero_cta_text,
        'contact_email':        settings_obj.contact_email,
        'GA_MEASUREMENT_ID':    settings_obj.ga_measurement_id,
        'ADSENSE_PUBLISHER_ID': settings_obj.adsense_publisher_id,
        'ADSENSE_ENABLED':      settings_obj.adsense_enabled,
        'social': {
            'linkedin':  settings_obj.linkedin_url,
            'twitter':   settings_obj.twitter_url,
            'instagram': settings_obj.instagram_url,
        },
        'footer_categories': footer_cats,
    }
