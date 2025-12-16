# -*- coding: utf-8 -*-
"""Get value of the toot/tweet option of the rss section"""

# standard library imports
import sys
import logging


def parsetootmaxlen(config):
    """Parse configuration value of the toot_max_len option of the rss section"""
    section = "rss"
    tootmaxlen = 500
    if config.has_section(section):
        ############################
        # toot_max_len parameter
        ############################
        confoption = "toot_max_len"
        if config.has_option(section, confoption):
            try:
                tootmaxlen = int(config.get(section, confoption))
            except ValueError as err:
                sys.exit(
                    "Error in configuration with the {confoption} parameter in [{section}]: {err}".format(
                        confoption=confoption, section=section, err=err
                    )
                )
    return tootmaxlen
