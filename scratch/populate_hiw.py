import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.core.models import HowItWorksStep

# Seeker Steps
seeker_steps = [
    ("Browse Available Jobs", "Head over to our Job Listings page and explore hundreds of verified entry-level opportunities."),
    ("Read the Full Description", "Click any job card to see the complete role description, requirements, salary range, and company details."),
    ("Click \"Apply Now\"", "Found the right fit? Hit Apply Now — you'll be taken straight to our Submit Resume page."),
    ("Fill In Your Details & Upload Your CV", "Complete the quick application form — add your contact info, cover note, and upload your CV in PDF format."),
    ("We Review & Forward Your Application", "Our team reviews your submission for quality and relevance, then forwards it directly to the hiring company on your behalf."),
]

# Employer Steps
employer_steps = [
    ("Go to Post a Job", "Navigate to our Post a Job page to get started — no account required."),
    ("Fill In the Job Details", "Provide the role title, description, requirements, salary range, location, and your company information."),
    ("Submit for Review", "Once you're happy with the listing, submit it. Our team will review it for quality and compliance."),
    ("Your Job Goes Live Within 24 Hours", "After approval, your job listing goes live on our platform and becomes visible to thousands of job seekers."),
    ("Applications Come Through Our Platform", "Candidates apply via Job Foundry Hub and we forward qualified applications directly to you — simple and hassle-free."),
]

for i, (title, desc) in enumerate(seeker_steps):
    HowItWorksStep.objects.get_or_create(
        title=title,
        category='seekers',
        defaults={'description': desc, 'order': i, 'is_active': True}
    )

for i, (title, desc) in enumerate(employer_steps):
    HowItWorksStep.objects.get_or_create(
        title=title,
        category='employers',
        defaults={'description': desc, 'order': i, 'is_active': True}
    )

print("How It Works steps populated.")
