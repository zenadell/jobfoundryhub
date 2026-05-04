from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.conf import settings
from apps.jobs.models import Job, JobCategory, Company
from apps.blog.models import Post
from .models import ContactMessage

User = get_user_model()

def home(request):
    from django.db.models import Count, Q
    
    # Priority categories for graduates
    priority_cats = ['Technology', 'Marketing', 'Finance', 'Data & Analytics', 'Design', 'Human Resources']
    
    # Base filter to exclude low-end/retail jobs from homepage
    low_end_keywords = ['Driver', 'Delivery', 'Barista', 'Cleaner', 'Warehouse', 'Sainsbury', 'Argos', 'Tesco', 'Lidl', 'Aldi', 'Customer Advisor']
    base_filter = Q(is_active=True)
    for kw in low_end_keywords:
        base_filter &= ~Q(title__icontains=kw)
        base_filter &= ~Q(company__name__icontains=kw)

    featured_jobs = Job.objects.filter(
        base_filter,
        category__name__in=priority_cats
    ).exclude(
        description__icontains="We are looking for a talented individual"
    ).select_related('company', 'category').order_by('-posted_at')[:6]

    # Fallback if we don't have enough priority jobs (still excluding low-end)
    if len(featured_jobs) < 6:
        featured_jobs = Job.objects.filter(
            base_filter
        ).exclude(
            description__icontains="We are looking for a talented individual"
        ).select_related('company', 'category').order_by('-posted_at')[:6]
    return render(request, 'pages/home.html', {
        'featured_jobs': featured_jobs,
        'recent_posts': Post.live.filter(
            status='published'
        ).select_related('author', 'category').order_by('-published_at')[:3],
        
        'job_count': Job.objects.filter(is_active=True).count(),
        'company_count': Company.objects.filter(is_active=True).count(),
        'user_count': User.objects.count() + 480,
        
        'partner_companies': Company.objects.filter(
            is_active=True
        ).annotate(
            total_jobs=Count('job')
        ).order_by('-total_jobs')[:5],
    })

def about(request):
    return render(request, 'pages/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        from apps.core.email_sender import send_templated_email
        from apps.core import email_templates
        
        # Notify admin
        try:
            send_templated_email(
                to=settings.SUPPORT_EMAIL,
                template=email_templates.contact_admin_notification(name, email, subject, message)
            )
        except Exception:
            pass

        # Confirm to user
        try:
            send_templated_email(
                to=email,
                template=email_templates.contact_user_confirmation(name, subject)
            )
        except Exception:
            pass

        return redirect(reverse('core:confirmation') + '?type=contact')
        
    return render(request, 'pages/contact.html')

def privacy(request):
    return render(request, 'pages/privacy.html')

def terms(request):
    return render(request, 'pages/terms.html')

def faq(request):
    from .models import FAQ
    faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')
    grouped = {}
    for faq in faqs:
        grouped.setdefault(faq.get_category_display(), []).append(faq)
    return render(request, 'pages/faq.html', {'faq_groups': grouped})

@staff_member_required
def licenses(request):
    return render(request, 'pages/licenses.html')

@staff_member_required
def style_guide(request):
    return render(request, 'pages/style_guide.html')

@staff_member_required
def changelog(request):
    return render(request, 'pages/changelog.html')

@staff_member_required
def coming_soon(request):
    return render(request, 'pages/coming_soon.html')

def confirmation(request):
    type_param = request.GET.get('type', 'contact')
    return render(request, 'pages/confirmation.html', {'type': type_param})



def newsletter_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            from apps.newsletter.models import NewsletterSubscriber
            NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'source': request.POST.get('source', 'homepage')}
            )
            from apps.core.email_sender import send_templated_email
            from apps.core import email_templates
            try:
                send_templated_email(
                    to=settings.SUPPORT_EMAIL,
                    template=email_templates.newsletter_admin_notification(email)
                )
            except Exception:
                pass
        return redirect(reverse('core:confirmation') + '?type=newsletter')
    return redirect('core:home')

def health_check(request):
    """
    UptimeRobot pings this every 5 minutes.
    Keeps Render free tier from spinning down.
    Also verifies DB is reachable.
    """
    from apps.jobs.models import Job
    try:
        job_count = Job.objects.filter(is_active=True).count()
        return JsonResponse({
            'status': 'ok',
            'active_jobs': job_count,
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'detail': str(e)}, status=500)
