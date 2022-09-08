#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from datetime import datetime
from common.db.models.alerts.alerts_metrics import AlertsMetrics
from common.config.parser.fullparser import FullConfParser
from common.db.models.prometheus_targets import PrometheusTargets
from common.db.models.metrics.custom_metrics import CustomMetrics
from .execute_command import ExecuteCommand
from prometheus_client import CollectorRegistry, Gauge, pushadd_to_gateway


class Pushgateway():
    """
    Executes a remote command on xNFs and persists it on Prometheus
    Pushgateway
    """

    def parser(self):
        general_conf = FullConfParser()
        mon_conf = general_conf.get("mon.yaml")
        metrics = mon_conf.get("metrics")
        targets = metrics.get("targets")
        self.allowed_commands = targets.get("allowed_commands")
        mon_category = mon_conf.get("prometheus")
        pushgateway_conf = mon_category.get("pushgateway")
        self.pushgateway_server_endpoint = "{}://{}:{}".format(
            pushgateway_conf.get("protocol"),
            pushgateway_conf.get("host"),
            pushgateway_conf.get("port"),
        )

    def persist_response_mongodb(self):
        pushgateway_response_model = CustomMetrics()
        pushgateway_response_model.xnf_id = self.nf_id
        pushgateway_response_model.metric_name = self.metric_name
        pushgateway_response_model.metric_command = self.metric_command
        pushgateway_response_model.data = self.data
        pushgateway_response_model.date = datetime.now()
        pushgateway_response_model.save()

    def mongodb_alerts_metrics(self):
        alerts_metrics = AlertsMetrics()
        alerts_metrics.vnf_id = self.vnf_id
        alerts_metrics.metric_name = self.metric_name
        alerts_metrics.metric_command = self.metric_command
        alerts_metrics.data = self.data
        alerts_metrics.date = datetime.now()
        alerts_metrics.save()

    def persist_metric_prometheus_pushgateway(self, request):

        request_body = request.json
        self.xnf_id = request_body.get("xnf-id")
        self.xnf_ip = request_body.get("xnf-ip")
        self.metric_name = request_body.get("metric-name")
        self.metric_command = request_body.get("metric-command")

        targets_list = PrometheusTargets.objects.order_by("-id")\
            .first().targets
        if self.xnf_id in targets_list:
            self.parser()

            parsed_metric_command = self.metric_command.split(";")
            parsed_metric_command1 = parsed_metric_command[0].split("&&")
            parsed_metric_command2 = parsed_metric_command1[0].split(" ")

            if parsed_metric_command2[0] in self.allowed_commands:
                self.data = ExecuteCommand.execute_command(
                    self.xnf_ip, parsed_metric_command1[0]
                )
                self.result = {
                    "xnf-id": self.xnf_id,
                    "metric-name": self.metric_name,
                    "metric-command": parsed_metric_command1[0],
                    "data": self.data,
                }
                so_pol = "__so_pol__"
                if so_pol in self.metric_name:
                    self.mongodb_alerts_metrics()
                else:
                    self.persist_response_mongodb()

                registry = CollectorRegistry()
                g = Gauge(self.metric_name, self.metric_name,
                          registry=registry)
                g.set(self.data)
                try:
                    pushadd_to_gateway("localhost:9091", job=self.xnf_ip,
                                       registry=registry)
                except Exception:
                    return "{} {}. {}".format(
                        self.pushgateway_server_endpoint,
                        "Pushgateway is not reachable.",
                        "Please check the connection"
                    )
                return self.result
            else:
                self.result = {
                    "xnf-id": self.xnf_id,
                    "metric-name": self.metric_name,
                    "metric-command": self.metric_command,
                    "data": "Command not allowed",
                }
                return self.result
        else:
            return "{} target is not registered".format(self.xnf_id)
