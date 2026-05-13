from django.urls import path
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from . import views
from .sitemaps import StaticViewSitemap, ServiceViewSitemap, JobSitemap, PostSitemap

app_name = 'core'

sitemaps = {
    'static': StaticViewSitemap,
    'services': ServiceViewSitemap,
    'jobs': JobSitemap,
    'posts': PostSitemap,
}

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy, name='privacy'),
    path('terms-of-service/', views.terms, name='terms'),
    path('faq/', views.faq, name='faq'),

    path('newsletter-signup/', views.newsletter_signup, name='newsletter_signup'),
    path('licenses/', views.licenses, name='licenses'),
    path('style-guide/', views.style_guide, name='style_guide'),
    path('changelog/', views.changelog, name='changelog'),
    path('coming-soon/', views.coming_soon, name='coming_soon'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('health/', views.health_check, name='health_check'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('ads.txt', TemplateView.as_view(template_name="ads.txt", content_type="text/plain")),
    path('test-email-debug/', views.test_email_debug, name='test_email_debug'),
]
