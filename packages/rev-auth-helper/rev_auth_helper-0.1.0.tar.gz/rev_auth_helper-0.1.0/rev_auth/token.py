from typing import Optional, Tuple
from urllib.parse import urlparse, urlunparse

import requests

from .creds import DEFAULT_CREDS_PATH, find_creds_for_host, load_creds

AUTH_PATH = "/api/v2/authenticate"


def _build_base_url(host_or_url: str) -> str:
    parsed = urlparse(host_or_url)
    if parsed.scheme and parsed.netloc:
        return urlunparse((parsed.scheme, parsed.netloc, "", "", "", ""))
    # default to https if scheme missing
    return f"https://{host_or_url.strip('/')}"


def get_token(host_or_url: str, creds_path: Optional[str] = None, timeout: int = 10, session: Optional[requests.Session] = None) -> Tuple[str, Optional[str]]:
    """
    Fetch vbrickAccessToken using API key/secret for the given host/url.
    Returns (token, expiration_iso_or_None).
    """
    creds_map = load_creds(creds_path or DEFAULT_CREDS_PATH)
    creds = find_creds_for_host(host_or_url, creds_map)
    if not creds:
        raise ValueError(f"No credentials found for host '{host_or_url}'")
    api_key, api_secret = creds

    base_url = _build_base_url(host_or_url)
    url = f"{base_url}{AUTH_PATH}"

    payload = {"apiKey": api_key, "secret": api_secret}
    sess = session or requests.Session()
    resp = sess.post(url, json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    token = data.get("token")
    if not token:
        raise ValueError("No access token in response")
    expiration = data.get("expiration")
    return token, expiration
