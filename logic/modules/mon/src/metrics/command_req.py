#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.config.parser.fullparser import FullConfParser
from common.db.models.prometheus_targets import PrometheusTargets
from common.db.models.remote_command import RemoteCommand
from datetime import datetime
from .execute_command import ExecuteCommand


class CommandReq():
    """
    Executes an UNIX-like command on remote VNFs
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
        self.vnf_id = request_body.get("vnf-id")
        vnf_ip = request_body.get("vnf-ip")
        self.metric_name = request_body.get("metric-name")
        self.metric_command = request_body.get("metric-command")

        targets_list = PrometheusTargets.objects.order_by("-id")\
            .first().targets
        if self.vnf_id in targets_list:

            parsed_metric_command = self.metric_command.split(";")
            parsed_metric_command1 = parsed_metric_command[0].split("&&")
            parsed_metric_command2 = parsed_metric_command1[0].split(" ")

            if parsed_metric_command2[0] in self.allowed_commands:
                self.data = ExecuteCommand.execute_command(
                    vnf_ip, parsed_metric_command1[0]
                )
                self.result = {
                    "vnf-id": self.vnf_id,
                    "metric-name": self.metric_name,
                    "metric-command": parsed_metric_command1[0],
                    "data": self.data,
                }
                self.persist_metric_remote_command()
                return self.result
            else:
                self.result = {
                    "vnf-id": self.vnf_id,
                    "metric-name": self.metric_name,
                    "metric-command": self.metric_command,
                    "data": "Command not allowed",
                }
                return self.result
        else:
            return "{} target is not registered".format(self.vnf_id)

    def persist_metric_remote_command(self):
        remote_metric_model = RemoteCommand()
        remote_metric_model.vnf_id = self.vnf_id
        remote_metric_model.metric_name = self.metric_name
        remote_metric_model.metric_command = self.metric_command
        remote_metric_model.data = self.data
        remote_metric_model.date = datetime.now()
        remote_metric_model.save()
