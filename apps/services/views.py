from django.shortcuts import render

def overview(request):
    return render(request, 'services/overview.html')

def curated_jobs(request):
    return render(request, 'services/curated_jobs.html')

def career_launch(request):
    return render(request, 'services/career_launch.html')

def resume_review(request):
    return render(request, 'services/resume_review.html')

def interview_coaching(request):
    return render(request, 'services/interview_coaching.html')

def salary_negotiation(request):
    return render(request, 'services/salary_negotiation.html')
