# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""Manage a lock file"""

# standard libraires imports
import datetime
import logging
import os
import os.path
import sys


def populate_rss(entry):
    """populate the rss dict with the new entry"""
    if "id" in entry:
        logging.debug("found feed entry {entryid}".format(entryid=entry["id"]))
        rss = {
            "id": entry["id"],
        }
    elif "guid" in entry:
        logging.debug("found feed entry {entryid}".format(entryid=entry["guid"]))
        rss = {
            "id": entry["guid"],
        }
    else:
        logging.debug("found feed entry {entryid}".format(entryid=entry["link"]))
        rss = {
            "id": entry["link"],
        }
    return rss
