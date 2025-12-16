# -*- coding: utf-8 -*-
"""Get value of the toot/tweet option of the rss section"""

# standard library imports
import sys
import logging


def parsetoot(config):
    """Parse configuration value of the toot/tweet optionof the rss section"""
    section = "rss"
    if config.has_section(section):
        ############################
        # tweet option
        ############################
        oldconfoption = "tweet"
        confoption = "toot"
        # manage 'tweet' for compatibility reason with first versions
        if config.has_option(section, oldconfoption):
            logging.warn(
                "Your configuration file uses a 'tweet' parameter instead of 'toot'. 'tweet' is deprecated and will be removed in Feed2toot 0.7"
            )
            tootformat = config.get(section, oldconfoption)
        elif config.has_option(section, confoption):
            tootformat = config.get(section, confoption)
        else:
            sys.exit(
                'You should define a format for your tweet with the parameter "{confoption}" in the [{section}] section'.format(
                    confoption=confoption, section=section
                )
            )
    return tootformat
