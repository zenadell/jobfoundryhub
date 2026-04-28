from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.db import models
from apps.jobs.models import Company, Job
import uuid

class Command(BaseCommand):
    help = 'Fixes missing slugs for companies and jobs'

    def handle(self, *args, **options):
        # Fix Companies
        companies = Company.objects.filter(models.Q(slug='') | models.Q(slug__isnull=True))
        for company in companies:
            base_slug = slugify(company.name) or 'company'
            unique_slug = base_slug
            while Company.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
            company.slug = unique_slug
            company.save(update_fields=['slug'])
            self.stdout.write(f"Fixed slug for Company: {company.name} -> {company.slug}")

        # Fix Jobs
        jobs = Job.objects.filter(models.Q(slug='') | models.Q(slug__isnull=True))
        for job in jobs:
            base_slug = slugify(job.title) or 'job'
            unique_slug = base_slug
            while Job.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
            job.slug = unique_slug
            job.save(update_fields=['slug'])
            self.stdout.write(f"Fixed slug for Job: {job.title} -> {job.slug}")

        self.stdout.write(self.style.SUCCESS("Slug fixing complete!"))
