# -*- coding: utf-8 -*-
"""Get value of the addtags option of the rss section"""

# standard library imports
import logging
import sys


def parseaddtags(config):
    """Parse configuration value of the addtags option of the rss section"""
    addtags = True
    section = "rss"
    if config.has_section(section):
        if config.has_option(section, "addtags"):
            try:
                addtags = config.getboolean(section, "addtags")
            except ValueError as err:
                logging.warn(err)
                addtags = True
    return addtags
