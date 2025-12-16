# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""Manage a cache with the ids of the feed entries"""

# standard libraires imports
from collections import deque
import os
import os.path


class FeedCache:
    """FeedCache class"""

    def __init__(self, options):
        """Constructore of the FeedCache class"""
        self.options = options
        self.main()

    def getdeque(self):
        """return the deque"""
        return self.dbfeed

    def main(self):
        """Main of the FeedCache class"""
        if os.path.exists(self.options["cachefile"]):
            with open(self.options["cachefile"]) as dbdsc:
                dbfromfile = dbdsc.readlines()
            dblist = [i.strip() for i in dbfromfile]
            self.dbfeed = deque(dblist, self.options["cache_limit"])
        else:
            self.dbfeed = deque([], self.options["cache_limit"])

    def append(self, rssid):
        """Append a rss id to the cache"""
        self.dbfeed.append(rssid)

    def close(self):
        """Close the cache"""
        with open(self.options["cachefile"], "w") as dbdsc:
            dbdsc.writelines(("".join([i, os.linesep]) for i in self.dbfeed))
