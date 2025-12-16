# -*- coding: utf-8 -*-
"""Get value of the uri_list option of the rss section"""

# standard library imports
import feedparser
import logging
import os.path
import ssl
import sys
import re


def parseurilist(config, accept_bozo_exceptions, ignoressl):
    """Parse configuration value of the uri_list option of the rss section"""
    bozoexception = False
    feeds = []
    patterns = []
    section = "rss"
    stringsep = ","
    if config.has_section(section):
        #################
        # uri_list option
        #################
        currentoption = "uri_list"
        if config.has_option(section, currentoption):
            rssfile = config.get(section, currentoption)
            rssfile = os.path.expanduser(rssfile)
            if not os.path.exists(rssfile) or not os.path.isfile(rssfile):
                sys.exit(
                    "The path to the uri_list parameter is not valid: {rssfile}".format(
                        rssfile=rssfile
                    )
                )
            with open(rssfile, "r") as rsfo:
                rsslist = rsfo.readlines()
            for line in rsslist:
                line = line.strip()
                # split each line in two parts, rss link and a string with the different patterns to look for
                feedname = ""
                if "<" in line:
                    matches = re.match("(.*) <(.*)>", line)
                    if not matches:
                        sys.exit(
                            "This line in the list of uri to parse is not formatted correctly: {line}".format(
                                line
                            )
                        )
                    feedname, line = matches.groups()
                confobjects = line.split("|")
                if len(confobjects) > 3 or len(confobjects) == 2:
                    sys.exit(
                        "This line in the list of uri to parse is not formatted correctly: {line}".format(
                            line
                        )
                    )
                if len(confobjects) == 3:
                    rss, rssobject, patternstring = line.split("|")
                if len(confobjects) == 1:
                    rss = confobjects[0]
                    rssobject = ""
                    patternstring = ""
                # split different searched patterns
                patterns = [i for i in patternstring.split(stringsep) if i]
                # ignore ssl if asked
                if ignoressl:
                    if hasattr(ssl, "_create_unverified_context"):
                        ssl._create_default_https_context = (
                            ssl._create_unverified_context
                        )
                # retrieve the content of the rss
                feed = feedparser.parse(rss)
                if "bozo_exception" in feed:
                    bozoexception = True
                    logging.warning(feed["bozo_exception"])
                    if not accept_bozo_exceptions:
                        continue
                # check if the rss feed and the rss entry are valid ones
                if "entries" in feed:
                    if rssobject and rssobject not in feed["entries"][0].keys():
                        sys.exit(
                            "The rss object {rssobject} could not be found in the feed {rss}".format(
                                rssobject=rssobject, rss=rss
                            )
                        )
                else:
                    sys.exit(
                        "The rss feed {rss} does not seem to be valid".format(rss=rss)
                    )
                feeds.append(
                    {
                        "feed": feed,
                        "patterns": patterns,
                        "rssobject": rssobject,
                        "feedname": feedname,
                    }
                )
            # test if all feeds in the list were unsuccessfully retrieved and if so, leave
            if not feeds and bozoexception:
                sys.exit("No feed could be retrieved. Leaving.")
    return feeds
