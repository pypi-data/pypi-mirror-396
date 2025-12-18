import argparse
import sys

from .token import get_token


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fetch a Rev access token for a host/url.")
    parser.add_argument("--host", "--rev-url", dest="host", required=True, help="Host or full Rev URL")
    parser.add_argument("--creds", dest="creds", help="Path to RevCreds.json (defaults to ~/.rev/RevCreds.json)")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    args = parser.parse_args(argv)

    try:
        token, expires_at = get_token(args.host, creds_path=args.creds, timeout=args.timeout)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(token)
    if expires_at:
        print(f"expires_at={expires_at}", file=sys.stderr)


if __name__ == "__main__":
    main()
