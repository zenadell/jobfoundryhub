#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements/base.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Sync real jobs from Adzuna API (dedup-safe, skips existing)
python manage.py sync_adzuna_jobs --delete-dummy

# Enrich newly synced companies with logos and descriptions via Clearbit & Wikipedia
python manage.py enrich_companies

# Inject robust 400-600 word authentic profiles for companies without using external AI quotas
python manage.py seed_company_profiles
