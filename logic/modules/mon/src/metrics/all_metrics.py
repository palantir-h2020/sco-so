#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from common.config.parser.fullparser import FullConfParser
from common.db.models.remote_command import RemoteCommand
import requests


class AllMetrics():
    """
    Base class to retrieve all metrics from the Prometheus node exporter.
    """

    def all_exporter_metrics(self, request):
        request_body = request.json
        self.vnf_ip = request_body.get("vnf-ip")
        self.general_conf = FullConfParser()
        self.mon_conf = self.general_conf.get("mon.yaml")
        self.mon_category = self.mon_conf.get("prometheus")
        self.mon_subcategory = self.mon_category.get("exporter")
        self.exporter_endpoint = "{}://{}:{}".format(
            self.mon_subcategory.get("protocol"),
            self.vnf_ip,
            self.mon_subcategory.get("port"))
        self.exporter_query_endpoint = "{}/{}".format(
            self.exporter_endpoint,
            self.mon_subcategory.get("query_endpoint"))

        exporter_data = requests.get(self.exporter_query_endpoint)
        return exporter_data.text

    def all_mongodb_metrics(self):
        try:
            data_list = []
            for i in RemoteCommand.objects:
                data_list.append(RemoteCommand.objects.order_by("vnf_id").first().vnf_id)
                data_list.append(RemoteCommand.objects.order_by("metric_name").first().metric_name)
                data_list.append(RemoteCommand.objects.order_by("metric_command").first().metric_command)
                data_list.append(RemoteCommand.objects.order_by("data").first().data)
            return data_list
                 
        except Exception:
            return []
       