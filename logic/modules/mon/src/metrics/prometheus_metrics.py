#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

import requests

from common.config.parser.fullparser import FullConfParser
from common.db.models.prometheus_targets import PrometheusTargets


class PrometheusMetrics():
    """
    Base class to retrieve metrics from the Prometheus server.
    """

    def __init__(self):
        self.general_conf = FullConfParser()
        self.mon_conf = self.general_conf.get("mon.yaml")
        self.mon_category = self.mon_conf.get("prometheus")
        self.prometheus_server_endpoint = "{}://{}:{}".format(
            self.mon_category.get("protocol"),
            self.mon_category.get("host"),
            self.mon_category.get("port"),
        )
        self.prometheus_query_endpoint = "{}/{}".format(
            self.prometheus_server_endpoint,
            self.mon_category.get("query_endpoint")
        )

    def prometheus_metrics(self, request):
        # Obtain values from request
        request_body = request.json
        target_id = request_body.get("vnf-id")
        instance = request_body.get("vnf-ip")
        metric_name = request_body.get("metric-name")

        targets_list = PrometheusTargets.objects.order_by("-id").first().targets
        if target_id in targets_list:
            # Execute the request
            self.client_query = "{}{}".format(
                self.prometheus_query_endpoint, metric_name)
            try:
                metrics_data = requests.get(self.client_query)
                metrics_json = metrics_data.json()
                result = metrics_json["data"]["result"]
                # Obtain vnf_index
                vnf_list = []
                for i in result:
                    vnf_list.append(i["metric"]["instance"])
                vnf_index = vnf_list.index(target_id)
                # Create metrics_dict
                metrics_dict = {
                    "vnf-id": target_id,
                    "metric-name": metric_name,
                    "metric-value": "",
                }
                try:
                    metric_value = result[vnf_index]["value"]
                    metrics_dict["metric-value"] = metric_value

                except KeyError:
                    # Print temporal, para pruebas.
                    print("Cannot obtain given metric from instance={}".format(instance))
                    metrics_dict["metric-value"] = "N/A"
                return metrics_dict
            except:
                return "Prometheus server is not running"
        else:
            return "{} target is not registered".format(target_id)
