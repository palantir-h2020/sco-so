#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

class WebHook():
    """
    Notification when an alarm start
    """
    def notification_alert(self, request):
        request_body = request.json
        vnf_id = request_body.get("vnf-id")
        metric_name = request_body.get("metric-name")
        data = request_body.get("data")
        threshold = request_body.get("threshold")
        alert_name = request_body.get("alert-name")

        print ("Alert: {}, vnf-id: {}, related to the metric: {}, threshold: {}, data: {}".format(alert_name, vnf_id, metric_name, threshold, data))
