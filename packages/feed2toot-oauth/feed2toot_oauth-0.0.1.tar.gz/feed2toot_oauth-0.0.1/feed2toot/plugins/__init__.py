#!/usr/bin/env python3
# vim:ts=4:sw=4:ft=python:fileencoding=utf-8
import importlib


def activate_plugins(plugins, finaltweet):
    """activate plugins"""
    for plugin in plugins:
        capitalizedplugin = plugin.title()
        pluginclassname = "{plugin}Plugin".format(plugin=capitalizedplugin)
        pluginmodulename = "feed2toot.plugins.{pluginmodule}".format(
            pluginmodule=pluginclassname.lower()
        )
        try:
            pluginmodule = importlib.import_module(pluginmodulename)
            pluginclass = getattr(pluginmodule, pluginclassname)
            pluginclass(plugins[plugin], finaltweet)
        except ImportError as err:
            print(err)
