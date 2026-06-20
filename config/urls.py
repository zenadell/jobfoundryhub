"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from apps.core import views as core_views

# Brand the admin panel
admin.site.site_header  = 'Job Foundry Hub'
admin.site.site_title   = 'JFH Admin'
admin.site.index_title  = '⚡ Site Management Dashboard'

urlpatterns = [
    # 301 Redirects for SEO stability
    path('blog/how-to-ace-your-next-interview/',
        RedirectView.as_view(
            url='/blog/first-job-interview-questions-answers/',
            permanent=True)),
    path('blog/5-tips-for-building-a-great-resume/',
        RedirectView.as_view(
            url='/blog/how-to-build-resume-no-work-experience/',
            permanent=True)),

    path('', include('apps.core.urls')),
    path('sw.js', TemplateView.as_view(template_name='sw.js', content_type='application/javascript')),
    path('ads.txt', TemplateView.as_view(template_name='ads.txt', content_type='text/plain')),
    path('admin/', admin.site.urls),
    path('', include('apps.jobs.urls')),
    path('', include('apps.blog.urls')),
    path('', include('apps.services.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('newsletter/', include('apps.newsletter.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
