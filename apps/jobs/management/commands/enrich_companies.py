import re
import requests
from io import BytesIO
from urllib.parse import quote_plus
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.jobs.models import Company

class Command(BaseCommand):
    help = 'Enrich companies with logos, descriptions, and websites using free APIs.'

    def handle(self, *args, **options):
        companies = Company.objects.all()
        total_enriched = 0
        total_skipped = 0

        for company in companies:
            self.stdout.write(f"\nEnriching: {company.name}")
            enriched_something = False

            # STEP 1 & 3: Clearbit Autocomplete for Domain/Website and Logo
            # It's better to use Clearbit Autocomplete to find the real domain first, 
            # then use that domain to fetch the logo.
            domain = None
            if not company.website:
                try:
                    query = quote_plus(company.name)
                    ac_url = f"https://autocomplete.clearbit.com/v1/companies/suggest?query={query}"
                    resp = requests.get(ac_url, timeout=5)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        if data and len(data) > 0:
                            domain = data[0].get('domain')
                            if domain:
                                company.website = f"https://{domain}"
                                enriched_something = True
                except Exception as e:
                    self.stderr.write(f"  [Error] Website fetch failed: {e}")
            else:
                # Extract domain from existing website
                domain = company.website.replace('https://', '').replace('http://', '').split('/')[0]

            # If Autocomplete didn't find a domain, fallback to guessing
            if not domain:
                clean_name = re.sub(r'[^a-z0-9]', '', company.name.lower())
                if len(clean_name) >= 3:
                    domain = f"{clean_name}.com"

            # Fetch Logo from Clearbit using the domain
            if domain and not company.logo:
                try:
                    logo_url = f"https://logo.clearbit.com/{domain}"
                    resp = requests.get(logo_url, timeout=5)
                    if resp.status_code == 200:
                        image_name = f"{domain}_logo.png"
                        company.logo.save(image_name, ContentFile(resp.content), save=False)
                        enriched_something = True
                except Exception as e:
                    self.stderr.write(f"  [Error] Logo fetch failed: {e}")

            # STEP 2: Wikipedia Description
            # Only enrich if it has the default tiny description or is blank
            default_snippet = "is a company hiring entry-level talent"
            if not company.description or default_snippet in company.description.lower():
                try:
                    wiki_name = quote_plus(company.name)
                    wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_name}"
                    headers = {"User-Agent": "JobFoundryHub/1.0 (hello@jobfoundryhub.com)"}
                    resp = requests.get(wiki_url, headers=headers, timeout=5)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        extract = data.get('extract', '')
                        if extract:
                            # Use first 3 sentences
                            sentences = extract.split('. ')
                            summary = '. '.join(sentences[:3])
                            if not summary.endswith('.'):
                                summary += '.'
                            company.description = f"<p>{summary}</p>"
                            enriched_something = True
                except Exception as e:
                    self.stderr.write(f"  [Error] Wikipedia fetch failed: {e}")

            # Save if modified
            if enriched_something:
                try:
                    company.save()
                    self.stdout.write(self.style.SUCCESS(f"Done: {company.name} ✅"))
                    total_enriched += 1
                except Exception as e:
                    self.stderr.write(f"  [Error] Failed to save company: {e}")
                    total_skipped += 1
            else:
                self.stdout.write(self.style.WARNING(f"Skipped: {company.name} ⚠️ (Already enriched or not found)"))
                total_skipped += 1

        self.stdout.write(self.style.SUCCESS(f"\nEnriched: {total_enriched} companies | Skipped: {total_skipped} companies"))
