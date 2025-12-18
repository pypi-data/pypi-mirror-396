import json
import os
from functools import lru_cache
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

DEFAULT_CREDS_PATH = os.path.join(os.path.expanduser("~"), ".rev", "RevCreds.json")


def _normalize_host(host_or_url: str) -> str:
    parsed = urlparse(host_or_url)
    if parsed.scheme and parsed.netloc:
        return parsed.netloc.lower()
    return host_or_url.lower().strip().strip("/")


@lru_cache(maxsize=1)
def load_creds(path: Optional[str] = None) -> Dict[str, Tuple[str, str]]:
    """Load creds from JSON into a host -> (apiKey, secret) map."""
    target = path or DEFAULT_CREDS_PATH
    with open(target, "r", encoding="utf-8") as f:
        data = json.load(f)
    entries = data  # expected to be a list of objects
    result = {}
    for entry in entries or []:
        host = _normalize_host(entry.get("host", ""))
        api_key = entry.get("apiKey")
        api_secret = entry.get("secret") or entry.get("apiSecret")
        if host and api_key and api_secret:
            result[host] = (api_key, api_secret)
    return result


def find_creds_for_host(host_or_url: str, creds: Dict[str, Tuple[str, str]]) -> Optional[Tuple[str, str]]:
    """Return (apiKey, apiSecret) for the best-matching host."""
    target = _normalize_host(host_or_url)
    if target in creds:
        return creds[target]
    # fallback: prefix/suffix matches
    for host, pair in creds.items():
        if target.endswith(host) or host.endswith(target):
            return pair
    return None
