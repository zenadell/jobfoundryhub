from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import models
from .models import Job, Company, JobCategory, ResumeSubmission, JobPostingRequest

def job_list(request):
    # Base queryset with requested ordering
    queryset = Job.objects.filter(is_active=True).select_related('company', 'category').order_by('company', '-posted_at')
    
    q = request.GET.get('q')
    category_slug = request.GET.get('category')
    job_type = request.GET.get('job_type')
    
    if q:
        queryset = queryset.filter(
            models.Q(title__icontains=q) | 
            models.Q(company__name__icontains=q)
        )
    
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
        
    if job_type:
        queryset = queryset.filter(job_type=job_type)

    # ── Manual Diversity Logic (Max 3 per company on page) ─────
    diverse_jobs = []
    company_counts = {}
    
    # We iterate and collect up to 100 jobs to handle pagination decently
    for job in queryset:
        c_id = job.company_id
        count = company_counts.get(c_id, 0)
        if count < 3:
            diverse_jobs.append(job)
            company_counts[c_id] = count + 1
        
        if len(diverse_jobs) >= 120: # Enough for ~10 pages of 12
            break
            
    paginator = Paginator(diverse_jobs, 12)
    page_number = request.GET.get('page')
    jobs = paginator.get_page(page_number)
    
    context = {
        'jobs': jobs,
        'categories': JobCategory.objects.all(),
        'current_category': category_slug,
        'current_job_type': job_type,
    }
    return render(request, 'jobs/list.html', context)

def job_detail(request, slug):
    job = get_object_or_404(Job, slug=slug, is_active=True)
    
    # Update view count
    job.views_count += 1
    job.save(update_fields=['views_count'])
    
    related_jobs = Job.objects.filter(
        category=job.category, 
        is_active=True
    ).exclude(id=job.id).order_by('-posted_at')[:3]
    
    context = {
        'job': job,
        'related_jobs': related_jobs,
    }
    return render(request, 'jobs/detail.html', context)

def company_list(request):
    companies = Company.objects.filter(is_active=True).order_by('name')
    paginator = Paginator(companies, 12)
    page_number = request.GET.get('page')
    companies_page = paginator.get_page(page_number)
    
    context = {
        'companies': companies_page,
    }
    return render(request, 'jobs/companies.html', context)

def company_detail(request, slug):
    company = get_object_or_404(Company, slug=slug)
    active_jobs = company.job_set.filter(is_active=True).order_by('-posted_at')
    
    context = {
        'company': company,
        'active_jobs': active_jobs,
    }
    return render(request, 'jobs/company_detail.html', context)

def submit_resume(request):
    if request.method == 'POST':
        from .models import ResumeSubmission
        from django.core.mail import send_mail
        from django.conf import settings
        
        full_name = request.POST.get('full_name', '')
        email = request.POST.get('email', '')
        position = request.POST.get('position', '')

        ResumeSubmission.objects.create(
            full_name  = full_name,
            email      = email,
            position   = position,
            resume     = request.FILES.get('resume'),
            cover_note = request.POST.get('message', ''),
        )

        # Send notification to admin
        try:
            send_mail(
                subject=f"New Resume: {full_name}",
                message=f"Name: {full_name}\nEmail: {email}\nPosition: {position}\n\nCheck admin for details.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.SUPPORT_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass

        # Send confirmation to user
        try:
            send_mail(
                subject="Resume Received - Job Foundry Hub",
                message=f"Hi {full_name},\n\nThank you for submitting your resume for the {position} position. Our team is reviewing your profile and will be in touch if there's a match.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
        except Exception:
            pass

        return redirect(reverse('core:confirmation') + '?type=resume')
    return render(request, 'jobs/submit_resume.html')

def post_job(request):
    if request.method == 'POST':
        from .models import JobPostingRequest
        from django.core.mail import send_mail
        from django.conf import settings

        company_name = request.POST.get('company_name', '')
        job_title = request.POST.get('job_title', '')
        contact_email = request.POST.get('contact_email', '')

        JobPostingRequest.objects.create(
            company_name     = company_name,
            contact_name     = request.POST.get('contact_name', ''),
            contact_email    = contact_email,
            contact_phone    = request.POST.get('contact_phone', ''),
            company_website  = request.POST.get('company_website', ''),
            job_title        = job_title,
            job_description  = request.POST.get('job_description', ''),
            job_requirements = request.POST.get('job_requirements', ''),
            job_location     = request.POST.get('job_location', ''),
            job_type         = request.POST.get('job_type', 'full-time'),
            is_remote        = request.POST.get('is_remote') == 'on',
            salary_range     = request.POST.get('salary_range', ''),
            apply_url        = request.POST.get('apply_url', ''),
        )

        # Send notification to admin
        try:
            send_mail(
                subject=f"Job Request: {job_title} @ {company_name}",
                message=f"Company: {company_name}\nJob: {job_title}\nContact: {contact_email}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.SUPPORT_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass

        # Send confirmation to company
        try:
            send_mail(
                subject="Job Posting Request Received - Job Foundry Hub",
                message=f"Hello {company_name},\n\nWe have received your request to post the '{job_title}' position. Our team will review the details and get back to you shortly.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[contact_email],
                fail_silently=True,
            )
        except Exception:
            pass

        return redirect(reverse('core:confirmation') + '?type=job')
    return render(request, 'jobs/post_job.html')
