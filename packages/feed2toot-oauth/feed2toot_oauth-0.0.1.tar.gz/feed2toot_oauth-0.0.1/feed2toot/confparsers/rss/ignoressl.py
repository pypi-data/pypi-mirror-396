# -*- coding: utf-8 -*-
"""Get values of the ignoressl option of the rss section"""

# standard library imports
import ssl


def parseignoressl(config, ignore_ssl_from_cli):
    """Parse configuration values and get values of the feedparser section"""
    section = "rss"
    option = "ignore_ssl"
    if config.has_option(section, option):
        ignoressl = config.getboolean(section, option)
    else:
        ignoressl = ignore_ssl_from_cli
    return ignoressl
