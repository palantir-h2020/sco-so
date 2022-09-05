#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

import requests

class AlertsMetricsRegister:
    """
    Registration of alerts related to metrics
    """
    def __init__(self) -> None:
        self.mon = "http://localhost:50106/mon/metrics/vnf"
        self.mon_bg = "http://localhost:50106/mon/metrics/background"
        pass
    def alert_metric_registration(self, request):
        request_body = request.json
        self.vnf_id = request_body.get("vnf-id")
        self.vnf_ip = request_body.get("vnf-ip")
        self.metric_name = request_body.get("metric-name")
        self.metric_command = request_body.get("metric-command")
        requests.post(
            self.mon,
            "",
            {
                "vnf-id": self.vnf_id,
                "vnf-ip": self.vnf_ip,
                "metric-name": self.metric_name,
                "metric-command": self.metric_command,
            },
        )
        requests.post(
            self.mon_bg,
            "",
            {
                "vnf-id": self.vnf_id,
                "vnf-ip": self.vnf_ip,
                "metric-name": self.metric_name,
                "metric-command": self.metric_command,
            },
        )
        return "OK"
