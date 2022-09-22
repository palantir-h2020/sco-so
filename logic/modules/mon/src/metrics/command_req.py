#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.db.models.alerts.alerts_metrics import AlertsMetrics
from common.config.parser.fullparser import FullConfParser
from common.db.models.prometheus_targets import PrometheusTargets
from common.db.models.custom_metrics import CustomMetrics
from datetime import datetime
from .execute_command import ExecuteCommand


class CommandReq():
    """
    Executes an UNIX-like command on remote xNFs
    """
    def parse_config(self):
        parser = FullConfParser()
        mon = parser.get("mon.yaml")
        metrics = mon.get("metrics")
        targets = metrics.get("targets")
        self.allowed_commands = targets.get("allowed_commands")

    def metric_remote_command(self, request):
        self.parse_config()
        request_body = request.json
        self.xnf_id = request_body.get("xnf-id")
        xnf_ip = request_body.get("xnf-ip")
        self.metric_name = request_body.get("metric-name")
        self.metric_command = request_body.get("metric-command")

        targets_list = PrometheusTargets.objects.order_by("-id")\
            .first().targets
        if self.xnf_id in targets_list:

            parsed_metric_command = self.metric_command.split(";")
            parsed_metric_command1 = parsed_metric_command[0].split("&&")
            parsed_metric_command2 = parsed_metric_command1[0].split(" ")

            if parsed_metric_command2[0] in self.allowed_commands:
                self.data = ExecuteCommand.execute_command(
                    xnf_ip, parsed_metric_command1[0]
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
                    self.persist_metric_remote_command()
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
            err_message = "{} target is not registered".format(self.xnf_id)
            err = {"Error": err_message}
            return err

    def persist_metric_remote_command(self):
        custom_metric = CustomMetrics()
        custom_metric.xnf_id = self.xnf_id
        custom_metric.metric_name = self.metric_name
        custom_metric.metric_command = self.metric_command
        custom_metric.data = self.data
        custom_metric.date = datetime.now()
        custom_metric.save()

    def mongodb_alerts_metrics(self):
        alerts_metrics = AlertsMetrics()
        alerts_metrics.xnf_id = self.xnf_id
        alerts_metrics.metric_name = self.metric_name
        alerts_metrics.metric_command = self.metric_command
        alerts_metrics.data = self.data
        alerts_metrics.date = datetime.now()
        alerts_metrics.save()
