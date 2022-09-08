#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

import time

from common.config.parser.fullparser import FullConfParser
from metrics.command_req import CommandReq

command_req = CommandReq()

class BackgroundMonitoring:
    """
    Background monitoring module
    """
    def parse_config(self):
        parser = FullConfParser()
        mon = parser.get("mon.yaml")
        metrics = mon.get("metrics")
        targets = metrics.get("targets")
        self.scrape_interval = targets.get("scrape_interval")

    def background_monitoring(self, request):
        self.parse_config()
        start_time = time.time()       
        monitoring_period = self.scrape_interval

        while True:
            data = command_req.metric_remote_command(request)
            sleep_time = monitoring_period - (
            (time.time() - start_time) % monitoring_period
            )
            time.sleep(sleep_time)
            print (data)
            
        return "OK"
            