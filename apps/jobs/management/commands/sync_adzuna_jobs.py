"""
Fetch real entry-level job listings from the Adzuna API
and save them into the local Job / Company / JobCategory tables.

Usage:
    python manage.py sync_adzuna_jobs
    python manage.py sync_adzuna_jobs --delete-dummy   # also purge old seed data
"""

import os
import random
import re
import time
import requests
from datetime import timedelta
from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.jobs.models import Job, Company, JobCategory


# ── Adzuna credentials ──────────────────────────────────────────
ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID', 'ce95f522')
ADZUNA_API_KEY = os.environ.get('ADZUNA_API_KEY', '59b8ac4579f4f1e5344cbb158b78c0c6')

# ── Countries & currency mapping ────────────────────────────────
COUNTRIES = {
    'us': {'currency': 'USD', 'country_name': 'United States'},
    'gb': {'currency': 'GBP', 'country_name': 'United Kingdom'},
}

# ── Search queries for variety ──────────────────────────────────
CURATED_COMPANIES = [
    'Hays',
    'Bupa',
    'Tesco',
    'Deliveroo',
    'Barclays',
    'Vodafone',
    'Sky',
    'Sainsbury',
    'O2',
    'EE',
]

# ── Category mapping (keyword → category name) ─────────────────
CATEGORY_MAP = [
    (['market', 'social media', 'seo', 'content'],       'Marketing'),
    (['develop', 'engineer', 'software', 'program', 'devops', 'frontend', 'backend'], 'Technology'),
    (['design', 'creative', 'graphic', 'ux', 'ui'],      'Design'),
    (['data', 'analyst', 'analytics', 'scientist'],       'Data & Analytics'),
    (['finance', 'account', 'audit', 'tax', 'banking'],   'Finance'),
    (['hr', 'human resource', 'recruit', 'talent'],       'Human Resources'),
    (['customer', 'support', 'service', 'help desk'],     'Customer Service'),
    (['sales', 'business develop'],                        'Sales'),
]

# ── Well-known company → domain mapping for logo fetching ──────
KNOWN_DOMAINS = {
    'hays': 'hays.co.uk',
    'bupa': 'bupa.co.uk',
    'tesco': 'tesco.com',
    'deliveroo': 'deliveroo.co.uk',
    'barclays': 'barclays.co.uk',
    'vodafone': 'vodafone.co.uk',
    'sky': 'sky.com',
    'sainsbury': 'sainsburys.co.uk',
    'o2': 'o2.co.uk',
    'ee': 'ee.co.uk',
}


class Command(BaseCommand):
    help = 'Fetch entry-level jobs from Adzuna API and save to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete-dummy',
            action='store_true',
            help='Delete old seed/dummy jobs before syncing',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Wiping database of all existing jobs and companies..."))
        Job.objects.all().delete()
        Company.objects.all().delete()

        total_saved = 0

        for company in CURATED_COMPANIES:
            count = self._fetch_and_save(company)
            total_saved += count
            # Be polite to the API
            time.sleep(0.5)

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Total curated jobs synced: {total_saved}'
        ))

    # ─────────────────────────────────────────────────────────────
    #  FETCH ONE SEARCH PAGE
    # ─────────────────────────────────────────────────────────────
    def _fetch_and_save(self, company):
        """Fetch one page of results from Adzuna and save them."""
        # Using UK as the primary market for these curated standard companies
        url = f'https://api.adzuna.com/v1/api/jobs/gb/search/1'
        params = {
            'app_id': ADZUNA_APP_ID,
            'app_key': ADZUNA_API_KEY,
            'results_per_page': 10,
            'company': company,
            'content-type': 'application/json',
        }

        try:
            self.stdout.write(f'  📡 Fetching jobs for: "{company}"...')
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            self.stderr.write(self.style.WARNING(
                f'  ⚠️  API error for "{company}": {e}'
            ))
            return 0

        results = data.get('results', [])
        saved = 0

        for item in results:
            try:
                meta = {'currency': 'GBP', 'country_name': 'United Kingdom'}
                if self._save_job(item, 'gb', meta):
                    saved += 1
            except Exception as e:
                self.stderr.write(self.style.WARNING(
                    f'  ⚠️  Skipped job: {e}'
                ))

        self.stdout.write(f'     → Saved {saved}/{len(results)} jobs')
        return saved

    # ─────────────────────────────────────────────────────────────
    #  SAVE ONE JOB
    # ─────────────────────────────────────────────────────────────
    def _save_job(self, item, country_code, meta):
        """Parse one Adzuna result dict and save as a Job."""
        title = (item.get('title') or '').strip()
        if not title:
            return False

        # Clean HTML tags from title
        title = re.sub(r'<[^>]+>', '', title).strip()
        if not title:
            return False

        # ── Company ─────────────────────────────────────────────
        company_data = item.get('company', {})
        company_name = (company_data.get('display_name') or '').strip()
        if not company_name:
            company_name = 'Unknown Company'

        company = self._get_or_create_company(company_name, item, meta)

        # ── Dedup: skip if same title + company already exists ─
        if Job.objects.filter(title=title[:300], company=company).exists():
            return False

        # ── Slug (unique) ──────────────────────────────────────
        base_slug = slugify(f"{title}-{company_name}")[:40]
        slug = f"{base_slug}-{random.randint(1000, 9999)}"

        # Ensure slug uniqueness
        while Job.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{random.randint(1000, 9999)}"

        # ── Description ────────────────────────────────────────
        description = item.get('description', '') or ''
        description = re.sub(r'<[^>]+>', '', description).strip()
        if not description:
            description = title

        # ── Location ───────────────────────────────────────────
        location_data = item.get('location', {})
        location = (location_data.get('display_name') or '').strip()
        if not location:
            location = meta['country_name']

        # Extract region from location areas
        areas = location_data.get('area', [])
        region = areas[0] if areas else ''

        # ── Remote detection ───────────────────────────────────
        combined_text = f"{title} {description}".lower()
        is_remote = 'remote' in combined_text or 'work from home' in combined_text

        # ── Salary ─────────────────────────────────────────────
        salary_min = item.get('salary_min')
        salary_max = item.get('salary_max')

        # ── Category ───────────────────────────────────────────
        category = self._detect_category(title)

        # ── Country name ───────────────────────────────────────
        country_names = {
            'us': 'United States',
            'gb': 'United Kingdom',
            'ng': 'Nigeria',
        }

        # ── Create the Job ─────────────────────────────────────
        Job.objects.create(
            title=title[:300],
            slug=slug,
            company=company,
            category=category,
            description=description,
            requirements='',
            location=location[:200],
            region=region[:100] if region else '',
            country=country_names.get(country_code, 'United States'),
            is_remote=is_remote,
            remote_type='remote' if is_remote else '',
            job_type='full-time',
            experience_level='entry',
            salary_min=salary_min,
            salary_max=salary_max,
            salary_currency=meta['currency'],
            salary_period='annual' if salary_min else '',
            apply_url='https://www.jobfoundryhub.com/submit-resume/',
            is_active=True,
            is_featured=False,
            expires_at=timezone.now() + timedelta(days=30),
        )

        self.stdout.write(f'  ✅ Saved: {title[:60]} at {company_name}')
        return True

    # ─────────────────────────────────────────────────────────────
    #  COMPANY
    # ─────────────────────────────────────────────────────────────
    def _get_or_create_company(self, name, item, meta):
        """Get or create a Company record with optional logo fetch."""
        slug = slugify(name)[:50]
        if not slug:
            slug = f"company-{random.randint(10000, 99999)}"

        company, created = Company.objects.get_or_create(
            slug=slug,
            defaults={
                'name': name[:200],
                'description': f'{name} is a company hiring entry-level talent.',
                'industry': self._guess_industry(item),
                'size': '51-200',
                'location': self._extract_location(item, meta),
                'website': '',
                'is_active': True,
            }
        )

        # Try to fetch a logo for new companies
        if created:
            self._try_fetch_logo(company, name)

        return company

    def _guess_industry(self, item):
        """Guess the industry from the Adzuna category tag."""
        cat = item.get('category', {})
        label = cat.get('label', '') or ''
        if label:
            return label[:100]
        return 'General'

    def _extract_location(self, item, meta):
        """Pull the company location from the job result."""
        loc = item.get('location', {})
        display = loc.get('display_name', '')
        return display[:200] if display else meta['country_name']

    def _try_fetch_logo(self, company, name):
        """Try fetching a company logo from Clearbit by guessing domain."""
        domain = self._guess_domain(name)
        if not domain:
            return

        logo_url = f'https://logo.clearbit.com/{domain}'
        try:
            resp = requests.head(logo_url, timeout=5, allow_redirects=True)
            if resp.status_code == 200:
                # Save the URL as the logo path
                # Since our model uses ImageField, we store externally
                # by saving the website field instead for reference
                company.website = f'https://{domain}'
                company.save(update_fields=['website'])
                self.stdout.write(f'     🖼  Found logo domain: {domain}')
        except requests.RequestException:
            pass

    def _guess_domain(self, name):
        """Guess a company's website domain from their name."""
        clean = name.lower().strip()

        # Check known domains first
        for key, domain in KNOWN_DOMAINS.items():
            if key in clean:
                return domain

        # Try simple guess: "Company Name" → companyname.com
        simple = re.sub(r'[^a-z0-9]', '', clean)
        if len(simple) >= 3:
            return f'{simple}.com'

        return None

    # ─────────────────────────────────────────────────────────────
    #  CATEGORY DETECTION
    # ─────────────────────────────────────────────────────────────
    def _detect_category(self, title):
        """Detect the job category from the title using keyword matching."""
        title_lower = title.lower()

        for keywords, cat_name in CATEGORY_MAP:
            if any(kw in title_lower for kw in keywords):
                cat, _ = JobCategory.objects.get_or_create(
                    slug=slugify(cat_name),
                    defaults={
                        'name': cat_name,
                        'icon': 'briefcase',
                        'description': f'{cat_name} jobs and opportunities.',
                    }
                )
                return cat

        # Default: General
        cat, _ = JobCategory.objects.get_or_create(
            slug='general',
            defaults={
                'name': 'General',
                'icon': 'briefcase',
                'description': 'General job opportunities.',
            }
        )
        return cat

    # ─────────────────────────────────────────────────────────────
    #  CLEANUP
    # ─────────────────────────────────────────────────────────────
    def _delete_dummy_data(self):
        """Remove old seed/dummy jobs and companies."""
        # Delete jobs with seed slugs (ending in -1234)
        dummy_jobs = Job.objects.filter(slug__endswith='-1234')
        count = dummy_jobs.count()
        dummy_jobs.delete()
        self.stdout.write(f'🗑  Deleted {count} dummy jobs')

        # Delete orphaned companies (no jobs)
        orphaned = Company.objects.filter(job__isnull=True)
        orphan_count = orphaned.count()
        orphaned.delete()
        self.stdout.write(f'🗑  Deleted {orphan_count} orphaned companies')
