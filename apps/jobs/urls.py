from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('job-listings/', views.job_list, name='job_list'),
    path('job-listings/<slug:slug>/', views.job_detail, name='job_detail'),
    path('companies/', views.company_list, name='company_list'),
    path('companies/<slug:slug>/', views.company_detail, name='company_detail'),
    path('submit-resume/', views.submit_resume, name='submit_resume'),
    path('post-job/', views.post_job, name='post_job'),
    path('feed.xml', views.job_feed_xml, name='job_feed_xml'),
    path('<slug:category_slug>-graduate-jobs-<slug:location_slug>/', views.seo_landing_page, name='seo_landing'),
]
