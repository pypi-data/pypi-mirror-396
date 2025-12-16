#!/usr/bin/env python3
"""Allow python -m feed2toot to run the CLI."""

import sys

from feed2toot.cli import main


if __name__ == "__main__":
    sys.exit(main())
