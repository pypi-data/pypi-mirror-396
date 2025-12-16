# -*- coding: utf-8 -*-
"""Get values of the no_tags_in_toot option of the hashtaglist section"""


def parsenotagsintoot(config):
    """Parse configuration values and get values of the the no_tags_in_toot option of the hashtaglist section"""
    section = "hashtaglist"
    option = "no_tags_in_toot"
    notagsintoot = False
    if config.has_option(section, option):
        notagsintoot = config.getboolean(section, option)
    return notagsintoot
