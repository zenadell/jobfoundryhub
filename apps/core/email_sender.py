"""
Custom email sender for Job Foundry Hub.
Uses Resend's HTTP API directly via `requests` — no special libraries,
no SMTP ports, no platform restrictions.  Works anywhere on port 443.

Usage:
    from apps.core.email_sender import send_email
    send_email(
        to="user@example.com",
        subject="Hello!",
        body="Your message here.",
    )
"""

import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


def send_email(to, subject, body, html=None):
    """
    Send an email using the Resend HTTP API.
    Falls back silently — the site never crashes.

    Args:
        to:      Recipient email (str or list)
        subject: Email subject line
        body:    Plain-text body
        html:    Optional HTML body
    """
    api_key = getattr(settings, 'RESEND_API_KEY', '')
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@jobfoundryhub.com')

    if not api_key:
        logger.warning("RESEND_API_KEY not set — email not sent.")
        return False

    if isinstance(to, str):
        to = [to]

    payload = {
        "from": from_email,
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
