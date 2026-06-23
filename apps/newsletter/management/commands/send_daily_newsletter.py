import datetime
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from apps.newsletter.models import NewsletterSubscriber
from apps.jobs.models import Job

class Command(BaseCommand):
    help = 'Sends the daily newsletter with the latest verified jobs to all active subscribers.'

    def handle(self, *args, **kwargs):
        # 1. Fetch the 5 most recent active jobs
        latest_jobs = Job.objects.filter(is_active=True).order_by('-posted_at')[:5]
        
        if not latest_jobs.exists():
            self.stdout.write(self.style.WARNING("No active jobs found. Skipping daily newsletter."))
            return

        # 2. Format the job list for the email
        jobs_text = ""
        for job in latest_jobs:
            # Build URL assuming production domain, since this runs from CLI
            domain = "https://jobfoundryhub.com"
            job_url = f"{domain}{job.get_absolute_url()}"
            
            jobs_text += f"- {job.title} at {job.company.name}\n"
            jobs_text += f"  Location: {job.location} | Type: {job.get_job_type_display()}\n"
            jobs_text += f"  Apply here: {job_url}\n\n"

        subject = f"Your Daily Job Updates from JobFoundryHub! ({timezone.now().strftime('%b %d')})"
        
        message = (
            f"Hello!\n\n"
            f"Here are the latest hand-picked jobs for you today:\n\n"
            f"{jobs_text}"
            f"---\n"
            f"Best of luck with your applications!\n"
            f"The JobFoundryHub Team\n"
            f"https://jobfoundryhub.com\n"
        )

        # 3. Fetch active subscribers
        subscribers = NewsletterSubscriber.objects.filter(is_active=True)
        recipient_list = [sub.email for sub in subscribers]

        if not recipient_list:
            self.stdout.write(self.style.WARNING("No active subscribers found."))
            return

        self.stdout.write(f"Sending daily newsletter to {len(recipient_list)} subscribers...")

        # 4. Send email (using mass sending or loop)
        # We'll use a loop so each subscriber gets their own email without seeing other recipients in 'To'
        sent_count = 0
        for email in recipient_list:
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=True,
                )
                sent_count += 1
            except Exception as e:
                self.stderr.write(f"Failed to send to {email}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Successfully sent {sent_count} daily newsletters!"))
