# 🎯 TEMPLATE INTEGRATION BRIEF
### For AI IDE | Read this ENTIRE document before touching any file

---

## THE SITUATION

You have been given the complete HTML export from a Webflow "Better Talent" 
job board template. It contains 11 page templates + utility pages.

Your job is NOT to redesign anything. Your job is to:
1. Use these HTML files as-is for ALL structure, layout, and CSS classes
2. Strip every piece of hardcoded content
3. Wire every dynamic section to Django views/DB
4. Use skeleton loaders wherever data comes from the database

**The HTML files are the final design. Do not change the design.**

---

## ⚠️ CRITICAL ARCHITECTURE DECISION — READ THIS FIRST

The `dynamic_render_protocol.md` uses JavaScript `fetch()` to load content 
client-side. **DO NOT USE THIS APPROACH for the main content on any page.**

Here is why this matters for this project specifically:

- Google AdSense reviewers visit the site and evaluate content quality
- Google's crawler indexes what it sees in the initial HTML response  
- If job listings, blog posts, and page content only appear after a JS fetch,
  Google may see empty pages and reject the AdSense application
- SEO rankings depend on server-rendered content in the initial HTML

**THE RULE:**
- All primary page content (jobs, blog posts, stats, company listings) = 
  **Server-side rendered via Django template tags** — in the HTML on first load
- Skeleton CSS = shown only when a queryset returns empty results
- The `DynamicRenderer` JS class = only for secondary interactive features 
  (live search filtering, infinite scroll, "load more" buttons) — NOT for 
  initial page content

This is the architecture that gets AdSense approved. Follow it exactly.

---

## WHAT YOU HAVE

### Page Templates (in pages-templets/)
| File | Django Template | URL |
|------|----------------|-----|
| home.html | templates/pages/home.html | / |
| jobs.html | templates/jobs/list.html | /jobs/ |
| job-post.html | templates/jobs/detail.html | /jobs/<slug>/ |
| blog.html | templates/blog/list.html | /blog/ |
| blog-post.html | templates/blog/detail.html | /blog/<slug>/ |
| about.html | templates/pages/about.html | /about/ |
| contact-us.html | templates/pages/contact.html | /contact/ |
| conpanies.html | templates/jobs/companies.html | /companies/ |
| company-single.html | templates/jobs/company_detail.html | /companies/<slug>/ |
| post-job.html | templates/jobs/post_job.html | /post-a-job/ |
| submit-resume.html | templates/accounts/submit_resume.html | /submit-resume/ |

### Utility Pages (in utility pages/)
| File | Django Template | URL |
|------|----------------|-----|
| error-404.html | templates/404.html | (Django handler404) |
| coming-soon.html | templates/pages/coming_soon.html | /coming-soon/ |
| confirmation-resume.html | templates/pages/confirm_resume.html | /confirm/resume/ |
| confirmation-contact.html | templates/pages/confirm_contact.html | /confirm/contact/ |
| confirmation-job-form.html | templates/pages/confirm_job.html | /confirm/job/ |
| style-guide.html | DELETE — not needed | — |
| license.html | DELETE — not needed | — |
| change-log.html | DELETE — not needed | — |

---

## THE STRIPPING RULES

Apply these to EVERY HTML file before converting to Django template.

### DELETE THESE ENTIRELY

```
1. The HTML comment on line 2: <!-- This site was created in Webflow -->
2. All data-wf-* attributes on <html> tag:
   data-wf-domain, data-wf-page, data-wf-site
3. <meta content="Webflow" name="generator">
4. All <link> tags pointing to cdn.prod.website-files.com
5. All <link> tags pointing to assets-global.website-files.com
6. The <script> block containing WebFont.load({...})
7. The <script> block containing window.__WEBFLOW_CURRENCY_SETTINGS
8. The <script> block containing the w-mod touch detection
9. The jQuery <script> tag from d3e54v103j8qbb.cloudfront.net
10. The webflow JS <script> tag from assets-global.website-files.com
11. All data-w-id="..." attributes from every element
12. All style="opacity:0" attributes (Webflow animation init)
13. The cart/ecommerce section (this is a job board, not a shop):
    - Everything with class w-commerce-* 
    - The cart icon and cart dropdown in the navbar
14. Footer links to: Style Guide, Licenses, Changelog, Coming Soon (template nav)
15. Footer text: "Design by We-R. | Powered by Webflow"
16. All srcset attributes on <img> tags (we'll handle responsive images ourselves)
```

### REPLACE THESE

```
<html data-wf-...>  →  <html lang="en" data-theme="light">

<title>Better Talent | ...</title>
→  <title>{% block title %}...{% endblock %} | {{ site_name }}</title>

All <meta> description/og/twitter content with Better Talent text
→  Django {% block %} tags as shown in MASTER_PROJECT.md Section 6

The Webflow CSS <link>
→  <link rel="stylesheet" href="{% static 'css/webflow-base.css' %}">
   <link rel="stylesheet" href="{% static 'css/main.css' %}">
   <link rel="stylesheet" href="{% static 'css/skeletons.css' %}">

The Google WebFont <script>
→  <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">

The logo <img src="https://cdn.prod...Logo.svg">
→  <img src="{% static 'images/logo.svg' %}" alt="{{ site_name }}" class="navbar-logo">

The favicon <link href="https://cdn.prod...favicon...">
→  <link rel="shortcut icon" href="{% static 'images/favicon.png' %}" type="image/png">

All CDN image URLs in static/decorative images (icons, UI elements, backgrounds)
→  {% static 'images/[descriptive-name].svg' %}
   Name them by what they ARE not by their Webflow filename
   Examples:
   - "lieu-de-recherche...svg" → location-icon.svg
   - "document-signe...svg"   → job-type-icon.svg
   - "illustration green.svg" → hero-illustration.svg

Copyright footer text
→  Copyright © {% now "Y" %} {{ site_name }}. All rights reserved.

All href="/job-offers/..." 
→  href="{% url 'jobs:detail' slug=job.slug %}"

All href="/blog/..."
→  href="{% url 'blog:detail' slug=post.slug %}"

All href="/companies/..."
→  href="{% url 'jobs:company_detail' slug=company.slug %}"
```

---

## PAGE-BY-PAGE CONVERSION GUIDE

---

### PAGE 1: home.html

**What stays static (keep the HTML exactly):**
- Navbar structure and all nav links (update hrefs only)
- Hero section layout — the heading, subtext, buttons, decorative images
- "Why choose us" / features section layout
- "Become a better talent" CTA section layout  
- Footer structure

**What becomes Django template variables (static text we control):**
```html
<!-- Hero heading — hardcoded by us, not from DB -->
<h1 class="heading-1">Launch Your Career with Confidence</h1>
<p>Browse {{ stats.active_jobs_count }}+ verified entry-level jobs curated for recent graduates.</p>

<!-- Stats section — from DB -->
<div class="heading-2">{{ stats.active_jobs_count }}+</div>
<p>Active Job Listings</p>

<div class="heading-2">{{ stats.companies_count }}+</div>
<p>Hiring Companies</p>

<div class="heading-2">{{ stats.users_count }}+</div>
<p>Registered Job Seekers</p>
```

**What becomes a Django loop (job listings section):**

The home page has 6 hardcoded `<div role="listitem" class="w-dyn-item">` job cards.
Replace ALL 6 of them with ONE loop + skeleton fallback:

```html
<!-- REMOVE: all 6 hardcoded w-dyn-item blocks -->
<!-- REPLACE WITH: -->

<div role="list" class="job-offers-listing-collection w-dyn-items">
  {% if featured_jobs %}
    {% for job in featured_jobs %}
    <div role="listitem" class="w-dyn-item">
      <div class="job-offer-wrapper">
        <div class="display-horizontal-space-btw vertical-left-mobile">
          <h3 class="no-margin">{{ job.title }}</h3>
          <div class="department-badge">
            <div>{{ job.category.name }}</div>
          </div>
        </div>
        <div class="margin-vertical margin-xsmall">
          <p>{{ job.description|truncatewords:20 }}</p>
        </div>
        <div class="display-horizontal-left gap-2rem vertical-left-mobile">
          <div class="display-horizontal-left gap-1rem">
            <img src="{% static 'images/location-icon.svg' %}" loading="lazy" alt="" class="icon-1x1-xsmall">
            <div class="job-info-text">
              {% if job.is_remote %}Remote{% else %}{{ job.location }}{% endif %}
            </div>
          </div>
          <div class="display-horizontal-left gap-1rem">
            <img src="{% static 'images/job-type-icon.svg' %}" loading="lazy" alt="" class="icon-1x1-xsmall">
            <div class="job-info-text">{{ job.get_job_type_display }}</div>
          </div>
          <a href="{% url 'jobs:company_detail' slug=job.company.slug %}"
             class="display-horizontal-left gap-1rem w-inline-block">
            {% if job.company.logo %}
              <img src="{{ job.company.logo.url }}" loading="lazy" alt="{{ job.company.name }}" class="icon-1x1-xsmall">
            {% else %}
              <div class="skeleton skeleton--logo-xsmall"></div>
            {% endif %}
            <div class="job-info-text">{{ job.company.name }}</div>
          </a>
        </div>
        <div class="margin-top margin-small">
          <a href="{% url 'jobs:detail' slug=job.slug %}" class="button button-small w-button">
            Learn more
          </a>
        </div>
      </div>
    </div>
    {% endfor %}
  {% else %}
    {# Skeleton cards — show 6 when DB is empty #}
    {% for i in "123456" %}
    <div role="listitem" class="w-dyn-item">
      <div class="job-offer-wrapper">
        <div class="display-horizontal-space-btw vertical-left-mobile">
          <div class="skeleton skeleton--text skeleton--text-xl no-margin"></div>
          <div class="skeleton skeleton--badge"></div>
        </div>
        <div class="margin-vertical margin-xsmall">
          <div class="skeleton skeleton--text skeleton--text-md"></div>
          <div class="skeleton skeleton--text skeleton--text-sm" style="margin-top:6px"></div>
        </div>
        <div class="display-horizontal-left gap-2rem vertical-left-mobile" style="margin-top:12px">
          <div class="skeleton skeleton--text skeleton--text-sm"></div>
          <div class="skeleton skeleton--text skeleton--text-sm"></div>
          <div class="skeleton skeleton--text skeleton--text-sm"></div>
        </div>
        <div class="margin-top margin-small">
          <div class="skeleton skeleton--badge" style="width:100px;height:36px;border-radius:4px"></div>
        </div>
      </div>
    </div>
    {% endfor %}
  {% endif %}
</div>
```

**What becomes a Django loop (blog section):**

The home page has 3 hardcoded blog cards. Replace ALL 3 with one loop:

```html
<div role="list" class="blog-listing-collection w-dyn-items">
  {% if recent_posts %}
    {% for post in recent_posts %}
    <div role="listitem" class="w-dyn-item">
      <a href="{% url 'blog:detail' slug=post.slug %}" class="blog-listing-wrapper w-inline-block">
        <div class="position-relative">
          {% if post.featured_image %}
            <img src="{{ post.featured_image.url }}" loading="lazy" alt="{{ post.title }}" class="blog-thumbnail">
          {% else %}
            <div class="skeleton skeleton--blog-img"></div>
          {% endif %}
          <div class="position-absolute item-19">
            <div>{{ post.category.name }}</div>
          </div>
        </div>
        <div class="margin-top margin-xsmall">
          <h3 class="heading-blog-title">{{ post.title }}</h3>
          <p>{{ post.excerpt|truncatewords:15 }}</p>
          <div class="text-link red">Read more</div>
        </div>
      </a>
    </div>
    {% endfor %}
  {% else %}
    {% for i in "123" %}
    <div role="listitem" class="w-dyn-item">
      <div class="blog-listing-wrapper">
        <div class="skeleton skeleton--blog-img"></div>
        <div class="margin-top margin-xsmall">
          <div class="skeleton skeleton--text skeleton--text-lg" style="margin-bottom:8px"></div>
          <div class="skeleton skeleton--text skeleton--text-md"></div>
          <div class="skeleton skeleton--text skeleton--text-sm" style="margin-top:6px"></div>
        </div>
      </div>
    </div>
    {% endfor %}
  {% endif %}
</div>
```

**home view context (views.py):**
```python
def home(request):
    from django.db.models import Count
    return render(request, 'pages/home.html', {
        'featured_jobs': Job.objects.filter(
            is_active=True, is_featured=True
        ).select_related('company', 'category').order_by('-posted_at')[:6],
        'recent_posts': Post.objects.filter(
            status='published'
        ).select_related('author', 'category').order_by('-published_at')[:3],
        'stats': {
            'active_jobs_count': Job.objects.filter(is_active=True).count(),
            'companies_count':   Company.objects.filter(is_active=True).count(),
            'users_count':       User.objects.filter(is_active=True).count(),
        },
    })
```

---

### PAGE 2: jobs.html → jobs/list.html

**Static structure:** Keep the filter sidebar, search bar, header exactly.

**Dynamic section — the job listings grid:**
The file has 7 `w-dyn-item` job cards. Replace with:

```html
<div role="list" class="jobs-listing-collection w-dyn-items" id="jobs-grid">
  {% if page_obj.object_list %}
    {% for job in page_obj %}
    <div role="listitem" class="w-dyn-item">
      <!-- same job-offer-wrapper structure as home, but with full detail -->
      <div class="job-offer-wrapper">
        <div class="display-horizontal-space-btw vertical-left-mobile">
          <h2 class="no-margin heading-5">{{ job.title }}</h2>
          <div class="department-badge">
            <div>{{ job.category.name }}</div>
          </div>
        </div>
        <div class="margin-vertical margin-xsmall">
          <p>{{ job.description|truncatewords:25 }}</p>
        </div>
        <div class="display-horizontal-left gap-2rem vertical-left-mobile">
          <div class="display-horizontal-left gap-1rem">
            <img src="{% static 'images/location-icon.svg' %}" alt="" class="icon-1x1-xsmall">
            <div class="job-info-text">{% if job.is_remote %}Remote{% else %}{{ job.location }}{% endif %}</div>
          </div>
          <div class="display-horizontal-left gap-1rem">
            <img src="{% static 'images/job-type-icon.svg' %}" alt="" class="icon-1x1-xsmall">
            <div class="job-info-text">{{ job.get_job_type_display }}</div>
          </div>
          {% if job.salary_min %}
          <div class="display-horizontal-left gap-1rem">
            <img src="{% static 'images/salary-icon.svg' %}" alt="" class="icon-1x1-xsmall">
            <div class="job-info-text">${{ job.salary_min|intcomma }}{% if job.salary_max %} – ${{ job.salary_max|intcomma }}{% endif %}</div>
          </div>
          {% endif %}
        </div>
        <div class="margin-top margin-small display-horizontal-space-btw">
          <a href="{% url 'jobs:company_detail' slug=job.company.slug %}" 
             class="display-horizontal-left gap-1rem w-inline-block">
            {% if job.company.logo %}
              <img src="{{ job.company.logo.url }}" alt="{{ job.company.name }}" class="icon-1x1-xsmall">
            {% else %}
              <div class="skeleton skeleton--logo-xsmall"></div>
            {% endif %}
            <div class="job-info-text">{{ job.company.name }}</div>
          </a>
          <a href="{% url 'jobs:detail' slug=job.slug %}" class="button button-small w-button">
            Learn more
          </a>
        </div>
      </div>
    </div>
    {% endfor %}
  {% else %}
    {% for i in "12345678" %}
    <div role="listitem" class="w-dyn-item">
      <!-- skeleton card same structure as home page skeleton -->
      <div class="job-offer-wrapper">
        <div class="skeleton skeleton--text skeleton--text-xl no-margin" style="margin-bottom:12px"></div>
        <div class="skeleton skeleton--text skeleton--text-md"></div>
        <div class="skeleton skeleton--text skeleton--text-sm" style="margin-top:6px"></div>
        <div class="display-horizontal-left gap-2rem" style="margin-top:14px">
          <div class="skeleton skeleton--text skeleton--text-sm"></div>
          <div class="skeleton skeleton--text skeleton--text-sm"></div>
        </div>
      </div>
    </div>
    {% endfor %}
  {% endif %}
</div>

<!-- Pagination -->
{% if page_obj.has_other_pages %}
<div class="pagination-wrapper">
  {% if page_obj.has_previous %}
    <a href="?page={{ page_obj.previous_page_number }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}{% if request.GET.category %}&category={{ request.GET.category }}{% endif %}" class="button black w-button">← Previous</a>
  {% endif %}
  <span class="pagination-info">Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>
  {% if page_obj.has_next %}
    <a href="?page={{ page_obj.next_page_number }}{% if request.GET.q %}&q={{ request.GET.q }}{% endif %}{% if request.GET.category %}&category={{ request.GET.category }}{% endif %}" class="button w-button">Next →</a>
  {% endif %}
</div>
{% endif %}
```

**Filter form — keep the HTML form structure, wire up GET params:**
```html
<form method="GET" action="{% url 'jobs:list' %}" class="jobs-filter-form">
  {% csrf_token %}
  <input type="text" name="q" value="{{ request.GET.q }}" 
         placeholder="Job title or keyword" class="search-input w-input">
  <input type="text" name="location" value="{{ request.GET.location }}"
         placeholder="Location" class="search-input w-input">
  <select name="category" class="select-field w-select">
    <option value="">All Categories</option>
    {% for cat in job_categories %}
      <option value="{{ cat.slug }}" {% if request.GET.category == cat.slug %}selected{% endif %}>
        {{ cat.name }}
      </option>
    {% endfor %}
  </select>
  <select name="job_type" class="select-field w-select">
    <option value="">All Types</option>
    <option value="full-time"   {% if request.GET.job_type == 'full-time' %}selected{% endif %}>Full Time</option>
    <option value="part-time"   {% if request.GET.job_type == 'part-time' %}selected{% endif %}>Part Time</option>
    <option value="contract"    {% if request.GET.job_type == 'contract' %}selected{% endif %}>Contract</option>
    <option value="internship"  {% if request.GET.job_type == 'internship' %}selected{% endif %}>Internship</option>
  </select>
  <label class="checkbox-field w-checkbox">
    <input type="checkbox" name="remote" value="true" class="w-checkbox-input"
           {% if request.GET.remote %}checked{% endif %}>
    <span class="w-form-label">Remote only</span>
  </label>
  <button type="submit" class="button w-button">Search Jobs</button>
  {% if request.GET.q or request.GET.category or request.GET.job_type or request.GET.remote %}
    <a href="{% url 'jobs:list' %}" class="button button-secondary w-button">Clear Filters</a>
  {% endif %}
</form>
```

**Result count (keep the HTML element, wire up data):**
```html
<div class="jobs-result-count">
  Showing {{ page_obj.start_index }}–{{ page_obj.end_index }} of {{ total_count }} jobs
</div>
```

**jobs list view:**
```python
def job_list(request):
    jobs = Job.objects.filter(is_active=True).select_related('company', 'category')
    q          = request.GET.get('q', '').strip()
    location   = request.GET.get('location', '').strip()
    category   = request.GET.get('category', '').strip()
    job_type   = request.GET.get('job_type', '').strip()
    remote     = request.GET.get('remote', '')
    
    if q:        jobs = jobs.filter(Q(title__icontains=q) | Q(description__icontains=q) | Q(company__name__icontains=q))
    if location: jobs = jobs.filter(location__icontains=location)
    if category: jobs = jobs.filter(category__slug=category)
    if job_type: jobs = jobs.filter(job_type=job_type)
    if remote:   jobs = jobs.filter(is_remote=True)
    
    jobs = jobs.order_by('-is_featured', '-posted_at')
    total_count = jobs.count()
    paginator = Paginator(jobs, 12)
    page_obj  = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'jobs/list.html', {
        'page_obj':       page_obj,
        'total_count':    total_count,
        'job_categories': JobCategory.objects.all().order_by('name'),
    })
```

---

### PAGE 3: job-post.html → jobs/detail.html

**All static text:** Keep headings, labels, "Apply Now" button text.

**Dynamic content — wire to the job object:**
```html
<!-- Page title / SEO -->
{% block title %}{{ job.title }} at {{ job.company.name }}{% endblock %}
{% block meta_description %}{{ job.description|truncatewords:25|striptags }}{% endblock %}

<!-- Job header -->
<h1>{{ job.title }}</h1>
<div class="department-badge"><div>{{ job.category.name }}</div></div>

<!-- Job meta pills -->
<div class="job-info-text">{% if job.is_remote %}Remote{% else %}{{ job.location }}{% endif %}</div>
<div class="job-info-text">{{ job.get_job_type_display }}</div>
{% if job.salary_min %}
<div class="job-info-text">${{ job.salary_min|intcomma }}{% if job.salary_max %} – ${{ job.salary_max|intcomma }}{% endif %} / {{ job.get_salary_period_display }}</div>
{% endif %}
<div class="job-info-text">Posted {{ job.posted_at|timesince }} ago</div>

<!-- Company sidebar -->
{% if job.company.logo %}
  <img src="{{ job.company.logo.url }}" alt="{{ job.company.name }}">
{% else %}
  <div class="skeleton skeleton--logo"></div>
{% endif %}
<h3>{{ job.company.name }}</h3>
<p>{{ job.company.description|truncatewords:30 }}</p>
<a href="{{ job.company.website }}" target="_blank" rel="noopener">Visit Website</a>

<!-- Job description body (HTML field from admin) -->
<div class="job-description-body">
  {{ job.description|safe }}
</div>

<!-- Requirements -->
<div class="job-requirements-body">
  {{ job.requirements|safe }}
</div>

<!-- Apply button -->
<a href="{{ job.apply_url }}" target="_blank" rel="noopener" class="button w-button"
   onclick="gtag('event','apply_click',{'job_id':'{{ job.id }}','job_title':'{{ job.title }}'})">
  Apply Now
</a>

<!-- Related jobs -->
<div role="list" class="w-dyn-items">
  {% if related_jobs %}
    {% for related in related_jobs %}
    <div role="listitem" class="w-dyn-item">
      <a href="{% url 'jobs:detail' slug=related.slug %}" class="job-offer-wrapper w-inline-block">
        <h4>{{ related.title }}</h4>
        <p>{{ related.company.name }} · {{ related.location }}</p>
      </a>
    </div>
    {% endfor %}
  {% else %}
    {% for i in "123" %}
    <div role="listitem" class="w-dyn-item">
      <div class="job-offer-wrapper">
        <div class="skeleton skeleton--text skeleton--text-lg"></div>
        <div class="skeleton skeleton--text skeleton--text-sm" style="margin-top:8px"></div>
      </div>
    </div>
    {% endfor %}
  {% endif %}
</div>
```

**CRITICAL — JobPosting Schema (add inside {% block structured_data %}):**
```html
{% block structured_data %}
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "JobPosting",
  "title": "{{ job.title|escapejs }}",
  "description": "{{ job.description|striptags|escapejs }}",
  "datePosted": "{{ job.posted_at|date:'c' }}",
  "validThrough": "{{ job.expires_at|date:'c' }}",
  "employmentType": "{{ job.get_job_type_schema }}",
  "hiringOrganization": {
    "@type": "Organization",
    "name": "{{ job.company.name|escapejs }}",
    "sameAs": "{{ job.company.website }}",
    "logo": "{% if job.company.logo %}{{ job.company.logo.url }}{% endif %}"
  },
  "jobLocation": {
    "@type": "Place",
    "address": {
      "@type": "PostalAddress",
      "addressLocality": "{{ job.location|escapejs }}",
      "addressCountry": "US"
    }
  }{% if job.is_remote %},
  "jobLocationType": "TELECOMMUTE"{% endif %}{% if job.salary_min %},
  "baseSalary": {
    "@type": "MonetaryAmount",
    "currency": "{{ job.salary_currency }}",
    "value": {
      "@type": "QuantitativeValue",
      "minValue": {{ job.salary_min }},
      "maxValue": {{ job.salary_max|default:job.salary_min }},
      "unitText": "{{ job.get_salary_period_schema }}"
    }
  }{% endif %}
}
</script>
{% endblock %}
```

**job detail view:**
```python
def job_detail(request, slug):
    job = get_object_or_404(Job, slug=slug, is_active=True)
    Job.objects.filter(pk=job.pk).update(views_count=F('views_count') + 1)
    related = Job.objects.filter(
        category=job.category, is_active=True
    ).exclude(pk=job.pk).select_related('company')[:3]
    return render(request, 'jobs/detail.html', {
        'job': job, 'company': job.company, 'related_jobs': related,
    })
```

---

### PAGE 4: blog.html → blog/list.html

**Dynamic section — the 4 w-dyn-item blog cards:**
```html
<div role="list" class="blog-listing-collection w-dyn-items">
  {% if page_obj.object_list %}
    {% for post in page_obj %}
    <div role="listitem" class="w-dyn-item">
      <a href="{% url 'blog:detail' slug=post.slug %}" class="blog-listing-wrapper w-inline-block">
        <div class="position-relative">
          {% if post.featured_image %}
            <img src="{{ post.featured_image.url }}" loading="lazy" alt="{{ post.title }}" class="blog-thumbnail">
          {% else %}
            <div class="skeleton skeleton--blog-img"></div>
          {% endif %}
          <div class="position-absolute item-19">
            <div>{{ post.category.name }}</div>
          </div>
        </div>
        <div class="margin-top margin-xsmall">
          <h3 class="heading-blog-title">{{ post.title }}</h3>
          <p>{{ post.excerpt }}</p>
          <div class="text-link red">Read more</div>
        </div>
      </a>
    </div>
    {% endfor %}
  {% else %}
    {% for i in "123456" %}
    <div role="listitem" class="w-dyn-item">
      <div class="blog-listing-wrapper">
        <div class="skeleton skeleton--blog-img"></div>
        <div class="margin-top margin-xsmall">
          <div class="skeleton skeleton--badge" style="margin-bottom:10px"></div>
          <div class="skeleton skeleton--text skeleton--text-lg" style="margin-bottom:8px"></div>
          <div class="skeleton skeleton--text skeleton--text-md"></div>
        </div>
      </div>
    </div>
    {% endfor %}
  {% endif %}
</div>

<!-- Category filter tabs (wire to GET param) -->
<div class="blog-categories-tabs">
  <a href="{% url 'blog:list' %}" 
     class="blog-category-tab {% if not request.GET.category %}active{% endif %}">All</a>
  {% for cat in blog_categories %}
  <a href="?category={{ cat.slug }}" 
     class="blog-category-tab {% if request.GET.category == cat.slug %}active{% endif %}">
    {{ cat.name }} ({{ cat.post_count }})
  </a>
  {% endfor %}
</div>
```

**blog list view:**
```python
def blog_list(request):
    posts = Post.objects.filter(status='published').select_related('author', 'category')
    cat_slug = request.GET.get('category', '')
    if cat_slug:
        posts = posts.filter(category__slug=cat_slug)
    posts = posts.order_by('-published_at')
    paginator = Paginator(posts, 9)
    page_obj  = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog/list.html', {
        'page_obj': page_obj,
        'blog_categories': BlogCategory.objects.annotate(post_count=Count('post')),
        'active_category': cat_slug,
    })
```

---

### PAGE 5: blog-post.html → blog/detail.html

```html
{% block title %}{{ post.title }}{% endblock %}
{% block meta_description %}{{ post.excerpt }}{% endblock %}
{% block og_image %}{{ post.featured_image.url }}{% endblock %}

<!-- Article hero image -->
{% if post.featured_image %}
  <img src="{{ post.featured_image.url }}" loading="lazy" alt="{{ post.title }}" class="blog-hero-image">
{% else %}
  <div class="skeleton skeleton--blog-img-hero"></div>
{% endif %}

<!-- Category badge -->
<div class="position-absolute item-19">{{ post.category.name }}</div>

<!-- Article header -->
<h1 class="heading-blog-title">{{ post.title }}</h1>
<div class="blog-meta">
  <span>By {{ post.author.get_full_name }}</span>
  <span>·</span>
  <span>{{ post.published_at|date:"F j, Y" }}</span>
  <span>·</span>
  <span>{{ post.read_time }} min read</span>
</div>

<!-- Article body -->
<div class="blog-post-body rich-text">
  {{ post.content|safe }}
</div>

<!-- Related posts (3 w-dyn-item blocks) -->
{% if related_posts %}
  {% for related in related_posts %}
  <div role="listitem" class="w-dyn-item">
    <a href="{% url 'blog:detail' slug=related.slug %}" class="blog-listing-wrapper w-inline-block">
      {% if related.featured_image %}
        <img src="{{ related.featured_image.url }}" loading="lazy" alt="{{ related.title }}" class="blog-thumbnail">
      {% else %}
        <div class="skeleton skeleton--blog-img"></div>
      {% endif %}
      <div class="margin-top margin-xsmall">
        <h3 class="heading-blog-title">{{ related.title }}</h3>
        <div class="text-link red">Read more</div>
      </div>
    </a>
  </div>
  {% endfor %}
{% else %}
  {% for i in "123" %}
  <div role="listitem" class="w-dyn-item">
    <div class="blog-listing-wrapper">
      <div class="skeleton skeleton--blog-img"></div>
      <div class="margin-top margin-xsmall">
        <div class="skeleton skeleton--text skeleton--text-lg"></div>
      </div>
    </div>
  </div>
  {% endfor %}
{% endif %}
```

**Article schema:**
```html
{% block structured_data %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "{{ post.title|escapejs }}",
  "description": "{{ post.excerpt|escapejs }}",
  "image": "{% if post.featured_image %}{{ post.featured_image.url }}{% endif %}",
  "author": {"@type": "Person", "name": "{{ post.author.get_full_name|escapejs }}"},
  "publisher": {"@type": "Organization", "name": "{{ site_name }}"},
  "datePublished": "{{ post.published_at|date:'c' }}",
  "dateModified": "{{ post.updated_at|date:'c' }}",
  "mainEntityOfPage": {"@type": "WebPage", "@id": "{{ request.build_absolute_uri }}"}
}
</script>
{% endblock %}
```

**blog detail view:**
```python
def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    Post.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
    related = Post.objects.filter(
        category=post.category, status='published'
    ).exclude(pk=post.pk).order_by('-published_at')[:3]
    return render(request, 'blog/detail.html', {
        'post': post, 'related_posts': related,
    })
```

---

### PAGE 6: conpanies.html → jobs/companies.html

```html
<!-- 4 w-dyn-item company cards → loop -->
<div role="list" class="companies-collection w-dyn-items">
  {% if companies %}
    {% for company in companies %}
    <div role="listitem" class="w-dyn-item">
      <a href="{% url 'jobs:company_detail' slug=company.slug %}" class="company-card-wrapper w-inline-block">
        {% if company.logo %}
          <img src="{{ company.logo.url }}" loading="lazy" alt="{{ company.name }}" class="company-logo">
        {% else %}
          <div class="skeleton skeleton--logo"></div>
        {% endif %}
        <h3>{{ company.name }}</h3>
        <p>{{ company.industry }}</p>
        <div class="job-info-text">{{ company.active_jobs_count }} open position{{ company.active_jobs_count|pluralize }}</div>
      </a>
    </div>
    {% endfor %}
  {% else %}
    {% for i in "12345678" %}
    <div role="listitem" class="w-dyn-item">
      <div class="company-card-wrapper">
        <div class="skeleton skeleton--logo" style="margin:0 auto 12px"></div>
        <div class="skeleton skeleton--text skeleton--text-md" style="margin-bottom:8px"></div>
        <div class="skeleton skeleton--text skeleton--text-sm"></div>
      </div>
    </div>
    {% endfor %}
  {% endif %}
</div>
```

---

### PAGE 7: company-single.html → jobs/company_detail.html

```html
{% if company.logo %}
  <img src="{{ company.logo.url }}" alt="{{ company.name }}">
{% else %}
  <div class="skeleton skeleton--logo"></div>
{% endif %}
<h1>{{ company.name }}</h1>
<p>{{ company.industry }}</p>
<a href="{{ company.website }}" target="_blank" rel="noopener">Visit Website →</a>

<!-- Company description -->
<div class="company-description">{{ company.description|safe }}</div>

<!-- Jobs from this company (3 w-dyn-item blocks → loop) -->
{% if company_jobs %}
  {% for job in company_jobs %}
  <!-- same job-offer-wrapper structure -->
  {% endfor %}
{% else %}
  <p>No active positions at this company right now.</p>
{% endif %}
```

---

### PAGE 8: about.html → pages/about.html

This page is mostly static layout — no database-driven collections.

**What to replace:**
- All 16 Lorem ipsum paragraphs → real about page copy from MASTER_PROJECT.md Section 10
- All 43 CDN images → self-hosted static files
- Testimonial photos → either leave skeleton placeholders or remove the testimonial section
- Team member photos → skeleton placeholders (until real photos are uploaded)
- Stats numbers (100%, 20M, +50) → `{{ stats.active_jobs_count }}` etc. from context

**about view:**
```python
def about(request):
    return render(request, 'pages/about.html', {
        'stats': {
            'active_jobs_count': Job.objects.filter(is_active=True).count(),
            'companies_count': Company.objects.filter(is_active=True).count(),
        }
    })
```

---

### PAGE 9: contact-us.html → pages/contact.html

The contact form HTML structure is already there. Wire it up:

```html
<form method="POST" action="{% url 'core:contact' %}" class="contact-form w-form">
  {% csrf_token %}
  <input type="text" name="name" placeholder="Full Name" required
         value="{{ form.name.value|default:'' }}" class="input-field w-input">
  <input type="email" name="email" placeholder="Email Address" required
         value="{{ form.email.value|default:'' }}" class="input-field w-input">
  <input type="text" name="subject" placeholder="Subject"
         value="{{ form.subject.value|default:'' }}" class="input-field w-input">
  <textarea name="message" placeholder="Your message..." required
            class="input-field text-area w-input">{{ form.message.value|default:'' }}</textarea>
  <button type="submit" class="button w-button">Send Message</button>
</form>

{% if messages %}
  {% for message in messages %}
    <div class="w-form-done {% if message.tags == 'error' %}w-form-fail{% endif %}">
      <p>{{ message }}</p>
    </div>
  {% endfor %}
{% endif %}
```

---

### PAGE 10: post-job.html → jobs/post_job.html

```html
<form method="POST" action="{% url 'jobs:post_job' %}" 
      enctype="multipart/form-data" class="post-job-form w-form">
  {% csrf_token %}
  {{ job_form.as_p }}
  {# OR manually render each field matching the Webflow HTML input structure #}
  <button type="submit" class="button w-button">Submit Job Posting</button>
</form>
```

---

### PAGE 11: submit-resume.html → accounts/submit_resume.html

```html
<form method="POST" action="{% url 'accounts:submit_resume' %}"
      enctype="multipart/form-data" class="resume-form w-form">
  {% csrf_token %}
  <input type="text"  name="full_name" placeholder="Full Name" class="input-field w-input">
  <input type="email" name="email"     placeholder="Email Address" class="input-field w-input">
  <input type="text"  name="position"  placeholder="Position applying for" class="input-field w-input">
  <input type="file"  name="resume"    accept=".pdf,.doc,.docx" class="input-field w-input">
  <textarea name="message" placeholder="Cover note..." class="input-field text-area w-input"></textarea>
  <button type="submit" class="button w-button">Submit Resume</button>
</form>
```

---

## THE SKELETON CSS TO ADD

Add this to `static/css/skeletons.css` (this is the same as TEMPLATE_MIGRATION_GUIDE.md 
plus the additional sizes needed by this template):

```css
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
  border-radius: 6px;
  display: block;
}
@keyframes skeleton-shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
.skeleton--logo        { width: 48px;  height: 48px;  border-radius: 10px; }
.skeleton--logo-xsmall { width: 24px;  height: 24px;  border-radius: 4px; }
.skeleton--badge       { width: 80px;  height: 24px;  border-radius: 100px; }
.skeleton--text        { height: 14px; border-radius: 4px; margin-bottom: 6px; }
.skeleton--text-sm     { width: 40%; }
.skeleton--text-md     { width: 70%; }
.skeleton--text-lg     { width: 90%; height: 20px; }
.skeleton--text-xl     { width: 60%; height: 26px; }
.skeleton--blog-img         { width: 100%; aspect-ratio: 16/9; border-radius: 0; }
.skeleton--blog-img-hero    { width: 100%; height: 400px; }
@media (prefers-reduced-motion: reduce) {
  .skeleton { animation: none; background: #efefef; }
}
[data-theme="dark"] .skeleton {
  background: linear-gradient(90deg, #2a2a2a 25%, #333 50%, #2a2a2a 75%);
  background-size: 200% 100%;
}
```

---

## THE CONTEXT PROCESSOR

Add this to `apps/core/context_processors.py` and register in settings:

```python
def site_context(request):
    return {
        'site_name':    settings.SITE_NAME,
        'site_tagline': settings.SITE_TAGLINE,
        'ADSENSE_PUBLISHER_ID': getattr(settings, 'ADSENSE_PUBLISHER_ID', ''),
        'GA_MEASUREMENT_ID':    getattr(settings, 'GA_MEASUREMENT_ID', ''),
    }
```

---

## VERIFICATION — RUN AFTER EVERY PAGE

After converting each template, run these checks.
ALL must return 0. If any return > 0, the page is NOT done.

```bash
# Replace [page].html with the actual template filename
grep -c "cdn.prod.website-files.com"       templates/[path]/[page].html  # must be 0
grep -c "assets-global.website-files.com"  templates/[path]/[page].html  # must be 0
grep -c "Better Talent"                    templates/[path]/[page].html  # must be 0
grep -c "Lorem ipsum"                      templates/[path]/[page].html  # must be 0
grep -c "data-wf-"                         templates/[path]/[page].html  # must be 0
grep -c "data-w-id"                        templates/[path]/[page].html  # must be 0
grep -c "style=\"opacity:0\""              templates/[path]/[page].html  # must be 0
grep -c "webflow.io"                       templates/[path]/[page].html  # must be 0
grep -c "We-R.be"                          templates/[path]/[page].html  # must be 0
grep -c "Amazon\|Apple Inc\|Google LLC"    templates/[path]/[page].html  # must be 0
```

**Run on all pages at once:**
```bash
for f in $(find templates/ -name "*.html"); do
  echo "=== $f ===" 
  grep -c "cdn.prod.website-files.com\|Better Talent\|Lorem ipsum\|data-w-id\|webflow.io" $f
done
```

---

## ORDER OF EXECUTION

Work through pages in this order:
1. ✅ base.html (navbar + footer — shared by all pages)
2. ✅ home.html
3. ✅ jobs/list.html  
4. ✅ jobs/detail.html  ← include JobPosting schema
5. ✅ blog/list.html
6. ✅ blog/detail.html ← include BlogPosting schema
7. ✅ pages/about.html
8. ✅ pages/contact.html
9. ✅ jobs/companies.html
10. ✅ jobs/company_detail.html
11. ✅ jobs/post_job.html
12. ✅ accounts/submit_resume.html
13. ✅ 404.html
14. ✅ Confirmation pages (3)
15. ✅ coming_soon.html

After EACH page: run verification grep commands. Report 0s. Then move on.

**After ALL pages complete:**
- Run the full template scan from MASTER_PROJECT.md Section 7 Phase 4
- Submit sitemap to Google Search Console
- Confirm AdSense checklist from MASTER_PROJECT.md Section 11

---

*Template Integration Brief v1.0 | Companion to MASTER_PROJECT.md + TEMPLATE_MIGRATION_GUIDE.md*
