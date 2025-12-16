# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
"""Manage a lock file"""

# standard libraires imports
import datetime
import logging
import os
import os.path
import sys


def sort_entries(is_all, cache, entries):
    """sort entries before sending"""
    totweet = []
    if not is_all:
        for i in entries:
            if "id" in i:
                if i["id"] not in cache.getdeque():
                    totweet.append(i)
            elif "guid" in i:
                if i["guid"] not in cache.getdeque():
                    totweet.append(i)
            else:
                # if id or guid not in the entry, use link
                if i["link"] not in cache.getdeque():
                    totweet.append(i)
    else:
        totweet = entries
    return totweet
