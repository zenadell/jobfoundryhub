from django.db import models
from django.urls import reverse
from django.utils import timezone
from ckeditor.fields import RichTextField

COMPANY_SIZE_CHOICES = [
    ('1-10', '1-10 employees'),
    ('11-50', '11-50 employees'),
    ('51-200', '51-200 employees'),
    ('201-500', '201-500 employees'),
    ('501-1000', '501-1000 employees'),
    ('1000+', '1000+ employees'),
]

REMOTE_CHOICES = [
    ('remote', 'Fully Remote'),
    ('hybrid', 'Hybrid'),
    ('on-site', 'On-Site'),
]

JOB_TYPE_CHOICES = [
    ('full-time', 'Full-time'),
    ('part-time', 'Part-time'),
    ('contract', 'Contract'),
    ('internship', 'Internship'),
]

EXPERIENCE_CHOICES = [
    ('entry', 'Entry Level'),
    ('junior', 'Junior'),
    ('mid', 'Mid Level'),
]

SALARY_PERIOD_CHOICES = [
    ('annual', 'Yearly'),
    ('monthly', 'Monthly'),
    ('hourly', 'Hourly'),
]

class Company(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True, default='')
    industry = models.CharField(max_length=100, blank=True, default='')
    size = models.CharField(choices=COMPANY_SIZE_CHOICES, max_length=20)
    location = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)
    is_partner = models.BooleanField(default=False, help_text="Show this company in the 'Partners' section on the Home page")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('jobs:company_detail', kwargs={'slug': self.slug})

    @property
    def active_jobs_count(self):
        return self.job_set.filter(is_active=True).count()

class JobCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50)  # Lucide icon name
    description = models.TextField()
    job_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Job Categories"

class Job(models.Model):
    # Core fields
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True)
    description = RichTextField()  # Full HTML job description
    requirements = RichTextField(blank=True, default='')
    
    # Location
    location = models.CharField(max_length=200)
    region = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, default='United States')
    is_remote = models.BooleanField(default=False)
    remote_type = models.CharField(choices=REMOTE_CHOICES, max_length=20, blank=True)  # remote/hybrid/on-site
    
    # Employment
    job_type = models.CharField(choices=JOB_TYPE_CHOICES, max_length=20)  # full-time/part-time/contract/internship
    experience_level = models.CharField(choices=EXPERIENCE_CHOICES, max_length=20)  # entry/junior/mid
    
    # Salary
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    salary_period = models.CharField(choices=SALARY_PERIOD_CHOICES, max_length=20, blank=True)  # annual/monthly/hourly
    
    # Meta
    apply_url = models.URLField()
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)
    posted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('jobs:job_detail', kwargs={'slug': self.slug})

    def get_job_type_schema(self):
        mapping = {
            'full-time': 'FULL_TIME',
            'part-time': 'PART_TIME',
            'contract': 'CONTRACTOR',
            'internship': 'INTERN',
        }
        return mapping.get(self.job_type, 'FULL_TIME')

    def get_salary_period_schema(self):
        mapping = {
            'annual': 'YEAR',
            'monthly': 'MONTH',
            'hourly': 'HOUR',
        }
        return mapping.get(self.salary_period, 'YEAR')

    @property
    def structured_data(self):
        """Returns JSON-LD JobPosting schema for Google Jobs"""
        schema = {
            "@context": "https://schema.org/",
            "@type": "JobPosting",
            "title": self.title,
            "description": self.description,
            "datePosted": self.posted_at.isoformat(),
            "validThrough": self.expires_at.isoformat(),
            "employmentType": self.get_job_type_schema(),
            "hiringOrganization": {
                "@type": "Organization",
                "name": self.company.name,
                "sameAs": self.company.website,
            },
            "jobLocation": {
                "@type": "Place",
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": self.location,
                    "addressRegion": self.region,
                    "addressCountry": "US"
                }
            },
            "educationRequirements": "Bachelor's degree or equivalent",
            "experienceRequirements": "0-2 years experience"
        }
        if self.company.logo:
            schema["hiringOrganization"]["logo"] = self.company.logo.url
            
        if self.is_remote:
            schema["jobLocationType"] = "TELECOMMUTE"
            
        if self.salary_min:
            schema["baseSalary"] = {
                "@type": "MonetaryAmount",
                "currency": self.salary_currency,
                "value": {
                    "@type": "QuantitativeValue",
                    "minValue": float(self.salary_min),
                    "maxValue": float(self.salary_max) if self.salary_max else float(self.salary_min),
                    "unitText": self.get_salary_period_schema()
                }
            }
        return schema

class JobAlert(models.Model):
    email = models.EmailField()
    keywords = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    job_type = models.CharField(max_length=50, blank=True)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert for {self.email}"

class ResumeSubmission(models.Model):
    full_name    = models.CharField(max_length=200)
    email        = models.EmailField()
    position     = models.CharField(max_length=200, blank=True,
                       help_text='Job title or position they are applying for')
    resume       = models.FileField(upload_to='resumes/%Y/%m/', blank=True, null=True)
    cover_note   = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_reviewed  = models.BooleanField(default=False)
    notes        = models.TextField(blank=True, help_text='Internal admin notes')

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.full_name} — {self.submitted_at.strftime('%Y-%m-%d')}"


class JobPostingRequest(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending Review'),
        ('approved', 'Approved — Published'),
        ('rejected', 'Rejected'),
    ]
    # Submitter info
    company_name   = models.CharField(max_length=200)
    contact_name   = models.CharField(max_length=200)
    contact_email  = models.EmailField()
    contact_phone  = models.CharField(max_length=30, blank=True)
    company_website = models.URLField(blank=True)

    # Job details
    job_title       = models.CharField(max_length=300)
    job_description = RichTextField()
    job_requirements = RichTextField(blank=True)
    job_location    = models.CharField(max_length=200)
    job_type        = models.CharField(choices=JOB_TYPE_CHOICES, max_length=20)
    is_remote       = models.BooleanField(default=False)
    salary_range    = models.CharField(max_length=100, blank=True)
    apply_url       = models.URLField(blank=True)

    # Admin workflow
    status     = models.CharField(choices=STATUS_CHOICES, max_length=20, default='pending')
    admin_notes = models.TextField(blank=True, help_text='Internal notes — not visible to submitter')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"[{self.status.upper()}] {self.job_title} @ {self.company_name}"
