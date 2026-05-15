from django.db import migrations
from django.utils import timezone


POSTS = [
    {
        "title": "How to Write a CV With No Work Experience (2025 Guide)",
        "slug": "how-to-write-cv-no-work-experience",
        "category_slug": "career-advice",
        "excerpt": "Writing your first CV feels daunting when you have no job history. This step-by-step guide shows you exactly what to include, what to leave out, and how to make recruiters take notice.",
        "focus_keyword": "how to write a CV with no experience",
        "meta_title": "How to Write a CV With No Work Experience | Job Foundry Hub",
        "meta_description": "No work experience? No problem. Learn how to write a compelling CV as a graduate or career-changer with our step-by-step 2025 guide.",
        "read_time": 7,
        "content": "<h2>You Don't Need a Job to Have a Great CV</h2><p>One of the biggest myths in job searching is that you need work experience before you can write a decent CV. The truth is that every recruiter reviewing graduate applications knows you haven't had a full-time role yet — they're not looking for that. They're looking for evidence that you can learn, contribute, and communicate.</p><h2>Start With a Strong Personal Statement</h2><p>The top third of your CV is prime real estate. Use three to four sentences to summarise who you are, what you studied or know, and what kind of role you're targeting. Be specific — \"Recent marketing graduate seeking a content or social media role in a growing tech company\" beats \"Motivated individual looking for an exciting opportunity\" every time.</p><h2>Lead With Education</h2><p>When you have no work history, your degree or qualification is your headline achievement. Include your degree title and university, graduation year, final grade if strong, and two or three relevant modules or academic projects. Connect the dots for the recruiter — don't make them guess.</p><h2>Turn University Life Into Experience</h2><p>You almost certainly have more experience than you think. Consider part-time or casual work, student societies or clubs, volunteering, freelance or personal projects, and placements or internships. For each one, follow the formula: action verb + what you did + result or scale.</p><h2>Build a Skills Section That's Actually Useful</h2><p>List hard skills — software, tools, languages — rather than soft skills. Include things like Microsoft Office, data analysis tools (Excel, Python, R), design tools (Canva, Figma), CRM platforms (HubSpot, Mailchimp), and foreign languages with proficiency level.</p><h2>Keep the Format Clean and Simple</h2><p>For an entry-level CV, one page is ideal. Use a clean font at 10–11pt, clear section headings, and consistent spacing. Avoid tables and graphics if you're applying through Applicant Tracking Systems. Save as a PDF unless the job advert specifically asks otherwise.</p><h2>Tailor It Every Time</h2><p>A generic CV sent to fifty employers will get fewer responses than a tailored CV sent to ten. Read each job description carefully and mirror the language they use. Present your real experience in the language the employer is already using.</p>",
    },
    {
        "title": "10 Best Entry-Level Jobs for Graduates in the UK (2025)",
        "slug": "best-entry-level-jobs-graduates-uk-2025",
        "category_slug": "job-market",
        "excerpt": "Not sure which career path to pursue after graduation? We break down the 10 most accessible, well-paying entry-level roles available to UK graduates right now — with typical salaries and what each job actually involves.",
        "focus_keyword": "best entry-level jobs for graduates UK",
        "meta_title": "10 Best Entry-Level Jobs for UK Graduates in 2025 | Job Foundry Hub",
        "meta_description": "Discover the 10 best entry-level jobs for graduates in the UK in 2025, with salary ranges, required skills, and how to land each role.",
        "read_time": 8,
        "content": "<h2>Finding Your First Graduate Role in the UK</h2><p>The UK graduate job market in 2025 remains competitive, but opportunities are there for candidates who know where to look. Some sectors are actively struggling to fill entry-level positions.</p><h2>1. Junior Software Developer — £28,000–£38,000</h2><p>Tech remains the most reliably hiring sector for graduates. Junior developer roles require programming knowledge (Python, JavaScript, Java) but rarely expect production-level experience. Many employers will hire candidates with a strong portfolio of projects even without a Computer Science degree.</p><h2>2. Marketing Executive — £22,000–£28,000</h2><p>One of the most common entry-level graduate roles across virtually every industry. Responsibilities typically include content creation, social media management, email campaigns, and basic analytics.</p><h2>3. Data Analyst — £25,000–£35,000</h2><p>Demand for data skills has grown every year for the past decade. Entry-level roles typically require Excel, SQL, and ideally Python or Tableau. Finance, retail, healthcare, and tech are all hiring heavily.</p><h2>4. HR Assistant — £21,000–£26,000</h2><p>Human Resources consistently takes on graduates from any discipline. HR assistants support recruitment, onboarding, payroll, and employee relations. Many large employers run dedicated graduate HR schemes with CIPD qualification support.</p><h2>5. Account Executive (Sales) — £22,000–£30,000 + commission</h2><p>Sales roles offer some of the fastest career progression available. An account executive in a B2B tech company can move to account manager within 18 months. Base salaries are modest but OTE can significantly increase total pay.</p><h2>6. Financial Analyst — £26,000–£34,000</h2><p>Graduate schemes at banks and consulting firms offer structured training and professional qualifications. Many mid-size firms offer excellent opportunities with less competition than the biggest names.</p><h2>7. Content Writer / Copywriter — £21,000–£28,000</h2><p>Every business that exists online needs content. Strong writing skills are the primary requirement — a portfolio of published or sample work carries more weight than your degree subject.</p><h2>8. UX/UI Designer — £25,000–£35,000</h2><p>Employers care about your portfolio far more than your qualification. Junior UX designers who can demonstrate user research, wireframing, and prototyping using Figma are in demand across tech, finance, and retail.</p><h2>9. Project Coordinator — £23,000–£29,000</h2><p>A role that exists in almost every sector and offers a clear path to project manager. PRINCE2 or APM Foundation qualifications are often funded by employers.</p><h2>10. Recruitment Consultant — £20,000–£26,000 + commission</h2><p>Recruitment is an often-underrated graduate career with fast progression. Consultants match candidates to roles and manage client relationships. Many perform well above their base salary within the first year.</p>",
    },
    {
        "title": "How to Prepare for a Graduate Job Interview (Complete Guide)",
        "slug": "how-to-prepare-graduate-job-interview",
        "category_slug": "interview-prep",
        "excerpt": "Your first graduate interview doesn't have to be terrifying. This guide covers everything from researching the company to answering competency questions — so you walk in prepared and walk out confident.",
        "focus_keyword": "how to prepare for a graduate job interview",
        "meta_title": "How to Prepare for a Graduate Job Interview | Job Foundry Hub",
        "meta_description": "Everything you need to know to prepare for a graduate job interview — research, competency questions, STAR answers, and what to do afterwards.",
        "read_time": 9,
        "content": "<h2>Preparation Is the Only Variable You Control</h2><p>In a job interview, you can't control which questions get asked or how many other candidates applied. What you can control is how prepared you are. Thorough preparation doesn't guarantee you the job — but it significantly raises the odds.</p><h2>Step 1: Research the Company Properly</h2><p>Deep research sounds like: \"I noticed you expanded into the German market last year — I'm curious whether that's changed how the marketing team thinks about localisation.\" Before any interview, know what the company does and how it makes money, its main competitors, recent news, and the specific team you'd be joining.</p><h2>Step 2: Understand the Job Description in Detail</h2><p>Highlight every responsibility and requirement. For each one, think of a specific example from your university, part-time work, or personal projects that demonstrates you can do that thing.</p><h2>Step 3: Prepare STAR Answers</h2><p>Most graduate interviews include competency questions. The STAR framework: Situation (set the context), Task (what did you need to achieve?), Action (what did YOU do?), Result (what was the outcome — quantify if possible). Prepare answers for working under pressure, solving problems, teamwork, conflict, showing initiative, and making a mistake.</p><h2>Step 4: Prepare for \"Why This Company?\"</h2><p>Connect something specific about the company to something specific about your interests or goals. \"I've been following your work on sustainability reporting since reading your 2023 annual review\" is far stronger than generic admiration.</p><h2>Step 5: Prepare Your Questions</h2><p>Good questions: \"What does success look like in this role at six months?\" / \"What are the biggest challenges facing the team right now?\" / \"What career paths have people in this role typically taken?\" Avoid asking about salary or benefits in a first interview.</p><h2>After the Interview</h2><p>Send a short thank-you email within 24 hours. Two or three sentences thanking them and reaffirming your interest. Most candidates don't bother — this immediately distinguishes you.</p>",
    },
    {
        "title": "LinkedIn for Graduates: How to Build a Profile That Gets You Noticed",
        "slug": "linkedin-tips-for-graduates",
        "category_slug": "networking",
        "excerpt": "Most graduates have a LinkedIn profile. Very few have a good one. Here's how to build a profile that attracts recruiters, gets connection requests accepted, and opens doors you didn't know existed.",
        "focus_keyword": "LinkedIn tips for graduates",
        "meta_title": "LinkedIn Tips for Graduates: Build a Profile That Gets You Hired | Job Foundry Hub",
        "meta_description": "Learn how to build a LinkedIn profile as a graduate that attracts recruiters and lands interviews. Practical tips on headlines, summaries, and outreach.",
        "read_time": 6,
        "content": "<h2>Why LinkedIn Matters More Than Job Boards</h2><p>The candidates who find the best opportunities — often before they're publicly advertised — are the ones who've built a presence on LinkedIn. Recruiters actively search LinkedIn every day for candidates who match their open roles.</p><h2>Your Profile Photo</h2><p>Use a clear, professional headshot — just your face and shoulders, against a plain background. No group photos, no holiday snaps. Profiles with photos receive roughly 21 times more views than those without.</p><h2>Your Headline</h2><p>Instead of \"Recent Graduate\", use: \"Marketing Graduate | Content, Social Media &amp; Brand | Open to Entry-Level Roles\". This tells a recruiter in one line exactly what they need to know and helps LinkedIn's search algorithm surface your profile.</p><h2>The About Section</h2><p>Write in first person, three short paragraphs: who you are and what you studied, what you've done (projects, work experience, skills), what you're looking for and how to contact you. Include a call to action: \"Feel free to connect or send me a message.\"</p><h2>Experience Section</h2><p>Add everything — part-time work, internships, volunteering, and society roles. Write two or three bullet points per entry using the action verb + result formula. Don't leave this section empty just because you haven't had a formal job.</p><h2>Getting Your First Connections</h2><p>Start by connecting with everyone you know: classmates, lecturers, people you've worked with. Aim for 100+ connections first. Then connect with people at target companies — send a short personalised note with each request.</p><h2>The Open to Work Feature</h2><p>Turn on \"Open to Work\" in settings. Choose the recruiter-only option to reach people actively searching for candidates without broadcasting your job search to your entire network.</p>",
    },
    {
        "title": "What to Expect in Your First Job: A Realistic Guide for New Graduates",
        "slug": "what-to-expect-first-job-graduates",
        "category_slug": "life-skills",
        "excerpt": "Starting your first real job comes with surprises no one warns you about. From imposter syndrome to office politics, here's an honest guide to the first few months so you can hit the ground running.",
        "focus_keyword": "what to expect in your first job",
        "meta_title": "What to Expect in Your First Job | Advice for New Graduates | Job Foundry Hub",
        "meta_description": "Starting your first graduate job? Here's what nobody tells you — imposter syndrome, workplace dynamics, how to build relationships, and how to thrive in month one.",
        "read_time": 7,
        "content": "<h2>Nobody Tells You This Before You Start</h2><p>University prepares you for a lot of things. Your first job prepares you for entirely different ones. The shift from education to full-time employment catches most new graduates off guard — not because the work is too hard, but because the context is so different.</p><h2>The First Week Is Mostly Waiting Around</h2><p>Almost every new starter spends their first few days setting up accounts, sitting in onboarding sessions, and getting introduced to people whose names they'll immediately forget. This is normal. Use this time to observe how people communicate and how decisions get made.</p><h2>Imposter Syndrome Is Almost Universal</h2><p>At some point you'll feel like you don't really belong there, that everyone else knows what they're doing and you're just pretending. This is imposter syndrome and it affects the vast majority of new graduates. The antidote is action — focus on small wins rather than measuring yourself against colleagues who've been there for years.</p><h2>Ask Questions — But Smartly</h2><p>Attempt to find answers yourself before going to a colleague. Batch your questions where possible. Take notes when someone explains something — being told the same thing twice is frustrating for the person explaining.</p><h2>Build Relationships Deliberately</h2><p>The quality of your working relationships will have more impact on your career progression than almost anything else. Make a point of getting to know people beyond your immediate team. Visible, genuine effort to connect builds the kind of trust that gets you included in interesting projects.</p><h2>Manage Up</h2><p>Don't wait for feedback to come to you. Proactively update your manager on your progress, ask for feedback explicitly, and tell them what you want to learn. Most managers appreciate direct, self-aware team members who don't need to be constantly prompted.</p>",
    },
    {
        "title": "Entry-Level Tech Jobs for Graduates: Your Complete 2025 Guide",
        "slug": "entry-level-tech-jobs-graduates-2025",
        "category_slug": "industry-guides",
        "excerpt": "Tech offers some of the best entry-level salaries and career progression for graduates. This guide covers the main roles available, what skills you actually need, and how to break in without a CS degree.",
        "focus_keyword": "entry-level tech jobs for graduates",
        "meta_title": "Entry-Level Tech Jobs for Graduates 2025 | Job Foundry Hub",
        "meta_description": "Discover the best entry-level tech jobs for graduates in 2025 — salaries, required skills, and how to break into tech without a Computer Science degree.",
        "read_time": 8,
        "content": "<h2>Why Tech Is Worth Targeting as a Graduate</h2><p>Technology companies consistently offer graduate salaries above the national average, clearer career progression, and a culture that invests in employee development. Tech roles exist across every industry — finance, retail, healthcare, media, and government all hire technical talent.</p><h2>Junior Software Developer — £28,000–£40,000</h2><p>Write, test, and maintain code within a development team using version control, code reviews, and Agile methodologies. Skills needed: at least one programming language (Python, JavaScript, Java, C#), understanding of data structures, familiarity with Git, and a portfolio of projects. Can you do it without a CS degree? Yes — bootcamp graduates with strong portfolios regularly compete successfully with CS graduates.</p><h2>Data Analyst — £25,000–£35,000</h2><p>Collect, clean, and analyse data to help organisations make better decisions. Skills needed: Excel (advanced), SQL (essential), Python or R (valuable), and data visualisation tools like Tableau or Power BI.</p><h2>QA / Test Engineer — £24,000–£32,000</h2><p>Test software applications to find bugs before they reach users. An often-overlooked entry point into software — many QA engineers transition to developer roles within two to three years.</p><h2>Cybersecurity Analyst — £26,000–£36,000</h2><p>Monitor systems for security threats and investigate incidents. One of the fastest-growing areas in tech with a significant skills shortage. CompTIA Security+ certification is well regarded.</p><h2>UX Designer — £25,000–£35,000</h2><p>Research how users interact with digital products, design wireframes and prototypes, conduct usability testing. Figma is the industry standard. A portfolio demonstrating design process — not just finished screens — is essential.</p><h2>Breaking In Without a CS Degree</h2><p>What matters most is evidence of ability: a portfolio of projects on GitHub or Behance, relevant certifications (Google, AWS, CompTIA), and demonstrable self-teaching ability. Target companies with graduate schemes or explicit \"no degree required\" policies.</p>",
    },
    {
        "title": "How to Negotiate Your First Salary as a Graduate",
        "slug": "how-to-negotiate-first-salary-graduate",
        "category_slug": "career-advice",
        "excerpt": "Most graduates accept the first salary offer they receive. That's a mistake that compounds for years. Here's how to negotiate confidently, professionally, and successfully — even when it feels uncomfortable.",
        "focus_keyword": "how to negotiate first salary graduate",
        "meta_title": "How to Negotiate Your First Salary as a Graduate | Job Foundry Hub",
        "meta_description": "Learn how to negotiate your first graduate salary confidently. Find out when to negotiate, what to say, and how to avoid common mistakes that cost you thousands.",
        "read_time": 6,
        "content": "<h2>Why Most Graduates Don't Negotiate</h2><p>Around 40% of people never negotiate their salary. Among new graduates, that number is even higher. Here's the reality: salary offers are almost always opening positions, not final ones. Employers expect some negotiation. And because your starting salary sets the baseline for every future pay rise, accepting less than you're worth has a compounding effect that can cost you tens of thousands over a career.</p><h2>Do Your Research First</h2><p>Research market rates using Glassdoor, LinkedIn Salary, Totaljobs, Reed, and Indeed salary tools. Find a realistic range: your floor (below which you'd decline), the midpoint (fair market value), and the upper end (what you'd be thrilled to receive).</p><h2>When to Bring It Up</h2><p>Wait until you have a firm offer. Once they've made an offer, they've invested in the process and want you specifically — that's when your leverage is highest.</p><h2>How to Ask</h2><p>A simple script: \"Thank you so much for the offer — I'm genuinely excited about the role. Based on my research into market rates for this position, I was hoping we could discuss a salary closer to [specific number]. Is there any flexibility?\" Reference external evidence, name a specific number, and ask a direct question.</p><h2>What to Avoid</h2><ul><li>Apologising for negotiating — it undermines you before you've said anything</li><li>Sharing personal financial pressures — this gives the employer no reason to pay more</li><li>Giving an ultimatum unless you're genuinely prepared to walk away</li><li>Accepting verbally then renegotiating — once you've accepted, the conversation is over</li></ul><h2>If They Say No</h2><p>Accept without resentment and get the agreed review date in writing. The confidence you build from having the negotiation conversation — regardless of outcome — makes the next one easier.</p>",
    },
]


def seed_posts(apps, schema_editor):
    Post = apps.get_model("blog", "Post")
    BlogCategory = apps.get_model("blog", "BlogCategory")
    User = apps.get_model("auth", "User")

    author = User.objects.filter(is_staff=True).order_by("id").first()
    if not author:
        author = User.objects.order_by("id").first()
    if not author:
        return

    now = timezone.now()

    for data in POSTS:
        if Post.objects.filter(slug=data["slug"]).exists():
            continue
        try:
            cat = BlogCategory.objects.get(slug=data["category_slug"])
        except BlogCategory.DoesNotExist:
            cat = BlogCategory.objects.first()
            if not cat:
                continue

        Post.objects.create(
            title=data["title"],
            slug=data["slug"],
            category=cat,
            author=author,
            excerpt=data["excerpt"],
            content=data["content"],
            read_time=data["read_time"],
            meta_title=data["meta_title"],
            meta_description=data["meta_description"],
            focus_keyword=data["focus_keyword"],
            status="published",
            published_at=now,
            updated_at=now,
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0005_add_soft_delete_trashed_status"),
    ]

    operations = [
        migrations.RunPython(seed_posts, noop),
    ]
