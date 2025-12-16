# -*- coding: utf-8 -*-
"""Get values of the media section"""

# standard library imports
import os.path
import sys


def parsemedia(config):
    """Parse configuration values and get values of the media section"""
    mediaconf = {}
    section = "media"
    ####################################
    # media option
    ####################################
    confoption = "custom"
    if config.has_section(section):
        if config.has_option(section, confoption):
            media = config.get(section, confoption)
            media = os.path.expanduser(media)
            if not os.path.exists(media) or not os.path.isfile(media):
                sys.exit(
                    "The path to the custom parameter is not valid: {media}".format(
                        media=media
                    )
                )
            else:
                mediaconf[confoption] = media
    return mediaconf
