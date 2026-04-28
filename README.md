# Job Foundry Hub

**Entry-level jobs and career resources for recent graduates.**

A full-stack job board platform built with Django, featuring Google for Jobs integration, a career advice blog, company profiles, and a complete admin system — built to achieve Google AdSense approval.

🌐 **Live site:** [jobfoundryhub.com](https://jobfoundryhub.com)

---

## What It Does

Job Foundry Hub connects recent graduates and entry-level job seekers with verified opportunities. It combines a curated job board, a career advice blog, and a set of tools that make the job search process less overwhelming for people at the start of their careers.

**For job seekers:**
- Browse and search verified entry-level jobs with filters for location, job type, salary, and remote status
- Set up job alerts to get emailed when new matching roles are posted
- Upload a resume and track saved jobs from a personal dashboard
- Read career guides covering interviews, resumes, salary negotiation, and more

**For employers:**
- Submit job postings for review and publication
- Company profile pages with all active listings in one place

**For admins:**
- Full Django admin panel to manage jobs, blog posts, companies, FAQs, and site settings
- Blog posts show live SEO health scores and word counts to maintain content quality
- AdSense toggle in site settings — disabled by default, one click to enable after approval

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 5.2 |
| Database | Turso (libSQL) |
| Media storage | Cloudinary |
| Hosting | Render (free tier) |
| Keep-alive | UptimeRobot |
| Static files | WhiteNoise |
| Frontend | HTMX + Alpine.js + Tailwind CSS |
| Rich text | django-ckeditor |
| API | Django REST Framework |

---

## Key Features

**Google for Jobs** — Every job detail page includes `JobPosting` JSON-LD structured data so listings appear directly in Google Search results.

**SEO-first blog** — Every blog post has a meta title, meta description, focus keyword, and `BlogPosting` structured data. The admin panel shows a live 0–5 SEO health score per post so thin content never gets published accidentally.

**Admin-controlled site settings** — Hero text, site tagline, social links, GA4 measurement ID, and the AdSense publisher ID are all editable from Django admin without touching code. The AdSense switch defaults to off and includes a warning label to prevent premature enabling.

**Skeleton loaders** — All dynamic content areas (job listings, blog cards, company logos) show CSS skeleton loaders when data is empty — no hardcoded placeholder content anywhere.

**Health check endpoint** — `/health/` returns live database status, used by UptimeRobot to keep the Render free tier from spinning down.

---

## Project Structure

```
apps/
├── accounts/     # User registration, login, dashboard, profiles
├── blog/         # Posts, categories, tags
├── core/         # Homepage, contact, FAQ, SiteSettings, health check
├── jobs/         # Job listings, companies, categories, alerts
├── newsletter/   # Subscriber model, subscribe view, CSV export
├── services/     # Service pages (resume review, interview coaching, etc.)
└── seo/          # Sitemap helpers
config/
├── settings/
│   ├── base.py         # Shared settings
│   ├── development.py  # Local dev
│   └── production.py   # Render deployment
templates/        # All Django HTML templates
static/           # CSS, JS, SVG icons
```

---

## Local Development

**Requirements:** Python 3.11+, Git

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/job-foundry-hub.git
cd job-foundry-hub

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements/base.txt

# Set up environment
cp .env.example .env
# Edit .env — set DEBUG=True, leave TURSO vars empty for local SQLite

# Run migrations
python manage.py migrate

# Seed initial data (SiteSettings, FAQs, job categories)
python manage.py seed_data

# Load the 24 blog posts
python manage.py load_initial_blog_posts

# Create admin user
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Visit `http://localhost:8000` — admin at `http://localhost:8000/admin/`

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values.

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for dev, `False` for production |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |
| `TURSO_DATABASE_URL` | Turso database URL (`libsql://...`) |
| `TURSO_AUTH_TOKEN` | Turso authentication token |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |
| `SITE_NAME` | Site display name |
| `GA_MEASUREMENT_ID` | Google Analytics 4 measurement ID |
| `ADSENSE_PUBLISHER_ID` | AdSense publisher ID (fill after approval) |

**Local dev tip:** Leave `TURSO_DATABASE_URL` empty in `.env` and Django automatically uses a local SQLite file.

---

## Deployment (Render + Turso + Cloudinary)

The project includes a `render.yaml` for one-click Render deployment.

1. Push repo to GitHub
2. Connect repo on render.com → New Web Service
3. Add the 5 secret environment variables in Render dashboard:
   - `TURSO_DATABASE_URL`
   - `TURSO_AUTH_TOKEN`
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
4. Deploy — Render runs migrations, seeds data, and loads blog posts automatically
5. Set up UptimeRobot to ping `https://yoursite.com/health/` every 5 minutes

Full deployment steps are in `DEPLOYMENT_GUIDE.md`.

---

## AdSense Setup

AdSense is disabled by default. To enable after receiving approval:

1. Django admin → Site Settings
2. Set `adsense_publisher_id` to your publisher ID
3. Set `adsense_enabled` to ✅
4. Save — ads go live immediately, no code change or redeploy needed

---

## Management Commands

```bash
# Seed SiteSettings, FAQs, and job categories
python manage.py seed_data

# Load all 24 blog posts
python manage.py load_initial_blog_posts

# Fix any duplicate slugs (utility)
python manage.py fix_slugs
```

---

## License

Private project. All rights reserved.
