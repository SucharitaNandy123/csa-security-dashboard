# backend/pdf_service.py

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import google.auth
import google.auth.transport.requests

def get_authenticated_session():
    """Creates a Requests Session with OAuth token and retry adapter."""
    credentials, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {credentials.token}",
        "User-Agent": "CSA-Dashboard/1.0",
        "Connection": "keep-alive"
    })
    
    # Configure retry policy for transient dropped connections
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

def download_pdf_from_url(url: str) -> bytes:
    """Downloads private GCS browser URLs safely with retry support."""
    session = get_authenticated_session()
    response = session.get(url, timeout=(10, 120))  # 10s connect, 120s read timeout
    response.raise_for_status()
    return response.content