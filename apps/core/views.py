import logging
import json
import os
import threading
from datetime import datetime
from django.core.management import call_command
from django.shortcuts import render, redirect

logger = logging.getLogger(__name__)
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
import requests as http_requests

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

def how_it_works(request):
    from .models import HowItWorksStep, SiteSettings
    seeker_steps = HowItWorksStep.objects.filter(category='seekers', is_active=True).order_by('order')
    employer_steps = HowItWorksStep.objects.filter(category='employers', is_active=True).order_by('order')
    return render(request, 'pages/how_it_works.html', {
        'seeker_steps': seeker_steps,
        'employer_steps': employer_steps,
        'site_settings': SiteSettings.get()
    })

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Save to database — skip silently if it fails
        try:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
        except Exception:
            pass
        
        # Send emails
        try:
            from apps.core.email_sender import send_templated_email
            from apps.core import email_templates

            send_templated_email(
                to=settings.SUPPORT_EMAIL,
                template=email_templates.contact_admin_notification(name, email, subject, message)
            )
            send_templated_email(
                to=email,
                template=email_templates.contact_user_confirmation(name, subject)
            )
        except Exception as e:
            logger.error(f"Contact email error: {e}")

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
            try:
                from apps.newsletter.models import NewsletterSubscriber
                NewsletterSubscriber.objects.get_or_create(
                    email=email,
                    defaults={'source': request.POST.get('source', 'homepage')}
                )
            except Exception:
                pass
            try:
                from apps.core.email_sender import send_templated_email
                from apps.core import email_templates
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


def test_email_debug(request):
    """Temporary diagnostic — hit /test-email-debug/ to see the raw Resend API response."""
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@jobfoundryhub.com')
    support_email = getattr(settings, 'SUPPORT_EMAIL', 'support@jobfoundryhub.com')

    if not api_key:
        return JsonResponse({
            'error': 'RESEND_API_KEY is empty or not set',
            'from_email': from_email,
            'support_email': support_email,
        })

    # Try sending a simple test email
    payload = {
        "from": f"Job Foundry Hub <{from_email}>",
        "to": ["jobfoundryhub@gmail.com"],
        "subject": "Resend Debug Test",
        "html": "<h1>Debug Test</h1><p>If you see this, Resend is working.</p>",
    }

    try:
        resp = http_requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=10,
        )
        return JsonResponse({
            'resend_status_code': resp.status_code,
            'resend_response': resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text,
            'payload_sent': {
                'from': payload['from'],
                'to': payload['to'],
                'subject': payload['subject'],
            },
            'settings': {
                'RESEND_API_KEY': f"{api_key[:8]}...{api_key[-4:]}",
                'DEFAULT_FROM_EMAIL': from_email,
                'SUPPORT_EMAIL': support_email,
            }
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'type': type(e).__name__,
        }, status=500)


@staff_member_required
def data_vault(request):
    """Render the Data Vault backup dashboard in the admin styling context."""
    # We pass the default Django admin site context so headers, titles, and menus align
    from django.contrib import admin
    context = admin.site.each_context(request)
    context.update({
        'title': 'Data Vault Management',
        'import_summary': request.session.pop('import_summary', None),
    })
    return render(request, 'admin/data_vault.html', context)


@staff_member_required
def data_vault_export(request):
    """Query the export engine and serve a serialized JSON file download."""
    from django.http import HttpResponse
    from apps.core.data_vault import export_all_data, DataVaultEncoder
    
    try:
        data = export_all_data()
        json_str = json.dumps(data, cls=DataVaultEncoder, indent=2)
        
        response = HttpResponse(json_str, content_type='application/json')
        filename = f"jfh_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except Exception as e:
        logger.error(f"Data Vault export failed: {e}")
        messages.error(request, f"❌ Data Vault export failed: {e}")
        return redirect('core:data_vault')


@staff_member_required
def data_vault_import(request):
    """Handle backup file upload, validate JSON payload, and restore database."""
    if request.method != 'POST':
        return redirect('core:data_vault')
        
    backup_file = request.FILES.get('backup_file')
    if not backup_file:
        messages.error(request, "❌ Please select a valid backup JSON file first.")
        return redirect('core:data_vault')
        
    clear_existing = request.POST.get('clear_existing') == 'on'
    
    try:
        data_dict = json.load(backup_file)
        
        # Quick sanity check on the JSON format
        if "export_meta" not in data_dict:
            messages.error(request, "❌ Invalid backup file format (missing export metadata).")
            return redirect('core:data_vault')
            
        from apps.core.data_vault import import_all_data
        summary = import_all_data(data_dict, clear_existing=clear_existing)
        
        # Save summary in session to display on next load
        request.session['import_summary'] = summary
        messages.success(request, "🎉 Database restored successfully! All tables mapped perfectly.")
        
    except json.JSONDecodeError:
        messages.error(request, "❌ Failed to parse backup file (invalid JSON formatting).")
    except Exception as e:
        logger.error(f"Data Vault import failed: {e}")
        import traceback
        traceback.print_exc()
        messages.error(request, f"❌ Restore failed due to an error: {e}")
        
    return redirect('core:data_vault')


def run_cron_tasks():
    """Run management commands in a background thread."""
    try:
        logger.info("Running automated cron tasks: cleanup_expired_jobs")
        call_command('cleanup_expired_jobs')
        logger.info("Running automated cron tasks: sync_adzuna_jobs")
        call_command('sync_adzuna_jobs')
        # Remove any duplicate listings the sync may have let through.
        # Idempotent — does nothing once the data is clean.
        logger.info("Running automated cron tasks: dedupe_jobs")
        call_command('dedupe_jobs')
        logger.info("Automated cron tasks completed successfully.")
    except Exception as e:
        logger.error(f"Error running cron tasks: {e}")


def cron_trigger(request):
    """
    Secure webhook endpoint to trigger automated tasks.
    Can be called by external cron services (e.g., cron-job.org).
    Requires ?token= match with CRON_SECRET_TOKEN env variable.
    """
    from django.http import JsonResponse
    token = request.GET.get('token')
    secret_token = os.environ.get('CRON_SECRET_TOKEN', 'jobfoundry-fallback-token-123')
    
    if token != secret_token:
        return JsonResponse({'status': 'error', 'message': 'Invalid or missing token'}, status=403)
        
    # Start the tasks in a background thread so the HTTP response returns immediately
    thread = threading.Thread(target=run_cron_tasks)
    thread.daemon = True
    thread.start()
    
    return JsonResponse({
        'status': 'success', 
        'message': 'Automated tasks have been triggered and are running in the background.'
    })
