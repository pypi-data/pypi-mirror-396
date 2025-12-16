# -*- coding: utf-8 -*-
"""Get value of the uri option of the rss section"""

# standard library imports
import feedparser
import ssl
import sys
import re


def parseuri(config, clioption, feeds, ignoressl):
    """Parse configuration value of the uri option of the rss section"""
    rssuri = ""
    feedname = ""
    nopatternurinoglobalpattern = False
    section = "rss"
    if config.has_section(section):
        ############
        # uri option
        ############
        if not feeds and not clioption:
            confoption = "uri"
            if config.has_option(section, confoption):
                urifeed = config.get("rss", "uri")
                feedname = None
                if "<" in urifeed:
                    matches = re.match("(.*) <(.*)>", urifeed)
                    if not matches:
                        sys.exit(
                            "This uri to parse is not formatted correctly: {urifeed}".format(
                                urifeed
                            )
                        )
                    feedname, finaluri = matches.groups()
                    rssuri = finaluri
                else:
                    rssuri = config.get("rss", "uri")
            else:
                sys.exit(
                    "{confoption} parameter in the [{section}] section of the configuration file is mandatory. Exiting.".format(
                        section=section, confoption=confoption
                    )
                )
        else:
            rssuri = clioption
        # ignore ssl if asked
        if ignoressl:
            if hasattr(ssl, "_create_unverified_context"):
                ssl._create_default_https_context = ssl._create_unverified_context
        # get the rss feed for rss parameter of [rss] section
        feed = feedparser.parse(rssuri)
        if not feed:
            sys.exit(
                "Unable to parse the feed at the following url: {rss}".format(rss=rss)
            )
        #########################################
        # no_uri_pattern_no_global_pattern option
        #########################################
        currentoption = "no_uri_pattern_no_global_pattern"
        # default value
        if config.has_option(section, currentoption):
            nopatternurinoglobalpattern = config.getboolean(section, currentoption)
        return rssuri, feed, feedname, nopatternurinoglobalpattern
