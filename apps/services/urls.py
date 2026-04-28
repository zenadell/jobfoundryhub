from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('services/', views.overview, name='overview'),
    path('services/curated-entry-level-jobs/', views.curated_jobs, name='curated_jobs'),
    path('services/career-launch-programs/', views.career_launch, name='career_launch'),
    path('services/resume-review/', views.resume_review, name='resume_review'),
    path('services/interview-coaching/', views.interview_coaching, name='interview_coaching'),
    path('services/salary-negotiation-guide/', views.salary_negotiation, name='salary_negotiation'),
]
