#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

import json
import requests
from requests.models import Response

class AlertsMetricsList():
    """
    Retrieve list of registered metrics related with alerts
    """
    def retrieve_registered_metric_alerts(self, xnf_id, metric_name):
        xnf_id_arg = "?xnf-id={}".format(xnf_id)
        metric_name_arg = "?metric-name={}".format(metric_name)
        all_args = "?xnf-id={}&metric-name={}".format(xnf_id, metric_name)
        no_args = ""
        if (xnf_id is None) and (metric_name is None):
            args = no_args
        else:
            if metric_name is None:
                args = xnf_id_arg
            else:
                if xnf_id is None:
                    args = metric_name_arg
                else:
                    args = all_args
       
        self.mon_alerts = "http://localhost:50106/mon/metrics/alerts{}".format(args)
        
        registered_alerts = requests.get(self.mon_alerts)
        if isinstance(registered_alerts, Response):
            status = registered_alerts.status_code
            registered_alerts = registered_alerts._content
            if isinstance(registered_alerts, bytes):
                registered_alerts = registered_alerts.decode("ascii")
        if isinstance(registered_alerts, str):
            try:
                registered_alerts = json.loads(registered_alerts)
            except:
                pass
        return registered_alerts
