# rev-auth-helper

Lightweight helper to load Rev API credentials and fetch access tokens for use in other scripts (like rev-jwt-tools or rev_c2pa_fetcher).

## Setup
- Install: `pip install git+https://github.com/agmcin/rev_auth_helper`
- Copy `RevCreds.example.json` to `%USERPROFILE%/.rev/RevCreds.json` (default lookup path) or another location.
- Fill in the API Key and Secret for an account admin user, plus the Rev host URL (include scheme, e.g., `https://...`), in RevCreds.json. If you keep it elsewhere, pass `--creds <path>`.

## Usage
- CLI token fetch: `python -m rev_auth --host https://b.rev-qa.vbrick.com`
  - Optional: `--creds <path>` to override default, `--timeout 10`.
- Library use:
  ```python
  from rev_auth import get_token
  token, expiration = get_token("https://b.rev-qa.vbrick.com")
  ```

## RevCreds.json format
- File path: default `%USERPROFILE%/.rev/RevCreds.json` (see `RevCreds.example.json` in the repo root for a template).
- Structure: a JSON list of objects with `host`, `apiKey`, and `secret` (or `apiSecret`).
- Minimal example:
  ```json
  [
    {
      "host": "b.rev-qa.vbrick.com",
      "apiKey": "your-api-key",
      "secret": "your-api-secret"
    },
    {
      "host": "prod.rev.vbrick.com",
      "apiKey": "prod-api-key",
      "secret": "prod-api-secret"
    }
  ]
  ```
- The helper normalizes the host: a full URL is OK; matching is done on the hostname. Multiple environments are supported; the best match wins.

## What it does
- Normalizes a host or full URL.
- Loads creds map from JSON.
- Selects best-matching host entry.
- Calls POST /api/v2/authenticate to get vbrickAccessToken.
- Returns token and expiration

## Config file
See RevCreds.example.json for structure (top-level list of objects with `host`, `apiKey`, `secret`). Multiple environments are supported; the helper picks the matching host. 

## Notes
- Depends only on requests.
- No network calls until you invoke token retrieval. CLI outputs token to stdout for easy piping into other scripts.
