# -*- coding: utf-8 -*-
"""Get values of the lock section"""

# standard library imports
import os.path
import sys


def parselock(lockfile, locktimeout, config):
    """Parse configuration values and get values of the hashtaglist section"""
    lockfile = lockfile
    locktimeout = locktimeout
    section = "lock"
    ##################
    # lockfile option
    ##################
    confoption = "lock_file"
    if config.has_section(section):
        lockfile = config.get(section, confoption)
    lockfile = os.path.expanduser(lockfile)
    lockfileparent = os.path.dirname(lockfile)
    if lockfileparent and not os.path.exists(lockfileparent):
        sys.exit(
            "The parent directory of the lock file does not exist: {lockfileparent}".format(
                lockfileparent=lockfileparent
            )
        )
    ######################
    # lock_timeout option
    ######################
    if config.has_section(section):
        confoption = "lock_timeout"
        if config.has_option(section, confoption):
            try:
                locktimeout = int(config.get(section, confoption))
            except ValueError as err:
                sys.exit(
                    "Error in configuration with the {confoption} parameter in [{section}]: {err}".format(
                        confoption=confoption, section=section, err=err
                    )
                )
    return lockfile, locktimeout
