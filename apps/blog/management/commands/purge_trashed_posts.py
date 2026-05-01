from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.blog.models import Post


class Command(BaseCommand):
    help = 'Permanently deletes trashed blog posts older than 30 days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(days=30)
        expired = Post.objects.filter(status='trashed', deleted_at__lte=cutoff)
        count = expired.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS('No expired trashed posts to purge.'))
            return

        if options['dry_run']:
            self.stdout.write(self.style.WARNING(f'[DRY RUN] Would permanently delete {count} post(s):'))
            for post in expired:
                days = (timezone.now() - post.deleted_at).days
                self.stdout.write(f'  - "{post.title}" (trashed {days} days ago)')
        else:
            titles = list(expired.values_list('title', flat=True))
            expired.delete()
            self.stdout.write(self.style.SUCCESS(f'Permanently deleted {count} post(s):'))
            for title in titles:
                self.stdout.write(f'  - "{title}"')
