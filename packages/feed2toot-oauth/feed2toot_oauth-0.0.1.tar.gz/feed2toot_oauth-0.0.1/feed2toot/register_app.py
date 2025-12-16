#!/usr/bin/env python3
"""Register a Feed2toot Mastodon application using OAuth."""

import sys
from argparse import ArgumentParser
from os import getcwd, sep, makedirs
from typing import List, Optional
from urllib.parse import urlparse

DIST_NAME = "feed2toot-oauth"

try:  # Python 3.8+
    from importlib import metadata as importlib_metadata
except ImportError:  # pragma: no cover - fallback for older Pythons
    importlib_metadata = None  # type: ignore

from mastodon import Mastodon
from mastodon.Mastodon import MastodonIllegalArgumentError

DESCRIPTION = "Create a Mastodon app for Feed2toot (OAuth code flow)"


def _package_version() -> str:
    if importlib_metadata:
        try:
            return importlib_metadata.version(DIST_NAME)
        except importlib_metadata.PackageNotFoundError:
            pass
    try:
        import pkg_resources

        return pkg_resources.get_distribution(DIST_NAME).version  # type: ignore
    except Exception:
        return "0.0.0"


__version__ = _package_version()


__version__ = _package_version()


def build_parser() -> ArgumentParser:
    """Return the CLI argument parser."""
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "-n",
        "--name",
        dest="name",
        default="feed2toot",
        help="Application name (default: feed2toot)",
    )
    parser.add_argument(
        "-c",
        "--client",
        dest="clientcredfile",
        default="feed2toot_clientcred.secret",
        help="Client credentials file (default: feed2toot_clientcred.secret)",
    )
    parser.add_argument(
        "-u",
        "--user",
        dest="usercredfile",
        default="feed2toot_usercred.secret",
        help="User credentials file (default: feed2toot_usercred.secret)",
    )
    return parser


def _validate_instance(instance: str) -> str:
    """Ensure the instance URL looks valid and return the normalized URL."""
    if not instance:
        sys.exit("No instance URL provided, aborting.")

    parsed = urlparse(instance)
    if not parsed.scheme or not parsed.netloc:
        sys.exit(
            "Invalid instance URL. Please include a scheme (e.g. https://example.org)."
        )

    return parsed.geturl().rstrip("/")


def main(argv: Optional[List[str]] = None) -> int:
    """Run the registration flow and return the exit status."""
    parser = build_parser()
    opts = parser.parse_args(args=argv)

    clientcredfile = opts.clientcredfile
    usercredfile = opts.usercredfile

    print(
        "WARNING: run this command from your feed2toot working directory so credentials land where you expect."
    )
    print(f"Registering app '{opts.name}' for Feed2toot")
    print(f"Client credentials file: {clientcredfile}")
    print(f"User credentials file:   {usercredfile}\n")
    print("Checking/Creating ./creds directory")

    makedirs("creds", exist_ok=True)

    instance = input("Instance URL (e.g. https://social.example.org): ").strip()
    instance = _validate_instance(instance)

    # Step 1: Register the app (this works on GoToSocial)
    client_path = f"{getcwd()}{sep}creds{sep}{clientcredfile}"

    print("\nCreating application on instance...")
    Mastodon.create_app(
        opts.name,
        api_base_url=instance,
        scopes=["read", "write"],
        redirect_uris="urn:ietf:wg:oauth:2.0:oob",
        to_file=client_path,
    )
    print(f"App registered and client credentials written to {client_path}")

    mastodon = Mastodon(
        client_id=client_path,
        api_base_url=instance,
        version_check_mode="none",
    )

    # Step 3: Get OAuth URL and have the user authorize
    print("\nGenerating OAuth authorization URL...")
    auth_url = mastodon.auth_request_url(
        redirect_uris="urn:ietf:wg:oauth:2.0:oob",
        scopes=["read", "write"],
    )
    print("Open this URL in a browser, log in, and authorize the app:\n")
    print(f"{auth_url}\n")
    oob_code = input("Paste the code shown by the instance here: ").strip()

    if not oob_code:
        sys.exit("No code provided, aborting.")

    # Step 4: Exchange code for token and store user credentials
    user_path = f"{getcwd()}{sep}creds{sep}{usercredfile}"
    print("\nExchanging code for access token...")

    try:
        mastodon.log_in(
            code=oob_code,
            redirect_uri="urn:ietf:wg:oauth:2.0:oob",
            scopes=["read", "write"],
            to_file=user_path,
        )
    except MastodonIllegalArgumentError as err:
        print(f"Error during OAuth code exchange: {err}")
        sys.exit("Authorization failed. Check instance URL, app scopes, and code.")

    print(f"User credentials written to {user_path}\n")
    print("Done. Use these files in your feed2toot config:")
    print(f"  client_credentials_file: {clientcredfile}")
    print(f"  user_credentials_file:   {usercredfile}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
