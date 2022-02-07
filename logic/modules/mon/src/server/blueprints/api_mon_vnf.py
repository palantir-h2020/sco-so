#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
from flask import Blueprint, request
from handlers.node_exporter_setup import NodeExporterSetup
from metrics.background_mon import BackgroundMonitoring
from metrics.command_req import CommandReq
from metrics.execute_command import ExecuteCommand
from metrics.metrics import Metrics
from metrics.prometheus_metrics import PrometheusMetrics
from metrics.pushgateway import Pushgateway
from server.logic.prometheus_targets import PrometheusTarget
from server.logic.vnf import VNF

background_mon = BackgroundMonitoring()
command_request = CommandReq()
execute_command = ExecuteCommand()
metrics_ = Metrics()
node = NodeExporterSetup()
prometheus_targets_handler = PrometheusTarget()
prometheus_metrics = PrometheusMetrics()
pushgateway = Pushgateway()
so_blueprints = Blueprint("so__mon__vnf", __name__)


@so_blueprints.route("/mon/vnf", methods=["GET"])
def vnf_list() -> HttpResponse:
    data = VNF.vnf_list()
    return HttpResponse.infer(data, HttpCode.OK)


@so_blueprints.route("/mon/targets", methods=["GET"])
def targets_list() -> HttpResponse:
    data = {"targets": prometheus_targets_handler.targets_list()}
    data = {"results": data}
    return HttpResponse.infer(data, HttpCode.OK)


@so_blueprints.route("/mon/targets", methods=["POST", "PUT", "DELETE"])
def targets_handle() -> HttpResponse:
    return_code = prometheus_targets_handler.update_target(request)
    return HttpResponse.infer("OK", return_code)


@so_blueprints.route("/mon/targets/metrics", methods=["GET"])
def vnf_metrics() -> HttpResponse:
    vnf_id = request.args.get("vnf-id")
    metric_name = request.args.get("metric-name")
    data = [
        metrics_.exporter_metrics(vnf_id, metric_name),
        metrics_.mongodb_metrics(vnf_id, metric_name),
        metrics_.mongodb_pushgateway_metrics(vnf_id, metric_name),
    ]
    data = {"results": data}
    return HttpResponse.infer(data, HttpCode.OK)


@so_blueprints.route("/mon/metrics", methods=["GET"])
def vnf_metrics_handle() -> HttpResponse:
    data = prometheus_metrics.prometheus_metrics(request)
    return HttpResponse.infer(data, HttpCode.OK)


@so_blueprints.route("/mon/metrics/vnf", methods=["POST"])
def vnf_metrics_request() -> HttpResponse:
    try:
        data = pushgateway.persist_metric_prometheus_pushgateway(request)
    except Exception:
        data = command_request.metric_remote_command(request)
    return HttpResponse.infer(data, HttpCode.OK)


@so_blueprints.route("/mon/metrics/node", methods=["POST", "DELETE"])
def vnf_metrics_node() -> HttpResponse:
    data = node.manual_install_uninstall_exporter(request)
    data = {"results": data}
    return HttpResponse.infer(data, HttpCode.OK)


@so_blueprints.route("/mon/metrics/background", methods=["POST"])
def background() -> HttpResponse:
    data = background_mon.background_monitoring(request)
    return HttpResponse.infer(data, HttpCode.OK)
