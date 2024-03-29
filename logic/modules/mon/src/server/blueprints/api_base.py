#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from alerts.alerts import Alerts
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


so_blueprints = Blueprint("so__mon__base", __name__)


alerts = Alerts()
background_mon = BackgroundMonitoring()
command_request = CommandReq()
execute_command = ExecuteCommand()
metrics_ = Metrics()
node = NodeExporterSetup()
prometheus_targets_handler = PrometheusTarget()
prometheus_metrics = PrometheusMetrics()
pushgateway = Pushgateway()


# FIXME look at logic/modules/lcm/src/server/blueprints:
# api_base.py
# api_lcm_ns.py
# api_lcm_vnf.py
# In api_base.py only this method below (/mon) should be
#
# Right now, some methods are being loaded twice => Repeated => Bad
# (Check logic/modules/mon/src/server/blueprints/api_mon_vnf.py)
# I have commented all methods there so far, but you must
# move methods in this module to other modules depending on their
# focus, like:
# api_mon_targets.py
# api_mon_metrics.py
# api_alerts.py
@so_blueprints.route("/mon", methods=["GET"])
def base() -> HttpResponse:
    data = {"name": "mon_api"}
    return HttpResponse.infer(data, HttpCode.OK)


# FIXME: start using SOEndpoints.* (and extending as needed). Check
# what is done in src/server/blueprints/api_mon_infra.py as example
# FIXME: remove these cURL calls from the source code everywhere
# These do not belong in a script but in the README!
@so_blueprints.route("/mon/targets", methods=["GET"])
def targets_list() -> HttpResponse:
    data = {
        "targets": prometheus_targets_handler.targets_list()
    }
    return HttpResponse.infer(data, HttpCode.OK)
# curl http://127.0.0.1:50106/mon/targets


@so_blueprints.route("/mon/targets", methods=["POST", "PUT", "DELETE"])
def targets_handle() -> HttpResponse:
    return_code = prometheus_targets_handler.update_target(request)
    return HttpResponse.infer(targets_list().json, return_code)
# curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:50106/mon/targets -d '{"url": "target-ip-or-fqdn:9090"}'
# curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X PUT http://127.0.0.1:50106/mon/targets -d '{"current-url": "target-ip-or-fqdn:9090", "new-url": "10.10.10.11:9090"}'
# curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X DELETE http://127.0.0.1:50106/mon/targets -d '{"url": "target-ip-or-fqdn:9090"}'


@so_blueprints.route("/mon/targets/metrics", methods=["GET"])
def xnf_metrics() -> HttpResponse:
    xnf_id = request.args.get("xnf-id")
    metric_name = request.args.get("metric-name")
    data = {
        "generic": metrics_.exporter_metrics(xnf_id, metric_name),
        "custom": metrics_.mongodb_metrics(xnf_id, metric_name)
    }
    return HttpResponse.infer(data, HttpCode.OK)
# curl http://127.0.0.1:50106/mon/targets/metrics 


# FIXME: GET methods shall have no payload
# Instead, these must be like:
# -X GET http://127.0.0.1:50106/mon/metrics?xnf-id=172.28.2.27:9100&xnf-ip=172.28.2.27&metric-name=node_disk_info
@so_blueprints.route("/mon/metrics", methods=["GET"])
def xnf_metrics_handle() -> HttpResponse:
    data = prometheus_metrics.prometheus_metrics(request)
    return HttpResponse.infer(data, HttpCode.OK)
# curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X GET http://127.0.0.1:50106/mon/metrics -d '{"xnf-id": "172.28.2.27:9100", "xnf-ip": "172.28.2.27", "metric-name": "node_disk_info"}'

@so_blueprints.route("/mon/metrics/xnf", methods=["POST"])
def xnf_metrics_request() -> HttpResponse:
    try:
        data = pushgateway.persist_metric_prometheus_pushgateway(request)
    except:
        data = command_request.metric_remote_command(request)
    return HttpResponse.infer(data, HttpCode.OK)
# curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:50106/mon/metrics/xnf -d '{"xnf-id": "172.28.2.27:9100", "xnf-ip": "172.28.2.27", "metric-name": "ls", "metric-command": "ls"}'


@so_blueprints.route("/mon/metrics/node", methods=["POST", "DELETE"])
def xnf_metrics_node() -> HttpResponse:
    data = node.manual_install_uninstall_exporter(request)
    data = {"results": data}    
    return HttpResponse.infer(data, HttpCode.OK)
# curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:50106/mon/metrics/node -d '{"xnf-ip": ["172.28.2.27"]}'
# curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X DELETE http://127.0.0.1:50106/mon/metrics/node -d '{"xnf-ip": ["172.28.2.27"]}'


@so_blueprints.route("/mon/metrics/alerts", methods=["GET"])
def xnf_metrics_alerts() -> HttpResponse:
    xnf_id = request.args.get("xnf-id")
    metric_name = request.args.get("metric-name")
    data = alerts.retrieve_registered_alerts(xnf_id, metric_name)
    return HttpResponse.infer(data, HttpCode.OK)
# curl http://127.0.0.1:50106/mon/metrics/alerts

@so_blueprints.route("/mon/metrics/background", methods=["POST"])
def background() -> HttpResponse:
    data = background_mon.background_monitoring(request)
    return HttpResponse.infer(data, HttpCode.OK)
# curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:50106/mon/metrics/background -d '{"xnf-id": "172.28.2.27:9100", "xnf-ip": "172.28.2.27", "metric-name": "ls", "metric-command": "ls"}'
