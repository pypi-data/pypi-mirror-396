# -*- coding: utf-8 -*-
"""Get values of the configuration file"""

# standard library imports
from configparser import SafeConfigParser
import logging
import os
import os.path
import sys
import re

# 3rd party library imports
import feedparser

# feed2toot library imports
from feed2toot.confparsers.cache import parsecache
from feed2toot.confparsers.hashtaglist import parsehashtaglist
from feed2toot.confparsers.hashtags.nohashtags import parsenotagsintoot
from feed2toot.confparsers.feedparser import parsefeedparser
from feed2toot.confparsers.lock import parselock
from feed2toot.confparsers.media import parsemedia
from feed2toot.confparsers.plugins import parseplugins
from feed2toot.confparsers.rss.ignoressl import parseignoressl
from feed2toot.confparsers.rss.pattern import parsepattern
from feed2toot.confparsers.rss.toot import parsetoot
from feed2toot.confparsers.rss.uri import parseuri
from feed2toot.confparsers.rss.urilist import parseurilist
from feed2toot.confparsers.rss.addtags import parseaddtags
from feed2toot.confparsers.rss.tootmaxlen import parsetootmaxlen


class ConfParse:
    """ConfParse class"""

    def __init__(self, clioptions):
        """Constructor of the ConfParse class"""
        self.clioptions = clioptions
        self.tweetformat = ""
        self.stringsep = ","
        self.confs = []
        self.main()

    def main(self):
        """Main of the ConfParse class"""
        for pathtoconfig in self.clioptions.configs:
            options = {}
            # read the configuration file
            config = SafeConfigParser()
            if not config.read(os.path.expanduser(pathtoconfig)):
                sys.exit("Could not read config file")
            ####################
            # feedparser section
            ####################
            accept_bozo_exceptions = parsefeedparser(config)
            ###########################
            # the rss section
            ###########################
            self.tweetformat = parsetoot(config)
            options["tootmaxlen"] = parsetootmaxlen(config)
            #################################################
            # pattern and patter_case_sensitive format option
            #################################################
            options["patterns"], options["patternscasesensitive"] = parsepattern(config)
            #################################################
            # lock file options
            #################################################
            options["lockfile"], options["locktimeout"] = parselock(
                self.clioptions.lockfile, self.clioptions.locktimeout, config
            )
            ###############################
            # addtags option, default: True
            ###############################
            options["addtags"] = parseaddtags(config)
            ###################
            # ignore_ssl option
            ###################
            ignore_ssl = parseignoressl(config, self.clioptions.ignore_ssl)
            #################
            # uri_list option
            #################
            feeds = []
            feeds = parseurilist(config, accept_bozo_exceptions, ignore_ssl)
            ############
            # uri option
            ############
            if config.has_option("rss", "uri") or self.clioptions.rss_uri:
                (
                    options["rss_uri"],
                    feed,
                    feedname,
                    options["nopatternurinoglobalpattern"],
                ) = parseuri(config, self.clioptions.rss_uri, feeds, ignore_ssl)
            else:
                if config.has_option("rss", "no_uri_pattern_no_global_pattern"):
                    options["nopatternurinoglobalpattern"] = config.getboolean(
                        "rss", "no_uri_pattern_no_global_pattern"
                    )
            ###########################
            # the cache section
            ###########################
            options["cachefile"], options["cache_limit"] = parsecache(
                self.clioptions.cachefile, config
            )
            ###########################
            # the hashtaglist section
            ###########################
            options["hashtaglist"] = parsehashtaglist(
                self.clioptions.hashtaglist, config
            )
            options["notagsintoot"] = parsenotagsintoot(config)
            ###########################
            # the media section
            ###########################
            options["media"] = parsemedia(config)
            ###########################
            # the plugins section
            ###########################
            plugins = parseplugins(config)
            ########################################
            # return the final configurations values
            ########################################
            if feeds:
                self.confs.append((options, config, self.tweetformat, feeds, plugins))
            else:
                self.confs.append(
                    (
                        options,
                        config,
                        self.tweetformat,
                        [
                            {
                                "feed": feed,
                                "patterns": [],
                                "rssobject": "",
                                "feedname": feedname,
                            }
                        ],
                        plugins,
                    )
                )

    @property
    def confvalues(self):
        """Return the values of the different configuration files"""
        return self.confs
