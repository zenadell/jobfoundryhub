import os
import json
import logging
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

logger = logging.getLogger(__name__)

# The endpoint for the Indexing API
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

def get_authorized_session():
    """
    Creates an authorized session using the Service Account JSON
    stored in the GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable.
    """
    json_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if not json_creds:
        logger.warning("GOOGLE_APPLICATION_CREDENTIALS_JSON not found in environment.")
        return None
        
    try:
        credentials_info = json.loads(json_creds)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=["https://www.googleapis.com/auth/indexing"]
        )
        return AuthorizedSession(credentials)
    except Exception as e:
        logger.error(f"Failed to load Google credentials: {e}")
        return None

def notify_google(url, action="URL_UPDATED"):
    """
    Ping Google Indexing API for a specific URL.
    `action` should be "URL_UPDATED" (for new or updated jobs) 
    or "URL_DELETED" (for expired jobs).
    """
    session = get_authorized_session()
    if not session:
        return False
        
    payload = {
        "url": url,
        "type": action
    }
    
    try:
        response = session.post(ENDPOINT, json=payload)
        if response.status_code == 200:
            logger.info(f"Successfully notified Google Indexing API for {url} ({action})")
            return True
        else:
            logger.error(f"Google Indexing API error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Exception calling Google Indexing API: {e}")
        return False
