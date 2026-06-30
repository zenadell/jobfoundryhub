"""
Remove duplicate job listings.

A "duplicate" is two or more jobs at the SAME company whose titles are
identical after normalization (lowercase, punctuation stripped). This catches
Adzuna re-posts like "Coordinator - X" vs "Coordinator – X" while leaving
genuinely different listings (different cities, clearance levels, etc.) alone.

The NEWEST job in each duplicate group is kept; the older copies are deleted.

Usage:
    python manage.py dedupe_jobs            # delete duplicates
    python manage.py dedupe_jobs --dry-run  # just report, change nothing
"""
from collections import defaultdict

from django.core.management.base import BaseCommand

from apps.jobs.models import Job
from apps.jobs.utils import normalize_title


class Command(BaseCommand):
    help = 'Delete duplicate jobs (same company + normalized title), keeping the newest.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Report duplicates without deleting anything.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Group every job by (company_id, normalized title).
        groups = defaultdict(list)
        qs = Job.objects.all().only('id', 'title', 'company_id', 'posted_at')
        for job in qs:
            key = (job.company_id, normalize_title(job.title))
            groups[key].append(job)

        to_delete = []
        dup_groups = 0
        for (company_id, norm), jobs in groups.items():
            if len(jobs) < 2:
                continue
            dup_groups += 1
            # Keep the newest (latest posted_at, then highest id); delete the rest.
            jobs.sort(key=lambda j: (j.posted_at, j.id))
            keep = jobs[-1]
            losers = jobs[:-1]
            to_delete.extend(losers)
            self.stdout.write(
                f'  • "{keep.title[:55]}" — {len(jobs)} copies, '
                f'keeping #{keep.id}, removing {[j.id for j in losers]}'
            )

        ids = [j.id for j in to_delete]
        self.stdout.write('')
        if not ids:
            self.stdout.write(self.style.SUCCESS('✅ No duplicates found.'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(
                f'🔎 DRY RUN — would delete {len(ids)} duplicate job(s) '
                f'across {dup_groups} group(s). Nothing changed.'
            ))
            return

        deleted, _ = Job.objects.filter(id__in=ids).delete()
        self.stdout.write(self.style.SUCCESS(
            f'🗑  Deleted {len(ids)} duplicate job(s) across {dup_groups} group(s).'
        ))
