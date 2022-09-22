#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from alerts.alerts import Alerts
from alerts.alerts_metrics import AlertsMetricsRegister
from alerts.alerts_metrics_list import AlertsMetricsList
from alerts.alerts_register import AlertsRegister
from alerts.events import Events
from alerts.webhook import WebHook
from common.server.http.http_code import HttpCode
from common.server.http.http_response import HttpResponse
from flask import Blueprint, request


so_blueprints = Blueprint("so__pol__base", __name__)
alerts_ = Alerts()
alerts_metrics_list = AlertsMetricsList()
alerts_registration = AlertsRegister()
alerts_metrics_registration = AlertsMetricsRegister()
events = Events()
web_hook = WebHook()


@so_blueprints.route("/pol", methods=["GET"])
def base() -> HttpResponse:
    data = {"name": "pol_api"}
    return HttpResponse.infer(data, HttpCode.OK)


@so_blueprints.route("/pol/alerts", methods=["GET"])
def alerts() -> HttpResponse:
    data = alerts_.retrieve_registered_alerts()
    return HttpResponse.infer(data, HttpCode.OK)
# curl http://localhost:50108/pol/alerts


@so_blueprints.route("/pol/alerts", methods=["POST", "PUT", "DELETE"])
def alerts_register() -> HttpResponse:
    data = alerts_registration.registration(request)
    return HttpResponse.infer(data, HttpCode.OK)
# curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:50108/pol/alerts -d '{"alert-name": "__so_pol__alert", "threshold": "2", "operator": "==", "time-validity": "5", "hook-type": "kafka/webhook", "hook-endpoint": "alerts"}'
# PUT, DELETE

@so_blueprints.route("/pol/metrics", methods=["GET"])
def alerts_metrics() -> HttpResponse:
    xnf_id = request.args.get("xnf-id")
    metric_name = request.args.get("metric-name")
    data = alerts_metrics_list.retrieve_registered_metric_alerts(xnf_id, metric_name)
    return HttpResponse.infer(data, HttpCode.OK)
# curl http://localhost:50108/pol/metrics


@so_blueprints.route("/pol/metrics", methods=["POST"])
def alerts_metrics_register() -> HttpResponse:
    data = alerts_metrics_registration.alert_metric_registration(request)
    return HttpResponse.infer(data, HttpCode.OK)
# curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:50108/pol/metrics -d '{"xnf-id": "172.28.2.27:9100", "xnf-ip": "172.28.2.27", "metric-name": "__so_pol__list", "metric-command": "ls"}'
# bg monitoring

@so_blueprints.route("/pol/events", methods=["POST"])
def alerts_events() -> HttpResponse:
    data = events.events(request)
    return HttpResponse.infer(data, HttpCode.OK)
# curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X POST http://127.0.0.1:50108/pol/events -d '{"alert-name": "__so_pol__date", "metric-name": "__so_pol__date"}'


@so_blueprints.route("/pol/notification", methods=["POST"])
def alerts_notification() -> HttpResponse:
    data = web_hook.notification_alert(request)
    return HttpResponse.infer(data, HttpCode.OK)
