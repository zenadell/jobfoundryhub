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
        # Limit to 50 companies that have no logo, so we don't hit the 15-min Render build timeout
        companies = Company.objects.filter(logo='').order_by('?')[:50]
        total_enriched = 0
        total_skipped = 0

        for company in companies:
            self.stdout.write(f"\nEnriching: {company.name}")
            enriched_something = False

            # STEP 1 & 3: Domain Mapping
            CURATED_DOMAINS = {
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

            # Get domain — try curated list first, then guess
            domain = None
            for key, val in CURATED_DOMAINS.items():
                if key in company.name.lower():
                    domain = val
                    break
            
            if not domain:
                # Fall back to guessing from company name
                clean = re.sub(
                    r'\b(inc|ltd|llc|corp|corporation|limited|group'
                    r'|holdings|services|solutions|technologies'
                    r'|technology|consulting|international|global'
                    r'|uk|us|usa|plc|co)\b',
                    '', company.name.lower()
                ).strip()
                simple = re.sub(r'[^a-z0-9]', '', clean)
                if len(simple) >= 3:
                    domain = f'{simple}.com'

            if domain:
                company.website = f"https://{domain}"
                enriched_something = True
                
                # Fetch logo
                if not company.logo:
                    try:
                        from django.core.files.base import ContentFile
                        logo_url = f"https://www.google.com/s2/favicons?sz=128&domain={domain}"
                        resp = requests.get(logo_url, timeout=5, allow_redirects=True)
                        if resp.status_code == 200 and len(resp.content) > 100:
                            filename = f"{re.sub(r'[^a-z0-9]', '', company.name.lower())}_logo.png"
                            company.logo.save(
                                filename,
                                ContentFile(resp.content),
                                save=False
                            )
                            enriched_something = True
                    except Exception as e:
                        pass

            # STEP 2: Wikipedia Description
            default_snippet = "is a company hiring entry-level talent"
            if not company.description or default_snippet in company.description.lower():
                try:
                    wiki_name = quote_plus(company.name)
                    wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_name}"
                    headers = {"User-Agent": "JobFoundryHub/1.0 (hello@jobfoundryhub.com)"}
                    resp = requests.get(wiki_url, headers=headers, timeout=2) # Short timeout
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        extract = data.get('extract', '')
                        if extract:
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
