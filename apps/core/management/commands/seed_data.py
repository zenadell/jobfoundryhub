from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.jobs.models import Company, JobCategory, Job
from apps.blog.models import BlogCategory, Post
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial data for development'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        user = User.objects.first()
        if not user:
            user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write('Created superuser: admin')

        # Categories
        job_categories = ['Technology', 'Design', 'Marketing', 'Sales', 'Customer Support']
        job_cat_objs = []
        for name in job_categories:
            obj, _ = JobCategory.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'icon': 'briefcase',
                    'description': f'Jobs in the {name} field.'
                }
            )
            job_cat_objs.append(obj)

        blog_categories = ['Career Advice', 'Hiring Trends', 'Platform News']
        blog_cat_objs = []
        for name in blog_categories:
            obj, _ = BlogCategory.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'description': f'Insights about {name}.',
                    'meta_title': f'{name} - Job Foundry Hub',
                    'meta_description': f'Read about {name} on our blog.'
                }
            )
            blog_cat_objs.append(obj)

        # Companies
        companies = [
            ('TechCorp', 'technology'),
            ('Designly', 'design'),
            ('MarketFlow', 'marketing'),
            ('SalePoint', 'sales'),
        ]
        company_objs = []
        for name, industry in companies:
            obj, _ = Company.objects.get_or_create(
                name=name,
                defaults={
                    'slug': slugify(name),
                    'description': f'{name} is a leading company in {industry}.',
                    'industry': industry,
                    'size': '51-200',
                    'location': 'New York, NY',
                    'website': f'https://{name.lower()}.com'
                }
            )
            company_objs.append(obj)

        # Jobs
        job_titles = [
            'Software Engineer', 'Frontend Developer', 'UI/UX Designer', 
            'Marketing Manager', 'Account Executive', 'Support Specialist'
        ]
        
        for i in range(10):
            title = random.choice(job_titles)
            Job.objects.get_or_create(
                slug=slugify(f'{title}-{i+1}-{1234}'), # Use a fixed salt for deterministic seeding
                defaults={
                    'title': f'{title} {i+1}',
                    'company': random.choice(company_objs),
                    'category': random.choice(job_cat_objs),
                    'description': '<p>We are looking for a talented individual to join our team.</p>',
                    'requirements': '<p>Must have experience in the field.</p>',
                    'location': 'New York, NY',
                    'region': 'New York',
                    'job_type': 'full-time',
                    'experience_level': 'junior',
                    'salary_period': 'annual',
                    'apply_url': 'https://example.com/apply',
                    'is_active': True,
                    'is_featured': random.choice([True, False]),
                    'expires_at': timezone.now() + timezone.timedelta(days=30)
                }
            )

        # Blog Posts
        post_titles = [
            'How to ace your next interview',
            'Remote work: The future of recruitment',
            '5 tips for building a great resume',
            'The rise of AI in the workplace'
        ]

        for title in post_titles:
            Post.objects.get_or_create(
                slug=slugify(title),
                defaults={
                    'title': title,
                    'category': random.choice(blog_cat_objs),
                    'author': user,
                    'excerpt': f'Summary of {title}.',
                    'content': '<p>Full content of the article goes here. It is very informative.</p>',
                    'read_time': 5,
                    'meta_title': title,
                    'meta_description': f'Read our latest post: {title}',
                    'focus_keyword': 'career',
                    'status': 'published',
                    'published_at': timezone.now()
                }
            )

        # Create SiteSettings singleton
        from apps.core.models import SiteSettings, FAQ
        SiteSettings.objects.get_or_create(pk=1, defaults={
            'site_name':    'Job Foundry Hub',
            'site_tagline': 'Entry-Level Jobs for Recent Graduates',
            'hero_heading': 'Launch Your Career with Confidence',
            'hero_subtext': 'Browse 100+ verified entry-level jobs curated for recent graduates. Free to use.',
            'hero_cta_text': 'Browse All Jobs',
            'contact_email': 'hello@jobfoundryhub.com',
        })

        # Seed FAQs
        faq_data = [
            ('Is it free to search for jobs?', 'Yes, completely free. Create a profile and apply to any job at no cost.', 'job-seekers', 1),
            ('How do I set up a job alert?', 'Go to Job Listings, set your filters, and click "Set Up Alert". You will receive an email whenever a matching job is posted.', 'job-seekers', 2),
            ('How do I upload my resume?', 'Visit the Submit Resume page or update your profile under Account Settings.', 'job-seekers', 3),
            ('Are all jobs entry-level?', 'Yes. Every job on Job Foundry Hub is verified to require 0–2 years of experience.', 'job-seekers', 4),
            ('How do I post a job?', 'Visit the Post a Job page. Submit your details and our team will review and publish within 24 hours.', 'employers', 1),
            ('Is job posting free for employers?', 'We offer free standard listings. Contact us about featured placement options.', 'employers', 2),
            ('How long do job listings stay active?', 'Standard listings are active for 30 days. You can request an extension from our team.', 'employers', 3),
            ('How do I create an account?', 'Click Get Started in the top navigation. Registration takes less than a minute.', 'platform', 1),
            ('Can I save jobs to apply later?', 'Yes. Click the Save button on any job listing. Saved jobs appear in your dashboard.', 'platform', 2),
            ('How do I delete my account?', 'Contact us at hello@jobfoundryhub.com and we will process your request within 48 hours.', 'platform', 3),
        ]
        for question, answer, category, order in faq_data:
            FAQ.objects.get_or_create(
                question=question,
                defaults={'answer': answer, 'category': category, 'order': order, 'is_active': True}
            )
        self.stdout.write('Created SiteSettings and FAQs.')

        self.stdout.write(self.style.SUCCESS('Successfully seeded data!'))
