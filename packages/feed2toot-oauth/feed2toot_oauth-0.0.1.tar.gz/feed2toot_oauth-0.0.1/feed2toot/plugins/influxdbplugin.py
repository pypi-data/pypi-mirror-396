# -*- coding: utf-8 -*-
"""Push values to a influxdb database"""

# 3rd party libraries imports
from influxdb import InfluxDBClient


class InfluxdbPlugin(object):
    """InfluxdbPlugin class"""

    def __init__(self, plugininfo, data):
        """Constructor of the InfluxdbPlugin class"""
        self.plugininfo = plugininfo
        self.data = data
        self.datatoinfluxdb = []
        self.client = InfluxDBClient(
            self.plugininfo["host"],
            self.plugininfo["port"],
            self.plugininfo["user"],
            self.plugininfo["pass"],
            self.plugininfo["database"],
        )
        self.main()

    def main(self):
        """Main of the PiwikModule class"""
        self.datatoinfluxdb.append(
            {
                "measurement": self.plugininfo["measurement"],
                "fields": {"value": self.data},
            }
        )
        self.client.write_points(self.datatoinfluxdb)
