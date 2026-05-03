"""
Custom email sender for Job Foundry Hub.
Uses Resend's HTTP API directly via `requests` — no special libraries,
no SMTP ports, no platform restrictions.  Works anywhere on port 443.

Usage:
    from apps.core.email_templates import contact_user_confirmation
    from apps.core.email_sender import send_templated_email

    send_templated_email(to="user@example.com", template=contact_user_confirmation("James", "Help needed"))
"""

import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


def send_email(to, subject, body, html=None):
    """
    Send a plain or HTML email using the Resend HTTP API.
    Falls back silently — the site never crashes.
    """
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@jobfoundryhub.com')

    if not api_key:
        logger.warning("RESEND_API_KEY not set — email not sent.")
        return False

    if isinstance(to, str):
        to = [to]

    payload = {
        "from": f"Job Foundry Hub <{from_email}>",
        "to": to,
        "subject": subject,
        "text": body,
    }

    if html:
        payload["html"] = html

    try:
        resp = requests.post(
            RESEND_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=5,
        )
        if resp.status_code in (200, 201):
            logger.info(f"Email sent to {to}: {subject}")
            return True
        else:
            logger.error(f"Resend API error {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return False


def send_templated_email(to, template: tuple):
    """
    Convenience wrapper — pass a template tuple (subject, html) directly.

    Example:
        from apps.core.email_templates import resume_user_confirmation
        send_templated_email(to=email, template=resume_user_confirmation(name, position))
    """
    subject, html = template
    return send_email(to=to, subject=subject, body="", html=html)
