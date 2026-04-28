# 🔄 WEBFLOW TEMPLATE MIGRATION GUIDE
### For AI IDE | Read alongside MASTER_PROJECT.md

> The client has provided a Webflow HTML template ("Better Talent") as the visual 
> design reference. We are NOT using Webflow. We are extracting the design and 
> rebuilding it inside Django templates — clean, data-driven, and ours.

---

## THE CORE PHILOSOPHY

Think of the Webflow HTML as a **design blueprint** — like an architect's sketch.
You use it to understand layout, spacing, component shapes, and visual style.
You do NOT copy its content, its scripts, its CDN links, or its branding.

**What we keep:** CSS class names, layout structure, component shapes
**What we strip:** Every single piece of content, every CDN image, every Webflow script, all hardcoded text, all fake data, all Webflow JS, all Webflow meta tags

---

## STEP 1: ASSET EXTRACTION

Before touching any HTML, do this first:

### Download and Self-Host the Webflow CSS
The template CSS lives at:
```
https://assets-global.website-files.com/66277126b8030d4bdcebdaf0/css/template-job-portal-recruitment.webflow.bc4ac94d8.css
```

1. Download this CSS file
2. Save it to `static/css/webflow-base.css` in the Django project
3. Audit it — remove any Webflow branding comments
4. We will override it with our own variables on top

### Download the Webflow JS
```
https://assets-global.website-files.com/66277126b8030d4bdcebdaf0/js/webflow.94da99589.js
```
Save to `static/js/webflow-interactions.js` — this powers the animations and dropdowns. Keep it for now, we'll replace it with Alpine.js in Phase 3.

### Font
The template uses **Figtree** from Google Fonts. Keep this font — it pairs well with our design system. Update the font reference in our base.html to load it directly.

---

## STEP 2: THE STRIPPING RULES

Apply these rules to EVERY HTML file the client provides.

### 🔴 REMOVE COMPLETELY (delete these elements entirely)

```html
<!-- Remove all Webflow meta attributes from <html> tag -->
data-wf-domain="..."
data-wf-page="..."
data-wf-site="..."

<!-- Remove Webflow generator meta -->
<meta content="Webflow" name="generator" />

<!-- Remove Webflow CDN preconnect -->
<link href="https://assets-global.website-files.com" rel="preconnect" .../>

<!-- Remove Webflow CSS link (we self-host it) -->
<link href="https://assets-global.website-files.com/...css..." rel="stylesheet" />

<!-- Remove WebFont.load script block -->
<script>WebFont.load({...})</script>

<!-- Remove Webflow currency settings script -->
<script>window.__WEBFLOW_CURRENCY_SETTINGS = {...}</script>

<!-- Remove Webflow touch detection script -->
<script>!function(o,c){...}(window, document)</script>

<!-- Remove jQuery from Webflow CDN -->
<script src="https://d3e54v103j8qbb.cloudfront.net/js/jquery-3.5.1..."></script>

<!-- Remove Webflow JS -->
<script src="https://assets-global.website-files.com/.../webflow.*.js"></script>

<!-- Remove all favicon links pointing to Webflow CDN -->
<link href="https://cdn.prod.website-files.com/...favicon..." rel="shortcut icon" />
<link href="https://cdn.prod.website-files.com/...webclipp..." rel="apple-touch-icon" />

<!-- Remove Webflow data-w-id attributes from all elements -->
data-w-id="257d7de2-..."  ← delete from any element that has it
```

### 🟡 REPLACE (change the value, keep the element)

```html
<!-- Replace <title> -->
BEFORE: <title>Better Talent | Webflow Ecommerce Website Template</title>
AFTER:  <title>{% block title %}Find Entry-Level Jobs{% endblock %} | {{ site.name }}</title>

<!-- Replace meta description -->
BEFORE: <meta content="Better Talent Job Portal..." name="description" />
AFTER:  <meta content="{% block meta_description %}...{% endblock %}" name="description" />

<!-- Replace OG tags -->
BEFORE: <meta content="Better Talent | ..." property="og:title" />
AFTER:  <meta content="{% block og_title %}{% block title %}{% endblock %}{% endblock %}" property="og:title" />

<!-- Replace ALL img src pointing to Webflow CDN -->
BEFORE: <img src="https://cdn.prod.website-files.com/..." alt="Better Talent..." />
AFTER:  See Section 3 — Image Replacement Rules

<!-- Replace logo -->
BEFORE: <img src="https://cdn.prod.website-files.com/...Logo.svg" alt="Better Talent..." class="navbar-logo" />
AFTER:  <img src="{% static 'images/logo.svg' %}" alt="{{ site.name }}" class="navbar-logo" />

<!-- Replace copyright footer -->
BEFORE: Copyright © Better Talent | Design by <a href="...">We-R.</a> | Powered by <a href="...">Webflow</a>
AFTER:  Copyright © {% now "Y" %} {{ site.name }}. All rights reserved.

<!-- Replace all href links -->
BEFORE: href="/job-offers/machine-learning-engineer"
AFTER:  href="{% url 'jobs:detail' slug=job.slug %}"  (or appropriate Django URL)
```

### 🟢 KEEP (these are fine as-is)
- All CSS class names (e.g., `class="hero-section"`, `class="navbar-container"`)
- Layout structure (divs, sections, their nesting)
- `data-animation`, `data-collapse`, `data-duration` attributes on nav (needed for Webflow JS)
- `role="navigation"`, `role="banner"`, `role="list"` (accessibility)
- The general component structure

---

## STEP 3: IMAGE REPLACEMENT RULES

Every `<img>` in the template falls into one of these categories:

### Category A — Static Brand Assets (logo, icons, decorative)
Replace with Django static files:
```html
<img src="{% static 'images/logo.svg' %}" alt="{{ site.name }}" />
<img src="{% static 'images/hero-decoration.svg' %}" alt="" role="presentation" />
```
For decorative images that are purely visual (squiggles, backgrounds), use:
```html
<img src="{% static 'images/[descriptive-name].svg' %}" alt="" role="presentation" aria-hidden="true" />
```

### Category B — Dynamic Data Images (company logos, blog post images, avatars)
Replace with Django template variables + skeleton loader fallback:
```html
<!-- Company logo on job card -->
{% if company.logo %}
  <img src="{{ company.logo.url }}" alt="{{ company.name }} logo" loading="lazy" />
{% else %}
  <!-- Skeleton loader -->
  <div class="skeleton-img skeleton-img--company-logo" aria-hidden="true"></div>
{% endif %}

<!-- Blog post featured image -->
{% if post.featured_image %}
  <img src="{{ post.featured_image.url }}" alt="{{ post.title }}" loading="lazy" />
{% else %}
  <div class="skeleton-img skeleton-img--blog" aria-hidden="true"></div>
{% endif %}
```

### Category C — Hero / Section Background Images
Replace with CSS background via Django static or a custom context variable:
```html
<!-- If it was an <img> used as background, convert to CSS -->
<section class="hero-section" style="background-image: url('{% static 'images/hero-bg.jpg' %}')">
```
Or better, add a hero image CSS variable in base.html so it's easy to swap per page.

### Category D — Fake "Client/Partner" Logos (Stripe, Apple, Airbnb etc.)
**DELETE THESE ENTIRELY.** The previous developer's mistake was listing logos of companies that never hired through the site. Do not replicate this. Replace the entire "trusted by" / "companies we work with" section with either:
- Real company logos (if any exist — if none, skip the section)
- A stat counter section showing real platform numbers
- A "Featured In" section using journalism/blog logos if applicable

---

## STEP 4: HARDCODED TEXT REPLACEMENT

Every piece of visible text on the page must be replaced. Here is the mapping:

### Navigation
```html
<!-- BEFORE -->
<a href="/" class="navbar-brand">
  <img src="...BetterTalent...Logo.svg" alt="Better Talent..." />
</a>

<!-- AFTER -->
<a href="{% url 'core:home' %}" class="navbar-brand">
  <img src="{% static 'images/logo.svg' %}" alt="{{ site.name }}" class="navbar-logo" />
</a>
```

Nav links — update hrefs to Django URL names:
```html
href="/about-us"    →  href="{% url 'core:about' %}"
href="/jobs"        →  href="{% url 'jobs:list' %}"
href="/companies"   →  href="{% url 'jobs:companies' %}"
href="/blog"        →  href="{% url 'blog:list' %}"
href="/contact"     →  href="{% url 'core:contact' %}"
href="/submit-resume" → href="{% url 'accounts:upload_resume' %}"
href="/post-a-job-offer" → href="{% url 'jobs:post_job' %}"
```

Remove "Template Pages", "Utility Pages", "Style Guide", "Licenses", "Changelog", "Coming Soon", "Confirmation" links from the dropdown entirely. These are Webflow template navigation items.

### Hero Section
```html
<!-- BEFORE: hardcoded heading -->
<h1>Find the right talent for your company</h1>
<p>Lorem ipsum dolor sit amet...</p>

<!-- AFTER: Django template with site-configurable content -->
<h1>{{ hero.heading|default:"Find Your First Career Opportunity" }}</h1>
<p>{{ hero.subtext|default:"Browse hundreds of verified entry-level jobs curated for recent graduates." }}</p>
```

For the hero search bar:
```html
<form action="{% url 'jobs:list' %}" method="GET" class="search-form">
  <input type="text" name="q" placeholder="Job title or keyword" 
         value="{{ request.GET.q }}" class="search-input" />
  <input type="text" name="location" placeholder="Location or Remote"
         value="{{ request.GET.location }}" class="search-input" />
  <button type="submit" class="btn-primary">Search Jobs</button>
</form>
```

### Hardcoded Job Cards → Dynamic Loop
```html
<!-- BEFORE: hardcoded fake job -->
<div class="job-card">
  <img src="https://cdn.prod.website-files.com/.../apple-logo.png" />
  <h3>Machine Learning Engineer</h3>
  <p>Apple Inc.</p>
  <span>Full-time</span>
  <span>$120,000 - $140,000</span>
</div>

<!-- AFTER: Django loop with skeleton fallback -->
{% if featured_jobs %}
  {% for job in featured_jobs %}
    <div class="job-card">
      {% if job.company.logo %}
        <img src="{{ job.company.logo.url }}" alt="{{ job.company.name }}" loading="lazy" />
      {% else %}
        <div class="skeleton skeleton--logo" aria-hidden="true"></div>
      {% endif %}
      <h3><a href="{{ job.get_absolute_url }}">{{ job.title }}</a></h3>
      <p>{{ job.company.name }}</p>
      <span class="badge badge--job-type">{{ job.get_job_type_display }}</span>
      {% if job.salary_min %}
        <span class="badge badge--salary">
          ${{ job.salary_min|intcomma }}{% if job.salary_max %} – ${{ job.salary_max|intcomma }}{% endif %}
        </span>
      {% endif %}
      <span class="badge badge--location">
        {% if job.is_remote %}Remote{% else %}{{ job.location }}{% endif %}
      </span>
      <div class="job-card-footer">
        <span class="posted-date">{{ job.posted_at|timesince }} ago</span>
        <a href="{{ job.get_absolute_url }}" class="btn-apply">Apply Now →</a>
      </div>
    </div>
  {% endfor %}
{% else %}
  <!-- Skeleton cards while loading or if empty -->
  {% for i in "123456" %}
    <div class="job-card job-card--skeleton">
      <div class="skeleton skeleton--logo" aria-hidden="true"></div>
      <div class="skeleton skeleton--text skeleton--text-sm" aria-hidden="true"></div>
      <div class="skeleton skeleton--text skeleton--text-lg" aria-hidden="true"></div>
      <div class="skeleton skeleton--text skeleton--text-sm" aria-hidden="true"></div>
      <div class="skeleton-row">
        <div class="skeleton skeleton--badge" aria-hidden="true"></div>
        <div class="skeleton skeleton--badge" aria-hidden="true"></div>
      </div>
    </div>
  {% endfor %}
{% endif %}
```

### Hardcoded Blog Posts → Dynamic Loop
```html
{% if recent_posts %}
  {% for post in recent_posts %}
    <div class="blog-card">
      {% if post.featured_image %}
        <img src="{{ post.featured_image.url }}" alt="{{ post.title }}" loading="lazy" />
      {% else %}
        <div class="skeleton skeleton--blog-img" aria-hidden="true"></div>
      {% endif %}
      <span class="badge badge--category">{{ post.category.name }}</span>
      <h3><a href="{{ post.get_absolute_url }}">{{ post.title }}</a></h3>
      <p>{{ post.excerpt }}</p>
      <div class="blog-card-meta">
        <span>{{ post.author.get_full_name }}</span>
        <span>·</span>
        <span>{{ post.read_time }} min read</span>
        <span>·</span>
        <span>{{ post.published_at|date:"M j, Y" }}</span>
      </div>
    </div>
  {% endfor %}
{% else %}
  {% for i in "123" %}
    <div class="blog-card blog-card--skeleton">
      <div class="skeleton skeleton--blog-img" aria-hidden="true"></div>
      <div class="skeleton skeleton--text skeleton--text-sm" aria-hidden="true"></div>
      <div class="skeleton skeleton--text skeleton--text-lg" aria-hidden="true"></div>
      <div class="skeleton skeleton--text skeleton--text-md" aria-hidden="true"></div>
    </div>
  {% endfor %}
{% endif %}
```

### Stats Section
```html
<!-- BEFORE: fake hardcoded numbers -->
<div class="stat">
  <h2>200+</h2>
  <p>Job Offers</p>
</div>

<!-- AFTER: real database counts -->
<div class="stat">
  <h2>{{ stats.active_jobs_count }}+</h2>
  <p>Active Job Listings</p>
</div>
<div class="stat">
  <h2>{{ stats.companies_count }}+</h2>
  <p>Hiring Companies</p>
</div>
<div class="stat">
  <h2>{{ stats.users_count }}+</h2>
  <p>Registered Job Seekers</p>
</div>

<!-- The Django view context provides these: -->
<!-- stats = { -->
<!--   'active_jobs_count': Job.objects.filter(is_active=True).count(), -->
<!--   'companies_count': Company.objects.filter(is_active=True).count(), -->
<!--   'users_count': User.objects.filter(is_active=True).count(), -->
<!-- } -->
```

### Category Cards
```html
{% if job_categories %}
  {% for category in job_categories %}
    <a href="{% url 'jobs:list' %}?category={{ category.slug }}" class="category-card">
      <div class="category-icon">
        <!-- Use Lucide icon based on category.icon field -->
        <img src="{% static 'icons/'|add:category.icon|add:'.svg' %}" 
             alt="{{ category.name }}" aria-hidden="true" />
      </div>
      <h3>{{ category.name }}</h3>
      <span>{{ category.job_count }} open positions</span>
    </a>
  {% endfor %}
{% else %}
  {% for i in "12345678" %}
    <div class="category-card category-card--skeleton">
      <div class="skeleton skeleton--icon" aria-hidden="true"></div>
      <div class="skeleton skeleton--text skeleton--text-sm" aria-hidden="true"></div>
    </div>
  {% endfor %}
{% endif %}
```

---

## STEP 5: SKELETON LOADER CSS

Add this to your main CSS file (or a dedicated `skeletons.css`). 
This must be self-contained — no JavaScript required for the skeleton effect.

```css
/* =============================================
   SKELETON LOADERS
   ============================================= */

.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
  border-radius: 6px;
}

@keyframes skeleton-shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Skeleton size variants */
.skeleton--logo {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  flex-shrink: 0;
}

.skeleton--icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
}

.skeleton--text {
  height: 14px;
  border-radius: 4px;
}

.skeleton--text-sm  { width: 40%; height: 12px; }
.skeleton--text-md  { width: 70%; height: 14px; }
.skeleton--text-lg  { width: 90%; height: 20px; }
.skeleton--text-xl  { width: 60%; height: 28px; }

.skeleton--badge {
  width: 80px;
  height: 24px;
  border-radius: 100px;
}

.skeleton--blog-img {
  width: 100%;
  aspect-ratio: 16/9;
  border-radius: 12px 12px 0 0;
}

.skeleton--avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

/* Job card skeleton layout */
.job-card--skeleton {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 24px;
}

.job-card--skeleton .skeleton-row {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

/* Blog card skeleton layout */
.blog-card--skeleton {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.blog-card--skeleton .skeleton--text-sm { margin-top: 12px; }

/* Dark mode skeleton */
[data-theme="dark"] .skeleton {
  background: linear-gradient(
    90deg,
    #2a2a2a 25%,
    #333333 50%,
    #2a2a2a 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
}

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  .skeleton {
    animation: none;
    background: #f0f0f0;
  }
}
```

---

## STEP 6: BASE.HTML TEMPLATE

This is the clean Django base template built from the Webflow structure.
Replace the `<head>` entirely and keep only the structural HTML from Webflow's body.

```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
{% load static %}
{% load humanize %}

<head>
  <meta charset="utf-8" />
  <meta content="width=device-width, initial-scale=1" name="viewport" />

  {# ── SEO Block ─────────────────────────────────────────────── #}
  <title>{% block title %}Find Entry-Level Jobs{% endblock %} | {{ site_name }}</title>
  <meta name="description" content="{% block meta_description %}Browse verified entry-level jobs curated for recent graduates. Free to use.{% endblock %}" />
  <link rel="canonical" href="{{ request.build_absolute_uri }}" />

  {# Open Graph #}
  <meta property="og:title"       content="{% block og_title %}{% block title_og %}{% endblock %}{% endblock %}" />
  <meta property="og:description" content="{% block og_description %}{% block meta_description_og %}{% endblock %}{% endblock %}" />
  <meta property="og:image"       content="{% block og_image %}{% static 'images/og-default.jpg' %}{% endblock %}" />
  <meta property="og:url"         content="{{ request.build_absolute_uri }}" />
  <meta property="og:type"        content="{% block og_type %}website{% endblock %}" />
  <meta name="twitter:card"       content="summary_large_image" />

  {# Fonts — Figtree (from Webflow template) #}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet" />

  {# Stylesheets #}
  <link rel="stylesheet" href="{% static 'css/webflow-base.css' %}" />
  <link rel="stylesheet" href="{% static 'css/main.css' %}" />
  <link rel="stylesheet" href="{% static 'css/skeletons.css' %}" />

  {# Favicon — our own #}
  <link rel="shortcut icon" href="{% static 'images/favicon.png' %}" type="image/png" />
  <link rel="apple-touch-icon"  href="{% static 'images/apple-touch-icon.png' %}" />

  {# Google Analytics 4 #}
  {% if GA_MEASUREMENT_ID %}
  <script async src="https://www.googletagmanager.com/gtag/js?id={{ GA_MEASUREMENT_ID }}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '{{ GA_MEASUREMENT_ID }}');
  </script>
  {% endif %}

  {# AdSense — uncomment ONLY after approval #}
  {# <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={{ ADSENSE_PUBLISHER_ID }}" crossorigin="anonymous"></script> #}

  {# Page-specific head content #}
  {% block extra_head %}{% endblock %}

  {# Structured data — page-specific JSON-LD #}
  {% block structured_data %}{% endblock %}
</head>

<body>

  {# ── Navigation (from Webflow structure, cleaned) ──────────── #}
  <section class="hero-section">
    <div class="background-image-hero">
      <div class="navbar">
        <div data-animation="default" data-collapse="medium" data-duration="400"
             data-easing="ease" data-easing2="ease" role="banner"
             class="navbar-container w-nav">
          <div class="container-regular">
            <div class="navbar-wrapper">

              {# Logo #}
              <a href="{% url 'core:home' %}" class="navbar-brand w-nav-brand"
                 {% if request.resolver_match.url_name == 'home' %}aria-current="page"{% endif %}>
                <img src="{% static 'images/logo.svg' %}" alt="{{ site_name }}" class="navbar-logo" />
              </a>

              {# Nav Menu #}
              <nav role="navigation" class="nav-menu-wrapper w-nav-menu">
                <ul role="list" class="nav-menu w-list-unstyled">
                  <li>
                    <a href="{% url 'core:about' %}" class="nav-link
                      {% if request.resolver_match.url_name == 'about' %}active{% endif %}">
                      About
                    </a>
                  </li>
                  <li>
                    <a href="{% url 'jobs:list' %}" class="nav-link
                      {% if 'jobs' in request.resolver_match.namespace %}active{% endif %}">
                      Find Jobs
                    </a>
                  </li>
                  <li>
                    <a href="{% url 'jobs:companies' %}" class="nav-link">Companies</a>
                  </li>
                  <li>
                    <a href="{% url 'blog:list' %}" class="nav-link
                      {% if 'blog' in request.resolver_match.namespace %}active{% endif %}">
                      Career Blog
                    </a>
                  </li>
                  <li>
                    <a href="{% url 'core:services' %}" class="nav-link">Resources</a>
                  </li>
                  <li>
                    <a href="{% url 'jobs:post_job' %}" class="nav-link">Post a Job</a>
                  </li>
                </ul>
              </nav>

              {# Auth Buttons #}
              <div class="navbar-buttons">
                {% if user.is_authenticated %}
                  <a href="{% url 'accounts:dashboard' %}" class="btn-nav-secondary">
                    Dashboard
                  </a>
                  <a href="{% url 'accounts:logout' %}" class="btn-nav-ghost">
                    Log Out
                  </a>
                {% else %}
                  <a href="{% url 'accounts:login' %}" class="btn-nav-ghost">
                    Sign In
                  </a>
                  <a href="{% url 'accounts:register' %}" class="btn-primary">
                    Get Started
                  </a>
                {% endif %}
              </div>

              {# Mobile Hamburger #}
              <div class="menu-button w-nav-button" aria-label="Open menu" role="button" tabindex="0">
                <div class="w-icon-nav-menu"></div>
              </div>

            </div>
          </div>
        </div>
      </div>

      {# ── Page-specific hero content ───────────────────────── #}
      {% block hero %}{% endblock %}

    </div>
  </section>

  {# ── Main Content ───────────────────────────────────────────── #}
  <main id="main-content">
    {% block content %}{% endblock %}
  </main>

  {# ── Footer ─────────────────────────────────────────────────── #}
  <footer class="footer-section">
    <div class="container-regular">
      <div class="footer-grid">

        {# Brand column #}
        <div class="footer-brand-col">
          <a href="{% url 'core:home' %}">
            <img src="{% static 'images/logo.svg' %}" alt="{{ site_name }}" class="footer-logo" />
          </a>
          <p>{{ site_tagline }}</p>
          <div class="footer-social-links">
            {% if social.linkedin %}
              <a href="{{ social.linkedin }}" target="_blank" rel="noopener" aria-label="LinkedIn">
                <img src="{% static 'icons/linkedin.svg' %}" alt="LinkedIn" class="icon-1x1-medium" />
              </a>
            {% endif %}
            {% if social.twitter %}
              <a href="{{ social.twitter }}" target="_blank" rel="noopener" aria-label="Twitter/X">
                <img src="{% static 'icons/twitter.svg' %}" alt="Twitter" class="icon-1x1-medium" />
              </a>
            {% endif %}
          </div>
        </div>

        {# Jobs column #}
        <div class="footer-nav-col">
          <div class="footer-nav-heading">Browse Jobs</div>
          {% for category in footer_categories %}
            <a href="{% url 'jobs:list' %}?category={{ category.slug }}" class="text-link---footer">
              {{ category.name }}
            </a>
          {% endfor %}
        </div>

        {# Company column #}
        <div class="footer-nav-col">
          <div class="footer-nav-heading">Company</div>
          <a href="{% url 'core:about' %}"   class="text-link---footer">About Us</a>
          <a href="{% url 'blog:list' %}"    class="text-link---footer">Career Blog</a>
          <a href="{% url 'core:contact' %}" class="text-link---footer">Contact</a>
          <a href="{% url 'jobs:post_job' %}" class="text-link---footer">Post a Job</a>
        </div>

        {# Legal column #}
        <div class="footer-nav-col">
          <div class="footer-nav-heading">Legal</div>
          <a href="{% url 'core:privacy' %}" class="text-link---footer">Privacy Policy</a>
          <a href="{% url 'core:terms' %}"   class="text-link---footer">Terms of Service</a>
          <a href="{% url 'core:sitemap' %}" class="text-link---footer">Sitemap</a>
        </div>

      </div>

      <div class="divider-footer"></div>

      <div class="footer-bottom">
        <span>Copyright © {% now "Y" %} {{ site_name }}. All rights reserved.</span>
      </div>

    </div>
  </footer>

  {# ── Scripts ──────────────────────────────────────────────── #}
  {# jQuery (needed for Webflow interactions — replace with Alpine.js in Phase 3) #}
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
  <script src="{% static 'js/webflow-interactions.js' %}"></script>
  <script src="{% static 'js/main.js' %}"></script>

  {# HTMX for dynamic job search filtering #}
  <script src="https://unpkg.com/htmx.org@1.9.10"></script>

  {# Alpine.js for UI interactions #}
  <script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>

  {# Page-specific scripts #}
  {% block extra_scripts %}{% endblock %}

</body>
</html>
```

---

## STEP 7: PAGE-BY-PAGE DATA MAPPING

For every page in the Webflow template, here is what the Django view must provide:

### Homepage View Context
```python
def home(request):
    return render(request, 'pages/home.html', {
        'featured_jobs':   Job.objects.filter(is_active=True, is_featured=True).select_related('company')[:6],
        'recent_jobs':     Job.objects.filter(is_active=True).order_by('-posted_at').select_related('company')[:9],
        'job_categories':  JobCategory.objects.annotate(job_count=Count('job')).order_by('-job_count')[:8],
        'recent_posts':    Post.objects.filter(status='published').order_by('-published_at').select_related('author', 'category')[:3],
        'stats': {
            'active_jobs_count':  Job.objects.filter(is_active=True).count(),
            'companies_count':    Company.objects.filter(is_active=True).count(),
            'users_count':        User.objects.filter(is_active=True).count(),
        },
        'footer_categories': JobCategory.objects.all()[:6],
        'site_name':    settings.SITE_NAME,
        'site_tagline': settings.SITE_TAGLINE,
    })
```

### Jobs List View Context
```python
def job_list(request):
    jobs = Job.objects.filter(is_active=True).select_related('company', 'category')
    
    # Apply filters from GET params
    q         = request.GET.get('q', '')
    location  = request.GET.get('location', '')
    category  = request.GET.get('category', '')
    job_type  = request.GET.get('job_type', '')
    remote    = request.GET.get('remote', '')
    salary_min = request.GET.get('salary_min', '')
    
    if q:         jobs = jobs.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if location:  jobs = jobs.filter(location__icontains=location)
    if category:  jobs = jobs.filter(category__slug=category)
    if job_type:  jobs = jobs.filter(job_type=job_type)
    if remote:    jobs = jobs.filter(is_remote=True)
    if salary_min: jobs = jobs.filter(salary_min__gte=salary_min)
    
    paginator = Paginator(jobs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'jobs/list.html', {
        'page_obj':       page_obj,
        'job_categories': JobCategory.objects.all(),
        'total_count':    jobs.count(),
        'active_filters': {'q': q, 'location': location, 'category': category, ...},
        'meta_title':     f'Entry-Level Jobs{" in " + location if location else ""} | {settings.SITE_NAME}',
    })
```

### Job Detail View Context
```python
def job_detail(request, slug):
    job = get_object_or_404(Job, slug=slug, is_active=True)
    Job.objects.filter(pk=job.pk).update(views_count=F('views_count') + 1)
    
    return render(request, 'jobs/detail.html', {
        'job':          job,
        'company':      job.company,
        'related_jobs': Job.objects.filter(category=job.category, is_active=True).exclude(pk=job.pk)[:3],
        'is_saved':     request.user.is_authenticated and job in request.user.profile.saved_jobs.all(),
        # For JobPosting schema
        'schema_json':  job.get_structured_data_json(),
    })
```

### Blog List View Context
```python
def blog_list(request):
    posts = Post.objects.filter(status='published').select_related('author', 'category')
    category_slug = request.GET.get('category', '')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    paginator = Paginator(posts.order_by('-published_at'), 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'blog/list.html', {
        'page_obj':          page_obj,
        'blog_categories':   BlogCategory.objects.annotate(post_count=Count('post')),
        'active_category':   category_slug,
        'featured_post':     posts.first(),
    })
```

---

## STEP 8: THE WORKFLOW FOR EACH NEW HTML PAGE THE CLIENT SENDS

When the client provides another Webflow page HTML, follow this exact process:

```
1. READ the HTML file fully
2. IDENTIFY: What page is this? (jobs, blog, about, etc.)
3. STRIP: Apply all rules from Step 2 above
4. MAP: Identify every dynamic data point (hardcoded text, images, counts)
5. REPLACE: Apply Django template variables + skeleton loaders using the patterns above
6. ADD: SEO meta blocks, canonical URL, structured data if applicable
7. CONNECT: Wire up the matching Django view with correct context variables
8. TEST: Confirm no Webflow CDN URLs remain, no hardcoded content remains
9. VERIFY: Run `grep -n "cdn.prod.website-files.com" template.html` — must return 0 results
         Run `grep -n "Better Talent" template.html` — must return 0 results
         Run `grep -n "Lorem ipsum" template.html` — must return 0 results
```

### Verification Commands (run these on every finished template)
```bash
# Must all return 0 matches
grep -c "cdn.prod.website-files.com" templates/[page].html
grep -c "assets-global.website-files.com" templates/[page].html  
grep -c "Better Talent" templates/[page].html
grep -c "Lorem ipsum" templates/[page].html
grep -c "webflow" templates/[page].html
grep -c "w-nav" templates/[page].html  # Webflow nav classes — should be minimal/zero
```

---

## STEP 9: CONTEXT PROCESSOR (Global Variables)

Add this to `apps/core/context_processors.py` so every template has access to site-wide variables:

```python
from django.conf import settings
from apps.jobs.models import JobCategory

def site_context(request):
    return {
        'site_name':       settings.SITE_NAME,
        'site_tagline':    settings.SITE_TAGLINE,
        'site_url':        settings.SITE_URL,
        'GA_MEASUREMENT_ID':   getattr(settings, 'GA_MEASUREMENT_ID', ''),
        'ADSENSE_PUBLISHER_ID': getattr(settings, 'ADSENSE_PUBLISHER_ID', ''),
        'footer_categories': JobCategory.objects.all()[:6],
        'social': {
            'linkedin': getattr(settings, 'SOCIAL_LINKEDIN', ''),
            'twitter':  getattr(settings, 'SOCIAL_TWITTER', ''),
            'instagram': getattr(settings, 'SOCIAL_INSTAGRAM', ''),
        }
    }
```

Register in `settings/base.py`:
```python
TEMPLATES = [{
    ...
    'OPTIONS': {
        'context_processors': [
            ...
            'apps.core.context_processors.site_context',
        ],
    },
}]
```

Add to `settings/base.py`:
```python
SITE_NAME    = env('SITE_NAME', default='Career Builders Hub')
SITE_TAGLINE = env('SITE_TAGLINE', default='Entry-Level Jobs for Recent Graduates')
SITE_URL     = env('SITE_URL', default='https://yourdomain.com')
```

---

## SUMMARY CHECKLIST FOR IDE

Before marking any template as "done", confirm ALL of these:

- [ ] Zero Webflow CDN image URLs remain
- [ ] Zero hardcoded text content remains (no fake job titles, no lorem ipsum, no "Better Talent")
- [ ] Zero Webflow scripts remain (webflow.js is self-hosted copy, not CDN)
- [ ] Zero fake company logos remain
- [ ] All `<img>` tags for dynamic data use `{% if %}` + skeleton fallback
- [ ] All loops use `{% for %}` Django template tags
- [ ] All links use `{% url %}` Django URL tags
- [ ] `{% load static %}` is at the top of every template
- [ ] `{% load humanize %}` is included wherever `intcomma` filter is used
- [ ] SEO meta block is extended from base.html
- [ ] Page has unique title and meta description block
- [ ] All forms have `{% csrf_token %}`
- [ ] Skeleton loaders are shown when querysets return empty
- [ ] Verification grep commands return 0 matches

---

*Migration Guide v1.0 | Part of Career Builders Hub Project*
*Read alongside: MASTER_PROJECT.md*
