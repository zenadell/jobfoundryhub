import os
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.jobs.models import Job

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Clean up expired jobs from the database'

    def handle(self, *args, **options):
        now = timezone.now()
        expired_jobs = Job.objects.filter(expires_at__lt=now)
        count = expired_jobs.count()
        
        if count > 0:
            self.stdout.write(f"Found {count} expired jobs. Deleting...")
            
            # Notify Google before deleting
            from apps.jobs.indexing import notify_google
            domain = os.environ.get('SITE_DOMAIN', 'https://jobfoundryhub.com')
            for job in expired_jobs:
                job_url = f"{domain}/job-listings/{job.slug}/"
                notify_google(job_url, action="URL_DELETED")
                
            expired_jobs.delete()
            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {count} expired jobs."))
        else:
            self.stdout.write(self.style.SUCCESS("No expired jobs found. Everything is up to date."))
