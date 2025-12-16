# -*- coding: utf-8 -*-
"""CLI parsing"""

# standard library imports
from argparse import ArgumentParser
import glob
import logging
import os
import os.path
import sys

DIST_NAME = "feed2toot-oauth"

try:  # Python 3.8+
    from importlib import metadata as importlib_metadata
except ImportError:  # pragma: no cover - fallback for older Pythons
    importlib_metadata = None  # type: ignore


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


class CliParse:
    """CliParse class"""

    def __init__(self):
        """Constructor for the CliParse class"""
        self.main()

    def main(self):
        """main of CliParse class"""
        feed2tootepilog = "For more information: https://feed2toot.readthedocs.io"
        feed2tootdescription = "Take rss feed and send it to Mastodon"
        parser = ArgumentParser(
            prog="feed2toot", description=feed2tootdescription, epilog=feed2tootepilog
        )
        parser.add_argument("--version", action="version", version=__version__)
        parser.add_argument(
            "-c",
            "--config",
            default=[
                os.path.join(os.getenv("XDG_CONFIG_HOME", "~/.config"), "feed2toot.ini")
            ],
            nargs="+",
            dest="config",
            help="Location of config file (default: %(default)s)",
            metavar="FILE",
        )
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            default=False,
            dest="all",
            help="tweet all RSS items, regardless of cache",
        )
        parser.add_argument(
            "--ignore-ssl",
            action="store_true",
            default=False,
            dest="ignore_ssl",
            help="ignore ssl errors while fetching rss feeds",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            default=10,
            type=int,
            help="tweet only LIMIT items (default: %(default)s)",
        )
        parser.add_argument(
            "-t",
            "--lock-timeout",
            dest="locktimeout",
            default=3600,
            type=int,
            help="lock timeout in seconds after which feed2toot can removes the lock itself",
        )
        parser.add_argument(
            "--cachefile",
            dest="cachefile",
            help="location of the cache file (default: %(default)s)",
        )
        parser.add_argument(
            "--lockfile",
            dest="lockfile",
            default=os.path.join(
                os.getenv("XDG_CONFIG_HOME", "~/.config"), "feed2toot.lock"
            ),
            help="location of the lock file (default: %(default)s)",
        )
        parser.add_argument(
            "-n",
            "--dry-run",
            dest="dryrun",
            action="store_true",
            default=False,
            help="Do not actually post tweets",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            "--info",
            dest="log_level",
            action="store_const",
            const="info",
            default="warning",
            help="enable informative (verbose) output, work on log level INFO",
        )
        parser.add_argument(
            "-d",
            "--debug",
            dest="log_level",
            action="store_const",
            const="debug",
            default="warning",
            help="enable debug output, work on log level DEBUG",
        )
        levels = [
            i for i in logging._nameToLevel.keys() if (type(i) == str and i != "NOTSET")
        ]
        parser.add_argument(
            "--syslog",
            nargs="?",
            default=None,
            type=str.upper,
            action="store",
            const="INFO",
            choices=levels,
            help="""log to syslog facility, default: no
                            logging, INFO if --syslog is specified without
                            argument""",
        )
        parser.add_argument(
            "--hashtaglist", dest="hashtaglist", help="a list of hashtags to match"
        )
        parser.add_argument(
            "-p",
            "--populate-cache",
            action="store_true",
            default=False,
            dest="populate",
            help="populate RSS entries in cache without actually posting them to Mastodon",
        )
        parser.add_argument(
            "-r",
            "--rss",
            help="the RSS feed URL to fetch items from",
            dest="rss_uri",
            metavar="http://...",
        )
        parser.add_argument(
            "--rss-sections",
            action="store_true",
            default=False,
            dest="rsssections",
            help="print the available sections of the rss feed to be used in the tweet template",
        )
        self.opts = parser.parse_args()
        # expand the path to the cache file if defined
        if self.opts.cachefile:
            self.opts.cachefile = os.path.expanduser(self.opts.cachefile)
        # verify if the path to cache file is an absolute path
        # get the different config files, from a directory or from a *.ini style
        self.opts.config = list(map(os.path.expanduser, self.options.config))
        for element in self.opts.config:
            if element and not os.path.exists(element):
                sys.exit(
                    "You should provide an existing path for the config file: %s"
                    % element
                )
            if os.path.isdir(element):
                self.opts.configs = glob.glob(os.path.join(element, "*.ini"))
            else:
                # trying to glob the path
                self.opts.configs = glob.glob(element)
        # verify if a configuration file is provided
        if not self.opts.configs:
            sys.exit(
                "no configuration file was found at the specified path(s) with the option -c"
            )
        # verify the path to the hashtaglist
        if self.opts.hashtaglist:
            hashtaglist = os.path.expanduser(self.opts.hashtaglist)
            if not os.path.exists(hashtaglist):
                sys.exit(
                    "the {hashtaglist} file does not seem to exist, please provide a valid path".format(
                        hashtaglist=hashtaglist
                    )
                )

    @property
    def options(self):
        """return the path to the config file"""
        return self.opts
