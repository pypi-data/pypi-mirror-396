#!/usr/bin/env python3
"""Command-line entry point for feed2toot."""

import sys

from feed2toot.main import Main


def main() -> int:
    """Launch feed2toot and return the exit status."""
    Main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
