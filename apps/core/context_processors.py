import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)


def site_context(request):
    """
    Injects site-wide settings into every template.
    Wrapped in try/except so a dead database never takes down the whole site.
    """
    try:
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
            'MONETAG_HEAD_SCRIPT':  settings_obj.monetag_head_script,
            'MONETAG_ENABLED':      settings_obj.monetag_enabled,
            'social': {
                'linkedin':  settings_obj.linkedin_url,
                'twitter':   settings_obj.twitter_url,
                'instagram': settings_obj.instagram_url,
            },
            'footer_categories': footer_cats,
        }
    except Exception as e:
        logger.error(f"Database unavailable in site_context: {e}")
        # Return safe defaults so the site still renders
        return {
            'site_name':            'Job Foundry Hub',
            'site_tagline':         'Entry-Level Jobs for Recent Graduates',
            'hero_heading':         'Launch Your Career with Confidence',
            'hero_subtext':         'Browse verified entry-level jobs curated for recent graduates.',
            'hero_cta_text':        'Browse All Jobs',
            'contact_email':        'support@jobfoundryhub.com',
            'GA_MEASUREMENT_ID':    '',
            'ADSENSE_PUBLISHER_ID': '',
            'ADSENSE_ENABLED':      False,
            'MONETAG_HEAD_SCRIPT':  '',
            'MONETAG_ENABLED':      False,
            'social': {
                'linkedin':  '',
                'twitter':   '',
                'instagram': '',
            },
            'footer_categories': [],
        }
