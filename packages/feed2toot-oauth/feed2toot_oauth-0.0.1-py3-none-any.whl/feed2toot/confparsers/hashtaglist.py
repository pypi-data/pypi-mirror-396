# -*- coding: utf-8 -*-
"""Get values of the hashtaglist section"""

# standard library imports
import os.path
import sys


def parsehashtaglist(clioption, config):
    """Parse configuration values and get values of the hashtaglist section"""
    hashtaglist = ""
    section = "hashtaglist"
    if not clioption:
        ####################################
        # several_words_hashtags_list option
        ####################################
        confoption = "several_words_hashtags_list"
        if config.has_section(section):
            if config.has_option(section, confoption):
                hashtaglist = config.get(section, confoption)
                hashtaglist = os.path.expanduser(hashtaglist)
                if not os.path.exists(hashtaglist) or not os.path.isfile(hashtaglist):
                    sys.exit(
                        "The path to the several_words_hashtags_list parameter is not valid: {hashtaglist}".format(
                            hashtaglist=hashtaglist
                        )
                    )
    return hashtaglist
