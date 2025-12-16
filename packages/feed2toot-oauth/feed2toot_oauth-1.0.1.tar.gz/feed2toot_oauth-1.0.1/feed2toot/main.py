#!/usr/bin/env python3
# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""Checks an RSS feed and posts new entries to Mastodon."""

# standard libraires imports
import codecs
import importlib
import logging
import logging.handlers
import sys
import re

# external liraries imports
from bs4 import BeautifulSoup

# app libraries imports
from feed2toot.addtags import AddTags
from feed2toot.cliparse import CliParse
from feed2toot.confparse import ConfParse
from feed2toot.feedcache import FeedCache
from feed2toot.filterentry import FilterEntry
from feed2toot.hashtags import build_hashtags
from feed2toot.hashtags import extract_hashtags_from_list
from feed2toot.lock import LockFile
from feed2toot.message import build_message
from feed2toot.message import send_message_dry_run
from feed2toot.message import send_message
from feed2toot.plugins import activate_plugins
from feed2toot.rss import populate_rss
from feed2toot.sortentries import sort_entries


class Main:
    """Main class of Feed2toot"""

    def __init__(self):
        self.main()

    def setup_logging(self, options):
        if options.syslog:
            sl = logging.handlers.SysLogHandler(address="/dev/log")
            sl.setFormatter(logging.Formatter("feed2toot[%(process)d]: %(message)s"))
            # convert syslog argument to a numeric value
            loglevel = getattr(logging, options.syslog.upper(), None)
            if not isinstance(loglevel, int):
                raise ValueError("Invalid log level: %s" % loglevel)
            sl.setLevel(loglevel)
            logging.getLogger("").addHandler(sl)
            logging.debug("configured syslog level %s" % loglevel)
        logging.getLogger("").setLevel(logging.DEBUG)
        sh = logging.StreamHandler()
        sh.setLevel(options.log_level.upper())
        logging.getLogger("").addHandler(sh)
        logging.debug("configured stdout level %s" % sh.level)

    def main(self):
        """The main function"""
        clip = CliParse()
        clioptions = clip.options
        self.setup_logging(clioptions)
        # iterating over the different configuration files
        cfgp = ConfParse(clioptions)
        confs = cfgp.confvalues
        for conf in confs:
            options = conf[0]
            config = conf[1]
            tweetformat = conf[2]
            feeds = conf[3]
            plugins = conf[4]
            # check the logfile and logtimeout
            lockfile = LockFile(options["lockfile"], options["locktimeout"])
            # create link to the persistent list
            cache = FeedCache(options)
            severalwordshashtags = extract_hashtags_from_list(options)
            # reverse feed entries because most recent one should be sent as the last one in Mastodon
            for feed in feeds:
                # store the patterns by rss
                if "patterns" in feed:
                    patterns = feed["patterns"]
                entries = feed["feed"]["entries"][0 : clioptions.limit]
                entries.reverse()
                # --rss-sections option: print rss sections and exit
                if clioptions.rsssections:
                    if entries:
                        print(
                            "The following sections are available in this RSS feed: {}".format(
                                [j for j in entries[0]]
                            )
                        )
                    else:
                        print("Could not parse the section of the rss feed")
                        # release the lock file
                    lockfile.release()
                    sys.exit(0)
                # sort entries and check if they were not previously sent
                totweet = sort_entries(clioptions.all, cache, entries)
                for entry in totweet:
                    # populate rss with new entry to send
                    rss = populate_rss(entry)
                    rss = build_hashtags(entry, rss, options, severalwordshashtags)
                    # parse tweetfomat to elements
                    elements = re.findall(r"\{(.*?)\}", tweetformat)
                    # strip : from elements to allow string formating, eg. {title:.20}
                    for i, s in enumerate(elements):
                        if s.find(":"):
                            elements[i] = s.split(":")[0]
                    fe = FilterEntry(
                        elements,
                        entry,
                        options,
                        feed["patterns"],
                        feed["rssobject"],
                        feed["feedname"],
                    )
                    entrytosend = fe.finalentry
                    if entrytosend:
                        finaltweet = build_message(
                            entrytosend,
                            tweetformat,
                            rss,
                            options["tootmaxlen"],
                            options["notagsintoot"],
                        )
                        if clioptions.dryrun:
                            send_message_dry_run(config, entrytosend, finaltweet)
                        else:
                            send_message(
                                config,
                                clioptions,
                                options,
                                entrytosend,
                                finaltweet,
                                cache,
                                rss,
                            )
                            # plugins
                            if plugins and entrytosend:
                                activate_plugins(plugins, finaltweet)
            # do not forget to close cache (shelf object)
            cache.close()
            # release the lock file
            lockfile.release()
