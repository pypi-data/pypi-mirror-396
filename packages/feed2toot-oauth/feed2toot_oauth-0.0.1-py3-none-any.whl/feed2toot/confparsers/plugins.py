# -*- coding: utf-8 -*-
"""Get values of the plugins section"""

# standard library imports
import sys


def parseplugins(config):
    """Parse configuration values and get values of the plugins section"""
    plugins = {}
    section = "influxdb"
    if config.has_section(section):
        ##########################################
        # host, port, user, pass, database options
        ##########################################
        plugins[section] = {}
        for currentoption in [
            "host",
            "port",
            "user",
            "pass",
            "database",
            "measurement",
        ]:
            if config.has_option(section, currentoption):
                plugins[section][currentoption] = config.get(section, currentoption)
        if "host" not in plugins[section]:
            plugins[section]["host"] = "127.0.0.1"
        if "port" not in plugins[section]:
            plugins[section]["port"] = 8086
        if "measurement" not in plugins[section]:
            plugins[section]["measurement"] = "toots"
        for field in ["user", "pass", "database"]:
            if field not in plugins[section]:
                sys.exit(
                    "Parsing error for {field} in the [{section}] section: {field} is not defined".format(
                        field=field, section=section
                    )
                )
    return plugins
