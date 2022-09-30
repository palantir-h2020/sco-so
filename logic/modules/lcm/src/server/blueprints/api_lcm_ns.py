#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT

from common.exception import exception
from common.nfv.nfv.ns import OSMInterfaceNS
from common.server.endpoints import SOEndpoints
from flask import Blueprint, request
import json


so_blueprints = Blueprint("so__lcm__ns", __name__)


def check_req_data_valid(request_content):
    if request_content is not None and len(request_content) > 0:
        return True
    return False


@so_blueprints.route(SOEndpoints.LCM_NS, methods=["GET"])
@exception.handle_exc_resp
def list_ns():
    _id = request.args.get("id")
    ns_obj = OSMInterfaceNS()
    return ns_obj.get_nsr_running(_id)


@so_blueprints.route(SOEndpoints.LCM_NS, methods=["POST"])
@exception.handle_exc_resp
def instantiate_ns():
    request_params = request.form.to_dict()
    try:
        request_params["ns-action-params"] = json.loads(
            request_params.get("ns-action-params"))
    except Exception:
        pass
    ns_obj = OSMInterfaceNS()
    return ns_obj.instantiate_ns(request_params)


@so_blueprints.route(SOEndpoints.LCM_NS, methods=["DELETE"])
@exception.handle_exc_resp
def delete_ns():
    _id = request.args.get("id")
    _force = request.args.get("force")
    try:
        _force = bool(_force)
    except Exception:
        pass
    ns_obj = OSMInterfaceNS()
    return ns_obj.delete_ns(_id, _force)


@so_blueprints.route(SOEndpoints.LCM_NS_ACT, methods=["GET"])
@exception.handle_exc_resp
def fetch_actions_on_ns():
    _ns_id = request.args.get("ns-id")
    _action_id = request.args.get("action-id")
    ns_obj = OSMInterfaceNS()
    return ns_obj.fetch_actions_in_ns(_ns_id, _action_id)


@so_blueprints.route(SOEndpoints.LCM_NS_ACT, methods=["POST"])
@exception.handle_exc_resp
def trigger_action_on_ns():
    _ns_id = request.args.get("id")
    _wait_for = None
    if "wait-for" in request.args.keys():
        _wait_for = request.args.get("wait-for")
    request_params = request.form.to_dict()
    try:
        request_params["ns-action-params"] = json.loads(
            request_params.get("ns-action-params"))
    except Exception:
        pass
    ns_obj = OSMInterfaceNS()
    return ns_obj.apply_action(_ns_id, request_params, _wait_for)


@so_blueprints.route(SOEndpoints.LCM_NS_HLT, methods=["GET"])
@exception.handle_exc_resp
def fetch_healthcheck_for_ns():
    _id = request.args.get("id")
    ns_obj = OSMInterfaceNS()
    return ns_obj.fetch_healthcheck_for_ns(_id)
