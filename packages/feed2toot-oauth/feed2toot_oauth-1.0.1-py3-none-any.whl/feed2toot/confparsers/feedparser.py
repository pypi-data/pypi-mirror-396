# -*- coding: utf-8 -*-
"""Get values of the feedparser section"""

# standard library imports
import sys


def parsefeedparser(config):
    """Parse configuration values and get values of the feedparser section"""
    section = "feedparser"
    option = "accept_bozo_exceptions"
    accept_bozo_exceptions = False
    if config.has_option(section, option):
        accept_bozo_exceptions = config.getboolean(section, option)
    return accept_bozo_exceptions
