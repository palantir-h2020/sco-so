#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

import requests

class AlertsMetricsRegister:
    """
    Registration of alerts related to metrics
    """
    def __init__(self) -> None:
        self.mon = "http://so-mon:50106/mon/metrics/xnf"
        self.mon_bg = "http://so-mon:50106/mon/metrics/background"
        pass
    def alert_metric_registration(self, request):
        request_body = request.json
        self.xnf_id = request_body.get("xnf-id")
        self.xnf_ip = request_body.get("xnf-ip")
        self.metric_name = request_body.get("metric-name")
        self.metric_command = request_body.get("metric-command")
        requests.post(
            self.mon,
            "",
            {
                "xnf-id": self.xnf_id,
                "xnf-ip": self.xnf_ip,
                "metric-name": self.metric_name,
                "metric-command": self.metric_command,
            },
        )
        requests.post(
            self.mon_bg,
            "",
            {
                "xnf-id": self.xnf_id,
                "xnf-ip": self.xnf_ip,
                "metric-name": self.metric_name,
                "metric-command": self.metric_command,
            },
        )
        message = {"Message": "Process done correctly"}
        return message
