# -*- coding: utf-8 -*-
"""Get values of the cache section"""

# standard library imports
import os.path
import sys


def parsecache(clioption, config):
    """Parse configuration values and get values of the hashtaglist section"""
    cachefile = ""
    cachelimit = 100
    section = "cache"
    if not clioption:
        ##################
        # cachefile option
        ##################
        confoption = "cachefile"
        if config.has_section(section):
            cachefile = config.get(section, confoption)
        else:
            sys.exit(
                "You should provide a {confoption} parameter in the [{section}] section".format(
                    section=section, confoption=confoption
                )
            )
        cachefile = os.path.expanduser(cachefile)
        cachefileparent = os.path.dirname(cachefile)
        if cachefileparent and not os.path.exists(cachefileparent):
            sys.exit(
                "The parent directory of the cache file does not exist: {cachefileparent}".format(
                    cachefileparent=cachefileparent
                )
            )
    else:
        cachefile = clioption
    ####################
    # cache_limit option
    ####################
    if config.has_section(section):
        confoption = "cache_limit"
        if config.has_option(section, confoption):
            try:
                cachelimit = int(config.get(section, confoption))
            except ValueError as err:
                sys.exit(
                    "Error in configuration with the {confoption} parameter in [{section}]: {err}".format(
                        confoption=confoption, section=section, err=err
                    )
                )
        else:
            cachelimit = 100
    return cachefile, cachelimit
