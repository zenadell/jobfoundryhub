"""
Premium HTML email templates for Job Foundry Hub.
Each function returns a (subject, html_body) tuple.
All templates are fully self-contained HTML — no external CSS dependencies.
"""

# ── Brand colours ─────────────────────────────────────────────────────────────
GREEN  = "#22c55e"
DARK   = "#0f172a"
GREY   = "#64748b"
LIGHT  = "#f8fafc"
WHITE  = "#ffffff"
BORDER = "#e2e8f0"

# ── Base layout wrapper ────────────────────────────────────────────────────────
def _wrap(content: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Job Foundry Hub</title>
</head>
<body style="margin:0;padding:0;background:{LIGHT};font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:{LIGHT};padding:40px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:{WHITE};border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08);">

        <!-- Header -->
        <tr>
          <td style="background:{DARK};padding:32px 40px;text-align:center;">
            <div style="font-size:22px;font-weight:800;color:{WHITE};letter-spacing:-0.5px;">
              Job <span style="color:{GREEN};">Foundry</span> Hub
            </div>
            <div style="width:40px;height:3px;background:{GREEN};border-radius:2px;margin:10px auto 0;"></div>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:40px;">
            {content}
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:{LIGHT};padding:24px 40px;border-top:1px solid {BORDER};text-align:center;">
            <p style="margin:0;font-size:12px;color:{GREY};">
              © 2025 Job Foundry Hub · <a href="https://www.jobfoundryhub.com" style="color:{GREEN};text-decoration:none;">jobfoundryhub.com</a>
            </p>
            <p style="margin:6px 0 0;font-size:11px;color:{BORDER};">
              This email was sent from an automated system. Please do not reply directly.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _heading(text: str) -> str:
    return f'<h1 style="margin:0 0 8px;font-size:24px;font-weight:700;color:{DARK};">{text}</h1>'


def _subheading(text: str) -> str:
    return f'<p style="margin:0 0 24px;font-size:15px;color:{GREY};">{text}</p>'


def _divider() -> str:
    return f'<hr style="border:none;border-top:1px solid {BORDER};margin:24px 0;"/>'


def _info_row(label: str, value: str) -> str:
    return f"""
    <tr>
      <td style="padding:10px 12px;font-size:13px;color:{GREY};font-weight:600;width:140px;border-bottom:1px solid {BORDER};">{label}</td>
      <td style="padding:10px 12px;font-size:14px;color:{DARK};border-bottom:1px solid {BORDER};">{value}</td>
    </tr>"""


def _info_table(rows: list) -> str:
    inner = "".join(_info_row(l, v) for l, v in rows)
    return f'<table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid {BORDER};border-radius:10px;overflow:hidden;margin-bottom:24px;">{inner}</table>'


def _button(text: str, url: str) -> str:
    return f"""
    <div style="text-align:center;margin:28px 0;">
      <a href="{url}" style="display:inline-block;background:{GREEN};color:{WHITE};text-decoration:none;font-weight:700;font-size:15px;padding:14px 36px;border-radius:8px;letter-spacing:0.3px;">
        {text}
      </a>
    </div>"""


def _alert_box(text: str, color: str = GREEN) -> str:
    return f"""
    <div style="background:{color}18;border-left:4px solid {color};border-radius:6px;padding:14px 18px;margin-bottom:24px;">
      <p style="margin:0;font-size:14px;color:{DARK};">{text}</p>
    </div>"""


# ══════════════════════════════════════════════════════════════════════════════
# 1. CONTACT FORM — User Confirmation
# ══════════════════════════════════════════════════════════════════════════════
def contact_user_confirmation(name: str, subject: str) -> tuple:
    content = f"""
    {_heading(f"Hi {name}, we got your message! 👋")}
    {_subheading("Thank you for reaching out to Job Foundry Hub.")}
    {_alert_box("Your message has been received and our team will review it within <strong>24 hours</strong>.")}
    {_divider()}
    <p style="font-size:14px;color:{DARK};margin:0 0 4px;"><strong>Your subject:</strong></p>
    <p style="font-size:15px;color:{GREY};margin:0 0 24px;font-style:italic;">"{subject}"</p>
    {_divider()}
    <p style="font-size:14px;color:{GREY};margin:0 0 20px;">
      While you wait, why not explore the latest opportunities we have available?
    </p>
    {_button("Browse Jobs", "https://www.jobfoundryhub.com/jobs/")}
    <p style="font-size:13px;color:{GREY};text-align:center;margin:0;">
      Need urgent help? Email us at 
      <a href="mailto:support@jobfoundryhub.com" style="color:{GREEN};">support@jobfoundryhub.com</a>
    </p>
    """
    return (
        f"We've received your message — Job Foundry Hub",
        _wrap(content),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 2. CONTACT FORM — Admin Notification
# ══════════════════════════════════════════════════════════════════════════════
def contact_admin_notification(name: str, email: str, subject: str, message: str) -> tuple:
    content = f"""
    {_heading("📬 New Contact Message")}
    {_subheading("Someone has submitted the contact form on Job Foundry Hub.")}
    {_info_table([
        ("From", name),
        ("Email", f'<a href="mailto:{email}" style="color:{GREEN};">{email}</a>'),
        ("Subject", subject),
    ])}
    <p style="font-size:13px;color:{GREY};margin:0 0 8px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Message</p>
    <div style="background:{LIGHT};border-radius:8px;padding:16px;font-size:14px;color:{DARK};line-height:1.7;margin-bottom:24px;">
      {message.replace(chr(10), '<br/>')}
    </div>
    {_button("Reply to " + name, f"mailto:{email}?subject=Re: {subject}")}
    """
    return (
        f"[Contact] {subject} — from {name}",
        _wrap(content),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 3. RESUME SUBMISSION — User Confirmation
# ══════════════════════════════════════════════════════════════════════════════
def resume_user_confirmation(name: str, position: str) -> tuple:
    pos_line = f" for the <strong>{position}</strong> position" if position else ""
    content = f"""
    {_heading(f"Resume received, {name}! 🎉")}
    {_subheading("We're excited to review your profile.")}
    {_alert_box(f"Your resume has been successfully submitted{pos_line}. Our team will carefully review your profile and reach out if there's a great match.")}
    {_divider()}
    <p style="font-size:14px;color:{DARK};margin:0 0 12px;"><strong>What happens next?</strong></p>
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
      <tr>
        <td width="36" valign="top" style="padding-top:2px;">
          <div style="width:28px;height:28px;background:{GREEN};border-radius:50%;text-align:center;line-height:28px;font-size:13px;font-weight:700;color:{WHITE};">1</div>
        </td>
        <td style="padding-left:12px;font-size:14px;color:{GREY};padding-bottom:14px;">Our team reviews your resume and matches it with current openings.</td>
      </tr>
      <tr>
        <td width="36" valign="top" style="padding-top:2px;">
          <div style="width:28px;height:28px;background:{GREEN};border-radius:50%;text-align:center;line-height:28px;font-size:13px;font-weight:700;color:{WHITE};">2</div>
        </td>
        <td style="padding-left:12px;font-size:14px;color:{GREY};padding-bottom:14px;">If there's a match, a member of our team will contact you directly.</td>
      </tr>
      <tr>
        <td width="36" valign="top" style="padding-top:2px;">
          <div style="width:28px;height:28px;background:{GREEN};border-radius:50%;text-align:center;line-height:28px;font-size:13px;font-weight:700;color:{WHITE};">3</div>
        </td>
        <td style="padding-left:12px;font-size:14px;color:{GREY};">You get interviewed and land your dream job! 🚀</td>
      </tr>
    </table>
    {_button("View Open Positions", "https://www.jobfoundryhub.com/jobs/")}
    """
    return (
        "Resume Received — Job Foundry Hub",
        _wrap(content),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 4. RESUME SUBMISSION — Admin Notification
# ══════════════════════════════════════════════════════════════════════════════
def resume_admin_notification(name: str, email: str, position: str, cover_note: str = "") -> tuple:
    rows = [
        ("Candidate", name),
        ("Email", f'<a href="mailto:{email}" style="color:{GREEN};">{email}</a>'),
        ("Position", position or "Not specified"),
    ]
    note_section = ""
    if cover_note:
        note_section = f"""
        <p style="font-size:13px;color:{GREY};margin:0 0 8px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">Cover Note</p>
        <div style="background:{LIGHT};border-radius:8px;padding:16px;font-size:14px;color:{DARK};line-height:1.7;margin-bottom:24px;">
          {cover_note.replace(chr(10), '<br/>')}
        </div>"""
    content = f"""
    {_heading("📄 New Resume Submission")}
    {_subheading("A candidate has submitted their resume on Job Foundry Hub.")}
    {_info_table(rows)}
    {note_section}
    {_button("View in Admin", "https://www.jobfoundryhub.com/admin/jobs/resumesubmission/")}
    """
    return (
        f"[Resume] New submission from {name}",
        _wrap(content),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 5. JOB POSTING REQUEST — Company Confirmation
# ══════════════════════════════════════════════════════════════════════════════
def job_request_company_confirmation(company_name: str, job_title: str) -> tuple:
    content = f"""
    {_heading(f"Job posting request received! ✅")}
    {_subheading(f"Thank you, {company_name}. We've received your request.")}
    {_alert_box(f"Your request to post <strong>{job_title}</strong> has been submitted. Our team will review it within <strong>1–2 business days</strong> and be in touch.")}
    {_divider()}
    <p style="font-size:14px;color:{DARK};margin:0 0 12px;"><strong>What happens next?</strong></p>
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
      <tr>
        <td width="36" valign="top" style="padding-top:2px;">
          <div style="width:28px;height:28px;background:{GREEN};border-radius:50%;text-align:center;line-height:28px;font-size:13px;font-weight:700;color:{WHITE};">1</div>
        </td>
        <td style="padding-left:12px;font-size:14px;color:{GREY};padding-bottom:14px;">Our team reviews your job listing for quality and relevance.</td>
      </tr>
      <tr>
        <td width="36" valign="top" style="padding-top:2px;">
          <div style="width:28px;height:28px;background:{GREEN};border-radius:50%;text-align:center;line-height:28px;font-size:13px;font-weight:700;color:{WHITE};">2</div>
        </td>
        <td style="padding-left:12px;font-size:14px;color:{GREY};padding-bottom:14px;">Once approved, your listing goes live and is visible to thousands of graduates.</td>
      </tr>
      <tr>
        <td width="36" valign="top" style="padding-top:2px;">
          <div style="width:28px;height:28px;background:{GREEN};border-radius:50%;text-align:center;line-height:28px;font-size:13px;font-weight:700;color:{WHITE};">3</div>
        </td>
        <td style="padding-left:12px;font-size:14px;color:{GREY};">You start receiving quality graduate applications directly!</td>
      </tr>
    </table>
    {_button("View Our Platform", "https://www.jobfoundryhub.com/jobs/")}
    <p style="font-size:13px;color:{GREY};text-align:center;margin:0;">
      Questions? Contact us at 
      <a href="mailto:support@jobfoundryhub.com" style="color:{GREEN};">support@jobfoundryhub.com</a>
    </p>
    """
    return (
        f"Job Posting Request Received — Job Foundry Hub",
        _wrap(content),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 6. JOB POSTING REQUEST — Admin Notification
# ══════════════════════════════════════════════════════════════════════════════
def job_request_admin_notification(company_name: str, job_title: str, contact_email: str) -> tuple:
    content = f"""
    {_heading("🏢 New Job Posting Request")}
    {_subheading("A company wants to post a job on Job Foundry Hub.")}
    {_info_table([
        ("Company", company_name),
        ("Job Title", job_title),
        ("Contact", f'<a href="mailto:{contact_email}" style="color:{GREEN};">{contact_email}</a>'),
    ])}
    {_button("Review in Admin", "https://www.jobfoundryhub.com/admin/jobs/jobpostingrequest/")}
    """
    return (
        f"[Job Request] {job_title} @ {company_name}",
        _wrap(content),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 7. NEWSLETTER — Admin Notification
# ══════════════════════════════════════════════════════════════════════════════
def newsletter_admin_notification(email: str) -> tuple:
    content = f"""
    {_heading("📧 New Newsletter Subscriber")}
    {_subheading("Someone just subscribed to the Job Foundry Hub newsletter.")}
    {_info_table([
        ("Email", f'<a href="mailto:{email}" style="color:{GREEN};">{email}</a>'),
    ])}
    {_button("View All Subscribers", "https://www.jobfoundryhub.com/admin/newsletter/newslettersubscriber/")}
    """
    return (
        f"[Newsletter] New subscriber: {email}",
        _wrap(content),
    )


# ══════════════════════════════════════════════════════════════════════════════
# 8. QUICK RESUME (Homepage "Can't find anything?" form)
# ══════════════════════════════════════════════════════════════════════════════
def quick_resume_user_confirmation(name: str) -> tuple:
    content = f"""
    {_heading(f"We've got you, {name}! 🙌")}
    {_subheading("Your interest has been registered with Job Foundry Hub.")}
    {_alert_box("Our team will proactively look for roles that match your profile and reach out as soon as something suitable comes up.")}
    {_divider()}
    <p style="font-size:14px;color:{GREY};margin:0 0 20px;">
      In the meantime, don't forget to browse our current listings — your perfect role might already be there!
    </p>
    {_button("Browse All Jobs", "https://www.jobfoundryhub.com/jobs/")}
    <p style="font-size:13px;color:{GREY};text-align:center;margin:8px 0 0;">
      Or submit a full resume for even better matching → 
      <a href="https://www.jobfoundryhub.com/submit-resume/" style="color:{GREEN};">Submit Resume</a>
    </p>
    """
    return (
        "We're on it — Job Foundry Hub",
        _wrap(content),
    )


def quick_resume_admin_notification(name: str, email: str) -> tuple:
    content = f"""
    {_heading("🔍 Quick Resume Interest")}
    {_subheading('Someone used the "Can\'t find anything?" form on the homepage.')}
    {_info_table([
        ("Name", name),
        ("Email", f'<a href="mailto:{email}" style="color:{GREEN};">{email}</a>'),
    ])}
    {_button("View Subscribers", "https://www.jobfoundryhub.com/admin/")}
    """
    return (
        f"[Quick Resume] {name} is looking for a job",
        _wrap(content),
    )
